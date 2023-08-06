import contextlib
import datetime
import gzip
import json
import logging
import pathlib
import threading
import time
import traceback
from enum import Enum
from queue import Queue
from typing import Union, List
from celery import shared_task
from celery.result import allow_join_result
from flask import current_app
from invenio_access.permissions import system_identity
from invenio_db import db
from werkzeug.utils import import_string

from oarepo_oaipmh_harvester.oaipmh_config.proxies import current_service as config_service
from oarepo_oaipmh_harvester.oaipmh_record.proxies import current_service as record_service
from .oaipmh_run.proxies import current_service as run_service
from .oaipmh_batch.proxies import current_service as batch_service
from oarepo_oaipmh_harvester.loaders import sickle_loader, filesystem_loader
from oarepo_oaipmh_harvester.models import OAIHarvesterConfig, OAIHarvestRun, OAIHarvestRunBatch
from oarepo_oaipmh_harvester.parsers import IdentityParser
from oarepo_oaipmh_harvester.proxies import current_harvester
from oarepo_oaipmh_harvester.transformer import OAIRecord
from .uow import BulkUnitOfWork

log = logging.getLogger('oarepo.oai.harvester')

from tqdm import tqdm


@shared_task
def oai_harvest(harvester_id: str, start_from: str, load_from: str = None, dump_to: str = None,
                on_background=False, identifiers=None):
    """
    @param harvester_id: id of the harvester configuration (OAIHarvesterConfig) object
    @param start_from: datestamp (either YYYY-MM-DD or YYYY-MM-DDThh:mm:ss,
           depends on the OAI endpoint), inclusive
    @param load_from: if set, a path to the directory on the filesystem where
           the OAI-PMH data are present (in *.json.gz files)
    @param dump_to: if set, harvested metadata will be parsed from xml to json
           and stored into this directory, not to the repository
    @param on_background: if True, transformation and storage will be started in celery tasks and can run in parallel.
           If false, they will run sequentially inside this task
    @param identifiers: if load_from is set, it is a list of file names within the directory.
           If load_from is not set, these are oai identifiers for GetRecord. If not set at all, all records from
           start_from are harvested
    """
    harvester = Harvester(harvester_id, on_background, load_from, dump_to)
    harvester.harvest(start_from, identifiers)

class HarvestStatus(Enum):
    RUNNING = 'R'
    FINISHED = 'O'
    WARNING = 'W'
    FAILED = 'E'
    INTERRUPTED = 'I'

def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
        millis = int(
            calendar.timegm(obj.timetuple()) * 1000 +
            obj.microsecond / 1000
        )
        return millis
    raise TypeError('Not sure how to serialize %s' % (obj,))
class Harvester:
    def __init__(self, harvester_id: str, on_background=False, load_from: str = None, dump_to: str = None):
        # self.harvester = OAIHarvesterConfig.query.get(harvester_id)
        self.harvester = config_service.read(system_identity, harvester_id).data
        self.harvester_id = harvester_id
        self.on_background = on_background
        self.load_from = load_from
        self.dump_to = dump_to
        self.app = current_app._get_current_object()
        self.loading_queue = Queue(maxsize=50)
        self.loading_task_thread = threading.Thread(target=lambda self: self.loading_task(), args=[self])
        self.loader_factory = None
        self.harvester_processes = []
        self.max_harvested_processes = 10

    def harvest(self, start_from: str, identifiers: Union[List[str], None] = None):
        print(f'harvesting {self.harvester["metadata"]["code"]} from {start_from}, identifiers {identifiers}')
        self.run = run_service.create(system_identity, {"metadata": {"harvester_id": self.harvester_id, "started":json.dumps(datetime.datetime.now(), default=default), "status": "R"}})
        # self.run = OAIHarvestRun(harvester_id=self.harvester_id,
        #                          started=datetime.datetime.now(),
        #                          status=HarvestStatus.RUNNING)
        # db.session.add(self.run)
        # db.session.commit()
        self.run_id = self.run['id']


        try:
            self.loader_factory = lambda: self.get_loader(start_from, identifiers)
            self.loading_task_thread.start()

            first = True
            last_record_timestamp = None

            def yielder():
                while True:
                    batch_idx, oai_records = self.loading_queue.get()
                    if batch_idx is None:
                        break
                    yield batch_idx, oai_records

            with tqdm(unit=' records') as q:
                for batch_idx, oai_records in yielder():
                    first_record_datestamp, last_record_datestamp = self.parse_and_save_records(batch_idx, oai_records)
                    if first:
                        first = False
                        # first_record_datestamp = first_record_datestamp[0:10]
                        self.run['metadata']['first_datestamp'] = first_record_datestamp
                        # self.run['metadata']['first_datestamp'] = json.dumps(first_record_datestamp, default= default)
                        # db.session.add(self.run)
                        # db.session.commit() #update!!
                        run_service.update(system_identity, self.run_id, {'metadata': self.run['metadata']})
                    q.update(len(oai_records))
            # last_record_datestamp = last_record_datestamp[0:10]
            self.run['metadata']['last_datestamp'] = last_record_datestamp

            error = False

            for hit in (batch_service.read_all(system_identity, ['metadata']).to_dict())['hits']['hits']:
                if hit['metadata']['run_id'] ==self.run_id and hit['metadata']['status'] == 'E':
                    error = True
                    break

            # error_count = OAIHarvestRunBatch.query.filter_by(run_id=self.run_id, status=HarvestStatus.FAILED).count()
            self.run['metadata']['status'] = "E" if error else "O"
            self.run['metadata']['finished'] = json.dumps(datetime.datetime.now(), default=default)
            run_service.update(system_identity, self.run_id, {'metadata': self.run['metadata']})
            # db.session.add(self.run)
            # db.session.commit()
        except KeyboardInterrupt:
            self.run['metadata']['status'] = 'I'
            self.run['metadata']['finished'] = json.dumps(datetime.datetime.now(), default=default)
            run_service.update(system_identity, self.run_id, {'metadata': self.run['metadata']})
            # db.session.add(self.run)
            # db.session.commit()
            raise
        except Exception as e:
            print(e)
            log.exception("Generic error in harvest, saving it to Run object")
            traceback.print_exc()
            # TODO: check transaction and fix any problem before saving

            # db.session.merge(self.run)
            self.run['metadata']['status'] = 'E'
            self.run['metadata']['finished'] = json.dumps(datetime.datetime.now(), default=default)
            self.run['metadata']['exception'] = ''.join(traceback.TracebackException.from_exception(e, capture_locals=False).format())
            run_service.update(system_identity, self.run_id, {'metadata': self.run['metadata']})

            # db.session.add(self.run)
            # db.session.commit()

        self.loading_task_thread.join()

    def loading_task(self):
        with self.app.app_context():
            loader = self.loader_factory()
            for batch_idx, batch in enumerate(loader):
                self.loading_queue.put((batch_idx, batch))
            self.loading_queue.put((None, None))

    def parse_and_save_records(self, batch_idx, oai_records):
        parser = self.get_parser()
        deleted_records = []
        updated_records = []
        records = []
        first_record_datestamp = None
        last_record_datestamp = None
        for x in oai_records:
            r = parser.parse(x)
            records.append(r)
        if records:
            first_record_datestamp = records[0]['datestamp']
            last_record_datestamp = records[-1]['datestamp']
        if self.dump_to:
            path = pathlib.Path(self.dump_to)
            path.mkdir(parents=True, exist_ok=True)
            with gzip.open(path / f'{batch_idx:08d}.json.gz', 'wt') as f:
                json.dump(records, f, indent=4, ensure_ascii=False)
            return

        for r in records:
            if r['deleted']:
                deleted_records.append(r)
            else:
                updated_records.append(r)

        if deleted_records:
            self.delete_records(batch_idx, deleted_records)
        else:
            self.update_records(batch_idx, updated_records)

        return first_record_datestamp, last_record_datestamp

    def delete_records(self, batch_idx, deleted_records):
        if self.on_background:
            res = oaipmh_delete_records_task.delay(self.harvester_id, self.run_id, batch_idx, deleted_records)
        else:
            res = oaipmh_delete_records_task.apply(args=(self.harvester_id, self.run_id, batch_idx, deleted_records))
        self.register_harvested_process(res)

    def update_records(self, batch_idx, updated_records):
        if self.on_background:
            res = oaipmh_update_records_task.delay(self.harvester_id, self.run_id, batch_idx, updated_records)
        else:
            res = oaipmh_update_records_task.apply(args=(self.harvester_id, self.run_id, batch_idx, updated_records))
        self.register_harvested_process(res)

    def register_harvested_process(self, res):
        self.harvester_processes.append(res)
        while len(self.harvester_processes) >= self.max_harvested_processes:
            running_processes = []
            for p in self.harvester_processes:
                if p.ready():
                    with allow_join_result():
                        p.get()
                else:
                    running_processes.append(p)
            self.harvester_processes = running_processes
            if len(self.harvester_processes) >= self.max_harvested_processes:
                time.sleep(1)

    def get_loader(self, start_from: str, identifiers: Union[List[str], None] = None):
        # need to get the harvester as we are in a different thread

        harvester = config_service.read(system_identity, self.harvester_id).data
        # harvester = OAIHarvesterConfig.query.get(self.harvester_id)
        # terminate the session - sqlite3 problem with locking
        # db.session.expunge(harvester)
        # db.session.rollback()
        if self.load_from:
            return filesystem_loader(harvester, self.load_from, identifiers)
        else:
            return sickle_loader(harvester, start_from, identifiers)

    def get_parser(self):
        if self.load_from:
            return IdentityParser(self.harvester)

        try:
            parser_class = self.harvester['metadata']['parser']
        except:
            parser_class = None
        if parser_class:
            parser_class = import_string(parser_class)
        else:
            parser_class = current_harvester.get_parser(self.harvester['metadata']['metadataprefix'])
        return parser_class(self.harvester)


@contextlib.contextmanager
def in_batch(run_id):

    batch = batch_service.create(system_identity, {'metadata' : {'run_id': run_id, 'started':json.dumps(datetime.datetime.now(), default=default),
                                                                 'status':'R' }})
    # batch = OAIHarvestRunBatch(run_id=run_id,
    #                            started=datetime.datetime.now(),
    #                            status=HarvestStatus.RUNNING)
    # db.session.add(batch)
    # db.session.commit()

    try:

        yield batch
        if batch['metadata']['status'] == 'R':
            batch['metadata']['status'] = 'O'



        batch['metadata']['finished'] = json.dumps(datetime.datetime.now(), default=default)

        # db.session.add(batch)
        # db.session.commit()

        batch_service.update(system_identity, batch['id'], {'metadata': batch['metadata']})

    except Exception as e:
        print(e)
        log.exception("Error in batch transformation & saving")
        # TODO: check transaction and fix any problem before saving
        # db.session.add(batch)
        batch['metadata']['status'] = 'E'
        batch['metadata']['finished'] = json.dumps(datetime.datetime.now(), default=default)
        # batch.add_exception(e)
        message = ''.join(traceback.TracebackException.from_exception(e, capture_locals=False).format())
        if not e:
            e = message
        else:
            e += "\n" + message
        batch['metadata']['exception'] = message
        batch_service.update(system_identity, batch['id'], {'metadata': batch['metadata']})

        # db.session.commit()


@shared_task
def oaipmh_delete_records_task(harvester_id, run_id, batch_id, records):
    with in_batch(run_id) as batch:

        # harvester = OAIHarvesterConfig.query.get(harvester_id)
        harvester = config_service.read(system_identity, harvester_id).data

        # run = OAIHarvestRun.query.get(run_id)
        run = run_service.read(system_identity, run_id).data

        records = [OAIRecord(x) for x in records]
        transformer = import_string(harvester['metadata']['transformer'])
        transformer_instance = transformer(harvester, run)
        transformer_instance.transform_deleted(records, batch)
        try:
            nested = db.session.begin_nested()
            uow = BulkUnitOfWork(session=nested)
            transformer_instance.delete(records, batch, uow)
            uow.commit()
        except Exception as e:
            # session already rolled back
            message = ''.join(traceback.TracebackException.from_exception(e, capture_locals=False).format())
            if not e:
                e = message
            else:
                e += "\n" + message
            batch['metadata']['exception'] = message
            batch['metadata']['status'] = 'E'
            batch_service.update(system_identity, batch['id'], {'metadata': batch['metadata']})
            # batch.add_exception(e)


@shared_task
def oaipmh_update_records_task(harvester_id, run_id, batch_id, records):
    with in_batch(run_id) as batch:

        # harvester = OAIHarvesterConfig.query.get(harvester_id)
        harvester = config_service.read(system_identity, harvester_id).data

        # run = OAIHarvestRun.query.get(run_id)
        run = run_service.read(system_identity, run_id).data

        transformer = import_string(harvester['metadata']['transformer'])
        transformer_instance = transformer(harvester, run)

        records = [OAIRecord(x) for x in records]
        transformer_instance.transform(records, batch)
        ok_records = []
        record_query = record_service.scan(system_identity, params={'facets': {'metadata_batch_id': [batch['id']]}})
        try:
            record_query = list(record_query.hits)
        except:
            record_query = []
        for rec in records:
            not_in_query = True
            for r in record_query:
                if r['metadata']['identifier'] == rec.identifier:
                    not_in_query = False
                    break
            if not_in_query or r['metadata']['status'] != 'E':
            # if 'failed_records' not in batch['metadata'] or rec.identifier not in batch['metadata']['failed_records']:
                ok_records.append(rec)
                unprocessed = rec.unprocessed
                if unprocessed:
                    log.error("identifier %s, unprocessed %s", rec.identifier, unprocessed)
                            # batch.record_warning(rec.identifier,
                            #              'unprocessed_properties',
                            #              f'unprocessed properties {unprocessed}',
                            #              properties=unprocessed)
                    batch['metadata']['status'] = 'W'
                    batch_service.update(system_identity, batch['id'], {'metadata': batch['metadata']})
                    record_service.create(system_identity, {'metadata': {'identifier': rec.identifier,'batch_id': batch['id'],'status': 'W', 'warning': str(unprocessed)}})


                else:
                    record_service.create(system_identity, {'metadata': {'identifier': rec.identifier,'batch_id': batch['id'],'status': 'O'}})

        try:
            nested = db.session.begin_nested()
            uow = BulkUnitOfWork(session=nested)
            transformer_instance.save(ok_records, batch, uow)
            uow.commit()
        except Exception as e:
            # session already rolled back
            message = ''.join(traceback.TracebackException.from_exception(e, capture_locals=False).format())
            if not e:
                e = message
            else:
                e = str(e)
                e += "\n" + message
            batch['metadata']['exception'] = message
            batch['metadata']['status'] = 'E'
            batch_service.update(system_identity, batch.id, {'metadata': batch['metadata']})
            # batch.add_exception(e)

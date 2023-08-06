import os
from typing import Callable, List, Type

from redis.client import Redis

from sync.backends.redislinkprovider import RedisLinkProvider
from demo.fixtures import populate_daphne, daphne_sqa_ds, desire_sqa_ds, populate_desire
from demo.celery.app import app
from celery.signals import worker_init
from sync.datasource import DataSource
from sync.mapping import Mapping
from sync.syncer import Syncer


def create_syncer(left_ds, right_ds, mappings):
    redis_link_provider = RedisLinkProvider(host="redis")
    syncer = Syncer(
        left_ds=left_ds,
        right_ds=right_ds,
        mappings=mappings,
        link_provider=redis_link_provider,
    )
    return syncer


@app.task
def sync_all(
    left_ds_producer: Callable[[], DataSource],
    right_ds_producer: Callable[[], DataSource],
    mappings: List[Mapping],
):
    syncer = create_syncer(left_ds_producer(), right_ds_producer(), mappings)
    return syncer.sync_all()


@app.task
def sync_one(
    left_ds_producer: Callable[[], DataSource],
    right_ds_producer: Callable[[], DataSource],
    mappings: List[Mapping],
    type: Type,
    id: str,
):
    syncer = create_syncer(left_ds_producer(), right_ds_producer(), mappings)
    return syncer.sync_entity(type, id)


# initialize desire and daphne
@worker_init.connect
def startup(**kwargs):
    cleanup()
    initialize()


def cleanup():
    Redis(host="redis").flushdb()
    if os.path.exists("/tmp/daphne.sqlite"):
        os.remove("/tmp/daphne.sqlite")
    if os.path.exists("/tmp/desire.sqlite"):
        os.remove("/tmp/desire.sqlite")


def initialize():
    populate_daphne(daphne_sqa_ds())
    populate_desire(desire_sqa_ds())

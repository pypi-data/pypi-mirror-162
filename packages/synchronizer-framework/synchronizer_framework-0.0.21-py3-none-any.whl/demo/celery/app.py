import os

from celery import Celery

from demo.fixtures import (
    make_mappings,
    populate_daphne,
    populate_desire,
    desire_sqa_ds,
    daphne_sqa_ds,
)

app = Celery(
    "synchronizer",
    broker="amqp://rabbitmq",
    backend="rpc://",
    include=["demo.celery.tasks"],
)

app.conf.update(result_expires=3600)
app.conf.task_serializer = "pickle"
app.conf.accept_content = ["pickle"]
app.conf.result_serializer = "pickle"
app.conf.result_accept_content = ["pickle"]

app.conf.beat_schedule = {
    "every-10-sec": {
        "schedule": 10,
        "task": "demo.celery.tasks.sync_all",
        "args": (daphne_sqa_ds, desire_sqa_ds, make_mappings()),
    }
}

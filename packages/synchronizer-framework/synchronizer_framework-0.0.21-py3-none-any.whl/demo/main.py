import sys

from demo.fixtures import (
    make_mappings,
    daphne_ds,
    desire_ds,
    populate_daphne,
    populate_desire,
    cleanup,
)
from sync.datasource import DataSource
from sync.syncer import Syncer

sys.path.append("src/")

import logging
from pprint import pformat


def main():
    logging.basicConfig(level=logging.INFO)
    logging.getLogger("sqlalchemy.engine").setLevel(level=logging.ERROR)

    cleanup()
    mappings = make_mappings()
    daphne_db = daphne_ds()
    desire_db = desire_ds()
    populate_daphne(daphne_db)
    populate_desire(desire_db)

    logging.info("Initial DB states")
    logging.info(show_db(desire_db))
    logging.info(show_db(daphne_db))

    syncer = Syncer(daphne_db, desire_db, mappings)
    operations = syncer.sync_all()
    logging.info(f"{len(operations)} operation(s) made")
    logging.info(f"Operations: {pformat(operations)}")

    logging.info("DB states after first and before second run")
    logging.info(show_db(desire_db))
    logging.info(show_db(daphne_db))

    operations = syncer.sync_all()
    logging.info(f"Sync with {len(operations)} operation(s) made")
    logging.info(f"Operations: {pformat(operations)}")

    logging.info("🙌 Final DB states")
    logging.info(show_db(desire_db))
    logging.info(show_db(daphne_db))

    operations = syncer.sync_all()
    logging.info(f"Sync with {len(operations)} operations made.")
    logging.info(f"Operations: {pformat(operations)}")
    if len(operations) == 0:
        logging.info("🎉🥳 Synchronization has converged.")
    else:
        logging.warning("Synchronization should have converged. Something is wrong.")


def show_db(ds: DataSource):
    return pformat(
        {
            entity_type: ds.all(entity_type, limit=10)
            for entity_type in ds.entity_types()
        }
    )


if __name__ == "__main__":
    main()

from demo.daphne import VlanServiceProvider
from demo.fixtures import daphne_sqa_ds, desire_sqa_ds, make_mappings
from sync import tasks

if __name__ == "__main__":
    ds = daphne_sqa_ds()
    vlsp = VlanServiceProvider(name="test")
    ds.create(vlsp)

    tasks.sync_one.delay(
        daphne_sqa_ds, desire_sqa_ds, make_mappings(), vlsp.__class__, vlsp.id
    )

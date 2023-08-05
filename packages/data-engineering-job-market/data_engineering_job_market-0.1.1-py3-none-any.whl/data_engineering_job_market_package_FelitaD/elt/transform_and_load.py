from data_engineering_job_market_package_FelitaD.elt.transform.transform import transform
from data_engineering_job_market_package_FelitaD.elt.load.load import Loader


def transform_and_load():
    pivotted_jobs = transform()

    loader = Loader(pivotted_jobs)
    loader.load()

transform_and_load()
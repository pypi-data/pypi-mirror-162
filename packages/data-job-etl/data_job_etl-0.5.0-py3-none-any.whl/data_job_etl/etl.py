from data_job_etl.transform.transform import transform
from data_job_etl.load.load import Loader


def transform_and_load():
    pivotted_jobs = transform()

    loader = Loader(pivotted_jobs)
    loader.load()

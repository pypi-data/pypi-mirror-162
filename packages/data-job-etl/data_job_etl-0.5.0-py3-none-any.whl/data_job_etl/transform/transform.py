import pandas as pd
import os

from data_job_etl.config.definitions import PROJECT_PATH, DATA_PATH
from data_job_etl.transform.preprocess import Preprocessor
# from ner_technos.ner_preprocessor import NERPreprocessor
# from ner_technos.train_model import NERTrainer
from data_job_etl.transform.process_technos import TechnosProcessor


def transform():
    # Preprocess columns such as title, text, etc.
    preprocessor = Preprocessor(number_of_jobs=None)
    preprocessor.preprocess()

    # Extract technologies from the text column.
    techno_processor = TechnosProcessor(preprocessor.jobs)
    processed_jobs = techno_processor.process_technos()

    return processed_jobs

# def run_ner():
    # preprocessor.jobs.to_csv(os.path.join(DATA_PATH, 'preprocessed_jobs.csv'))
    # jobs = pd.read_csv(os.path.join(DATA_PATH, 'preprocessed_jobs.csv'))
    
    # techno_recogniser = NERPreprocessor(preprocessor.jobs)
    # techno_recogniser.prepare_training()
    #
    # ner_trainer = NERTrainer()
    # ner_trainer.init_config()
    # ner_trainer.train()


# if __name__ == '__main__':
#
#     transform()

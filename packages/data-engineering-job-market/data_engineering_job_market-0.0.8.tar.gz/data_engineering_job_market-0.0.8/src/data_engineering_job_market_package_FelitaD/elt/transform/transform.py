import pandas as pd
import os

from data_engineering_job_market_package_FelitaD.config.definitions import PROJECT_PATH, DATA_PATH
from data_engineering_job_market_package_FelitaD.elt.transform.preprocess import Preprocessor
# from ner_technos.ner_preprocessor import NERPreprocessor
# from ner_technos.train_model import NERTrainer
from data_engineering_job_market_package_FelitaD.elt.transform.process_technos import TechnosProcessor


def transform():
    # Preprocess columns such as title, text, etc.
    preprocessor = Preprocessor(number_of_jobs=None)
    preprocessor.preprocess()
    # print('Preprocessed jobs :\n', preprocessor.jobs.head())

    # Extract technologies from the text column.
    techno_processor = TechnosProcessor(preprocessor.jobs)
    processed_jobs = techno_processor.process_technos()
    # print('Processed jobs (with technos) :\n', processed_jobs[['title', 'company', 'technos']][:10])

    # Write new dataframe to csv.
    processed_jobs.to_csv(os.path.join(DATA_PATH, 'pivotted.csv'))

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

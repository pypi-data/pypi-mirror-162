import os
from typing import Union, Any
from os.path import exists
import csv
import shutil
from dsframework.base.trainer.pl_wrapper import Dataset, IterableDataset, random_split, transforms, datasets
from comparison import generatedProjectNameComparison
from config import config
from data import generatedProjectNameData
from model import generatedProjectNameModel
from test import generatedProjectNameTest
from train import generatedProjectNameTrain
from tester.general_tester import generatedProjectNameGeneralTester

##
# @file
# @brief TrainerMain class.
class TrainerMain:
    """! Trainer main class, this is where all training components orchestrate.

    Its main job is to run:
    - training - train the model using train dataset and validation dataset.
    - testing - running model against test dataset.
    - eval - running the same test dataset

    Important node:
    It includes a split() method, which needs to be implemented. This is where the dataset gets split to
    train, validation and test datasets.

    """
    general_config = None
    trainer_config = None

    def __init__(self, cfg, dataset: Union[IterableDataset, Dataset, Any] = None):
        """! Trainer main initializer."""
        self.save_path = None
        self.train_class = None
        self.model_class = None
        self.data_class = None
        self.data_class_test = None
        self.test_class = None
        self.general_config = cfg['general_config']
        self.trainer_config = cfg['trainer_config']
        self.metrics_config = cfg['metrics']
        self.dataset = dataset
        self.dataset_train = None
        self.dataset_validation = None
        self.dataset_test = None
        self.eval_res = None
        self.split()

    def split(self):
        """! Implement this method to split between the different datasets:
        For the trainer supply: dataset_train, self.dataset_validation
        For test supply: self.dataset_test

        For example:
            self.dataset = datasets.MNIST(os.getcwd() + '/datasets', download=True, train=True,
                                      transform=transforms.ToTensor())
            self.dataset_train, self.dataset_validation = random_split(self.dataset, [55000, 5000])
            self.dataset_test = datasets.MNIST(os.getcwd() + '/datasets', download=True, train=False,
                                           transform=transforms.ToTensor())
        """

        raise 'Dataset TrainerMain.split() not implemented exception.'

    def save_dataset(self, dataset_path):
        """! Saves a copy of the dataset in /training_output/v1 folder zipped.

        In a later stage the trained model is created in the same folder, so we have a pair of the model and the
        dataset used to create it.
        """
        if not self.general_config['save_dataset']:
            return

        if os.path.isdir(dataset_path):
            if os.listdir(dataset_path):
                shutil.make_archive(os.path.join(self.save_path, 'dataset'), 'zip', dataset_path)

    def execute_trainer(self):
        """ Executes training process. it initializes the main 3 trainer modules:

        generatedProjectNameData - Class for holding datasets and functionality related to dataset handling
        generatedProjectNameModel - Network definition and all functionality related to creating the model.
        generatedProjectNameTrain - Execute trainer and all trainer related functionality.
        """

        self.save_path = self._create_save_path()
        self.save_dataset(os.getcwd() + '/datasets')

        self.data_class = generatedProjectNameData(dataset_train=self.dataset_train,
                                                   dataset_validation=self.dataset_validation,
                                                   save_path=self.save_path)
        self.model_class = generatedProjectNameModel(self.general_config, self.metrics_config)
        self.train_class = generatedProjectNameTrain(
            trainer_config=self.trainer_config,
            general_config=self.general_config,
            data_module=self.data_class.get_data_module(),
            model=self.model_class.get_model(),
            save_path=self.save_path)

        self.train_class.execute()

    def execute_test(self, model_path):
        """ Executes test process. runs the model against a test dataset.

        Initializes:
            generatedProjectNameData - Created with test dataset.
            generatedProjectNameTest - Loads model and executes test.

        Args:
            model_path: Path to saved model
        Returns:
            mmodel_test_results: Metrics - defined in config.
        """

        self.data_class_test = generatedProjectNameData(dataset_test=self.dataset_test)

        self.test_class = generatedProjectNameTest(
            data_module=self.data_class_test.get_data_module(),
            model_path=model_path,
            trainer_config=self.trainer_config)

        model_test_results = self.test_class.execute_test()

        return model_test_results

    def execute_eval(self):
        """ Executes evaluation process on an existing model against a test dataset.

        Notes:
            Test dataset must be in Pandas dataframe format.

        Returns:
            eval_res - Evaluation metrics result.

        Result format example:
            self.eval_res = {'precision': 1.1, 'accuracy': 1.2, 'recall': 1.3, 'f1': 1.4,
                            'confusion_matrix': {'tp': 0, 'tn': 0, 'fp': 0, 'fn': 0}}
        """

        model_tester = generatedProjectNameGeneralTester()

        try:
            dataframe_ds = self.convert_to_dataframe(self.dataset_test)
            output_path = model_tester.test_from_dataset(dataframe_ds, 1)
            self.eval_res = self.get_eval_results(output_path)

        except Exception as e:
            print(f'Could not start evaluation process: {e}')

        return self.eval_res

    def get_eval_results(self, output_path):
        """Reads evaluation results from path and returns it.

        Args:
            output_path - Location of eval results

        Returns:
            evaluation results - In dictionary format.

        """
        if exists(output_path):
            return csv.DictReader(open(output_path))
        else:
            return None

    def convert_to_dataframe(self, dataset_test):
        """Conversion of test dataset to Pandas dataframe, to run evaluation process.

        Not implemented.
        """
        raise "To run evaluation, convert dataset tn pandas dataframe format, implement convert_to_dataframe()."

    def _create_save_path(self):
        """Create the next version folder (v1, v2, v3 ... vn) inside training_output folder.

        Returns:
            save_path - The newly created folder path.
        """

        current_folder = os.path.dirname(os.path.realpath(__file__))

        path = os.path.join(current_folder, 'training_output')

        if not os.path.exists(path):
            os.makedirs(path)

        all_folders = [file for file in os.listdir(path) if os.path.isdir(os.path.join(path, file))]

        if all_folders:
            num_list = [int(folder.replace('v', '')) for folder in all_folders if folder.replace('v', '').isdigit()]
            num_list.sort()
            new_version = num_list[-1] + 1
        else:
            new_version = 1

        save_path = os.path.join(path, f'v{new_version}')
        os.makedirs(save_path)

        return save_path

##
# @file
#
# @brief TrainerMain usage simulation.
if __name__ == '__main__':
    ## TrainerMain for training process
    trainer_main_class = TrainerMain(config, dataset=None)
    trainer_main_class.execute_trainer()

    ## Path to last saved model
    model_path = os.path.join(trainer_main_class.save_path, config['general_config']['model_name'])
    ## TrainerMain for testing process
    trainer_main_class_test = TrainerMain(config, dataset=None)
    test_results = trainer_main_class_test.execute_test(model_path=model_path)
    eval_results = trainer_main_class_test.execute_eval()

    ## The results of the comparison between trained model and existing model evaluation.
    comparison_results = generatedProjectNameComparison(
        test_results=test_results,
        eval_results=eval_results,
        metrics_config=config['metrics']).compare()

    print('comparison_results', comparison_results)

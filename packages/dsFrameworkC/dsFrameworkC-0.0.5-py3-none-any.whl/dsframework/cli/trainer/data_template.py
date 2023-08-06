from dsframework.base.trainer.data import ZIDSTrainerData
from trainer.pl_wrapper.data_module import generatedProjectNameDataModule

##
# @file
# @brief generatedClass class, Datasets and functionality related to datasets.
class generatedClass(ZIDSTrainerData):
    """generatedClass, holds datasets and functionality related to it."""
    dataset_train = None
    dataset_validation = None
    dataset_test = None
    data_module = None

    def __init__(self, dataset_train=None, dataset_validation=None, dataset_test=None, save_path=''):
        """generatedClass class initializer."""
        super().__init__(dataset_train, dataset_validation, dataset_test, save_path)

    def create_data_module(self):
        """! Creates data module in the format you use in the fit/train method. Called from super().__init__().

        Needs to be implemented.

        Example (pytorch lightning):
            self.data_module = generatedProjectNameDataModule(
            dataset=self.dataset_train,
            valid_set=self.dataset_validation,
            test_set=self.dataset_test)

            return self.data_module
        """
        if self.data_module is None:
            raise Exception('Implement data module in data.py -> create_data_module()')

    def get_data_module(self):
        """! Returns data module in the format you use in the fit/train method.

        Returns:
            data_module

        """
        if self.data_module is None:
            raise Exception('Implement data module in data.py -> create_data_module()')

        return self.data_module

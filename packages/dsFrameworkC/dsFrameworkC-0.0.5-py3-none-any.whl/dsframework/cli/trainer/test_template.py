from dsframework.base.trainer.test import ZIDSTrainerTest
from pl_wrapper.plmodel import generatedProjectNamePlmodel
from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief generatedClass class, executes test process.
class generatedClass(ZIDSTrainerTest):
    """! Test class, runs the model against a labeled test dataset to evaluate its metrics.

        Three things needs to be done for this to work:
            1. Receive data_module with labeled dataset loaded.
            2. Load model
            3. Create and Run trainer instance.
    """

    def __init__(self, data_module=None, model_path=None, trainer_config=None):
        """generatedClass Initializer.

        Runs trainer_setup() and load_model() methods/
        """
        super().__init__(data_module, model_path, trainer_config)
        self.trainer_setup(trainer_config)
        self.load_model(model_path)

    def trainer_setup(self, trainer_config):
        """! Instantiate trainer class

        Needs to be implemented.

        Example (pytorch lightning):
            self.trainer = pl.Trainer(**trainer_config)
        """

        if self.trainer is None:
            raise Exception('trainer_setup() method in test.py, not implement.')

    def load_model(self, model_path):
        """! Loads a model

        Needs to be implemented.

        Example (pytorch lightning):
            self.model = generatedProjectNamePlmodel.load_from_checkpoint(model_path)
        """

        if self.model is None:
            raise Exception('load_model() method in test.py, not implement.')

    def execute_test(self):
        """! Implement test process and return the results.

        Returns:
            test results - Metric results from test.

        Example (pytorch lightning):
            if self.model is None or self.data_module is None or self.trainer is None:
                return None
            self.trainer.test(self.model, self.data_module)
            return self.model.get_test_results()
        """

        raise Exception('Methods execute_test() not implemented in test.py.')

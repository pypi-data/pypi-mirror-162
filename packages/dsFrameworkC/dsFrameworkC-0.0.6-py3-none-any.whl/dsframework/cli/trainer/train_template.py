import os

from dsframework.base.trainer.train import ZIDSTrainClass
from dsframework.base.trainer.pl_wrapper import *

##
# @file
# @brief generatedClass class, executes training process.
class generatedClass(ZIDSTrainClass):
    """ Trainer class, responsible to execute training process and save the model."""

    def __init__(self, trainer_config=None, general_config=None, train_dataset=None, validation_dataset=None,
                 model=None, data_module=None, save_path=''):
        """ Train class initializer."""
        super().__init__(trainer_config, general_config, train_dataset, validation_dataset, model, data_module,
                         save_path)

    def execute(self):
        """ Execute the train process and saves the model.

        Needs to be implemented.

        Example (pytorch lightning):
            self.trainer = pl.Trainer(**self.trainer_config)
            self.trainer.fit(self.model, self.data_module)
        """

        if self.general_config['save_model']:
            self.save_model(os.path.join(self.save_path, self.general_config['model_name']))

        if self.trainer is None:
            raise Exception('Implement train process in train.py, execute() method.')

    def save_model(self, model_path):
        """ Saves the model, runs at the end of the training process.

        Needs to be implemented.

        Notes:
            Saves the last model, which doesn't mean it is the best model. If using pytorch lightning, use
            ModelCheckpoint callback to save the best model, callback defined in config.py.

        Example (pytorch lightning):
            if self.trainer is not None:
                self.trainer.save_checkpoint(model_path)
                print(message)
        """

        message = 'Saves the last model, which doesn\'t mean it is the best model. If using pytorch lightning, ' \
                  'use ModelCheckpoint callback to save the best model, callback defined in config.py.'

        raise 'train.py save_model() not implemented. ' + message

    def get_trainer(self):
        """Returns trainer instance."""
        return self.trainer

class ZIDSTrainerTest:

    trainer = None
    model = None
    data_module = None

    def __init__(self, data_module=None, model_path=None, trainer_config=None):
        self.data_module = data_module
        self.model_path = model_path

        self.trainer_setup(trainer_config)
        self.load_model(model_path)

    def trainer_setup(self, trainer_config):
        pass

    def load_model(self, model_path):
        pass

    def execute_test(self):
        self.trainer.test(self.model, self.data_module)

        return self.model.get_test_results()

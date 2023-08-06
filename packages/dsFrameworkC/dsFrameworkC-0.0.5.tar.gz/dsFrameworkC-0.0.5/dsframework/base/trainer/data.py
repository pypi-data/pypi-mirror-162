class ZIDSTrainerData:

    dataset_train = None
    dataset_validation = None
    dataset_test = None
    data_module = None
    save_path = ''

    def __init__(self, dataset_train=None, dataset_validation=None, dataset_test=None, save_path=''):
        self.dataset_train = dataset_train
        self.dataset_validation = dataset_validation
        self.dataset_test = dataset_test
        self.save_path = save_path

        self.create_data_module()

    def create_data_module(self):
        pass

    def get_data_module(self):

        self.data_module = None

        return self.data_module

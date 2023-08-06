class ZIDSTrainerModel:

    model = None
    config = None
    metrics_config = None

    def __init__(self, config, metrics_config):
        self.config = config
        self.metrics_config = metrics_config
        self.define_model()

    def define_model(self):
        self.model = None

    def get_model(self):
        return self.model

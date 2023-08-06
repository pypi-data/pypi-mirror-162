from dsframework.base.trainer.model import ZIDSTrainerModel
from trainer.pl_wrapper.plmodel import generatedProjectNamePlmodel

##
# @file
# @brief generatedClass class, defines model class.
class generatedClass(ZIDSTrainerModel):
    """Model class - defines the network, loss function etc."""
    model = None
    config = None
    metrics_config = None

    def __init__(self, config, metrics_config):
        super().__init__(config, metrics_config)
        self.metrics_config = metrics_config

    def define_model(self):
        """! Implement model class in the format you use in the fit/train method.
        Create a new model or load from pretrained model.

        Needs to be implemented.

        Example (pytorch lightning):
            self.model = generatedProjectNamePlmodel(
                loss_function=self.config['loss_function'],
                num_classes=self.config['num_classes'],
                num_classes_conf_matrix=self.config['num_classes_confusion_matrix'],
                learn_rate=self.config['learning_rate'],
                nnetwork=self.config['nnetwork'],  # Create a new model or load from pretrained model.
                metrics=self.metrics_config
            )
        """
        if self.model is None:
            raise Exception('Implement model in model.py')

    def get_model(self):
        """Returns model class"""
        return self.model

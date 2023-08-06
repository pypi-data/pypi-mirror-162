from abc import ABC, abstractmethod


class ModelConfig:

    def __init__(self, id, name, version, extra, path, model_package, model_class):
        self.path = path
        self.id = id
        self.name = name
        self.extra = extra
        self.version = version
        self.model_package = model_package
        self.model_class = model_class

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'version': self.version,
            'extra': self.extra,
            'path': self.path,
            'model_package': self.model_package,
            'model_class': self.model_class,
        }

    @staticmethod
    def from_dict(config_dict):

        return ModelConfig(
            id=config_dict['id'],
            name=config_dict['name'],
            version=config_dict['version'],
            extra=config_dict['extra'],
            path=config_dict['path'],
            model_package=config_dict['model_package'],
            model_class=config_dict['model_class']
        )


class BaseModel(ABC):

    @abstractmethod
    def save_model(self, path, model_id, version) -> ModelConfig:
        """
        Save model files
        :return: config dict
        """
        raise NotImplemented()

    @staticmethod
    @abstractmethod
    def load_model(config: ModelConfig):
        """

        :param config: dict with config
        :return:
        """
        raise NotImplemented()

    @abstractmethod
    def model_name(self) -> str:
        """
        :return: model name
        """
        raise NotImplemented()

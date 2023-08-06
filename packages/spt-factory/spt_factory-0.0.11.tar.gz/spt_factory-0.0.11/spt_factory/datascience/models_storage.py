from abc import ABC, abstractmethod
from importlib import import_module

from spt_factory.datascience.models.base_model import BaseModel, ModelConfig
from spt_factory.datascience.singleton import Singleton


class ModelStorage(metaclass=Singleton):

    @abstractmethod
    def save_model(self, path, model, model_id, version: int):
        pass

    @abstractmethod
    def load_model(self, model_id):
        pass

    @abstractmethod
    def load_model_config(self, model_id):
        pass


class MongoModelStorage(ModelStorage, metaclass=Singleton):

    def __init__(self, spt):
        self.mongo_client = spt.get_mongo()

    def save_model(self, path, model, model_id, version: int):
        model_config = model.save_model(path, model_id, version)
        return model_config

    def _load_model_object(self, model_package, model_class, model_config):
        module = import_module(model_package)
        return getattr(
            module, model_class
        ).load_model(model_config)

    def load_model(self, model_id):
        model_config_dict = self.mongo_client.spt.models.find_one({'id': model_id})
        model_config = ModelConfig.from_dict(model_config_dict)
        model_package = model_config.model_package
        model_class = model_config.model_class
        return self._load_model_object(model_package, model_class, model_config)

    def load_model_config(self, model_id):
        model_config_dict = self.mongo_client.spt.models.find_one({'id': model_id})
        model_config = ModelConfig.from_dict(model_config_dict)
        return model_config
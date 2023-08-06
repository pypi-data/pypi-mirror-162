from abc import ABC, abstractmethod
from hashlib import sha256

from spt_factory.datascience.model_util import ModelUtil
from spt_factory.datascience.models.base_model import BaseModel, ModelConfig
from functools import lru_cache
from spt_factory.datascience.singleton import Singleton
from spt_factory.datascience.models_storage import MongoModelStorage


class ModelManager(metaclass=Singleton):
    __slots__ = 'model_util', 'model_storage'

    def __init__(self, model_util, model_storage):
        self.model_util = model_util
        self.model_storage = model_storage

    @abstractmethod
    def get_model(self, model_id) -> BaseModel:
        """
        Return model object by id
        :param model_id: id of the model
        :return:
        """
        pass

    @abstractmethod
    def save_model(self, path,  model) -> str:
        """
        Save model and return model id
        :param model: model inherit from BaseModel
        :return: model id
        """
        pass

    @abstractmethod
    def get_model_config(self, model_id) -> ModelConfig:
        """
        Return model object by id
        :param model_id: id of the model
        :return:
        """
        pass

    @abstractmethod
    def save_model_config(self, model_config):
        """
        Save model config
        :param model: model inherit from BaseModel
        """
        pass


class SPTModelManager(ModelManager):

    def __init__(self, model_util: ModelUtil, model_storage: MongoModelStorage):
        super().__init__(model_util, model_storage)

    @lru_cache(maxsize=512)
    def get_model(self, model_id) -> BaseModel:
        return self.model_storage.load_model(
            model_id=model_id
        )

    def save_model(self, path, model: BaseModel) -> str:
        model_name = model.model_name()
        model_version = self.increment_model_version(
            self.model_util.get_model_version(model_name)
        )
        model_id = self.produce_model_id(model_name, model_version)
        model_config = self.model_storage.save_model(path, model, model_id, model_version)
        self.model_util.save_model_config(model_config)
        return model_id

    def produce_model_id(self, model_name, model_version):
        return sha256(f"{model_name}-{model_version}".encode("utf-8")).hexdigest()

    def increment_model_version(self, version):
        return version + 1

    def get_model_config(self, model_id):
        return self.model_storage.load_model_config(model_id)

    def save_model_config(self, model_config):
        self.model_util.save_model_config(model_config)
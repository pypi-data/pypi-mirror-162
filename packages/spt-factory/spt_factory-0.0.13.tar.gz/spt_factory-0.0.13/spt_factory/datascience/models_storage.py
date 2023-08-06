from abc import ABC, abstractmethod
from importlib import import_module

from spt_factory.datascience.models.base_model import BaseModel, ModelConfig
from spt_factory.datascience.singleton import Singleton

MODELS_BUCKET = 'theme-models'


class ModelStorage(metaclass=Singleton):

    @abstractmethod
    def save_model(self, model, model_id, version: int):
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

    def save_model(self, model, model_id, version: int):
        model_config = model.save_model(model_id, version)
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


class S3ModelStorage(ModelStorage, metaclass=Singleton):

    def __init__(self, spt):
        self.s3_client = spt.get_s3_manager()
        self.mongo_client = spt.get_mongo()

    def save_model(self, model, model_id, version: int):
        model_config = model.save_model(model_id, version)
        for bin_name, bin_obj in model_config.bins.items():
            model_path = model_config.id + '/' + bin_name
            self.s3_client.upload_bin(bucket_name=MODELS_BUCKET, id=model_path, bin_str=bin_obj)
            model_config.bins[bin_name] = model_path
        model_config.bins['s3_bucket'] = MODELS_BUCKET
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
        model_bins = model_config.bins
        model_bucket = MODELS_BUCKET
        for bin_name, bin_path in model_bins.items():
            model_bins[bin_name] = self.s3_client.download_bin(bucket_name=model_bucket, id=bin_path)
        model_config.bins = model_bins
        return self._load_model_object(model_package, model_class, model_config)

    def load_model_config(self, model_id):
        model_config_dict = self.mongo_client.spt.models.find_one({'id': model_id})
        model_config = ModelConfig.from_dict(model_config_dict)
        return model_config

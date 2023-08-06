from abc import ABC, abstractmethod
from spt_factory.resources import AnyCreds, ModelManagerResource, PipelineManagerResource, S3ManagerResource
from spt_factory.credentials import AnyMongoCredentials, ModelManagerCredentials, PipelineManagerCredentials
from spt_factory.resources import Postgres, Mongo
from spt_factory.credentials import PostgresMongoCredentials, MongoMongoCredentials, S3ManagerCredentials
from functools import partial


class Factory(ABC):

    @abstractmethod
    def get_resource_crede_pairs(self):
        pass

    @abstractmethod
    def get_crede_object(self, **factory_params):
        pass

    def __init__(self, **factory_params):
        self.factory_params = factory_params
        self.resources = {}
        for resource, credentials in self.get_resource_crede_pairs():

            def get_resource(resource, credentials, **params):
                c = credentials(
                    spt=self,
                    factory_params=self.factory_params,
                    custom_params=params
                )
                return resource(c).get_object()

            def get_credentials(credentials, **params):
                return credentials(
                    spt=self,
                    factory_params=self.factory_params,
                    custom_params=params
                ).get_credentials()

            setattr(self, f'get_{resource.get_name()}', partial(get_resource, resource=resource, credentials=credentials))
            setattr(self, f'get_{resource.get_name()}_credentials', partial(get_credentials, credentials=credentials))


class MongoFactory(Factory):

    def __init__(self, mongo_url, tlsCAFile):
        super().__init__(mongo_url=mongo_url, tlsCAFile=tlsCAFile)

    def get_crede_object(self):
        return Mongo(
            MongoMongoCredentials(
                spt=self,
                factory_params=self.factory_params,
                custom_params={}
            )
        ).get_object()

    def get_resource_crede_pairs(self):
        return (
            (Postgres, PostgresMongoCredentials),
            (Mongo, MongoMongoCredentials),
            (AnyCreds, AnyMongoCredentials),
            (ModelManagerResource, ModelManagerCredentials),
            (PipelineManagerResource, PipelineManagerCredentials),
            (S3ManagerResource, S3ManagerCredentials)
        )

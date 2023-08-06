from abc import ABC, abstractmethod


class Credentials(ABC):
    __slots__ = 'crede', 'crede_object', 'factory_params', 'custom_params', 'spt'

    def __init__(self, spt, factory_params, custom_params):
        self.spt = spt
        self.factory_params = factory_params
        self.custom_params = custom_params

    def get_credentials(self):
        return self.crede


class PostgresMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_crede_object() as mongo_client:
            postgres_crede = mongo_client.spt.credentials.find_one({"type": "postgres"})
        postgres_crede['sslrootcert'] = factory_params['tlsCAFile']
        del postgres_crede['_id']
        del postgres_crede['type']
        self.crede = postgres_crede
        self.crede.update(custom_params)


class MongoMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        self.crede = {
            'host': factory_params['mongo_url'],
            'tlsCAFile': factory_params['tlsCAFile']
        }
        self.crede.update(custom_params)


class AnyMongoCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        with spt.get_crede_object() as mongo_client:
            any_crede = mongo_client.spt.credentials.find_one({"type": custom_params.get('type', "undefined")})
        if any_crede is None:
            self.crede = {'type': custom_params.get('type', "undefined")}
        else:
            del any_crede['_id']
            del custom_params['type']
            self.crede = any_crede
            self.crede.update(custom_params)


class ModelManagerCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        self.crede = dict(spt=spt)


class PipelineManagerCredentials(Credentials):

    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)
        self.crede = dict(spt=spt)


class S3ManagerCredentials(Credentials):
    def __init__(self, spt, factory_params, custom_params):
        super().__init__(spt, factory_params, custom_params)

        with spt.get_crede_object() as mongo_client:
            s3_crede = mongo_client.spt.credentials.find_one({"type": "theme-s3"})
        del s3_crede['_id']
        del s3_crede['type']
        self.crede = s3_crede
        self.crede.update(custom_params)

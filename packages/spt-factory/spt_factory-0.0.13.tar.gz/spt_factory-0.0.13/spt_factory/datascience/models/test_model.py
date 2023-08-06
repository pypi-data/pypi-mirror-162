from spt_factory.datascience import BaseModel, ModelConfig


class TestModel(BaseModel):

    def save_model(self, path, model_id, version) -> ModelConfig:
        return ModelConfig(
            path='mongo',
            id=model_id,
            version=version,
            name=self.model_name(),
            extra={},
            model_package=self.__module__,
            model_class=self.__class__.__name__,
            bins={
                'greeting': self.greeting.encode('utf-8')
            }
        )

    @staticmethod
    def load_model(config: ModelConfig):
        return TestModel(
            greeting=config.bins['greeting'].decode('utf-8')
        )

    def model_name(self) -> str:
        return 'test-model'

    def __init__(self, greeting):
        self.greeting = greeting

    def do(self):
        print(self.greeting)


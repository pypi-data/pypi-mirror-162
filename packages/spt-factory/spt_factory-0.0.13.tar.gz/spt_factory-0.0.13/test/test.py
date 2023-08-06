import os

from spt_factory import MongoFactory


if __name__ == '__main__':
    print(os.getenv('SSLROOT'))
    f = MongoFactory(
        mongo_url=os.getenv('MONGO_URL'),
        tlsCAFile=os.getenv('SSLROOT'),
    )

    print(f'moniback-telegram = {f.get_any_creds_credentials(type="moniback-telegram")}')
    print(f'moniback-mlg = {f.get_any_creds_credentials(type="moniback-mlg")}')
    print(f'postgres = {f.get_postgres_credentials()}')

    print(f.get_postgres_credentials(**{
        'host': 'localhost',
        'port': '5432',
        'dbname': 'moniback'
    }))

    # one object, two links
    model_manager_1 = f.get_model_manager()
    model_manager_2 = f.get_model_manager()

    pipeline_manager = f.get_pipeline_manager()

    tfidf_config = model_manager_1.get_model_config(model_id='global_tfidf')

    print(tfidf_config)
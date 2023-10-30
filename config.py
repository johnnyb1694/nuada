import os

from dotenv import load_dotenv
load_dotenv()

class Config():

    db_dialect = os.environ.get('DB_DIALECT')
    db_api = os.environ.get('DB_API')
    db_host = os.environ.get('DB_HOST')
    db_port = os.environ.get('DB_PORT')
    db_user = os.environ.get('DB_USER')
    db_pwd = os.environ.get('DB_PWD')
    db_name = os.environ.get('DB_NAME')

    def __repr__(self) -> str:
        return f'Configuration for "Nuada" (with remote database stored in/at "{self.db_name}")'

if __name__ == '__main__':
    print(Config())
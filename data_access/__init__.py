from peewee import Model, MySQLDatabase

DATABASE_FILE_PATH = '/home/machiry/Downloads/debiancodeql/debiancodeql.db'

database = MySQLDatabase(DATABASE_FILE_PATH)

class BaseModel(Model):
    class Meta:
        database = database
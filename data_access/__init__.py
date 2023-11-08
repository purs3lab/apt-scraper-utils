from peewee import Model, SqliteDatabase

DATABASE_FILE_PATH = '/home/machiry/Downloads/debiancodeql.db'

database = SqliteDatabase(DATABASE_FILE_PATH)

class BaseModel(Model):
    class Meta:
        database = database
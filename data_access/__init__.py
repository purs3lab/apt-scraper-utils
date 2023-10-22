from peewee import Model, SqliteDatabase

DATABASE_FILE_PATH = '/media/machiry/PurS3Disk/debiancodeql/debiancodeql.db'

database = SqliteDatabase(DATABASE_FILE_PATH)

class BaseModel(Model):
    class Meta:
        database = database
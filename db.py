from peewee import *
import json


db = SqliteDatabase('listgir.db')

class Base(Model):
    class Meta:
        database = db

class data(Base):
    group_id = TextField()
    charge = BigIntegerField(default=0)
    creator = BigIntegerField(null=True)
    admins = TextField(default=json.dumps([]))
    account = TextField(null=True)
    main = TextField(null=True)
    main_link = TextField(null=True)

class accounts(Base):
    group_id = TextField()
    owner = BigIntegerField()
    number = TextField()
    session_string = TextField()
    name = TextField()
    uid = BigIntegerField()

db.connect()
db.create_tables([data,accounts])
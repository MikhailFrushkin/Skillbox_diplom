from peewee import *

db = SqliteDatabase('Telegram.db')


class BaseModel(Model):
    class Meta:
        database = db


class Users(BaseModel):
    user_id = IntegerField(primary_key=True)
    first_name = CharField(default='')
    last_name = CharField(default='')
    user_name = CharField(default='')


class Message(BaseModel):
    message_id = IntegerField(primary_key=True)
    command = CharField()
    created_at = TimestampField()
    city_name = CharField()
    hotels_amount = IntegerField()
    photo_amount = IntegerField(default=0)
    max_price = FloatField(default=0.0)
    distance_from_center = FloatField(default=0.0)
    check_in = CharField()
    check_out = CharField()


class Hotels(BaseModel):
    name = CharField()
    hotel_id = IntegerField()
    hotel_name = CharField()
    hotel_adress = CharField()
    distance_from_center = FloatField(default=0.0)
    price = CharField()


class Photos(BaseModel):
    hotel_id = IntegerField()
    photo_url = CharField()


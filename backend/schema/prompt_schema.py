from mongoengine import Document,StringField

class prompt (Document):
    prompt_name=StringField(required=True)
    prompt=StringField(required=True)
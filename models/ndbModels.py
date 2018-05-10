from google.appengine.ext import ndb


class User(ndb.Model):
    user_key = ndb.StringProperty(required=True)
    name = ndb.StringProperty(required=True)
    is_admin = ndb.IntegerProperty(required=True)


class Teacher(ndb.Model):
    name = ndb.StringProperty(required=True)
    surname = ndb.StringProperty(required=True)
    user_key = ndb.KeyProperty(kind=User)


class Subject(ndb.Model):
    name = ndb.StringProperty(required=True)
    year = ndb.IntegerProperty(required=True)
    quarter = ndb.IntegerProperty(required=True)
    user_key = ndb.KeyProperty(kind=User)


class Software(ndb.Model):
    name = ndb.StringProperty(required=True)
    url = ndb.StringProperty(required=True)
    instalation_notes = ndb.StringProperty(required=True)
    needs_root = ndb.IntegerProperty(required=True)


class Request(ndb.Model):
    date = ndb.DateTimeProperty(required=True)
    user_key = ndb.KeyProperty(kind=User)
    subject_key = ndb.KeyProperty(kind=Subject)


class Request_Software(ndb.Model):
    request_key = ndb.KeyProperty(kind=Request)
    software_key = ndb.KeyProperty(kind=Software)
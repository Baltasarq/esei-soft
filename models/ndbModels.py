from google.appengine.ext import ndb
from google.appengine.ext.ndb import msgprop
from protorpc import messages
from google.appengine.api import users


class System(messages.Enum):
    LINUX = 1
    WINDOWS = 2
    BOTH = 3


class User(ndb.Model):
    user_id = ndb.StringProperty(required=True, indexed=True)
    name = ndb.StringProperty(required=True, indexed=True)
    is_admin = ndb.BooleanProperty(required=True, default=False)

    def __unicode__(self):
        return self.user_id + ' ' + self.name + " admin: " + str(self.is_admin)

    @staticmethod
    def get_current_user():
        toret = None
        gae_user = users.get_current_user()

        if (users.is_current_user_admin()
         or (gae_user and gae_user.email().lower().endswith("@esei.uvigo.es"))):
            try:
                located_user = User.query(User.user_id == gae_user.user_id()).fetch(1)

                if located_user:
                    toret = located_user[0]
                else:
                    print("Creating new user...")
                    toret = User()

                    toret.user_id = gae_user.user_id()
                    toret.name = gae_user.nickname().split('@')[0]
                    toret.is_admin = users.is_current_user_admin()
                    toret.gae_user = gae_user

                    print("User created: " + unicode(toret))
                    toret.put()
            except Exception as e:
                print(e)

        return toret


class Subject(ndb.Model):
    name = ndb.StringProperty(required=True, indexed=True)
    abbreviation = ndb.StringProperty(required=True, indexed=True)
    year = ndb.IntegerProperty(required=True, indexed=True)
    quarter = ndb.IntegerProperty(required=True, indexed=True)
    user_key = ndb.KeyProperty(kind=User)


class Software(ndb.Model):
    name = ndb.StringProperty(required=True, indexed=True)
    url = ndb.StringProperty(required=True)
    installation_notes = ndb.StringProperty(required=True, default="")
    needs_root = ndb.BooleanProperty(required=True, indexed=True)


class Request(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True, required=True, indexed=True)
    user_key = ndb.KeyProperty(kind=User)
    subject_key = ndb.KeyProperty(kind=Subject)
    system = msgprop.EnumProperty(System, required=True)


class RequestSoftware(ndb.Model):
    request_key = ndb.KeyProperty(kind=Request)
    software_key = ndb.KeyProperty(kind=Software)

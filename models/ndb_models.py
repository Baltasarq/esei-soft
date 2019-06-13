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
    url = ndb.StringProperty(required=True, default="")
    installation_notes = ndb.StringProperty(required=True, default="")
    needs_root = ndb.BooleanProperty(required=True, indexed=True)


class Request(ndb.Model):
    date = ndb.DateTimeProperty(auto_now_add=True, indexed=True)
    user_key = ndb.KeyProperty(kind=User)
    subject_key = ndb.KeyProperty(kind=Subject)
    system = msgprop.EnumProperty(System, required=True)


class RequestSoftware(ndb.Model):
    request_key = ndb.KeyProperty(kind=Request)
    software_key = ndb.KeyProperty(kind=Software)


from flask import flash


def retrieve_obj(cls, str_key):
    """Retrieves an object from the data store, given its key.

        :param str_key: The string that holds the key.
        :param cls: The class for the key (one of the ndb models).
        :return: The retrieved object, honoring the given key.
    """

    def build_msg():
        return "*** ERROR: retrieve_obj(" + cls.__name__ + ", \"" + str_key + "\")";

    toret = None

    if str_key:
        str_key = str_key.strip()
        int_key = 0

        try:
            int_key = int(str_key)
        except Exception as e:
            print(build_msg() + ": key to int: " + str(e))
            flash("Int key??", 'error')

        key = ndb.Key(cls, int_key)

        if not key:
            print(build_msg() + ": key building")
            flash("Object key??", 'error')
        else:
            toret = key.get()

            if not toret:
                print(build_msg() + ": obj retrieval failed")
                flash("Object??", 'error')

    return toret

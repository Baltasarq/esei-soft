class RequestComplete:

    def __init__(self, key,  user, subject, softwares, pairs_keys, so, date):
        self.key = key
        self.user = user
        self.date = date
        self.subject = subject
        self.softwares= softwares
        self.pairs_keys = pairs_keys
        self.system = so

    def getKey(self):
        return self.key

    def getUser(self):
        return self.user

    def getDate(self):
        return self.date

    def getSubject(self):
        return self.subject

    def getSoftwares(self):
        return self.softwares

    def getPairsKeys(self):
        return self.pairs_keys

    def getSystem(self):
        return self.system

    def __str__(self):
        return "Request: " + str(self.getKey()) + ", date: " + str(self.getDate()) + "\n" \
        + "Subject: " + str(self.getSubject()) + "\n" \
        + "Softwares: " + str(self.getSoftwares())

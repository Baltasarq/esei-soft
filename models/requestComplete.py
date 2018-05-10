class RequestComplete:

    def __init__(self, key,  user, subject, software, date):
        self.key = key
        self.user = user
        self.date = date
        self.subject = subject
        self.software = software

    def getKey(self):
        return self.key

    def getUser(self):
        return self.user

    def getDate(self):
        return self.date

    def getSubject(self):
        return self.subject

    def getSoftware(self):
        return self.software

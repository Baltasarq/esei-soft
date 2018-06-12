class RequestComplete:

    def __init__(self, key,  user, subject, software, so, date):
        self.key = key
        self.user = user
        self.date = date
        self.subject = subject
        self.software = software
        self.system = so

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

    def getSystem(self):
        return self.system

    def __str__(self):
        return "Request: " + str(self.getKey()) + ", date: " + str(self.getDate()) + "\n" \
        + "Subject: " + str(self.getSubject()) + "\n" \
        + "Software: " + str(self.getSoftware())

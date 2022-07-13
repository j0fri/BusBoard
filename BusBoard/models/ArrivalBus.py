import time
from datetime import datetime
from time import mktime

class ArrivalBus:
    def __init__(self, lineName, destinationName, expectedArrival):
        self.lineName = lineName
        self.destinationName = destinationName
        self.expectedArrival = expectedArrival

    def minsToArrivalInt(self):
        expectedArrivalTime = datetime.fromtimestamp(mktime(time.strptime(self.expectedArrival, "%Y-%m-%dT%H:%M:%SZ")))
        currentTime = datetime.utcnow()
        difference = expectedArrivalTime-currentTime

        mins = difference.days*24*60 + difference.seconds//60

        return mins

    def minsToArrivalStr(self):
        mins = self.minsToArrivalInt()
        return str(mins) if mins else "Due"

    def __lt__(self, other):
        return self.minsToArrivalInt() < other.minsToArrivalInt()

    def getDict(self):
        return {"lineID": self.lineName, "destinationName": self.destinationName, "minsToArrival": self.minsToArrivalStr()}



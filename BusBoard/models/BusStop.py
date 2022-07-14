import time
from datetime import datetime
from time import mktime

class BusStop:
    def __init__(self, id, commonName, indicator, distance):
        self.id = id
        self.commonName = commonName
        self.indicator = indicator
        self.distance = distance

    def __lt__(self, other):
        return self.distance < other.distance

    def getDict(self):
        return {"id": self.id, "commonName": self.commonName, "indicator": self.indicator,"distance": self.distance}


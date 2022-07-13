import time
from datetime import datetime
from time import mktime

class BusStop:
    def __init__(self, id, commonName, distance):
        self.id = id
        self.commonName = commonName
        self.distance = distance

    def __lt__(self, other):
        return self.distance < other.distance

    def getDict(self):
        return {"id": self.id, "commonName": self.commonName, "distance": self.distance}


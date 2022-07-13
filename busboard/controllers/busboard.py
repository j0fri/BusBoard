import ast

from flask import Flask
from flask import request
import requests
from markupsafe import escape
import random

from busboard.models import ArrivalBus

BASE_URL = "https://api.tfl.gov.uk"
CREDENTIALS = "?app_id=c6406c3cdd754b47af354088b60735a9&app_key=21a0ba9164ed46a3b81f5aaa4c4b635d"

def getRequestUrl(requestBody):
    return BASE_URL + requestBody + CREDENTIALS


def busboardRoutes(app):

    @app.route('/healthcheck')
    def healthCheck():
        return {"status": "OK"}

    @app.route('/getArrivalsByStopID/<stopID>')
    def getArrivalsByStopID(stopID):

        requestBody = "/StopPoint/" + stopID + "/Arrivals"

        data = requests.get(getRequestUrl(requestBody)).content
        dataList = ast.literal_eval(data.decode('utf-8'))
        dataArgs = list(map(lambda x: (x["lineName"], x["destinationName"], x["expectedArrival"]), dataList))
        arrivals = [ArrivalBus.ArrivalBus(*args) for args in dataArgs]

        arrivals.sort()
        arrivals = arrivals[:5]
        arrivalsOutputDict = [arrival.getDict() for arrival in arrivals]

        return {"data": arrivalsOutputDict}





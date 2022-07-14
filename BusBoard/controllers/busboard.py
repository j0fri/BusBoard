import ast

from flask import Flask
from flask import request
import requests
from markupsafe import escape
import random

from BusBoard.models import ArrivalBus, BusStop

BASE_URL_TFL = "https://api.tfl.gov.uk"
CREDENTIALS = "app_id=c6406c3cdd754b47af354088b60735a9&app_key=21a0ba9164ed46a3b81f5aaa4c4b635d"

BASE_URL_POSTCODES = "https://api.postcodes.io"

def getRequestUrl(requestBody):
    return BASE_URL_TFL + requestBody + CREDENTIALS


def busboardRoutes(app):

    @app.route('/healthcheck')
    def healthCheck():
        return {"status": "OK"}

    @app.route('/getArrivalsByStopID/<stopID>')
    def getArrivalsByStopID(stopID):

        requestBody = "/StopPoint/" + stopID + "/Arrivals?"

        data = requests.get(getRequestUrl(requestBody)).content
        dataList = ast.literal_eval(data.decode('utf-8'))

        if type(dataList) is dict:
            if 'exceptionType' in dataList:
                return {"error": dataList['exceptionType']}
            else:
                return {"error": 'Unknown error. Please try again later.'}

        dataArgs = list(map(lambda x: (x["lineName"], x["destinationName"], x["expectedArrival"]), dataList))
        arrivals = [ArrivalBus.ArrivalBus(*args) for args in dataArgs]

        arrivals.sort()
        arrivals = arrivals[:5]
        arrivalsOutputDict = [arrival.getDict() for arrival in arrivals]



        return {"data": arrivalsOutputDict}

    #TODO: Handle duplicate bus stops
    @app.route('/getNearBusStops/<postcode>')
    def getNearBusStops(postcode):
        postcodeRequestUrl = BASE_URL_POSTCODES + "/postcodes/" + postcode

        postcodeData = requests.get(postcodeRequestUrl).json()
        lat, lon = postcodeData["result"]["latitude"], postcodeData["result"]["longitude"]

        tflRequestBody = "/StopPoint?lat=" + str(lat) + "&lon=" + str(lon) + "&stopTypes=NaptanPublicBusCoachTram&radius=500&"

        data = requests.get(getRequestUrl(tflRequestBody)).json()["stopPoints"]

        dataArgs = list(map(lambda x: (x["id"], x["commonName"], x["distance"]), data))
        busStops = [BusStop.BusStop(*args) for args in dataArgs]

        busStops.sort()
        print([stop.getDict() for stop in busStops])
        busStops = busStops[:2]
        busStopsOutputDict = [stop.getDict() for stop in busStops]

        return {"stops": busStopsOutputDict}

    @app.route('/getArrivalsByPostcode/<postcode>')
    def getArrivalsByPostcode(postcode):
        nearbyStops = getNearBusStops(postcode)

        stopID1 = nearbyStops["stops"][0]["id"]
        stopID2 = nearbyStops["stops"][1]["id"]

        buses1 = getArrivalsByStopID(stopID1)
        buses2 = getArrivalsByStopID(stopID2)

        return {
            "stop1": {"name": nearbyStops["stops"][0]["commonName"], "buses": buses1["data"]},
            "stop2": {"name": nearbyStops["stops"][1]["commonName"], "buses": buses2["data"]}
        }





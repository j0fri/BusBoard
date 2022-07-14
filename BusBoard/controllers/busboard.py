import ast

from flask import Flask
from flask import request
import requests
from markupsafe import escape
import random

from BusBoard.models import ArrivalBus, BusStop

BASE_URL_TFL = "https://api.tfl.gov.uk"
CREDENTIALS =  "app_id=c6406c3cdd754b47af354088b60735a9&app_key=21a0ba9164ed46a3b81f5aaa4c4b635d"

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

    def collateStops(busStops):
        collated = {}
        for stop in busStops:
            name = stop.commonName
            if name in collated:
                collated[name] = collated[name] + [stop]
            else:
                collated[name] = [stop]

        return [collated[stop] for stop in collated]



    #TODO: Handle duplicate bus stops
    #TODO: Handle stands
    @app.route('/getNearBusStops/<postcode>')
    def getNearBusStops(postcode):
        postcodeRequestUrl = BASE_URL_POSTCODES + "/postcodes/" + postcode

        postcodeData = requests.get(postcodeRequestUrl).json()
        lat, lon = postcodeData["result"]["latitude"], postcodeData["result"]["longitude"]

        radius = 500
        results = 0

        while results < 2 and radius < 10000000:
            tflRequestBody = "/StopPoint?lat=" + str(lat) + "&lon=" + str(lon) + "&stopTypes=NaptanPublicBusCoachTram&radius=" + str(radius) + "&"
            data = requests.get(getRequestUrl(tflRequestBody)).json()["stopPoints"]

            dataArgs = list(map(lambda x: (x["id"], x["commonName"], x["indicator"], x["distance"]), data))
            busStops = [BusStop.BusStop(*args) for args in dataArgs]

            busStops.sort()
            # print([stop.getDict() for stop in busStops])
            busStops = collateStops(busStops)

            results = len(busStops)
            radius *= 2

        print(busStops)

        busStops = busStops[:2]
        busStopsOutputDict = [[stop.getDict() for stop in stops] for stops in busStops]
        # busStops.sort()
        # busStopsOutputDict = [stop.getDict() for stop in busStops]

        return {"stops": busStopsOutputDict}

    @app.route('/getArrivalsByPostcode/<postcode>')
    def getArrivalsByPostcode(postcode):
        nearbyStops = getNearBusStops(postcode)

        print(nearbyStops)

        stops1 = nearbyStops["stops"][0]
        stops2 = nearbyStops["stops"][1]

        stopID1 = stops1[0]["id"]
        stopID2 = stops2[0]["id"]

        buses1 = [{stop1["indicator"]: getArrivalsByStopID(stop1["id"])["data"]} for stop1 in stops1]
        buses2 = [{stop2["indicator"]: getArrivalsByStopID(stop2["id"])["data"]} for stop2 in stops2]

        return {
            "stop1": {"name": stops1[0]["commonName"], "buses": buses1},
            "stop2": {"name": stops2[0]["commonName"], "buses": buses2}
        }





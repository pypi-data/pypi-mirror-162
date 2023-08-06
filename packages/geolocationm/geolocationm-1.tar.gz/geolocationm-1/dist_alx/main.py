import requests

class GetGeoLocation():

    def GetIp():
        return requests.get("http://ipwho.is/").json()["ip"]
    
    def GetCountry():
        return requests.get("http://ipwho.is/").json()["country"]
    
    def GetCity():
        return requests.get("http://ipwho.is/").json()["city"]

    def GetRegion():
        return requests.get("http://ipwho.is/").json()["region"]

    def GetLongitude():
        return requests.get("http://ipwho.is/").json()["longitude"]

    def GetLatitude():
        return requests.get("http://ipwho.is/").json()["latitude"]

    def GetType():
        return requests.get("http://ipwho.is/").json()["type"]

    def GetContinent():
        return requests.get("http://ipwho.is/").json()["continent"]
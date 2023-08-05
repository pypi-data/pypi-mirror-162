import requests
import json

from ciptest.exception import *

class CIP():
    urls = {
        "user_me" : "https://api.criminalip.io/v1/user/me",
        "ip_data" : "https://api.criminalip.io/v1/ip/data",
        "ip_summary" : "https://api.criminalip.io/v1/ip/summary",
        "ip_vpn" : "https://api.criminalip.io/v1/ip/vpn",
        "ip_hosting" : "https://api.criminalip.io/v1/ip/hosting",
        "banner_search" : "https://api.criminalip.io/v1/banner/search",
        "banner_stats" : "https://api.criminalip.io/v1/banner/stats",
        "domain_reports" : "https://api.criminalip.io/v1/domain/reports",
        "domain_report_id" : "https://api.criminalip.io/v1/domain/report/",
        "domain_scan" : "https://api.criminalip.io/v1/domain/scan"
    }

    def __init__(self, api_key):
        headers = {}
        headers["x-api-key"] = api_key
        self.headers = headers

    def user_me(self):
        response = requests.request("POST", self.urls["user_me"], headers=self.headers)
        dict_data = json.loads(response.text)
        if(dict_data["status"] != 200):
            raise APIException(dict_data["status"], dict_data["message"], "user")
        return response.text

    def ip_data(self, params):
        response = requests.request("GET", self.urls["ip_data"], headers=self.headers, params=params)
        return response.text

    def ip_summary(self, params):
        response = requests.request("GET", self.urls["ip_summary"], headers=self.headers, params=params)
        return response.text

    def ip_vpn(self, params):
        response = requests.request("GET", self.urls["ip_vpn"], headers=self.headers, params=params)
        return response.text

    def ip_hosting(self, params):
        response = requests.request("GET", self.urls["ip_hosting"], headers=self.headers, params=params)
        return response.text

    def banner_search(self, params):
        response = requests.request("GET", self.urls["banner_search"], headers=self.headers, params=params)
        dict_data = json.loads(response.text)
        if(dict_data["status"] != 200):
            raise APIException(dict_data["status"], dict_data["message"], "banner")
        return response.text

    def banner_stats(self, params):
        response = requests.request("GET", self.urls["banner_stats"], headers=self.headers, params=params)
        dict_data = json.loads(response.text)
        if(dict_data["status"] != 200):
            raise APIException(dict_data["status"], dict_data["message"], "banner")
        return response.text

    def domain_reports(self, params):
        response = requests.request("GET", self.urls["domain_reports"], headers=self.headers, params=params)
        dict_data = json.loads(response.text)
        if(dict_data["status"] != 200):
            raise APIException(dict_data["status"], dict_data["message"], "domain")
        return response.text

    def domain_report_id(self, params):
        response = requests.request("GET", self.urls["domain_report_id"] + str(params), headers=self.headers, data={})
        dict_data = json.loads(response.text)
        if(dict_data["status"] != 200):
            raise APIException(dict_data["status"], dict_data["message"], "domain")
        return response.text

    def domain_scan(self, params):
        response = requests.request("POST", self.urls["domain_scan"], headers=self.headers, data=params)
        dict_data = json.loads(response.text)
        if(dict_data["status"] != 200):
            raise APIException(dict_data["status"], dict_data["message"], "domain")
        return response.text

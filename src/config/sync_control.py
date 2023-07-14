import os

from ntplib import NTPClient, NTPException

c = NTPClient()

def get_latency(ip):
    try:
        response = c.request(ip, version=3)

        return response.offset * 1000.0

    except NTPException as e:
        return e

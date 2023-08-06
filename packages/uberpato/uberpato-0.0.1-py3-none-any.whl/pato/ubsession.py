import requests
from pato.ubclient import UBClient

# from juco import Session as JucoSession
class UBSession(object):
    def __init__(self, uberduck_api_key, uberduck_secret_key):

        self.set_credentials(uberduck_api_key, uberduck_secret_key)

    def set_credentials(self, uberduck_api_key, uberduck_secret_key):
        self.uberduck_api_key = uberduck_api_key
        self.uberduck_secret_key = uberduck_secret_key

    def client(self):

        uberduck_client = UBClient(self.uberduck_api_key, self.uberduck_secret_key)
        return uberduck_client

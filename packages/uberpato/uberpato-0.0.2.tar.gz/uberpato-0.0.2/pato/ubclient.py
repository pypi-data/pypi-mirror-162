import requests
import time


class UBClient(object):
    def __init__(self, uberduck_api_key, uberduck_secret_key):
        self.uberduck_api_key = uberduck_api_key
        self.uberduck_secret_key = uberduck_secret_key

    def get_audio(self, text="test", voice="zwf"):
        auth = (self.uberduck_api_key, self.uberduck_secret_key)
        data_params = {"speech": text, "voice": voice}
        response = requests.post(
            "https://api.uberduck.ai/speak", json=data_params, auth=auth
        )
        uuid = response.json()
        output = requests.get(
            "https://api.uberduck.ai/speak-status", auth=auth, params=uuid
        )
        while output.json()["path"] is None:
            time.sleep(1)
            output = requests.get(
                "https://api.uberduck.ai/speak-status", auth=auth, params=uuid
            )

        return output

from io import BytesIO
import requests
from uuid import uuid4


class LovoClient:
    url = "https://api.lovo.ai"

    def __init__(self, api_key, s3_client, s3_bucket, s3_region):
        self.api_key = api_key
        self.s3_client = s3_client
        self.s3_bucket = s3_bucket
        self.s3_region = s3_region

    def synthesize_speech(self, text, voice_id, emphasis=None):
        json = {"text": text, "speaker_id": voice_id}
        if emphasis:
            json["emphasis"] = emphasis
        response = requests.post(
            f"{self.url}/v1/conversion",
            json=json,
            headers={
                "apiKey": self.api_key,
                "Content-Type": "application/json",
            },
        )
        assert response.status_code == 200, response.text
        raw_audio = response.content
        uuid = str(uuid4())
        bio = BytesIO()
        bio.write(raw_audio)
        bio.flush()
        bio.seek(0)
        object_name = f"{uuid}.wav"
        self.s3_client.upload_fileobj(bio, self.s3_bucket, object_name)
        return (
            f"https://{self.s3_bucket}.s3.{self.s3_region}.amazonaws.com/{object_name}"
        )

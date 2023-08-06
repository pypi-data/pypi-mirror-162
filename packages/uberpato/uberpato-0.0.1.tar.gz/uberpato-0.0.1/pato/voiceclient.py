from boto3 import Session as BotoSession
from pato.lovo import LovoClient
from pato.ubsession import UBSession

POLLY = "polly"
UBERDUCK = "uberduck"
LOVO = "lovo"


class VoiceClient(object):
    def __init__(self, aws_params, uberduck_params=None, lovo_params=None):

        if uberduck_params:
            self.uberduck_session = UBSession(
                uberduck_params["api_key"], uberduck_params["secret_key"]
            )
            self.uberduck_client = self.uberduck_session.client()
        # Create a client using the credentials and region defined in the [adminuser]
        # section of the AWS credentials file (~/.aws/credentials)
        self.boto_session = BotoSession(
            aws_access_key_id=aws_params["access_key_id"],
            aws_secret_access_key=aws_params["secret_access_key"],
            region_name=aws_params["region"],
        )
        bucket = aws_params["bucket"]
        self.polly_client = self.boto_session.client("polly")
        self.polly_client.aws_bucket = bucket

        if lovo_params:
            s3_client = self.boto_session.client("s3")
            self.lovo_client = LovoClient(
                **lovo_params,
                s3_client=s3_client,
                s3_bucket=bucket,
                s3_region=aws_params["region"],
            )

    def synthesize_speech(self, text, voice_id, voice_source):

        if voice_source == POLLY:
            output = self.polly_client.start_speech_synthesis_task(
                Text=text,
                OutputFormat="mp3",
                VoiceId=voice_id,
                Engine="neural",
                OutputS3BucketName=self.polly_client.aws_bucket,
            )
            path = output["SynthesisTask"]["OutputUri"]
            fmt = "pcm"
        elif voice_source == UBERDUCK:
            output = self.uberduck_client.get_audio(text=text, voice=voice_id)
            path = output.json()["path"]
            fmt = "wav"
        elif voice_source == LOVO:
            path = self.lovo_client.synthesize_speech(text, voice_id)
            fmt = "wav"
        return (path, fmt)

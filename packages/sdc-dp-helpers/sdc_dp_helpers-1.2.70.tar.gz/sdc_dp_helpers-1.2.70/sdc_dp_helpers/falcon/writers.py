# pylint: disable=too-few-public-methods

"""
    CUSTOM WRITER CLASSES
"""
import json
import os
from datetime import datetime

import boto3


class CustomFalconWriter:
    """ "
    Writer for falcon API
    Works with dictionary object from the readers
    """

    def __init__(self, bucket, file_path, profile_name=None):
        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)
        self.s3_resource = self.boto3_session.resource("s3")
        self.bucket = bucket
        self.file_path = file_path
        self.data = None

    def write_to_s3(self, payload: dict) -> None:
        """
        This pulls the yielded dataset from the GA reader in a manner
        that consumes the dataset of the given view_id and date,
        and writes it to s3 so that duplication does not occur.
        :param payload: This is a key value object that looks like:
                        {
                            "data": list(),
                            "date": string,
                            "networks": string
                        }
        """

        # confirm the payload keys are matching accurately with what is expected
        if list(payload.keys()).sort() != ["data", "date", "networks"].sort():
            raise KeyError("Invalid payload")

        _data: dict = payload["data"]
        _date: str = payload["date"].replace("-", "")
        _networks: str = payload["networks"]

        write_path: str = f"{self.file_path}/{_networks}/{_date}.json"
        if _data:
            print(
                f"Writing data to s3://{self.bucket}/{write_path}  \
                partitioned by networks and date."
            )
            self.s3_resource.Object(self.bucket, write_path).put(Body=json.dumps(_data))
            self.data = {}


class CustomS3JsonWriter:
    """Class Extends Basic LocalGZJsonWriter"""

    def __init__(self, bucket, file_path, profile_name=None):
        self.bucket = bucket
        self.file_path = file_path

        self.profile_name = profile_name

        if profile_name is None:
            self.boto3_session = boto3.Session()
        else:
            self.boto3_session = boto3.Session(profile_name=profile_name)

        self.s3_resource = self.boto3_session.resource("s3")

    def write_to_s3(self, json_data):
        """
        Writes json data to s3 and names it by
        date of writing.
        """
        now = datetime.now().strftime("%Y_%m_%d_%H%M%S")
        key_path = f"{os.path.join(self.file_path, now)}.json"

        self.s3_resource.Object(self.bucket, key_path).put(Body=json.dumps(json_data))

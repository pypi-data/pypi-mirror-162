import io
import json
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Union

import boto3
import smart_open


def json_serial(obj):
    """
    JSON serializer for objects not serializable by default.
    """

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    else:
        return str(obj)


class S3Sink:

    """
    Uploads data to the bucket. In case of JSON/str data it is automatically compressed
    to gz and output name is changed to reflect that.

    **Initiate sink:**


            s3sink = S3Sink(
                bucket="databucket",
                prefix="/data/output/",
                session=boto3.Session(),
            )

    **Usage with JSON:**

            s3sink.submit(
                payload={"testing": True},
                name="important_file"
            )

    > Results in a filename: f"s3://{bucket}{prefix}{name}.gz"

    **Usage with files:**
            fileobj = open("important_file.zip")
            s3sink.submit(
                payload=fileobj,
                name="important_file.zip"
            )
    """

    def __init__(self, session: boto3.Session, bucket: str, prefix: str):
        self.session = session
        self.bucket = bucket
        if not prefix.endswith("/"):
            prefix = f"{prefix}/"

        if prefix.startswith("/"):
            prefix = prefix[1:]

        self.prefix = prefix

        self._client = self.session.client("s3")

    def _s3_path(self, name: str):
        return f"s3://{self.bucket}/{self.prefix}{name}"

    def put(self, payload: Union[str, dict, io.BufferedReader, io.TextIOWrapper], name: str):

        filemode = "w" if not isinstance(payload, io.IOBase) else payload.mode
        filemode = filemode.replace("r", "w")

        open_kwargs: Dict[str, Any] = dict(
            uri=self._s3_path(name=name), mode=filemode, transport_params=dict(client=self._client)
        )

        if isinstance(payload, (dict, str)):
            open_kwargs["compression"] = ".gz"
            open_kwargs["uri"] += ".gz"

        with smart_open.open(**open_kwargs) as f:
            if isinstance(payload, str):
                f.write(payload)

            elif isinstance(payload, dict):
                json.dump(payload, f, default=json_serial)

            elif isinstance(payload, (io.BufferedReader, io.TextIOWrapper)):
                for line in payload:
                    f.write(line)

            else:
                raise ValueError(f"{type(payload)} payload type is not supported")

    def get(self, name: str):
        try:

            open_kwargs = dict(uri=self._s3_path(name=name), transport_params=dict(client=self._client))
            if ".gz" in name:
                open_kwargs["compression"] = ".gz"
                open_kwargs["mode"] = "rb"

            with smart_open.open(**open_kwargs) as f:
                return f.read()

        except OSError as e:
            raise FileNotFoundError(e)

    def delete(self, name: str) -> bool:
        self.session.client("s3").delete_object(Bucket=self.bucket, Key=f"{self.prefix}{name}")
        return True

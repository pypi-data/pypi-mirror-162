import io
import json
from datetime import date
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Union

import boto3
import msgspec
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

    def _s3_path(self, name: str, is_file=False):
        if is_file:
            return f"s3://{self.bucket}/{self.prefix}{name}"
        else:
            return f"s3://{self.bucket}/{self.prefix}{name}.json.gz"

    def put_file(
        self,
        payload: Union[io.BufferedReader, io.TextIOWrapper],
        name: str,
        buffer_size=1024,
        encoding="utf-8",
    ) -> bool:
        open_kwargs: Dict[str, Any] = dict(
            uri=self._s3_path(name=name, is_file=True), mode="wb", transport_params=dict(client=self._client)
        )

        with smart_open.open(**open_kwargs) as f:
            if isinstance(payload, io.BufferedReader):
                data = payload.read(buffer_size)
                while data:
                    f.write(data)
                    data = payload.read(buffer_size)

            elif isinstance(payload, io.TextIOWrapper):
                data = payload.read(buffer_size).encode(encoding=encoding)
                while data:
                    f.write(data)
                    data = payload.read(buffer_size)

            else:
                raise ValueError(f"{type(payload)} payload type is not supported")
        return True

    def put(self, payload: Union[str, dict], name: str) -> bool:
        open_kwargs: Dict[str, Any] = dict(
            uri=self._s3_path(name=name), mode="wb", transport_params=dict(client=self._client), compression=".gz"
        )

        with smart_open.open(**open_kwargs) as f:
            if isinstance(payload, str):
                f.write(payload.encode(encoding="UTF-8"))

            elif isinstance(payload, dict):
                data = msgspec.json.encode(payload, enc_hook=json_serial)
                f.write(data)

            else:
                raise ValueError(f"{type(payload)} payload type is not supported")

        return True

    def get(self, name: str):
        try:
            open_kwargs = dict(
                uri=self._s3_path(name=name), compression=".gz", transport_params=dict(client=self._client), mode="rb"
            )

            with smart_open.open(**open_kwargs) as f:
                response = f.read()
                return msgspec.json.decode(response)
                return response

        except OSError as e:
            raise FileNotFoundError(e)

    def get_file(self, name: str):
        try:
            open_kwargs = dict(
                uri=self._s3_path(name=name, is_file=True), transport_params=dict(client=self._client), mode="rb"
            )

            with smart_open.open(**open_kwargs) as f:
                return f.read()

        except OSError as e:
            raise FileNotFoundError(e)

    def delete_file(self, name: str) -> bool:
        self.session.client("s3").delete_object(Bucket=self.bucket, Key=f"{self.prefix}{name}")
        return True

    def delete(self, name: str) -> bool:
        self.session.client("s3").delete_object(Bucket=self.bucket, Key=f"{self.prefix}{name}.json.gz")
        return True

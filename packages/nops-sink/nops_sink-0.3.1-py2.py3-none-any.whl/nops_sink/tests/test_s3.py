import json
import uuid
from datetime import datetime

import boto3
import pytest

from nops_sink import S3Sink


@pytest.fixture
def sink():
    prefix = "/nopssinktest/output"
    bucket = "nikita-data"

    sink = S3Sink(
        bucket=bucket,
        prefix=prefix,
        session=boto3.Session(),
    )
    return sink


def test_s3sink_json_upload(sink):
    random_string = str(uuid.uuid4())
    filename = "testing_json"
    datetime_obj = datetime.now()
    payload = {"test": random_string, "date": datetime_obj}
    sink.put(payload=payload, name=filename)

    response = sink.get(name=filename)
    assert response["date"] == datetime_obj.isoformat()
    payload["date"] = datetime_obj.isoformat()
    assert response == payload

    sink.delete(name=filename)

    with pytest.raises(FileNotFoundError):
        assert sink.get(name=filename)


def test_s3sink_file_binary_upload(sink):
    filename = "testing_file"
    random_string = str(uuid.uuid4())
    with open("/tmp/testfile", "wb") as f:
        f.write(random_string.encode("utf-8"))

    with open("/tmp/testfile", "rb") as f:
        sink.put_file(payload=f, name=filename)

    assert sink.get_file(name=filename) == random_string.encode("utf-8")

    sink.delete(name=filename)

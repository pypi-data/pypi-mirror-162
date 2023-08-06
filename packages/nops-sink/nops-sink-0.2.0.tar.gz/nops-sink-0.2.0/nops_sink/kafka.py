from functools import lru_cache

from nops_kafka import Producer
from nops_kafka import ensure_topics


class KafkaSink:
    """
    Usage:

            message_sink = KafkaSink(
                topic="data.output",
                headers={"client_id": "1337"},
                bootstrap_servers=settings.KAFKA_URL,
            )
            message_sink.put(payload={"testing": True})
            message_sink.flush()

    """

    def __init__(self, topic, headers, bootstrap_servers):
        self.bootstrap_servers = bootstrap_servers
        self.producer = Producer(bootstrap_servers=bootstrap_servers)
        self.topic = topic
        self.headers = headers

    @lru_cache
    def _ensure_topics(self) -> bool:
        return ensure_topics(bootstrap_servers=self.bootstrap_servers, required_topics=[self.topic])

    def put(self, payload):
        self._ensure_topics()
        self.producer.send(self.topic, value=payload, headers=self.headers)

    def flush(self) -> bool:
        self.producer.flush()
        return True

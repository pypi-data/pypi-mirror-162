import os
from typing import ClassVar

from graphdb import GraphDb, GraphDbConnection

config_connection_uri_writer = os.getenv(
    "GRAPH_CONN_URI_WRITER",
    "ws://dev-neptune-write-292706514.ap-southeast-1.elb.amazonaws.com:8182/gremlin",
)
config_connection_uri_reader = os.getenv(
    "GRAPH_CONN_URI_READER",
    "ws://dev-neptune-376859199.ap-southeast-1.elb.amazonaws.com:8182/gremlin",
)


class ANGraphDb:
    def __init__(self, connection_class: GraphDbConnection):
        self.graph = GraphDb.from_connection(connection_class)

    @classmethod
    def new_connection_config(cls) -> ClassVar:
        """Create new connection from configs
        :return: current object class
        """
        return cls(
            GraphDbConnection.from_uri(
                config_connection_uri_writer,
                config_connection_uri_reader,
                pool_size=5,
                max_workers=5,
            )
        )

    @classmethod
    def from_connection_uri(
        cls,
        connection_uri_writer: str,
        connection_uri_reader: str,
        pool_size: int = 0,
        max_workers: int = 0,
    ) -> ClassVar:
        """Create new object based on connection uri
        :param connection_uri_writer: string from connection uri writers
        :param connection_uri_reader: string from connection uri readers
        :param pool_size: int pool size
        :param max_workers: int for max workers
        :return: object class
        """
        return cls(
            GraphDbConnection.from_uri(
                connection_uri_writer, connection_uri_reader, pool_size, max_workers
            )
        )

    @classmethod
    def from_connection_class(cls, connection_class: GraphDbConnection) -> ClassVar:
        """Define new class based on object connection
        :param connection_class: object connection class
        :return: object class
        """
        return cls(connection_class)

"""
Kafka Module for sending, receiving data to AWS MSK.
"""
from json import dumps, loads
from kafka.admin import KafkaAdminClient, NewTopic
from kafka import KafkaConsumer, KafkaProducer


class KafkaMSK:
    def __init__(self, bootstrap_server: str, topic_name: str = None):
        """
        Initializes the Kafka MSK Module.

        Parameters
        ----------
        bootstrap_server : list, required
            List of MSK servers

        topic_name : str, optional
            Where to hold the message

        """
        self.bootstrap_server = bootstrap_server
        self.topic_name = topic_name

    def create_topic(self, partition_number=1, replication_factor=1):
        """
        Creation of New Topic

        Parameters
        ----------
        partition_number : int, optional
            number of partition

        replication_factor : int, optional
            number of replicated message

        Returns
        -------
        Python object
        """
        try:
            kafka_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_server, security_protocol="SSL"
            )

            topic_list = []
            topic_list.append(
                NewTopic(
                    name=self.topic_name,
                    num_partitions=partition_number,
                    replication_factor=replication_factor,
                )
            )
            kafka_client.create_topics(new_topics=topic_list, validate_only=False)

            return {"message": "success"}
        except Exception as err:
            raise Exception("ERROR - Receving Data from Kafka MSK:", err)

    def list_topics(self):
        """
        Get List of Available Topics

        Returns
        -------
        Python object
        """
        try:
            kafka_client = KafkaAdminClient(
                bootstrap_servers=self.bootstrap_server, security_protocol="SSL"
            )
            topics = kafka_client.list_topics()

            return topics
        except Exception as err:
            raise Exception("ERROR - Getting List of MSK Topics:", err)

    def send_data(self, message: dict):
        """
        Send Data to Specific Kafka Topic

        Parameters
        ----------
        message : dict, requires
            message to be sent on kafka

        Returns
        -------
        Python object
        """
        try:
            producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_server,
                value_serializer=lambda x: dumps(x).encode("utf-8"),
                security_protocol="SSL",
            )
            producer.send(self.topic_name, value=message)
        except Exception as err:
            raise Exception("ERROR - Sending Data to Kafka MSK:", err)

    def init_receive_data(self, offset_reset: str = "earlier"):
        try:
            """
            Initialize Receiving of Real-time Data

            Parameters
            ----------
            message : dict, requires
                message to be sent on kafka

            Returns
            -------
            Python object
            """

            consumer = KafkaConsumer(
                self.topic_name,
                group_id=None,
                bootstrap_servers=self.bootstrap_server,
                auto_offset_reset=offset_reset,
                value_deserializer=lambda x: loads(x.decode("utf-8")),
                security_protocol="SSL",
                enable_auto_commit=True,
            )

            return consumer

        except Exception as err:
            raise Exception("ERROR - Initialize Receving Data from Kafka MSK:", err)

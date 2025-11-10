import json
import os
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from minio import Minio
from minio.error import S3Error
import time


# --- NEW: Helper function to build a JSON schema ---
def build_json_schema(data: dict):
    """
    Infers a simple JSON schema from a data dictionary.
    This is the format required by Kafka Connect's JsonConverter
    when 'schemas.enable=true'.
    """
    field_map = {
        str: "string",
        int: "int64",  # Use int64 for Postgres BIGINT
        float: "float64",
        bool: "boolean",
    }

    fields = []
    for key, value in data.items():
        # Default to string if type is unknown (e.g., NoneType)
        field_type = field_map.get(type(value), "string")
        fields.append(
            {
                "type": field_type,
                "optional": True,  # All fields are optional
                "field": key,
            }
        )

    return {
        "type": "struct",
        "fields": fields,
        "optional": False,
        "name": "UserLogin",  # Can be any arbitrary name
    }


class DataLakeClient:
    """
    A simple SDK to interact with our Data Lake POC stack.
    """

    def __init__(
        self,
        kafka_server="localhost:9092",
        minio_endpoint="localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadminpassword",
    ):
        print("Initializing DataLakeClient...")

        # --- Kafka Setup ---
        self.kafka_producer = None
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=kafka_server,
                # Key is just a string
                key_serializer=lambda k: k.encode("utf-8"),
                # Value is a full JSON object (schema + payload)
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print("✅ Kafka Producer connection successful.")
        except Exception as e:
            print(f"❌ ERROR connecting to Kafka: {e}")

        # --- MinIO Setup ---
        self.minio_client = None
        try:
            self.minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False,
            )
            self.minio_client.list_buckets()
            print("✅ MinIO Client connection successful.")
        except Exception as e:
            print(f"❌ ERROR connecting to MinIO: {e}")

    def send_to_kafka(self, topic: str, key: str, data: dict):
        """
        Sends a schema-wrapped JSON message to a Kafka topic.

        :param topic: The name of the Kafka topic
        :param key: The message key
        :param data: The Python dictionary (this is the payload).
        """
        if not self.kafka_producer:
            print("❌ Kafka producer is not initialized.")
            return

        # --- FIX: Build the schema-wrapped message ---
        schema = build_json_schema(data)
        schema_wrapped_message = {"schema": schema, "payload": data}

        try:
            print(f"Sending schema-wrapped message to '{topic}' (Key: {key})...")
            # Send both the key and the new wrapped value
            self.kafka_producer.send(topic, key=key, value=schema_wrapped_message)
            self.kafka_producer.flush()
            print("  -> Message sent successfully.")

        except Exception as e:
            print(f"❌ Failed to send message to Kafka: {e}")

    def upload_to_minio(self, bucket_name: str, object_name: str, file_path: str):
        if not self.minio_client:
            print("❌ MinIO client is not initialized. Cannot upload file.")
            return
        if not os.path.exists(file_path):
            print(f"❌ Local file not found at: {file_path}")
            return
        try:
            print(
                f"Uploading '{file_path}' to MinIO bucket '{bucket_name}' as '{object_name}'..."
            )
            self.minio_client.fput_object(bucket_name, object_name, file_path)
            print("  -> File uploaded successfully.")
        except S3Error as e:
            print(f"❌ Failed to upload file to MinIO: {e}")

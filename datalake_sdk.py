import json
import os
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
from minio import Minio
from minio.error import S3Error
from time import sleep


class DataLakeClient:
    """
    A simple SDK to interact with our Data Lake POC stack.

    This client handles connections to:
    - Kafka (for JSON event streaming)
    - MinIO (for unstructured file storage)
    """

    def __init__(
        self,
        kafka_server="localhost:9092",
        minio_endpoint="localhost:9000",
        minio_access_key="minioadmin",
        minio_secret_key="minioadminpassword",
    ):
        """
        Initializes the clients for Kafka and MinIO.
        """
        print("Initializing DataLakeClient...")

        # --- Kafka Setup ---
        self.kafka_producer = None
        try:
            self.kafka_producer = KafkaProducer(
                bootstrap_servers=kafka_server,
                # --- FIX: Add a serializer for the message key (which will be a string) ---
                key_serializer=lambda k: k.encode("utf-8"),
                # Serialize Python dicts to JSON and encode as UTF-8
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            )
            print("✅ Kafka Producer connection successful.")
        except NoBrokersAvailable:
            print(f"❌ ERROR: Cannot connect to Kafka at {kafka_server}.")
            print("   Please ensure the Kafka container is running.")
        except Exception as e:
            print(f"❌ An unexpected error occurred with Kafka: {e}")

        # --- MinIO Setup ---
        self.minio_client = None
        try:
            self.minio_client = Minio(
                minio_endpoint,
                access_key=minio_access_key,
                secret_key=minio_secret_key,
                secure=False,  # Set to False because we are using http
            )
            self.minio_client.list_buckets()
            print("✅ MinIO Client connection successful.")
        except Exception as e:
            print(f"❌ ERROR: Cannot connect to MinIO at {minio_endpoint}.")
            print(f"   Details: {e}")

    # --- FIX: Update function to accept a 'key' argument ---
    def send_to_kafka(self, topic: str, key: str, data: dict):
        """
        Sends a single JSON message (as a Python dict) to a Kafka topic.

        :param topic: The name of the Kafka topic (e.g., 'user_activity')
        :param key: The message key (will be used as the Primary Key).
        :param data: The Python dictionary to send as JSON.
        """
        if not self.kafka_producer:
            print("❌ Kafka producer is not initialized. Cannot send message.")
            return

        try:
            print(f"Sending message to Kafka topic '{topic}' (Key: {key})...")
            # --- FIX: Send both the key and the value ---
            self.kafka_producer.send(topic, key=key, value=data)
            self.kafka_producer.flush()  # Ensure message is sent
            print("  -> Message sent successfully.")

        except Exception as e:
            print(f"❌ Failed to send message to Kafka: {e}")

    def upload_to_minio(self, bucket_name: str, object_name: str, file_path: str):
        """
        Uploads a local file to a MinIO bucket.
        """
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
            print(
                f"  -> View it on the MinIO console: http://localhost:9001/buckets/{bucket_name}/{object_name}"
            )

        except S3Error as e:
            print(f"❌ Failed to upload file to MinIO: {e}")
        except Exception as e:
            print(f"❌ An unexpected error occurred during upload: {e}")

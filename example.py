import os
import time
from datalake_sdk import DataLakeClient


def run_pii_demo():
    """
    Runs a demo sending PII and non-PII data to Kafka.
    """

    print("--- Starting PII Data Lake Demo ---")

    client = DataLakeClient()

    print("\n--- Kafka PII/Non-PII Demo ---")
    if not client.kafka_producer:
        print("❌ Kafka producer not connected. Aborting demo.")
        return

    # --- Event 1: A user login with clear PII data ---
    user_login_event = {
        "email": "jane.doe@example.com",
        "ip_address": "192.168.1.101",
        "full_name": "Jane Doe",
        "user_id": "u-1001",  # This is now just part of the data
        "action": "login_success",
        "timestamp": int(time.time()),
        "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...",
    }

    # --- Event 2: A second user login ---
    user_2_event = {
        "email": "john.smith@company.com",
        "ip_address": "10.0.0.52",
        "full_name": "John Smith",
        "user_id": "u-1002",
        "action": "login_failed",
        "timestamp": int(time.time()) + 1,
        "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...",
    }

    print(f"Sending PII event for user 'Jane Doe' to topic 'user_logins'...")
    # --- FIX: Pass the 'user_id' as the new 'key' argument ---
    client.send_to_kafka(
        topic="user_logins", key=user_login_event["user_id"], data=user_login_event
    )

    print(f"Sending PII event for user 'John Smith' to topic 'user_logins'...")
    # --- FIX: Pass the 'user_id' as the new 'key' argument ---
    client.send_to_kafka(
        topic="user_logins", key=user_2_event["user_id"], data=user_2_event
    )

    print("\n--- Demo Complete ---")
    print("Wait ~10-15 seconds for Kafka Connect to process the messages.")
    print("Then, check the 'user_logins' table in Postgres!")


if __name__ == "__main__":
    run_pii_demo()

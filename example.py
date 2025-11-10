import os
import time
import uuid
from datalake_sdk import DataLakeClient  # Import our SDK


def run_full_demo():
    """
    Runs a demo of the DataLakeClient, sending data to
    both Kafka and MinIO.
    """

    print("--- Starting Full Data Lake SDK Demo ---")
    
    client = DataLakeClient()
    
    # ... (MinIO demo can stay the same) ...

    # -----------------------------------------------
    # --- Kafka PII/Non-PII Demo ---
    # -----------------------------------------------
    print("\n--- Kafka Demo ---")
    if not client.kafka_producer:
        print("❌ Kafka producer not connected. Skipping Kafka demo.")
    else:
        
        # --- 2. Generate random user IDs ---
        user_1_id = f"u-{uuid.uuid4()}"
        user_2_id = f"u-{uuid.uuid4()}"

        # Define Event 1
        user_login_event = {
            'email': 'jane.doe@example.com',
            'ip_address': '192.168.1.101',
            'full_name': 'Jane Doe',
            'user_id': user_1_id, # <-- 3. Use the random ID
            'action': 'login_success',
            'timestamp': int(time.time()),
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...'
        }
        
        # Define Event 2
        user_2_event = {
            'email': 'john.smith@company.com',
            'ip_address': '10.0.0.52',
            'full_name': 'John Smith',
            'user_id': user_2_id, # <-- 3. Use the random ID
            'action': 'login_failed',
            'timestamp': int(time.time()) + 1,
            'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) ...'
        }
        
        print(f"Sending PII event for user '{user_1_id}'...")
        client.send_to_kafka(
            topic='user_logins', 
            key=user_login_event['user_id'], 
            data=user_login_event
        )
        
        print(f"Sending PII event for user '{user_2_id}'...")
        client.send_to_kafka(
            topic='user_logins', 
            key=user_2_event['user_id'], 
            data=user_2_event
        )
    # -----------------------------------------------
    # --- MinIO Unstructured Data Demo ---
    # -----------------------------------------------
    print("\n--- MinIO Demo ---")
    if not client.minio_client:
        print("❌ MinIO client not connected. Skipping MinIO demo.")
    else:
        # Create a dummy log file to upload
        dummy_file = "sample_log.txt"
        with open(dummy_file, "w") as f:
            f.write("This is a sample log file for unstructured data.\n")
            f.write(f"Timestamp: {int(time.time())}\n")
            f.write("Event: SERVICE_RESTART\n")

        # Upload to MinIO
        client.upload_to_minio(
            bucket_name="datalake-poc",  # The bucket our 'minio-mc' created
            object_name="logs/server_log_001.txt",  # The name/path inside the bucket
            file_path=dummy_file,  # The local file
        )

        # Clean up the dummy file
        os.remove(dummy_file)

    print("\n--- Demo Complete ---")
    print("Wait ~10-15 seconds for Kafka Connect to process the messages.")
    print("You can now verify the results in Postgres and MinIO.")


# -----------------------------------------------------------------
# ---  Run the example ---
# -----------------------------------------------------------------

if __name__ == "__main__":
    run_full_demo()

# Data Lake POC Platform

This project uses Docker Compose to launch a complete proof-of-concept (POC) data platform. It includes:

  * **Data Streaming:** Kafka (and Zookeeper)
  * **Streaming ETL:** Kafka Connect
  * **Stream UI:** Kafka UI
  * **Unstructured Storage:** MinIO (S3-compatible)
  * **Metadata Store:** PostgreSQL
  * **Search Index:** Elasticsearch
  * **Data Catalog:** OpenMetadata
  * **Data Visualization:** Metabase

[Image of the Data Lake POC architecture]

The services are pre-configured to demonstrate a full data lifecycle:

1.  **Produce:** A Python SDK sends schema-wrapped JSON (with PII) to Kafka and files to MinIO.
2.  **Stream:** Kafka Connect reads the schema-wrapped data, auto-creates a table in PostgreSQL, and sinks the data.
3.  **Catalog:** OpenMetadata ingests the Kafka and Postgres metadata and auto-tags the PII.
4.  **Visualize:** Metabase connects to the auto-created PostgreSQL table to build dashboards.

## ⚠️ Critical Prerequisites

1.  **Docker Desktop Memory:** This stack is memory-intensive. You **must** increase the memory allocated to Docker.

      * Go to Docker Desktop \> **Settings** \> **Resources** \> **Advanced**.
      * Set **Memory** to **at least 10 GiB**.
      * Apply & Restart.

2.  **Python 3.x:** Required to run the SDK and example scripts.

3.  **`curl`:** Required to configure Kafka Connect.

## 📁 File Structure

Your project directory must contain the following 7 files:

1.  `docker-compose.yml` (The main file defining all services)
2.  `init-metabase.sh` (A script to create the Metabase DB user in Postgres)
3.  `connect.Dockerfile` (A Dockerfile to build our custom Kafka Connect image)
4.  `datalake_sdk.py` (Our custom Python client that sends schema-wrapped data)
5.  `example.py` (The script to run our test use cases)
6.  `requirements.txt` (Python dependencies for the SDK)
7.  `README.md` (This file)

## 🚀 How to Run

1.  **Install Python Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Build and Start All Services:**
    This command will build the custom `connect` image (which installs the JDBC plugin) and then start all containers in detached mode.

    ```bash
    docker compose up -d --build
    ```

    The first launch will take 5-10 minutes as it downloads all the images, builds the `connect` image, and runs database migrations.

## 💻 Service Access

Once running, all services are available on your `localhost`:

| Service | URL | Credentials |
| :--- | :--- | :--- |
| **OpenMetadata** | `http://localhost:8585` | **User:** `admin`, **Pass:** `admin` |
| **Metabase** | `http://localhost:3000` | (User-created on first login) |
| **Kafka UI** | `http://localhost:8090` | (No login required) |
| **MinIO Console** | `http://localhost:9001` | **User:** `minioadmin`, **Pass:** `minioadminpassword` |
| **Kafka Broker** | `localhost:9092` | (For Python scripts) |
| **Kafka Connect API** | `http://localhost:8083` | (For `curl` commands) |
| **PostgreSQL** | `localhost:5432` | **User:** `postgres`, **Pass:** `password` |
| **Elasticsearch** | `http://localhost:9200` | (For OpenMetadata) |

-----

## ✅ Use Case 1: Configure the Kafka-to-Postgres Pipeline

Before we send data, we must configure Kafka Connect. This new config tells the connector to expect a schema and to auto-create the table.

**Action:**

1.  **Post the New Connector Configuration:**
    Run the following `curl` command. This tells the connector to use the schema from the message (`"value.converter.schemas.enable": "true"`) and to use `user_id` as the primary key.

    ```bash
    curl -i -X POST -H "Content-Type:application/json" http://localhost:8083/connectors -d '{
      "name": "jdbc-sink-with-schema",
      "config": {
        "connector.class": "io.confluent.connect.jdbc.JdbcSinkConnector",
        "tasks.max": "1",
        "topics": "user_logins",
        "connection.url": "jdbc:postgresql://postgresql:5432/postgres",
        "connection.user": "postgres",
        "connection.password": "password",
        "table.name.format": "public.user_logins",
        
        "auto.create": "true",
        "auto.evolve": "true",
        
        "pk.mode": "record_value",
        "pk.fields": "user_id",
        "insert.mode": "upsert",
        
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "true"
      }
    }'
    ```

**Result:**
You should get an `HTTP/1.1 201 Created` response. The pipeline is now active.

-----

## ✅ Use Case 2: Test the Data Pipeline (Python SDK)

This single script will test both the Kafka streaming pipeline (with schema) and the MinIO file upload.

**Action:**
Run the `example.py` script (which uses the updated `datalake_sdk.py`).

```bash
python example.py
```

**How to Verify:**

1.  **Check Kafka UI (Optional):**

      * Go to `http://localhost:8090`.
      * Navigate to the `user_logins` topic.
      * Click the **Messages** tab to see the raw JSON, including the `schema` and `payload` wrapper.

2.  **Check PostgreSQL (Primary Verification):**

      * Wait 10-15 seconds for Kafka Connect to create the table and sink the messages.
      * Run this command to query the database directly:
        ```bash
        docker compose exec postgresql psql -U postgres -c "SELECT user_id, email, action, \"timestamp\" FROM user_logins;"
        ```
      * **You will see your data\!** The table was created automatically.
        ```
         user_id |         email         |    action     |  timestamp
        ---------+-----------------------+---------------+-------------
         u-1001  | jane.doe@example.com  | login_success | 1762797000
         u-1002  | john.smith@company.com| login_failed  | 1762797001
        (2 rows)
        ```

3.  **Check MinIO:**

      * Go to `http://localhost:9001` (login with `minioadmin` / `minioadminpassword`).
      * Open the `datalake-poc` bucket.
      * You will see the `logs/server_log_001.txt` file.

-----

## ✅ Use Case 3: Visualize the Data in Metabase

Let's connect Metabase to the `user_logins` table that was just auto-created.

**Action:**

1.  Go to Metabase at `http://localhost:3000` and log in.
2.  Click the **Settings ⚙️ icon** \> **Admin settings** \> **Databases** tab.
3.  Click **"Add database"** and fill in these details:
      * **Database type**: **PostgreSQL**
      * **Host**: `postgresql`
      * **Port**: `5432`
      * **Database name**: `postgres`
      * **Username**: `postgres`
      * **Password**: `password`
      * **Display name**: `Data Lake DB`
4.  Click **Save**.

**How to Verify:**

1.  From the Metabase home page, click **"Browse data"**.
2.  Click on your **"Data Lake DB"** database.
3.  You will see the **`user_logins`** table. Click it to see your data\!

-----

## ✅ Use Case 4: Catalog PII in OpenMetadata

Finally, let's see OpenMetadata automatically tag the sensitive data in our Kafka topic.

**Action:**

1.  Go to OpenMetadata at `http://localhost:8585` and log in.
2.  Go to **Settings** \> **Messaging** \> **Add New Service**.
3.  Select **Kafka**.
4.  Give it a name (e.g., "Kafka POC") and click Next.
5.  For **Bootstrap Servers**, enter `kafka:29092` (the internal Docker network name) and click Next.
6.  Click **Save**.
7.  On the new service page, click the **"Ingestion"** tab.
8.  Click **"Add Ingestion"** and select **"Metadata Ingestion"**.
9.  In the **"Topic Filter Pattern"** section, toggle on **"Include"** and enter `user_logins`.
10. Click **Next**, set a schedule (e.g., daily), and click **"Add & Deploy"**.
11. On the Ingestion page, click the **"Run"** button to start the ingestion immediately.

**How to Verify:**

1.  Wait 1-2 minutes for the ingestion to complete.
2.  Go to the **Data Assets** (home page) and find the `user_logins` topic.
3.  Click the **"Schema"** tab.
4.  You will see that OpenMetadata has read the schema from our message and automatically applied the **`PII.Sensitive`** tag to the `email`, `full_name`, and `ip_address` fields.

-----

## 🛑 How to Stop

To stop and remove all services, data, and volumes, run:

```bash
docker compose down -v
```

*(The `-v` flag is important as it removes all volumes, giving you a clean slate for the next run.)*

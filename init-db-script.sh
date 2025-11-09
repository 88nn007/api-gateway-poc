#!/bin/bash
set -e

# Create a database and user for OpenMetadata
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER openmetadata_user WITH ENCRYPTED PASSWORD 'openmetadata_password';
    CREATE DATABASE openmetadata_db OWNER openmetadata_user;
    GRANT ALL PRIVILEGES ON DATABASE openmetadata_db TO openmetadata_user;
EOSQL

# Create a database and user for Metabase
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER metabase_user WITH ENCRYPTED PASSWORD 'metabase_password';
    CREATE DATABASE metabase_app_db OWNER metabase_user;
    GRANT ALL PRIVILEGES ON DATABASE metabase_app_db TO metabase_user;
EOSQL

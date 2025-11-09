#!/bin/bash
set -e

# This script runs as the default POSTGRES_USER (postgres)
# It creates a new user and database just for Metabase.

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER metabase_user WITH ENCRYPTED PASSWORD 'metabase_password';
    CREATE DATABASE metabase_app_db OWNER metabase_user;
    GRANT ALL PRIVILEGES ON DATABASE metabase_app_db TO metabase_user;
EOSQL

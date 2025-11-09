curl -i -X POST -H "Content-Type:application/json" http://localhost:8083/connectors -d '{
  "name": "jdbc-sink-autocreate",
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
    
    "pk.mode": "record_key",
    "insert.mode": "upsert",
    
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
}'

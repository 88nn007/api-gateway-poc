# Use the official Confluent Kafka Connect image as our base
FROM confluentinc/cp-kafka-connect:7.5.0

# Switch to root user to install the plugin
USER root

# Run the confluent-hub command to install the JDBC connector
# This will download the plugin and put it in the correct plugin path
RUN confluent-hub install --no-prompt confluentinc/kafka-connect-jdbc:latest

USER appuser

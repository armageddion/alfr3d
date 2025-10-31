#!/usr/bin/env python3

from kafka import KafkaProducer

# Kafka bootstrap servers - adjust if needed
KAFKA_URL = 'localhost:9092'

producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])

# Send the message to trigger checkLAN()
#producer.send('device', b'scan net')

# Send the message to trigger refreshAll()
producer.send('user', b'refresh-all')

producer.flush()

print("Sent 'scan net' to device topic")
print("Sent 'refresh-all' to user topic")

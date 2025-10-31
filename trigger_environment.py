#!/usr/bin/env python3

from kafka import KafkaProducer

# Kafka bootstrap servers - adjust if needed
KAFKA_URL = 'localhost:9092'

producer = KafkaProducer(bootstrap_servers=[KAFKA_URL])

# Send messages to trigger checkLocation() and checkWeather()
producer.send('environment', b'check location')
producer.send('environment', b'check weather')
producer.flush()

print("Sent 'check location' and 'check weather' to environment topic")
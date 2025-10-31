import pytest
from confluent_kafka import Producer, Consumer
import time

def test_kafka_produce_consume(kafka_bootstrap_servers):
    """Test producing and consuming messages from Kafka topics."""
    topics = ["speak", "environment", "device", "user", "google"]
    test_message = b"test message"

    producer = Producer({'bootstrap.servers': kafka_bootstrap_servers})

    # For each topic, subscribe first, then produce, then consume
    for i, topic in enumerate(topics):
        consumer = Consumer({
            'bootstrap.servers': kafka_bootstrap_servers,
            'group.id': f'test-group-{topic}-{i}',
            'auto.offset.reset': 'latest'
        })
        consumer.subscribe([topic])
        time.sleep(0.1)  # Small delay

        # Produce after subscribe
        producer.produce(topic, test_message)
        producer.flush()

        messages = []
        start_time = time.time()
        while time.time() - start_time < 10:  # 10 seconds timeout
            msg = consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                print(f"Consumer error: {msg.error()}")
                continue
            messages.append(msg.value())
            if len(messages) >= 1:
                break
        consumer.close()
        assert len(messages) > 0, f"No messages received from topic {topic}"
        assert messages[0] == test_message, f"Message mismatch in topic {topic}"
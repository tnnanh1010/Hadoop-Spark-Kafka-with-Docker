#!/bin/bash
pip install kafka 
# Run the consumer (received.py)
spark-submit /app/received.py &
# Run the producer (send.py)

python /app/send.py &



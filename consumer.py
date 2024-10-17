import pika
import subprocess
import os
import tempfile
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("/home/azureuser/executed_scripts/consumer.log"),
        logging.StreamHandler()
    ]
)

# Define the RabbitMQ broker URL
credentials = pika.PlainCredentials('user', 'password')
parameters = pika.ConnectionParameters('rabbitmqservername.eastus.azurecontainer.io', 5672, '/', credentials)

# Establish a connection to RabbitMQ server
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

# Declare the same fanout exchange
channel.exchange_declare(exchange='pubsub_exchange', exchange_type='fanout')

# Create a temporary queue and bind it to the exchange
result = channel.queue_declare(queue='', exclusive=True)
queue_name = result.method.queue

channel.queue_bind(exchange='pubsub_exchange', queue=queue_name)

logging.info(' [*] Waiting for messages. To exit press CTRL+C')

# Define a callback function to process incoming messages
def callback(ch, method, properties, body):
    logging.info(f" [x] Received script content")
    
    # Create a directory for executed scripts if it doesn't exist
    script_dir = "/home/azureuser/executed_scripts"
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)
    
    # Write the received script content to a file in the created directory
    script_path = os.path.join(script_dir, "received_script.sh")
    with open(script_path, 'wb') as script_file:
        script_file.write(body)
    
    # Set execute permissions for the script
    os.chmod(script_path, 0o755)
    
    # Execute the script on the host OS using docker exec
    try:
        result = subprocess.run([script_path], check=True, capture_output=True, text=True)
        logging.info("Script Output:")
        logging.info(result.stdout)
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing script: {e}")
        logging.error("Error Output:", e.stderr)

# Start consuming messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
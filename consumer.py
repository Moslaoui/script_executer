import pika
import subprocess
import os

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

print(' [*] Waiting for messages. To exit press CTRL+C')

# Define a callback function to process incoming messages
def callback(ch, method, properties, body):
    print(f" [x] Received script content")
    
    # Write the received script content to a file
    script_path = "/app/received_script.sh"
    with open(script_path, 'wb') as script_file:
        script_file.write(body)
    
    # Set execute permissions for the script
    os.chmod(script_path, 0o755)
    
    # Execute the script on the host OS using docker exec
    try:
        result = subprocess.run([script_path], check=True, capture_output=True, text=True)
        print("Script Output:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")
        print("Error Output:", e.stderr)

# Start consuming messages
channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

channel.start_consuming()
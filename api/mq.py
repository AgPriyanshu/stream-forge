import pika
from settings import settings


def publish(data):
    try:
        credentials = pika.PlainCredentials(settings.mq_username, settings.mq_password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host=settings.mq_host, credentials=credentials, port=5672
            )
        )

        with connection.channel() as channel:
            # Without a declared queue, the default exchange silently drops the message.
            channel.queue_declare(queue="default", durable=True)
            channel.basic_publish(exchange="", routing_key="default", body=data)

        connection.close()

    except Exception as e:
        print(e)

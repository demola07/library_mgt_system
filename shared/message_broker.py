import json
from typing import Any, Dict
import aio_pika
from datetime import datetime

class MessageBroker:
    def __init__(self, rabbitmq_url: str):
        self.url = rabbitmq_url
        self.connection = None
        self.channel = None
        self.exchange = None

    async def connect(self):
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            self.exchange = await self.channel.declare_exchange(
                "library_events",
                aio_pika.ExchangeType.TOPIC,
                durable=True
            )

    async def close(self):
        if self.connection:
            await self.connection.close()
            self.connection = None
            self.channel = None
            self.exchange = None

    async def publish(self, routing_key: str, data: Dict[str, Any]):
        await self.connect()
        message = aio_pika.Message(
            body=json.dumps({
                "data": data,
                "timestamp": datetime.utcnow().isoformat()
            }).encode(),
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT
        )
        await self.exchange.publish(message, routing_key=routing_key)

    async def subscribe(self, routing_key: str, callback):
        await self.connect()
        queue = await self.channel.declare_queue(
            f"{routing_key}_queue",
            durable=True
        )
        await queue.bind(self.exchange, routing_key)
        
        async def process_message(message: aio_pika.IncomingMessage):
            async with message.process():
                try:
                    body = json.loads(message.body.decode())
                    await callback(body['data'])
                except Exception as e:
                    print(f"Error processing message: {e}")
                    # Implement proper error handling/logging here
        
        await queue.consume(process_message) 
from typing import Optional, Dict, Any
import aio_pika
import json
import logging

from src.settings import settings


class RabbitMQService:
    """Сервис для асинхронной работы с RabbitMQ"""

    def __init__(
            self,
            url: str = "amqp://guest:guest@localhost/",
            queue_name: str = "default_queue",
            exchange_name: str = "",
            exchange_type: str = "direct"
    ):
        self.url = url
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None

    async def connect(self) -> None:
        """Установка подключения к RabbitMQ и создание канала"""
        try:
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)

            # Создаем exchange если указано
            if self.exchange_name:
                self.exchange = await self.channel.declare_exchange(
                    name=self.exchange_name,
                    type=aio_pika.ExchangeType[self.exchange_type.upper()],
                    durable=True
                )
            else:
                self.exchange = self.channel.default_exchange

            # Создаем очередь
            self.queue = await self.channel.declare_queue(
                name=self.queue_name,
                durable=True,
                auto_delete=False
            )

            # Биндим очередь к exchange если нужно
            if self.exchange_name:
                await self.queue.bind(self.exchange, routing_key=self.queue_name)

            logging.info(f"Connected to RabbitMQ. Queue: {self.queue_name}")

        except Exception as e:
            logging.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    async def disconnect(self) -> None:
        """Закрытие подключения к RabbitMQ"""
        if self.connection and not self.connection.is_closed:
            await self.connection.close()
            logging.info("Disconnected from RabbitMQ")

    async def is_connected(self) -> bool:
        """Проверка подключения к RabbitMQ"""
        return (
                self.connection is not None and
                not self.connection.is_closed and
                self.channel is not None and
                not self.channel.is_closed
        )

    async def ensure_connection(self) -> None:
        """Гарантирует что подключение установлено"""
        if not await self.is_connected():
            await self.connect()

    async def publish_message(
            self,
            message: Dict[str, Any],
            routing_key: Optional[str] = None,
            persistent: bool = True
    ) -> bool:
        """
        Публикация сообщения в очередь

        Args:
            message: Словарь с данными сообщения
            routing_key: Ключ маршрутизации (если не указан, используется имя очереди)
            persistent: Сохранять сообщение при перезапуске брокера

        Returns:
            bool: Успешность отправки
        """
        try:
            await self.ensure_connection()

            routing_key = routing_key or self.queue_name
            delivery_mode = (
                aio_pika.DeliveryMode.PERSISTENT
                if persistent
                else aio_pika.DeliveryMode.NOT_PERSISTENT
            )

            message_body = json.dumps(message).encode()

            await self.exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=delivery_mode,
                    content_type="application/json"
                ),
                routing_key=routing_key
            )

            logging.info(f"Message published to {routing_key}")
            return True

        except Exception as e:
            logging.error(f"Failed to publish message: {e}")
            return False

    async def consume_messages(
            self,
            callback: callable,
            auto_ack: bool = False
    ) -> None:
        """
        Запуск потребителя сообщений

        Args:
            callback: Асинхронная функция для обработки сообщений
            auto_ack: Автоматическое подтверждение получения
        """
        try:
            await self.ensure_connection()

            async def message_handler(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        body = json.loads(message.body.decode())
                        await callback(body, message)
                    except Exception as e:
                        logging.error(f"Error processing message: {e}")
                        if not auto_ack:
                            await message.nack()

            await self.queue.consume(message_handler)
            logging.info(f"Started consuming messages from {self.queue_name}")

        except Exception as e:
            logging.error(f"Failed to start consuming messages: {e}")
            raise


async def get_rabbitmq_service() -> RabbitMQService:
    """Зависимость для получения сервиса RabbitMQ"""
    await broker_service.ensure_connection()
    return broker_service


broker_service = RabbitMQService(url=settings.broker_url, queue_name=settings.broker_queue)
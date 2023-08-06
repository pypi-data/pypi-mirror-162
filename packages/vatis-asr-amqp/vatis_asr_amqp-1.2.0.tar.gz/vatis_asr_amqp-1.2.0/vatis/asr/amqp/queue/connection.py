import dataclasses
import time
from enum import Enum
from threading import RLock, Thread
from typing import Optional, List

import pika
from pika import BlockingConnection, ConnectionParameters
from pika.adapters.blocking_connection import BlockingChannel
from vatis.asr_commons.config.logging import get_logger

from . import environment
from .exceptions import ConnectionClosedException, RetriesExceededException
from .listener import ConnectionListener


logger = get_logger(__name__)


class ConnectionState(Enum):
    CONNECTING = 'CONNECTING'
    CONNECTED = 'CONNECTED'
    RECONNECTING = 'RECONNECTING'
    CLOSED = 'CLOSED'
    NOT_CREATED = 'NOT_CREATED'


class SafeConnectionListener(ConnectionListener):
    def __init__(self, connection_listener: ConnectionListener):
        self._connection: connection_listener = connection_listener

    def safe_on_connection_permanently_lost(self):
        try:
            self._connection.on_connection_permanently_lost(None)
        except Exception:
            pass

    def safe_on_connection_lost(self):
        try:
            self._connection.on_connection_lost(None)
        except Exception:
            pass

    def safe_on_connect(self):
        try:
            self._connection.on_connect(None)
        except Exception:
            pass


class ReconnectingAMQPConnection:
    CONNECTION_COUNTER = 0

    def __init__(self, host: str = ConnectionParameters.DEFAULT_HOST,
                 port: int = ConnectionParameters.DEFAULT_PORT,
                 user: str = ConnectionParameters.DEFAULT_USERNAME,
                 password: str = ConnectionParameters.DEFAULT_PASSWORD,
                 reconnection_delay: float = 3,
                 reconnection_retries: int = 50,
                 name: Optional[str] = None,
                 connection_listener: Optional[ConnectionListener] = None):
        """
        :param host: rabbitmq host
        :param port: rabbitmq port
        :param user: rabbitmq user
        :param password: rabbitmq pass
        :param reconnection_delay: delay in seconds between reconnection attempts
        :param reconnection_retries: maximum retries before declaring the connection lost
        :param name: connection name
        :param connection_listener: connection listener
        """
        self._connection_parameters: ConnectionParameters = pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(username=user, password=password),
            heartbeat=0  # deactivate due to generated overheads (https://github.com/pika/pika/issues/734)
        )
        self._connection: Optional[BlockingConnection] = None
        self._connection_lock: RLock = RLock()
        self._closed: bool = False
        self._reconnection_delay: float = reconnection_delay
        self._reconnection_retries: int = reconnection_retries
        self._state: ConnectionState = ConnectionState.CONNECTING
        self._name: str = name if name is not None else f'connection-{str(ReconnectingAMQPConnection.CONNECTION_COUNTER)}'
        ReconnectingAMQPConnection.CONNECTION_COUNTER += 1
        self._connection_listener: SafeConnectionListener = SafeConnectionListener(connection_listener)

        self._reestablish_connection_if_dropped()

        logger.info('%s: queue connection established: %s@%s:%d', self._name, user, host, port)

    def _reestablish_connection_if_dropped(self):
        if self._closed:
            raise ConnectionClosedException()

        try:
            self._connection.process_data_events()  # check for connectivity
        except Exception:
            pass

        if self._connection_closed():
            with self._connection_lock:
                retries = 1
                self._state = ConnectionState.RECONNECTING

                while retries <= self._reconnection_retries and self._connection_closed():
                    try:
                        self._connection = pika.BlockingConnection(self._connection_parameters)
                        self._connection.process_data_events()
                    except Exception as e:
                        if retries == 1:
                            self._connection_listener.safe_on_connection_lost()

                        logger.exception(f'{self._name}: Retry {retries} of {self._reconnection_retries}. Exception {str(e)}')
                        retries += 1
                        time.sleep(self._reconnection_delay)

                if self._connection_closed():
                    self.close()
                    self._connection_listener.safe_on_connection_permanently_lost()
                    raise RetriesExceededException()

                self._state = ConnectionState.CONNECTED
                self._connection_listener.safe_on_connect()

    def _connection_closed(self) -> bool:
        return self._connection is None or not self._connection.is_open or self._connection.is_closed

    def channel(self) -> BlockingChannel:
        if self._closed:
            raise ConnectionClosedException()

        with self._connection_lock:
            try:
                return self._connection.channel()
            except Exception as e:
                logger.exception('Connection dropped: %s', str(e))
                self._reestablish_connection_if_dropped()
                return self._connection.channel()

    @property
    def is_closed(self) -> bool:
        return self._closed

    @property
    def state(self) -> ConnectionState:
        return self._state

    def close(self):
        self._closed = True
        self._state = ConnectionState.CLOSED

        with self._connection_lock:
            if self._connection is not None and not self._connection.is_closed:
                self._connection.close()
                del self._connection
                self._connection = None

        logger.info(f'{self._name}: closed')


@dataclasses.dataclass(eq=False)
class ConnectionFactory:
    host: str = environment.RABBITMQ_HOST
    port: int = environment.RABBITMQ_PORT
    user: str = environment.RABBITMQ_USER
    password: str = environment.RABBITMQ_PASS
    _closed: bool = False
    _connections: Optional[List[ReconnectingAMQPConnection]] = None
    _lock: RLock = RLock()

    def __post_init__(self):
        self._connections = []

    def create(self, connection_listener: Optional[ConnectionListener] = None) -> ReconnectingAMQPConnection:
        if self._closed:
            raise ConnectionClosedException()

        connection: ReconnectingAMQPConnection = ReconnectingAMQPConnection(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            connection_listener=connection_listener
        )

        self._connections.append(connection)

        return connection

    def close(self):
        self._closed = True

        with self._lock:
            for connection in self._connections:
                if not connection.is_closed:
                    try:
                        connection.close()
                    except Exception as e:
                        logger.exception('Error while closing connection: %s', str(e))

            self._connections = []


connection_factory: Optional[ConnectionFactory]


def __init__(host: str = environment.RABBITMQ_HOST,
             port: int = environment.RABBITMQ_PORT,
             user: str = environment.RABBITMQ_USER,
             password: str = environment.RABBITMQ_PASS):
    global connection_factory

    connection_factory = ConnectionFactory(host=host,
                                           port=port,
                                           user=user,
                                           password=password)


def close():
    try:
        connection_factory.close()
    except Exception as e:
        logger.exception('Error while closing connection factory: %s', str(e))

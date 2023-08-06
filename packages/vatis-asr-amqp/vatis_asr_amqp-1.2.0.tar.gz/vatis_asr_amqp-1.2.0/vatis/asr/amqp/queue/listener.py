from abc import ABC
from typing import List, Optional

from .constants import Component


class ConnectionListener(ABC):
    def on_connection_permanently_lost(self, component: Component):
        pass

    def on_connection_lost(self, component: Component):
        pass

    def on_connect(self, component: Component):
        pass


class ComponentConnectionListener(ConnectionListener):
    def __init__(self, component: Component):
        assert component is not None
        self._component: Component = component

    def on_connection_permanently_lost(self, component: Component):
        if component == self._component:
            self.on_component_connection_permanently_lost()

    def on_connection_lost(self, component: Component):
        if component == self._component:
            self.on_component_connection_lost()

    def on_connect(self, component: Component):
        if component == self._component:
            self.on_component_connect()

    def on_component_connection_permanently_lost(self):
        pass

    def on_component_connection_lost(self):
        pass

    def on_component_connect(self):
        pass


class ConsumerConnectionListener(ComponentConnectionListener):
    def __init__(self):
        super().__init__(Component.CONSUMER)


class RpcConnectionListener(ComponentConnectionListener):
    def __init__(self):
        super().__init__(Component.RPC)


class ConnectionListenerAggregator(ConnectionListener):
    def __init__(self, connection_listeners: Optional[List[ConnectionListener]], component: Optional[Component] = None):
        self._connection_listeners: List[ConnectionListener] = connection_listeners if connection_listeners is not None else []
        self._component: Optional[Component] = component

    def on_connect(self, component: Component):
        for listener in self._connection_listeners:
            if self._component is not None:
                component = self._component

            try:
                listener.on_connect(component)
            except Exception:
                pass

    def on_connection_lost(self, component: Component):
        for listener in self._connection_listeners:
            if self._component is not None:
                component = self._component

            try:
                listener.on_connection_lost(component)
            except Exception:
                pass

    def on_connection_permanently_lost(self, component: Component):
        for listener in self._connection_listeners:
            if self._component is not None:
                component = self._component

            try:
                listener.on_connection_permanently_lost(component)
            except Exception:
                pass

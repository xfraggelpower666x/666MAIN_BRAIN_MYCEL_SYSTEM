"""UI-facing Resin 3 status model; the existing 3DX Tk layout remains the host UI."""
from .status_bus import StatusBus

LED_COMPONENTS = ("source", "monitor", "encoder", "server", "relay", "error")


class StatusLEDModel:
    def __init__(self, bus):
        self.bus = bus
        self.states = {name: ("unknown", "") for name in LED_COMPONENTS}
        self._unsubscribe = bus.subscribe(self._on_event)

    def _on_event(self, event):
        if event.component in self.states:
            self.states[event.component] = (event.state, event.message)

    def snapshot(self):
        return dict(self.states)

    def close(self):
        self._unsubscribe()

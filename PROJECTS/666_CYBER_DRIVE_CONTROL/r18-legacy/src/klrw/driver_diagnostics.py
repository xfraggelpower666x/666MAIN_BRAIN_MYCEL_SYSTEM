"""Explicit diagnostic capability policy; never loads, attaches to, or monitors drivers."""
from dataclasses import dataclass

@dataclass(frozen=True)
class DiagnosticCapability:
    name: str
    available: bool
    reason: str


def driver_monitor_status():
    return DiagnosticCapability("kernel_driver_events", False,
        "Driver event collection requires a separate reviewed Windows backend, permissions and explicit user opt-in; no driver shipped.")

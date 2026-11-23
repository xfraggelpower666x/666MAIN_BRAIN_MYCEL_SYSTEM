"""Windows IMMDevice endpoint identities via native Core Audio COM (read-only).

Only active render endpoints are enumerated. COM pointers and allocated strings
are released deterministically. No audio driver, registry write or COM server is
installed. The returned ID is IMMDevice::GetId, not a PortAudio list index.
"""
from dataclasses import dataclass
import base64
import ctypes
import sys
import uuid


@dataclass(frozen=True)
class RenderEndpoint:
    endpoint_id: str
    friendly_name: str


def _native_render_endpoints():
    if sys.platform != "win32":
        return []

    from ctypes import (POINTER, Structure, Union, byref, c_byte, c_int,
                        c_long, c_uint16, c_uint32, c_ubyte, c_void_p)

    class GUID(Structure):
        _fields_ = [("d1", c_uint32), ("d2", c_uint16), ("d3", c_uint16),
                    ("d4", c_ubyte * 8)]

    class PROPERTYKEY(Structure):
        _fields_ = [("fmtid", GUID), ("pid", c_uint32)]

    class VALUE(Union):
        _fields_ = [("ptr", c_void_p), ("raw", c_byte * 16)]

    class PROPVARIANT(Structure):
        _fields_ = [("vt", c_uint16), ("w1", c_uint16), ("w2", c_uint16),
                    ("w3", c_uint16), ("value", VALUE)]

    def guid(value):
        return GUID.from_buffer_copy(uuid.UUID(value).bytes_le)

    ole32 = ctypes.OleDLL("ole32")
    ole32.CoInitializeEx.argtypes = (c_void_p, c_uint32)
    ole32.CoInitializeEx.restype = c_long
    ole32.CoUninitialize.argtypes = ()
    ole32.CoCreateInstance.argtypes = (POINTER(GUID), c_void_p, c_uint32,
                                      POINTER(GUID), POINTER(c_void_p))
    ole32.CoCreateInstance.restype = c_long
    ole32.CoTaskMemFree.argtypes = (c_void_p,)
    ole32.PropVariantClear.argtypes = (POINTER(PROPVARIANT),)
    ole32.PropVariantClear.restype = c_long

    def check(hr, action):
        if hr < 0:
            raise OSError(f"{action} failed: HRESULT 0x{hr & 0xffffffff:08x}")

    def method(obj, index, *args):
        return ctypes.WINFUNCTYPE(c_long, c_void_p, *args)(
            ctypes.cast(obj, POINTER(POINTER(c_void_p))).contents[index])

    def release(obj):
        if obj:
            method(obj, 2)(obj)

    hr = ole32.CoInitializeEx(None, 0)  # COINIT_MULTITHREADED
    initialized = hr in (0, 1)
    # RPC_E_CHANGED_MODE means the calling thread is already in an STA.
    if not initialized and (hr & 0xffffffff) != 0x80010106:
        check(hr, "CoInitializeEx")

    enumerator = c_void_p()
    collection = c_void_p()
    result = []
    try:
        check(ole32.CoCreateInstance(
            byref(guid("BCDE0395-E52F-467C-8E3D-C4579291692E")), None,
            1, byref(guid("A95664D2-9614-4F35-A746-DE8DB63617E6")),
            byref(enumerator)), "IMMDeviceEnumerator")
        check(method(enumerator, 3, c_int, c_uint32, POINTER(c_void_p))(
            enumerator, 0, 1, byref(collection)), "EnumAudioEndpoints")
        count = c_uint32()
        check(method(collection, 3, POINTER(c_uint32))(
            collection, byref(count)), "IMMDeviceCollection.GetCount")
        key = PROPERTYKEY(guid("A45C254E-DF1C-4EFD-8020-67D146A850E0"), 14)
        for i in range(count.value):
            device = c_void_p()
            store = c_void_p()
            endpoint_ptr = c_void_p()
            prop = PROPVARIANT()
            try:
                check(method(collection, 4, c_uint32, POINTER(c_void_p))(
                    collection, i, byref(device)), "IMMDeviceCollection.Item")
                check(method(device, 5, POINTER(c_void_p))(
                    device, byref(endpoint_ptr)), "IMMDevice.GetId")
                endpoint_id = ctypes.wstring_at(endpoint_ptr)
                check(method(device, 4, c_uint32, POINTER(c_void_p))(
                    device, 0, byref(store)), "IMMDevice.OpenPropertyStore")
                check(method(store, 5, POINTER(PROPERTYKEY), POINTER(PROPVARIANT))(
                    store, byref(key), byref(prop)), "IPropertyStore.GetValue")
                name = ctypes.wstring_at(prop.value.ptr) if prop.vt == 31 and prop.value.ptr else ""
                if endpoint_id and name:
                    result.append(RenderEndpoint(endpoint_id, name))
            finally:
                ole32.PropVariantClear(byref(prop))
                if endpoint_ptr:
                    ole32.CoTaskMemFree(endpoint_ptr)
                release(store)
                release(device)
    finally:
        release(collection)
        release(enumerator)
        if initialized:
            ole32.CoUninitialize()
    return result


def render_endpoints():
    """Read active render endpoints. Windows failures propagate to caller."""
    return _native_render_endpoints()


def normalize_name(name):
    """Exact-match-friendly normalization: do not guess different physical devices."""
    name = str(name or "").strip().casefold()
    for suffix in (" (loopback)", " [loopback]", " - loopback"):
        if name.endswith(suffix):
            name = name[:-len(suffix)]
    return " ".join(name.split())


def unique_endpoint_for_name(endpoints, name):
    matches = [e for e in endpoints if normalize_name(e.friendly_name) == normalize_name(name)]
    return matches[0] if len(matches) == 1 else None


def identity_by_id(endpoints, endpoint_id):
    matches = [e for e in endpoints if e.endpoint_id == endpoint_id]
    if len(matches) != 1:
        raise RuntimeError("Saved Windows endpoint ID unavailable or duplicated; refresh selection.")
    return matches[0]


def stable_label(endpoint):
    """Serializable IMMDevice ID label; never a PortAudio numeric index."""
    encoded = base64.urlsafe_b64encode(endpoint.endpoint_id.encode("utf-8")).decode("ascii").rstrip("=")
    return f"IMM:{encoded} | {endpoint.friendly_name}"


def parse_stable_label(selected):
    if not str(selected).startswith("IMM:"):
        return None
    token, separator, _name = str(selected)[4:].partition(" | ")
    if not separator or not token:
        raise RuntimeError("Malformed saved Windows endpoint identity.")
    try:
        padded = token + "=" * (-len(token) % 4)
        return base64.b64decode(padded, altchars=b"-_", validate=True).decode("utf-8")
    except (ValueError, UnicodeError) as exc:
        raise RuntimeError("Invalid saved Windows endpoint identity.") from exc


def unique_native_device_index(endpoints, endpoint_id, devices, name_index=1, api_index=None):
    """Safe mapping only when endpoint name and native device name are both unique.

    Name-only native API bindings cannot establish an IMMDevice-to-PortAudio
    relationship when names collide. Return None instead of guessing.
    """
    endpoint = identity_by_id(endpoints, endpoint_id)
    if unique_endpoint_for_name(endpoints, endpoint.friendly_name) != endpoint:
        return None
    candidates = [item for item in devices
                  if normalize_name(item[name_index]) == normalize_name(endpoint.friendly_name)
                  and (api_index is None or "wasapi" in str(item[api_index]).casefold())]
    return candidates[0][0] if len(candidates) == 1 else None

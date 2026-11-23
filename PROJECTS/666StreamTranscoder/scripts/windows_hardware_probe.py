"""R11 read-only Windows endpoint inventory. No stream, driver install or secrets.

Use from an actual Windows host, not as evidence of physical audio on CI.
"""
import argparse
import hashlib
import json
import sys

from radiostreamer.resin3 import windows_endpoints


def inventory():
    endpoints = windows_endpoints.render_endpoints()
    rows = []
    for endpoint in endpoints:
        rows.append({
            "id_sha256_12": hashlib.sha256(endpoint.endpoint_id.encode("utf-8")).hexdigest()[:12],
            "name": endpoint.friendly_name,
            "native_immdevice_id_available": bool(endpoint.endpoint_id),
        })
    return {
        "platform": sys.platform,
        "native_core_audio_endpoint_count": len(rows),
        "endpoints": rows,
        "physical_monitor_verified": False,
        "wasapi_capture_verified": False,
        "virtual_cable_verified": False,
        "remote_shoutcast_icecast_verified": False,
        "windows_installer_verified": False,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON evidence without raw IMMDevice IDs")
    args = parser.parse_args()
    if sys.platform != "win32":
        print("Windows host required for IMMDevice hardware inventory.", file=sys.stderr)
        return 2
    try:
        report = inventory()
    except Exception as exc:
        print(f"Native endpoint inventory failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

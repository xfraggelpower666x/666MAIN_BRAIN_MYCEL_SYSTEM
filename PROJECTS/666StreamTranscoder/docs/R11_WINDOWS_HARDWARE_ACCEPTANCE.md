# R11 · Windows Core Audio identity and host acceptance

## What changed

- `radiostreamer/resin3/windows_endpoints.py` reads active Windows audio
  **render** endpoints from the native MMDeviceEnumerator COM interface:
  IMMDeviceCollection, IMMDevice::GetId and PKEY_Device_FriendlyName.
- This is an actual persistent Windows IMMDevice ID, **not** a PortAudio or
  PyAudioWPatch enumeration index. The value is serialized in an `IMM:` label.
- The current capture/monitor adapters can bind the stable ID to a native
  PortAudio/WASAPI device only if both the Core Audio friendly name and the
  native device name are unique. Ambiguous, missing and stale IDs fail closed.
- Existing `PA:` and `WASAPI:` labels, legacy unambiguous names, queue,
  system audio, app capture, virtual cables, Shoutcast/Icecast and monitors
  retain their previous behavior.
- This cannot guarantee mapping every vendor's duplicate/friendly-name alias
  to the correct PortAudio or PyAudioWPatch endpoint. Such cases remain
  explicitly unresolved, rather than secretly choosing another output.

## Actual Windows host read-only inventory

From the repository project root on the target Windows PC:

```powershell
python scripts/windows_hardware_probe.py --json
```

The report prints only a short SHA256 fingerprint of each endpoint ID.
It does **not** print server passwords, station tokens, raw device IDs or
perform driver installation. It never connects to an external provider.

## Physical host acceptance matrix (manual)

1. **Stable render selection:** In Broadcast > Local Monitor, refresh devices;
   select an IMM-prefixed entry (only if an exact match is available). Close and
   restart the app. The saved identity must resolve to the same physical output
   even when the order of PortAudio devices changes.
2. **Hotplug:** While **OFF AIR**, unplug the selected USB headset or interface,
   refresh devices and attempt monitor playback. Confirm an explicit error
   rather than playback on another output. Reconnect and refresh to restore it.
3. **WASAPI capture:** Choose a matching IMM-prefixed loopback endpoint when
   available. Record a test source on a local server and verify the intended
   speaker's audio is captured and different devices remain isolated.
4. **VB-CABLE:** Select CABLE Output as capture and a physical speaker as
   monitor. Verify no feedback. Attempt monitoring into the matching CABLE
   Input and verify the safety guard blocks it. Test separate A/B cables
   independently if installed.
5. **Monitor versus stream:** Adjust local volume and stop local monitor; the
   radio stream must stay connected and its output gain must not change.
6. **Remote providers:** Separately connect to a user-owned Shoutcast v1/v2
   and Icecast endpoint with test credentials kept in local user settings;
   verify relay recovery after network interruption.
7. **Build:** Produce a Windows portable EXE and Inno Setup installer, start
   each under a normal user account, verify packaged Core Audio lookup and
   FFmpeg/monitor dependencies.

For each run record Windows build, playback endpoint fingerprint, audio
interface, VB-CABLE version, timestamp, app commit, logs, pass/fail and
observed behavior. Do not commit private tokens, raw device IDs or logs that
contain personal machine data.

## Verification boundaries

- Linux/CI tests for identity mapping use fake PortAudio/WASAPI inventories.
- A Windows CI runner may exercise COM enumeration, but it is not the user's
  physical hardware and does not prove acoustic signal routing.
- Genuine device tests and real provider tests remain OPEN until performed
  on a Windows host / owned radio endpoint with an evidence receipt.

"""Use the DAW's local ACE-Step queue without loading a second model."""

import json
import time
from urllib.parse import parse_qs, urlsplit


LOCAL_API = "http://127.0.0.1:8001"
JOB_TIMEOUT_SECONDS = 3600
REQUEST_TIMEOUT_SECONDS = 30


def build_request(params, settings):
    task = params.get("task_type", "text2music")
    if task not in {"text2music", "cover", "repaint"}:
        raise ValueError(f"Local queue does not support task type: {task}")
    if params.get("sample_mode"):
        raise ValueError("Sample mode is not supported by the shared local node yet.")
    if params.get("audio_codes"):
        raise ValueError("Audio codes are not supported by the shared local node yet.")
    if task in {"cover", "repaint"} and params.get("src_audio") is None:
        raise ValueError(f"{task} requires source audio.")
    if (task == "text2music" and params.get("auto_metas", True)
            and not settings.get("thinking", True)
            and not settings.get("use_cot_caption", True)
            and not settings.get("use_cot_language", True)):
        raise ValueError("Auto metadata alone cannot initialize the local language model yet.")
    top_p = settings.get("lm_top_p", 0.9)
    if not 0 < top_p < 1:
        raise ValueError("The local queue only preserves top_p values between 0 and 1.")

    seed = str(settings.get("seed", "-1")).strip().split(",")[0].strip()
    try:
        seed_number = int(seed)
    except ValueError as exc:
        raise ValueError(f"Invalid seed: {seed!r}") from exc

    direct = task in {"cover", "repaint"}
    request = {
        "task_type": task,
        "prompt": params.get("caption", ""),
        "lyrics": "[Instrumental]" if params.get("instrumental") else params.get("lyrics", ""),
        "vocal_language": params.get("vocal_language", "en"),
        "audio_format": "wav",
        "batch_size": 1,
        "thinking": False if direct else settings.get("thinking", True),
        "use_cot_caption": False if direct else settings.get("use_cot_caption", True),
        "use_cot_language": False if direct else settings.get("use_cot_language", True),
        "use_cot_metas": False if direct else params.get("auto_metas", True),
        "lm_temperature": settings.get("temperature", 0.85),
        "lm_cfg_scale": settings.get("lm_cfg_scale", 2.0),
        "lm_top_p": top_p,
        "lm_top_k": settings.get("lm_top_k", 0),
        "guidance_scale": settings.get("dit_guidance_scale", 7.0),
        "inference_steps": settings.get("dit_inference_steps", 8),
        "infer_method": settings.get("dit_infer_method", "ode"),
        "use_random_seed": seed_number == -1,
        "seed": seed_number,
    }
    for source, target in (
        ("duration", "audio_duration"), ("bpm", "bpm"),
        ("key_scale", "key_scale"), ("time_signature", "time_signature"),
    ):
        value = params.get(source)
        if value is not None and value != "" and value != 0 and value != -1:
            request[target] = value
    if task == "cover":
        request["audio_cover_strength"] = params.get("remix_strength", 1.0)
        request["cover_noise_strength"] = params.get("cover_strength", 0.0)
    if task == "repaint":
        request["repainting_start"] = params.get("repaint_start", 0.0)
        if params.get("repaint_end", 0.0) > 0:
            request["repainting_end"] = params["repaint_end"]
    return request


def _data(response):
    response.raise_for_status()
    envelope = response.json()
    if envelope.get("error") or envelope.get("code", 200) != 200:
        raise RuntimeError(f"ACE-Step API error: {envelope.get('error') or envelope.get('code')}")
    return envelope["data"]


def _audio_path(value):
    if value.startswith("/v1/audio?"):
        values = parse_qs(urlsplit(value).query).get("path", [])
        if len(values) != 1:
            raise RuntimeError("ACE-Step returned an invalid audio URL.")
        return values[0]
    if "://" in value or not value:
        raise RuntimeError("ACE-Step returned an invalid audio path.")
    return value


def generate(params, settings, encode_audio, http, *, sleep=time.sleep, clock=time.monotonic):
    request = build_request(params, settings)
    files = {}
    for key, field in (("src_audio", "src_audio"), ("refer_audio", "reference_audio")):
        if params.get(key) is not None:
            files[field] = (f"{field}.wav", encode_audio(params[key]), "audio/wav")
    form = {key: str(value).lower() if isinstance(value, bool) else str(value)
            for key, value in request.items()}
    if files:
        response = http.post(f"{LOCAL_API}/release_task", data=form, files=files, timeout=REQUEST_TIMEOUT_SECONDS)
    else:
        response = http.post(f"{LOCAL_API}/release_task", json=request, timeout=REQUEST_TIMEOUT_SECONDS)
    task_id = _data(response)["task_id"]
    deadline = clock() + JOB_TIMEOUT_SECONDS
    while clock() < deadline:
        result = _data(http.post(
            f"{LOCAL_API}/query_result", json={"task_id_list": [task_id]},
            timeout=REQUEST_TIMEOUT_SECONDS,
        ))
        if not isinstance(result, list) or len(result) != 1 or result[0].get("task_id") != task_id:
            raise RuntimeError("ACE-Step returned an invalid task result.")
        entry = result[0]
        if entry.get("status") == 0:
            sleep(1)
            continue
        items = json.loads(entry.get("result", "[]"))
        if entry.get("status") != 1:
            detail = items[0].get("error") if items and isinstance(items[0], dict) else None
            raise RuntimeError(f"ACE-Step generation failed: {detail or entry.get('progress_text') or 'unknown error'}")
        if not items or not isinstance(items[0], dict):
            raise RuntimeError("ACE-Step returned no audio result.")
        path = _audio_path(items[0].get("file", ""))
        audio = http.get(f"{LOCAL_API}/v1/audio", params={"path": path}, timeout=REQUEST_TIMEOUT_SECONDS)
        audio.raise_for_status()
        return audio.content, json.dumps(items[0], ensure_ascii=False)
    raise TimeoutError("ACE-Step task timed out; generation may still be running on the server.")

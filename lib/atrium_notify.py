#!/usr/bin/env python3.11
"""
atrium_notify — routing logic, channel implementations, and state persistence
for the atrium-notify primitive.

Supports urgency: critical | high | normal | low
Supports modality: auto | voice | telegram | reach | sms | log

Routing matrix (auto mode):
  critical  → voice + telegram; escalate: reach_ring +30s no-ack; always: breadcrumb
  high      → telegram; escalate: voice if up; always: breadcrumb
  normal    → telegram; escalate: none; always: breadcrumb
  low       → breadcrumb only

Defaults enforced:
  1. Quiet hours 23:00–07:00 mute voice + reach_ring (bypassed for critical)
  2. Fire-and-forget — escalation runs in background subprocess
  3. Silent downgrade on channel failure (telegram → reach text → log)
  4. Auto-prefix sender if ATRIUM_NOTIFY_SENDER env is set
  5. SMS banned from auto-routing
  6. Auto-thread by topic (1h TTL, state in ~/Atrium/state/notify-threads.json)
"""
from __future__ import annotations

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

# ── logging ────────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.WARNING,
    format="atrium-notify: %(levelname)s: %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger("atrium_notify")

# ── constants ──────────────────────────────────────────────────────────────────
ATRIUM_ROOT = Path(os.environ.get("ATRIUM_ROOT", Path.home() / "Atrium"))
STATE_DIR = ATRIUM_ROOT / "state"
THREADS_FILE = STATE_DIR / "notify-threads.json"
LOG_FILE = STATE_DIR / "notify.log"
BREADCRUMBS_FILE = Path.home() / ".claude" / "cache" / "session-breadcrumbs.md"

TELEGRAM_ENV = Path.home() / ".claude" / "channels" / "telegram" / ".env"
TELEGRAM_ACCESS = Path.home() / ".claude" / "channels" / "telegram" / "access.json"

REACH_SRC = Path.home() / ".claude" / "mcp-servers" / "reach"

QUIET_START = 23  # 23:00 local
QUIET_END = 7     # 07:00 local
THREAD_TTL_SECONDS = 3600  # 1 hour

URGENCY_LEVELS = ("critical", "high", "normal", "low")
MODALITY_CHOICES = ("auto", "voice", "telegram", "reach", "sms", "log")

# ── helpers ────────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).astimezone().isoformat(timespec="seconds")


def _is_quiet_hours() -> bool:
    hour = datetime.now().hour
    if QUIET_START > QUIET_END:
        return hour >= QUIET_START or hour < QUIET_END
    return QUIET_START <= hour < QUIET_END


def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.rename(path)


def _telegram_creds() -> tuple[str, str] | None:
    """Return (token, chat_id) or None.

    Token resolution order:
      1. TELEGRAM_BOT_TOKEN environment variable (allows test overrides)
      2. ~/.claude/channels/telegram/.env file
    """
    # env var takes precedence (enables garbage-token testing per AC4)
    token: str | None = os.environ.get("TELEGRAM_BOT_TOKEN") or None
    if not token:
        try:
            for line in TELEGRAM_ENV.read_text().splitlines():
                if line.startswith("TELEGRAM_BOT_TOKEN="):
                    token = line.split("=", 1)[1].strip()
        except Exception:
            return None

    try:
        access = json.loads(TELEGRAM_ACCESS.read_text())
        chat_id = str(access["allowFrom"][0])
    except Exception:
        return None

    if not token or not chat_id:
        return None
    return token, chat_id


# ── breadcrumb channel ─────────────────────────────────────────────────────────

def channel_breadcrumb(message: str, urgency: str) -> bool:
    """Append a breadcrumb. Always succeeds."""
    try:
        BREADCRUMBS_FILE.parent.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y-%m-%dT%H:%M")
        line = f"- [NOTIFY-{urgency.upper()}] {message}\n"
        with BREADCRUMBS_FILE.open("a") as f:
            f.write(line)
        return True
    except Exception as e:
        log.warning("breadcrumb write failed: %s", e)
        return False


# ── telegram channel ───────────────────────────────────────────────────────────

def channel_telegram(
    message: str,
    reply_to_message_id: Optional[int] = None,
) -> Optional[int]:
    """Send a Telegram message. Returns message_id on success, None on failure."""
    import requests as req

    creds = _telegram_creds()
    if not creds:
        log.warning("Telegram credentials not found")
        return None

    token, chat_id = creds
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload: dict = {"chat_id": chat_id, "text": message}
    if reply_to_message_id is not None:
        payload["reply_to_message_id"] = reply_to_message_id

    try:
        resp = req.post(url, json=payload, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("ok"):
                return data["result"]["message_id"]
            log.warning("Telegram API error: %s", data.get("description", "unknown"))
            return None
        log.warning(
            "Telegram POST failed: HTTP %s — %s",
            resp.status_code,
            resp.text[:120],
        )
        return None
    except Exception as e:
        log.warning("Telegram request exception: %s", e)
        return None


# ── reach channel ──────────────────────────────────────────────────────────────

def _reach_client():
    """Import and return a connected GSConnectClient, or None."""
    if str(REACH_SRC) not in sys.path:
        sys.path.insert(0, str(REACH_SRC))
    try:
        from dbus_client import GSConnectClient  # type: ignore
        client = GSConnectClient()
        if client.connect_to_device():
            return client
        log.warning("reach: no connected device found")
        return None
    except Exception as e:
        log.warning("reach: could not import dbus_client: %s", e)
        return None


def channel_reach_text(message: str) -> bool:
    """Send text via GSConnect. Returns True on success."""
    client = _reach_client()
    if not client:
        return False
    err = client.share_text(message)
    if err:
        log.warning("reach text failed: %s", err)
        return False
    return True


def channel_reach_ring() -> bool:
    """Ring the phone via GSConnect. Returns True on success."""
    client = _reach_client()
    if not client:
        return False
    err = client.ring()
    if err:
        log.warning("reach ring failed: %s", err)
        return False
    return True


def channel_reach_ping(message: str) -> bool:
    """Ping the phone via GSConnect. Returns True on success."""
    client = _reach_client()
    if not client:
        return False
    err = client.ping(message)
    if err:
        log.warning("reach ping failed: %s", err)
        return False
    return True


# ── voice channel (stub) ───────────────────────────────────────────────────────

def channel_voice(message: str) -> bool:
    """
    Voice route — NOT YET IMPLEMENTED.
    TODO (Phase 2.2b): wire to voicemode MCP tool / Kokoro TTS.
    """
    print(
        "atrium-notify: voice route requested but not yet implemented",
        file=sys.stderr,
    )
    channel_breadcrumb(f"[voice-stub] {message}", "voice")
    return False


# ── SMS channel ────────────────────────────────────────────────────────────────

def channel_sms(message: str, number: str) -> bool:
    """Send SMS via GSConnect. Only fires on explicit --modality sms."""
    if not number:
        log.warning("sms: no phone number provided (--sms-to required)")
        return False
    client = _reach_client()
    if not client:
        return False
    err = client.send_sms(number, message)
    if err:
        log.warning("sms send failed: %s", err)
        return False
    return True


# ── thread state ───────────────────────────────────────────────────────────────

def _load_threads() -> dict:
    return _load_json(THREADS_FILE)


def _save_threads(threads: dict) -> None:
    _save_json(THREADS_FILE, threads)


def get_thread_id(topic: str) -> Optional[int]:
    """Return reply_to_message_id if topic has a recent (< 1h) entry, else None."""
    threads = _load_threads()
    entry = threads.get(topic)
    if not entry:
        return None
    last_ts = entry.get("last_ts_iso")
    if not last_ts:
        return None
    try:
        then = datetime.fromisoformat(last_ts)
        now = datetime.now(tz=then.tzinfo)
        age = (now - then).total_seconds()
        if age < THREAD_TTL_SECONDS:
            return entry.get("last_message_id")
    except Exception:
        pass
    return None


def save_thread_id(topic: str, message_id: int, chat_id: str) -> None:
    """Persist the latest message_id for a topic."""
    threads = _load_threads()
    threads[topic] = {
        "chat_id": chat_id,
        "last_message_id": message_id,
        "last_ts_iso": _now_iso(),
    }
    _save_threads(threads)


# ── observability log ──────────────────────────────────────────────────────────

def append_log(
    urgency: str,
    modality: str,
    channels_used: list[str],
    message: str,
) -> None:
    """Append a structured line to notify.log."""
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        ts = _now_iso()
        channels_str = ",".join(channels_used) if channels_used else "none"
        msg_trunc = message[:120].replace("\t", " ")
        line = f"{ts}\t{urgency}\t{modality}\t{channels_str}\t{msg_trunc}\n"
        with LOG_FILE.open("a") as f:
            f.write(line)
    except Exception as e:
        log.warning("notify.log write failed: %s", e)


# ── escalation subprocess ──────────────────────────────────────────────────────

def _spawn_escalation_ring(delay_s: int = 30) -> None:
    """Spawn a background process that rings after delay if no ack (fire-forget)."""
    script = f"""
import time, sys, os
sys.path.insert(0, '{str(REACH_SRC)}')
time.sleep({delay_s})
try:
    from dbus_client import GSConnectClient
    c = GSConnectClient()
    if c.connect_to_device():
        c.ring()
except Exception as e:
    print(f"escalation ring failed: {{e}}", file=sys.stderr)
"""
    subprocess.Popen(
        [sys.executable, "-c", script],
        start_new_session=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


# ── core router ────────────────────────────────────────────────────────────────

def notify(
    message: str,
    urgency: str = "normal",
    modality: str = "auto",
    topic: Optional[str] = None,
    thread_id: Optional[int] = None,
    sms_to: Optional[str] = None,
) -> int:
    """
    Main entry point. Returns exit code (0 = success, 1 = all channels failed).

    Applies sender prefix from ATRIUM_NOTIFY_SENDER env var.
    """
    # ── sender prefix (default 4) ──────────────────────────────────────────────
    sender = os.environ.get("ATRIUM_NOTIFY_SENDER", "")
    if sender:
        message = f"[{sender}] {message}"

    # ── validate args ──────────────────────────────────────────────────────────
    if urgency not in URGENCY_LEVELS:
        print(f"atrium-notify: unknown urgency {urgency!r}", file=sys.stderr)
        return 2
    if modality not in MODALITY_CHOICES:
        print(f"atrium-notify: unknown modality {modality!r}", file=sys.stderr)
        return 2

    quiet = _is_quiet_hours()
    channels_used: list[str] = []

    # ── explicit modality routes ───────────────────────────────────────────────
    if modality == "log":
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    if modality == "sms":
        ok = channel_sms(message, sms_to or "")
        if ok:
            channels_used.append("sms")
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0 if ok else 1

    if modality == "voice":
        bypass_quiet = (urgency == "critical")
        if quiet and not bypass_quiet:
            print(
                "atrium-notify: voice muted (quiet hours 23:00–07:00); downgrading to telegram",
                file=sys.stderr,
            )
            channel_breadcrumb(f"[voice-muted→telegram] {message}", urgency)
            _send_telegram_with_fallback(message, urgency, topic, thread_id, channels_used)
        else:
            channel_voice(message)
            channels_used.append("voice-stub")
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    if modality == "reach":
        ok = channel_reach_text(message)
        if ok:
            channels_used.append("reach-text")
        else:
            log.warning("reach text failed, falling back to log")
            channels_used.append("log-fallback")
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    if modality == "telegram":
        _send_telegram_with_fallback(message, urgency, topic, thread_id, channels_used)
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    # ── auto routing ───────────────────────────────────────────────────────────
    assert modality == "auto"

    if urgency == "low":
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    if urgency == "normal":
        _send_telegram_with_fallback(message, urgency, topic, thread_id, channels_used)
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    if urgency == "high":
        _send_telegram_with_fallback(message, urgency, topic, thread_id, channels_used)
        # escalation: voice (if service up — stub, so skip silently)
        # breadcrumb always
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")
        append_log(urgency, modality, channels_used, message)
        return 0

    if urgency == "critical":
        bypass_quiet = True  # critical bypasses quiet hours
        # primary: voice + telegram (fire voice in bg, fire telegram now)
        # voice is stubbed — log it
        channel_voice(message)
        channels_used.append("voice-stub")

        _send_telegram_with_fallback(message, urgency, topic, thread_id, channels_used)
        channel_breadcrumb(message, urgency)
        channels_used.append("breadcrumb")

        # escalation: reach_ring after 30s if not quiet (or critical bypasses quiet)
        if not quiet or bypass_quiet:
            _spawn_escalation_ring(delay_s=30)
            channels_used.append("reach-ring-escalation-bg")

        append_log(urgency, modality, channels_used, message)
        return 0

    # unreachable
    return 1


def _send_telegram_with_fallback(
    message: str,
    urgency: str,
    topic: Optional[str],
    thread_id: Optional[int],
    channels_used: list[str],
) -> None:
    """
    Try Telegram. On failure, fall back to reach text, then log.
    Updates thread state if topic is provided and send succeeds.
    """
    # resolve reply_to from topic state or explicit thread_id
    reply_to: Optional[int] = thread_id
    if topic and reply_to is None:
        reply_to = get_thread_id(topic)

    msg_id = channel_telegram(message, reply_to_message_id=reply_to)

    if msg_id is not None:
        channels_used.append("telegram")
        # persist thread state
        if topic:
            creds = _telegram_creds()
            chat_id = creds[1] if creds else "unknown"
            save_thread_id(topic, msg_id, chat_id)
        return

    # fallback 1: reach text
    print(
        "atrium-notify: telegram failed, falling back to reach text",
        file=sys.stderr,
    )
    channel_breadcrumb(f"[telegram-failed→reach] {message}", urgency)
    ok = channel_reach_text(message)
    if ok:
        channels_used.append("reach-text-fallback")
        return

    # fallback 2: log
    print(
        "atrium-notify: reach text failed, falling back to log only",
        file=sys.stderr,
    )
    channel_breadcrumb(f"[all-channels-failed] {message}", urgency)
    channels_used.append("log-fallback")


# ── CLI entry point ────────────────────────────────────────────────────────────

def _build_parser():
    import argparse

    p = argparse.ArgumentParser(
        prog="atrium-notify",
        description="Unified operator notification primitive for Atrium.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Urgency levels:
  critical  voice + telegram; reach_ring escalation +30s; bypasses quiet hours
  high      telegram primary; breadcrumb always
  normal    telegram primary; breadcrumb always
  low       breadcrumb only

Modality:
  auto      routing matrix above (default)
  voice     voice channel (stub in 2.2; 2.2b will wire Kokoro)
  telegram  telegram only (with fallback chain on failure)
  reach     GSConnect text share
  sms       SMS via phone (explicit only; never auto-selected)
  log       breadcrumb only, no network calls

Quiet hours: 23:00–07:00 local — voice + reach_ring muted (critical bypasses).

Topic threading: --topic name groups messages into a Telegram thread for 1h.
State at ~/Atrium/state/notify-threads.json.

Environment:
  ATRIUM_NOTIFY_SENDER   if set, prepend [SENDER] to message (for subagents)
""",
    )
    p.add_argument("message", nargs="?", help="Message text to send")
    p.add_argument(
        "--urgency",
        default="normal",
        choices=URGENCY_LEVELS,
        help="Urgency tier (default: normal)",
    )
    p.add_argument(
        "--modality",
        default="auto",
        choices=MODALITY_CHOICES,
        help="Channel selection (default: auto)",
    )
    p.add_argument("--topic", default=None, help="Topic name for thread grouping")
    p.add_argument(
        "--thread-id",
        type=int,
        default=None,
        help="Explicit Telegram reply_to_message_id",
    )
    p.add_argument(
        "--sms-to",
        default=None,
        help="Phone number for --modality sms",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    if not args.message:
        parser.print_help()
        return 2

    return notify(
        message=args.message,
        urgency=args.urgency,
        modality=args.modality,
        topic=args.topic,
        thread_id=args.thread_id,
        sms_to=args.sms_to,
    )


if __name__ == "__main__":
    sys.exit(main())

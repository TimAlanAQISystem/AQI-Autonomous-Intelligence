"""Simple polling tool to watch GOA/relay state via /debug_state.

Run this alongside an active test call to observe:
  - goa_listen_gate_active
  - pre_gate_human_speech
  - conversation_state
  - audio_playing / twilio_playback_done
  - any active_conversations

Usage:
  python goa_micro_audit_poll.py --interval 0.5
"""

import argparse
import json
import time
import urllib.request


def fetch_state(url):
    try:
        data = urllib.request.urlopen(url, timeout=3).read().decode('utf-8')
        return json.loads(data)
    except Exception as e:
        return {"error": str(e)}


def short(ctx):
    return {
        "call_sid": ctx.get("call_sid"),
        "conversation_state": ctx.get("conversation_state"),
        "goa_listen_gate_active": ctx.get("_goa_listen_gate_active"),
        "pre_gate_human_speech": ctx.get("_pre_gate_human_speech"),
        "audio_playing": ctx.get("audio_playing"),
        "twilio_playback_done": ctx.get("twilio_playback_done"),
        "first_turn_complete": ctx.get("first_turn_complete"),
        "eab_env_class": ctx.get("_eab_env_class"),
    }


def main():
    parser = argparse.ArgumentParser(description="Poll /debug_state for GOA gate/audit info")
    parser.add_argument("--url", default="http://localhost:8777/debug_state", help="Debug state endpoint")
    parser.add_argument("--interval", type=float, default=1.0, help="Polling interval (seconds)")
    parser.add_argument("--count", type=int, default=0, help="Number of iterations to run (0 = forever)")
    args = parser.parse_args()

    print(f"Polling {args.url} every {args.interval}s (count={args.count or '∞'})")

    try:
        n = 0
        while args.count == 0 or n < args.count:
            n += 1
            state = fetch_state(args.url)
            if "error" in state:
                print(f"ERROR: {state['error']}")
            else:
                governor = state.get("governor", {})
                relay = state.get("relay", {})
                active = relay.get("active_conversations", [])
                print(f"[{time.strftime('%H:%M:%S')}] governor.call_in_progress={governor.get('call_in_progress')} cooldown={governor.get('cooldown_remaining')}")
                if active:
                    for c in active:
                        print("  -", json.dumps(short(c), ensure_ascii=False))
                else:
                    print("  (no active conversations)")
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("Stopped.")


if __name__ == '__main__':
    main()

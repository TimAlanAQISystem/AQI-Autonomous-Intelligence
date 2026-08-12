# Alan Voice and Telephony Integration Guide

## Purpose

Wire the sales autonomy layer into Alan's existing telephony stack without bypassing the governance spine.

## Existing Repo Surfaces

- Primary conversation relay: [aqi_conversation_relay_server.py](/c:/Users/signa/OneDrive/Desktop/Agent X/aqi_conversation_relay_server.py)
- Secondary relay server: [agent_x_conversation_relay_server.py](/c:/Users/signa/OneDrive/Desktop/Agent X/agent_x_conversation_relay_server.py)
- Control boundary: [control_api_fixed.py](/c:/Users/signa/OneDrive/Desktop/Agent X/control_api_fixed.py)
- Outbound dialer: [outbound_controller.py](/c:/Users/signa/OneDrive/Desktop/Agent X/outbound_controller.py)
- Telephony perception canon: [CONSTITUTIONAL_CORE/telephony_perception_canon.py](/c:/Users/signa/OneDrive/Desktop/Agent X/CONSTITUTIONAL_CORE/telephony_perception_canon.py)

## Sales-Autonomy Adapter Surface

Implemented in [sales_autonomy/telephony_handler.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/telephony_handler.py).

### Expected Adapter Contract

```python
class TelephonyAdapter(Protocol):
    def call(self, phone_number: str) -> str:
        ...

    def play(self, call_id: str, text: str) -> None:
        ...
```

## Recommended Wiring Path

### Outbound

- `TelephonyAdapter.call()` should delegate to the call-initiation path in [outbound_controller.py](/c:/Users/signa/OneDrive/Desktop/Agent X/outbound_controller.py)
- Opening script playback should reuse the existing voice-play path after call creation

### Realtime Speech Loop

- Incoming STT events from ConversationRelay should be adapted into:

```python
{
    "type": "incoming_speech",
    "call_id": call_id,
    "text": transcript,
}
```

- These events can be routed through `on_call_event()` in [sales_autonomy/telephony_handler.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/telephony_handler.py)

### Telephony Governance

- Telephony perception from [CONSTITUTIONAL_CORE/telephony_perception_canon.py](/c:/Users/signa/OneDrive/Desktop/Agent X/CONSTITUTIONAL_CORE/telephony_perception_canon.py) should remain authoritative for line health
- If telephony perception returns withdrawal or callback posture, the sales workflow should stop advancing toward close

## Governance Requirements Before Call Initiation

Before placing any outbound call:

1. Build live governance posture through [sales_autonomy/sales_governance.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_governance.py)
2. Verify the call through [sales_autonomy/sales_verifier.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_verifier.py)
3. Only dial when the verification result is allowed

## Logging Expectations

- Real call transcript data should remain in the existing relay and monitoring stack
- Close-relevant artifacts should additionally flow into:
  - [sales_autonomy/sales_metrics.py](/c:/Users/signa/OneDrive/Desktop/Agent X/sales_autonomy/sales_metrics.py)
  - CRM logging via [src/crm.py](/c:/Users/signa/OneDrive/Desktop/Agent X/src/crm.py)

## Minimal Wiring Example

```python
from sales_autonomy.telephony_handler import on_call_event

event = {
    "type": "incoming_speech",
    "call_id": call_id,
    "text": transcript,
}
response = on_call_event(event, telephony_api, context={"lead_id": lead_id})
```

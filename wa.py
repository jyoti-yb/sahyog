import os, httpx, json

GRAPH_BASE = "https://graph.facebook.com/v20.0"
ACCESS_TOKEN = os.getenv("WA_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.getenv("WA_PHONE_NUMBER_ID")

async def send_text(to: str, text: str):
    url = f"{GRAPH_BASE}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"preview_url": False, "body": text}
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(url, headers=headers, json=payload)
        try:
            return r.json()
        except Exception:
            return {"status": r.status_code, "text": r.text}

async def send_buttons(to: str, body: str, buttons: list):
    """buttons = [{"id":"btn_id","title":"Title"}, ...]"""
    url = f"{GRAPH_BASE}/{PHONE_NUMBER_ID}/messages"
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": body},
            "action": {"buttons": [{"type":"reply","reply":{"id":b["id"],"title":b["title"]}} for b in buttons]}
        }
    }
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    async with httpx.AsyncClient(timeout=15) as c:
        r = await c.post(url, headers=headers, json=payload)
        try:
            return r.json()
        except Exception:
            return {"status": r.status_code, "text": r.text}

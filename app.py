import os, json, re
from datetime import datetime, date
from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse, JSONResponse
from dotenv import load_dotenv

from models import init_db, SessionLocal, User, Child
from vaccinate_rules import due_windows
from wa import send_text, send_buttons

load_dotenv()
app = FastAPI(title="SwasthyaSaathi MVP")

VERIFY_TOKEN = os.getenv("WA_VERIFY_TOKEN", "test-token")

# load content seeds
def load_seed(topic: str, lang: str):
    fname = f"content_seeds/{topic}_{lang}.json"
    if not os.path.exists(fname):
        fname = f"content_seeds/{topic}_en.json"
    with open(fname, "r", encoding="utf-8") as f:
        return json.load(f)

def disclaimer(lang="en"):
    return "Awareness info only. Not medical advice." if lang=="en" else "केवल जागरूकता हेतु जानकारी। यह चिकित्सा सलाह नहीं है।"

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health")
def health():
    return {"ok": True}

# WhatsApp webhook verification (GET)
@app.get("/webhook/whatsapp", response_class=PlainTextResponse)
def verify(hub_mode: str = "", hub_challenge: str = "", hub_verify_token: str = ""):
    if hub_verify_token == VERIFY_TOKEN:
        return hub_challenge
    return "error"

# WhatsApp incoming (POST)
@app.post("/webhook/whatsapp")
async def incoming(req: Request):
    body = await req.json()
    # Parse WhatsApp webhook payload (simplified for MVP)
    try:
        entry = body["entry"][0]["changes"][0]["value"]
        if "messages" in entry:
            msg = entry["messages"][0]
            from_ = msg["from"]                       # user phone
            msg_type = msg.get("type", "text")
            text = ""
            if msg_type == "text":
                text = msg["text"]["body"].strip()
            elif msg_type == "interactive":
                # button reply
                text = msg["interactive"]["button_reply"]["id"]
            else:
                text = ""

            await route_message(from_, text)
    except Exception as e:
        print("Webhook parse error:", e, body)
    return {"status":"ok"}

async def route_message(user_id: str, text: str):
    # fetch or create user
    db = SessionLocal()
    user = db.query(User).filter(User.wa_user_id==user_id).first()
    if not user:
        user = User(wa_user_id=user_id, language="hi", consent=False)
        db.add(user); db.commit()

    t = text.lower()

    # first-time greeting
    if t in ("hi","hello","नमस्ते","start") or not user.consent:
        await send_buttons(user_id,
            "👋 SwasthyaSaathi — रोकथाम स्वास्थ्य जानकारी (Gov/WHO)। यह चिकित्सा सलाह नहीं है। जारी रखें?",
            [{"id":"consent_yes","title":"हाँ / Yes"},{"id":"consent_no","title":"नहीं / No"}])
        return

    # consent flow
    if t in ("consent_yes","y","yes","हाँ","haan"):
        user.consent = True; db.commit()
        await send_buttons(user_id, "भाषा चुनें / Choose language",
            [{"id":"lang_hi","title":"हिंदी"},{"id":"lang_en","title":"English"}])
        return
    if t in ("consent_no","no","नहीं"):
        await send_text(user_id, "ठीक है। आप 'hi' भेजकर फिर शुरू कर सकते हैं।")
        return

    # language set
    if t in ("lang_hi","हिंदी"):
        user.language = "hi"; db.commit()
        await send_text(user_id, "✅ भाषा सेट: हिंदी। अपना पिनकोड भेजें (उदा: 560001)। " + disclaimer("hi"))
        return
    if t in ("lang_en","english"):
        user.language = "en"; db.commit()
        await send_text(user_id, "✅ Language set: English. Please send your pincode (e.g., 560001). " + disclaimer("en"))
        return

    # pincode capture (6 digits)
    if re.fullmatch(r"[1-9][0-9]{{5}}", t):
        user.pincode = t; db.commit()
        await main_menu(user_id, user.language)
        return

    # menu routes
    if t in ("menu","help","मदद"):
        await main_menu(user_id, user.language); return

    if t in ("vaccination","टीकाकरण रिमाइंडर","vaccination_reminder"):
        lang = user.language
        msg = "Send child's DOB (DD-MM-YYYY). Awareness only." if lang=="en" else "बच्चे की जन्म-तिथि भेजें (DD-MM-YYYY). केवल जागरूकता हेतु।"
        await send_text(user_id, msg + " " + disclaimer(lang)); return

    # capture DOB
    m = re.fullmatch(r"(\d{2})[-/](\d{2})[-/](\d{4})", t)
    if m:
        dd, mm, yyyy = map(int, m.groups())
        try:
            dob = date(yyyy, mm, dd)
            # store as a child (first child only for MVP)
            child = db.query(Child).filter(Child.user_id==user.id).first()
            if not child:
                child = Child(user_id=user.id, dob=dob); db.add(child); db.commit()
            else:
                child.dob = dob; db.commit()
            # compute awareness windows
            windows = due_windows(dob)[:2]  # show next 2
            lines = []
            for w in windows:
                lines.append(f"• {w['vaccine']}: {w['start'].strftime('%d-%b-%Y')} → {w['end'].strftime('%d-%b-%Y')}")
            title = "Upcoming awareness windows:\n" if user.language=="en" else "आगामी जागरूकता विंडो:\n"
            src = "Source: Govt UIP (awareness). " if user.language=="en" else "स्रोत: Govt UIP (जागरूकता)। "
            await send_text(user_id, title + "\n".join(lines) + "\n" + src + disclaimer(user.language))
            return
        except Exception:
            pass

    if t in ("seasonal","मौसमी","dengue","डेंगू"):
        await send_topic(user_id, "dengue_prevention"); return
    if t in ("diarrhea","डायरिया","जलजनित"):
        await send_topic(user_id, "diarrhea_prevention"); return
    if t in ("maternal","मातृ","iron","folate"):
        await send_topic(user_id, "maternal_iron_folate"); return

    if t in ("alerts","local","स्थानीय"):
        lang = user.language
        msg = "Local alert: (demo) No new alerts. You can trigger a mock alert via /alerts/mock." if lang=="en" else "स्थानीय अलर्ट: (डेमो) कोई नया अलर्ट नहीं। आप /alerts/mock से मॉक अलर्ट भेज सकते हैं।"
        await send_text(user_id, msg + " " + disclaimer(lang)); return

    # safety guard: if message seems like symptoms, redirect
    if any(k in t for k in ["fever","pain","vomit","खून","बुखार","सरदर्द"]):
        msg = "For symptoms or emergencies, contact nearest PHC or dial 108. " if user.language=="en" else "लक्षण/आपात स्थिति में नज़दीकी PHC से संपर्क करें या 108 डायल करें। "
        await send_text(user_id, msg + disclaimer(user.language)); return

    # fallback
    await main_menu(user_id, user.language)

async def main_menu(user_id: str, lang: str):
    if lang=="en":
        await send_buttons(user_id,
            "What would you like?",
            [
                {"id":"vaccination","title":"Vaccination reminders"},
                {"id":"seasonal","title":"Seasonal prevention"},
                {"id":"alerts","title":"Local alerts (demo)"}
            ])
    else:
        await send_buttons(user_id,
            "आप क्या जानना चाहेंगे?",
            [
                {"id":"vaccination","title":"टीकाकरण रिमाइंडर"},
                {"id":"seasonal","title":"मौसमी बचाव"},
                {"id":"alerts","title":"स्थानीय अलर्ट (डेमो)"}
            ])

async def send_topic(user_id: str, topic_key: str):
    # use user's language
    db = SessionLocal()
    user = db.query(User).filter(User.wa_user_id==user_id).first()
    lang = (user.language if user else "en")
    seed = load_seed(topic_key, lang)
    bullets = "\n".join([f"• {b}" for b in seed["bullets"]])
    text = (seed.get("title","") + "\n" if seed.get("title") else "") + bullets + "\n" + seed["source"] + " " + disclaimer(lang)
    await send_text(user_id, text)

# --- Mock alert broadcast ---
@app.post("/alerts/mock")
async def mock_alert(payload: dict):
    """payload: {"pincode":"560001","disease":"dengue"} -> pushes a tip to all users with that pincode"""
    pin = payload.get("pincode","")
    dis = payload.get("disease","dengue")
    db = SessionLocal()
    users = db.query(User).filter(User.pincode == pin, User.consent == True).all()
    if not users:
        return JSONResponse({"sent":0, "note":"No users with that pincode/consent"})
    for u in users:
        lang = u.language
        if dis == "dengue":
            seed = load_seed("dengue_prevention", lang)
            bullets = "\n".join([f"• {b}" for b in seed["bullets"][:3]])
            msg = ("🔔 Local alert (demo): Recent dengue uptick in your area.\n" if lang=="en"
                   else "🔔 स्थानीय अलर्ट (डेमो): आपके क्षेत्र में डेंगू मामलों में वृद्धि।\n")
            src = "Source: State health bulletin (demo)." if lang=="en" else "स्रोत: राज्य स्वास्थ्य बुलेटिन (डेमो)।"
            text = msg + bullets + "\n" + src + " " + disclaimer(lang)
            await send_text(u.wa_user_id, text)
        else:
            await send_text(u.wa_user_id, "Alert (demo). " + disclaimer(lang))
    return {"sent": len(users)}

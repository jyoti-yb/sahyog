# SAHYOG MVP (WhatsApp/SMS Awareness-Only Chatbot)

A 3–4 hour **minimum viable product** for a multilingual, awareness-first public health chatbot.
**No diagnosis**; only **preventive tips**, **vaccination schedule awareness**, and **mock local alerts**.

---

## 🚀 Quick Start (Fastest Path)

### 0) Prereqs
- Python 3.10+
- A Meta for Developers account and **WhatsApp Cloud API** test setup:
  - Create an app at https://developers.facebook.com/
  - Add WhatsApp product → get a **test phone number**, **phone number ID**, and **temporary access token** (later use long-lived token).
  - In **WhatsApp → API Setup**, add your phone as a **tester** and message the test number from your phone.
- **ngrok** (or similar tunnel) to expose localhost to the internet.
  - `ngrok http 8000`

### 1) Clone & Install
```bash
cd swasthyasaathi_mvp
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your WA_VERIFY_TOKEN, WA_ACCESS_TOKEN, WA_PHONE_NUMBER_ID, APP_BASE_URL (ngrok URL)
```

### 2) Run the server
```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

### 3) Expose webhook
```bash
ngrok http 8000
# copy the https URL and update APP_BASE_URL in .env if needed
```

### 4) Configure WhatsApp webhook
In Meta → WhatsApp → Configuration:
- Callback URL: `{APP_BASE_URL}/webhook/whatsapp`
- Verify Token: value of `WA_VERIFY_TOKEN` from your `.env`
- Subscribe to **messages**.

### 5) Test End-to-End
- From your WhatsApp (tester phone), send **"hi"** to your test number.
- Your webhook will receive the event and reply with the language & consent flow.

### 6) Demo Scenarios
- **Vaccination reminder (awareness)**: pick "Vaccination reminders" → send child DOB (e.g., `12-04-2023`) → bot returns upcoming awareness windows.
- **Seasonal tips**: choose Monsoon/Dengue tips.
- **Local alert (mock)**: trigger a district alert message by hitting:
  ```bash
  curl -X POST "{APP_BASE_URL}/alerts/mock" -H "Content-Type: application/json" -d '{"pincode":"560001","disease":"dengue"}'
  ```

> **Note**: For hackathon speed, this MVP:
> - Stores users/state in SQLite file (`swasthya.db`).
> - Uses **Hindi + English** seed content; you can add more languages quickly under `content_seeds/`.
> - Includes a small **UIP schedule rules** stub (deterministic) for awareness-only reminders.
> - Outbreak alerts are **mock** (manual trigger) to keep the build inside 3–4 hours.
> - You can later integrate Bhashini/ULCA for translation/TTS and IDSP/WHO fetchers.

---

## 🧠 What This MVP Demonstrates
- **Multilingual menus** (EN/HI), consent, pincode capture, preferences.
- **Awareness-first** flows with **sources** referenced in messages.
- **Zero-diagnosis** guardrails and PHC/108 escalation template.
- **Proactive alert push (mock)** to show the broadcast concept.
- **Simple accuracy & awareness survey harness** to show impact potential.

---

## 🗂️ Project Structure
```
swasthyasaathi_mvp/
  app.py                # FastAPI app & webhook handlers
  wa.py                 # WhatsApp Cloud API send helpers
  models.py             # SQLAlchemy models (SQLite)
  vaccinate_rules.py    # UIP awareness schedule rules (subset)
  content_seeds/
    dengue_en.json
    dengue_hi.json
    diarrhea_en.json
    diarrhea_hi.json
    maternal_iron_en.json
    maternal_iron_hi.json
  requirements.txt
  .env.example
  README.md
```

---

## 🧪 Local Accuracy & Awareness Harness
- After a session, the bot sends a 3-question micro-survey to estimate awareness lift.
- You can track logs in the console for **intent detection** and **answers served**.

---

## 🔒 Safety
- Every flow includes: "**Awareness info only. Not medical advice.**"
- Any symptom-like message triggers PHC/108 guidance.

---


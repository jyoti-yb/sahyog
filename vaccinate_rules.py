from datetime import date, timedelta

# Minimal UIP-like awareness windows (subset for MVP)
# Windows are indicative; ALWAYS present as "awareness-only, check PHC schedule".

def due_windows(dob: date):
    items = []

    # Birth doses: BCG / HepB / OPV-0 (0-14 days window)
    items.append({
        "vaccine": "Birth doses: BCG / HepB / OPV-0",
        "start": dob,
        "end": dob + timedelta(days=14),
        "note": "Birth dose window. Awareness only; verify at PHC."
    })

    # 6,10,14 weeks: Pentavalent/OPV/Rotavirus (simplified)
    items.append({
        "vaccine": "6 weeks: Penta-1 / OPV-1 / Rota-1",
        "start": dob + timedelta(weeks=6),
        "end": dob + timedelta(weeks=8),
        "note": "First 6-week visit."
    })
    items.append({
        "vaccine": "10 weeks: Penta-2 / OPV-2 / Rota-2",
        "start": dob + timedelta(weeks=10),
        "end": dob + timedelta(weeks=12),
        "note": "Second visit."
    })
    items.append({
        "vaccine": "14 weeks: Penta-3 / OPV-3 / Rota-3",
        "start": dob + timedelta(weeks=14),
        "end": dob + timedelta(weeks=16),
        "note": "Third visit."
    })

    # 9-12 months: MR-1 (Measles-Rubella)
    items.append({
        "vaccine": "9–12 months: MR-1",
        "start": dob + timedelta(weeks=39),
        "end": dob + timedelta(weeks=52),
        "note": "Measles-Rubella first dose."
    })

    # 16-24 months: MR-2, DPT booster (simplified)
    items.append({
        "vaccine": "16–24 months: MR-2 / DPT booster",
        "start": dob + timedelta(weeks=69),
        "end": dob + timedelta(weeks=104),
        "note": "Toddler boosters."
    })

    # 5 years: DPT booster (awareness)
    items.append({
        "vaccine": "5 years: DPT booster",
        "start": dob + timedelta(days=int(365.25*5)),
        "end": dob + timedelta(days=int(365.25*5) + 90),
        "note": "Pre-school booster."
    })

    # 10 years & 16 years: Td boosters (awareness)
    items.append({
        "vaccine": "10 years: Td booster",
        "start": dob + timedelta(days=int(365.25*10)),
        "end": dob + timedelta(days=int(365.25*10) + 180),
        "note": "Adolescent booster."
    })
    items.append({
        "vaccine": "16 years: Td booster",
        "start": dob + timedelta(days=int(365.25*16)),
        "end": dob + timedelta(days=int(365.25*16) + 180),
        "note": "Adolescent booster."
    })

    return items

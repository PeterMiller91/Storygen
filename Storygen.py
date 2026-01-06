import os
import json
import textwrap
from datetime import datetime
import streamlit as st

# OpenAI Python SDK (>=1.0)
from openai import OpenAI

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="IG Story Generator – Narzissmus-Hilfe",
    page_icon="📲",
    layout="wide"
)

# -----------------------------
# Helpers
# -----------------------------
def get_api_key() -> str:
    """
    Priority:
    1) Streamlit secrets (Streamlit Cloud)
    2) Environment variable
    3) Manual input (session only)
    """
    key = ""
    try:
        key = st.secrets.get("OPENAI_API_KEY", "")  # type: ignore[attr-defined]
    except Exception:
        key = ""
    return key or os.getenv("OPENAI_API_KEY", "")

def safe_json_loads(text: str):
    try:
        return json.loads(text)
    except Exception:
        return None

def build_system_prompt():
    return (
        "Du bist ein erfahrener Social-Media-Redakteur und Trauma-informierter Content-Stratege "
        "für einen Instagram-Kanal, der Betroffene von narzisstischem Missbrauch unterstützt. "
        "Du formulierst empathisch, klar, nicht reißerisch, ohne Diagnosen oder medizinische/therapeutische Anweisungen. "
        "Du vermeidest gefährliche oder eskalierende Ratschläge (z.B. Konfrontationspläne, Rache, Stalking, Manipulation). "
        "Du nutzt eine respektvolle Sprache: 'narzisstische Muster', 'emotionaler Missbrauch', 'Kontrolle', 'Gaslighting'. "
        "Du gibst keine Rechts- oder Therapieanweisungen, sondern alltagstaugliche, sichere Mikro-Schritte und Selbstschutz. "
        "Wenn sensible Themen vorkommen (Gewalt, Suizid, akute Gefahr), empfiehlst du Hilfe über lokale Notrufnummern/Hotlines. "
        "Output immer im gewünschten Format als valides JSON."
    )

def build_user_prompt(cfg: dict) -> str:
    # Compact but explicit instructions for consistent output
    return f"""
Erstelle Instagram-Story-Inhalte in deutscher Sprache für einen Kanal mit Fokus: Hilfe für Betroffene von narzisstischem Missbrauch.

KONFIG:
- Ziel der Story: {cfg["goal"]}
- Textart: {cfg["text_type"]}
- Tonalität: {cfg["tone"]}
- Phase/Zustand der Zielgruppe: {cfg["stage"]}
- Hauptthema: {cfg["topic"]}
- Sensibilität/Trigger: {cfg["sensitivity"]}
- Länge pro Slide: {cfg["slide_length"]}
- Anzahl Slides: {cfg["num_slides"]}
- CTA/Interaktion: {cfg["cta"]}
- Tabu-Wörter/No-Gos: {cfg["no_gos"]}
- Optionaler Kontext (Channel-Style, spezielle Situation): {cfg["extra_context"]}

ANFORDERUNGEN:
1) Liefere ein JSON mit diesem Schema:
{{
  "title_hook": "Sehr kurzer Hook (max 8 Wörter)",
  "slides": [
    {{
      "slide_no": 1,
      "headline": "max 7 Wörter",
      "body": "max. {cfg["slide_length"]} Zeichen, kurze Zeilen, story-tauglich",
      "sticker_suggestion": "z.B. Umfrage, Fragen-Sticker, Slider, Quiz",
      "visual_suggestion": "z.B. Hintergrundidee / Symbolik / Farben"
    }}
  ],
  "caption_variants": [
    "1-2 Sätze, empathisch, ohne Diagnose, mit CTA",
    "Alternative"
  ],
  "cta_options": [
    "Kurzer CTA 1",
    "Kurzer CTA 2",
    "Kurzer CTA 3"
  ],
  "poll_or_question": {{
    "type": "poll|question|quiz|slider",
    "prompt": "Text",
    "options": ["Option A", "Option B"]
  }},
  "hashtags": ["max 12, deutsch, thematisch, nicht zu generisch"],
  "safety_note": "1 Satz: keine Diagnose, bei akuter Gefahr Hilfe holen"
}}

2) Achte darauf:
- Keine Täter-Labels/Diagnosen als Fakt. Keine Schuldumkehr. Keine Eskalations-Tipps.
- Konkrete, sichere Mikro-Schritte (z.B. Grenzen, Dokumentation für sich, Unterstützung suchen, Selbstfürsorge).
- Variation: nicht jede Slide gleich starten; ein klarer Gedanke pro Slide.
- Für die Zielgruppe passend: validierend, stärkend, handlungsfähig.

3) Wenn 'Sensibilität/Trigger' hoch ist: sanfter, vorsichtiger Ton, Hinweis auf Unterstützung.

Jetzt generieren.
""".strip()

def render_story(data: dict):
    st.subheader("🧩 Story Output")
    st.markdown(f"**Hook:** {data.get('title_hook','')}")
    st.divider()

    slides = data.get("slides", [])
    if slides:
        cols = st.columns(3)
        for i, slide in enumerate(slides):
            with cols[i % 3]:
                st.markdown(f"### Slide {slide.get('slide_no', i+1)}")
                st.markdown(f"**{slide.get('headline','')}**")
                st.write(slide.get("body",""))
                st.caption(f"Sticker: {slide.get('sticker_suggestion','')}")
                st.caption(f"Visual: {slide.get('visual_suggestion','')}")
                st.divider()

    st.subheader("✍️ Caption-Varianten")
    for c in data.get("caption_variants", []):
        st.write(f"- {c}")

    st.subheader("👉 CTA-Optionen")
    for cta in data.get("cta_options", []):
        st.write(f"- {cta}")

    st.subheader("📊 Interaktion (Umfrage/Frage)")
    pq = data.get("poll_or_question", {})
    if pq:
        st.write(f"**Typ:** {pq.get('type','')}")
        st.write(f"**Prompt:** {pq.get('prompt','')}")
        opts = pq.get("options", [])
        if opts:
            st.write("**Optionen:** " + " | ".join(opts))

    st.subheader("🏷️ Hashtags")
    st.write(" ".join([f"#{h.strip('#')}" for h in data.get("hashtags", [])]))

    st.info(data.get("safety_note", "Hinweis: Keine Diagnose. Bei akuter Gefahr bitte Hilfe holen."))

def make_export_text(data: dict) -> str:
    # Simple copy/paste export format
    lines = []
    lines.append(f"HOOK: {data.get('title_hook','')}\n")
    for s in data.get("slides", []):
        lines.append(f"--- SLIDE {s.get('slide_no','')} ---")
        lines.append(s.get("headline",""))
        lines.append(s.get("body",""))
        lines.append(f"[Sticker] {s.get('sticker_suggestion','')}")
        lines.append(f"[Visual] {s.get('visual_suggestion','')}\n")
    lines.append("CAPTIONS:")
    for c in data.get("caption_variants", []):
        lines.append(f"- {c}")
    lines.append("\nCTA:")
    for c in data.get("cta_options", []):
        lines.append(f"- {c}")
    pq = data.get("poll_or_question", {})
    if pq:
        lines.append("\nINTERAKTION:")
        lines.append(f"- Typ: {pq.get('type','')}")
        lines.append(f"- Prompt: {pq.get('prompt','')}")
        if pq.get("options"):
            lines.append(f"- Optionen: {', '.join(pq.get('options'))}")
    lines.append("\nHASHTAGS:")
    lines.append(" ".join([f"#{h.strip('#')}" for h in data.get("hashtags", [])]))
    lines.append("\nSAFETY:")
    lines.append(data.get("safety_note", "Keine Diagnose. Bei akuter Gefahr Hilfe holen."))
    return "\n".join(lines)

# -----------------------------
# UI
# -----------------------------
st.title("📲 Instagram Story Generator – Narzissmus-Hilfe")
st.caption("Erstellt Story-Slides, Captions, Sticker-Ideen & Hashtags per OpenAI API (ohne Diagnosen, trauma-informiert).")

api_key = get_api_key()

with st.sidebar:
    st.header("⚙️ Einstellungen")

    if not api_key:
        api_key = st.text_input("OpenAI API Key (Session)", type="password", help="Wird nicht gespeichert – nur für die aktuelle Session.")
    model = st.selectbox(
        "Modell",
        options=["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini", "gpt-4.1"],
        index=0,
        help="Wenn du Kosten drücken willst: mini. Wenn du maximalen Feinschliff willst: gpt-4o / 4.1."
    )

    st.divider()
    st.subheader("🧠 Inhaltliche Vorauswahl")

    goal = st.selectbox(
        "Ziel der Story",
        [
            "Validierung & Entlastung (Du bist nicht verrückt)",
            "Aufklärung (Muster erkennen: Gaslighting, Silent Treatment, Triangulation)",
            "Selbstschutz (Grenzen, Abstand, No-Contact/Low-Contact Prinzipien ohne Anleitung zur Eskalation)",
            "Stärkung (Selbstwert, innere Klarheit, Identität zurückholen)",
            "Community & Interaktion (Umfrage/Frage/DM-Trigger)",
            "Motivation (Mut machen, kleine Schritte)",
            "Mythen brechen (z.B. 'Wenn ich mich nur besser erkläre…')",
        ],
        index=0
    )

    text_type = st.selectbox(
        "Art des Textes",
        [
            "Sprüche / One-Liner (Punchy, kurz)",
            "Mini-Carousel in Story (3–7 Slides, logisch aufgebaut)",
            "Checkliste (Warnsignale / Red Flags)",
            "Reframe (Gedanken umdrehen: Schuld → Klarheit)",
            "Übung / Mikro-Schritt (2 Minuten, sicher)",
            "Grenzsatz-Vorlagen (kommunikativ, nicht eskalierend)",
            "Story-Quiz (Mythos vs Fakt / Erkennen von Mustern)",
        ],
        index=1
    )

    tone = st.selectbox(
        "Tonalität",
        ["Sehr empathisch & sanft", "Klar & direkt (ohne hart zu sein)", "Mutmachend & hoffnungsvoll", "Faktenorientiert & ruhig"],
        index=1
    )

    stage = st.selectbox(
        "Phase/Zustand der Zielgruppe",
        [
            "Noch drin / verwirrt / Selbstzweifel",
            "Trennung läuft / emotional instabil",
            "No-Contact/Abstand / Stabilisierung",
            "Rückfallgefahr / Trauma-Bond / Sehnsucht",
            "Heilung & Neuaufbau / Identität",
        ],
        index=0
    )

    topic = st.selectbox(
        "Hauptthema",
        [
            "Gaslighting",
            "Silent Treatment / Entzug",
            "Love Bombing → Abwertung",
            "Triangulation (Dritte ins Spiel bringen)",
            "Schuldumkehr & Projektion",
            "Grenzen setzen ohne Rechtfertigen",
            "Trauma Bond / Suchtgefühl",
            "Co-Abhängigkeit / People-Pleasing",
            "Eifersucht & Kontrolle",
            "Aftermath: Selbstwert & Vertrauen",
        ],
        index=0
    )

    sensitivity = st.selectbox(
        "Sensibilität/Trigger",
        ["Niedrig", "Mittel", "Hoch (sehr vorsichtig formulieren)"],
        index=1
    )

    slide_length = st.select_slider(
        "Länge pro Slide (Zeichen)",
        options=[120, 160, 220, 300],
        value=160
    )

    num_slides = st.slider("Anzahl Slides", min_value=3, max_value=10, value=6, step=1)

    cta = st.selectbox(
        "CTA / Interaktion",
        [
            "Frage-Sticker: 'Was war dein Aha-Moment?'",
            "Umfrage: 'Kennst du das?'",
            "DM-Trigger: 'Schreib mir 'KLARHEIT' für…'",
            "Speichern/Teilen: 'Speicher dir das für schlechte Tage'",
            "Quiz: Mythos vs Fakt",
            "Kein CTA (nur Validierung)",
        ],
        index=2
    )

    no_gos = st.text_input(
        "Tabu-Wörter/No-Gos (kommagetrennt)",
        value="diagnose, narzisst, narzisstin, psychopat, rache, konfrontiere ihn, konfrontiere sie"
    )

    extra_context = st.text_area(
        "Optionaler Kontext (dein Stil / Worte, die du oft nutzt)",
        placeholder="z.B. 'kurze Zeilen', 'du-form', 'klarer Abschluss pro Slide', 'mehr Hoffnung', 'kein Drama'..."
    )

    st.divider()
    st.subheader("📅 Batch-Mode")
    batch_mode = st.toggle("7 Story-Ideen auf einmal (Wochenplan)", value=False)
    st.caption("Wenn aktiv: du bekommst 7 kompakte Story-Konzepte statt 1 fertige Story.")

# -----------------------------
# Main Actions
# -----------------------------
if not api_key:
    st.warning("Bitte API-Key in der Sidebar setzen (oder via OPENAI_API_KEY / Streamlit Secrets).")
    st.stop()

client = OpenAI(api_key=api_key)

cfg = {
    "goal": goal,
    "text_type": text_type,
    "tone": tone,
    "stage": stage,
    "topic": topic,
    "sensitivity": sensitivity,
    "slide_length": slide_length,
    "num_slides": num_slides,
    "cta": cta,
    "no_gos": no_gos,
    "extra_context": extra_context.strip(),
}

colA, colB = st.columns([1, 1])

with colA:
    generate = st.button("✨ Story generieren", type="primary", use_container_width=True)

with colB:
    creativity = st.slider("Kreativität", 0.0, 1.0, 0.6, 0.05, help="0 = sehr nüchtern, 1 = mehr Variation/Metaphern")

st.divider()

def generate_single_story():
    user_prompt = build_user_prompt(cfg)

    resp = client.chat.completions.create(
        model=model,
        temperature=creativity,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": user_prompt},
        ],
    )
    text = resp.choices[0].message.content or "{}"
    data = safe_json_loads(text)
    return data, text

def generate_week_plan():
    plan_prompt = f"""
Erstelle einen 7-Tage-Plan für Instagram Stories (deutsch) für einen Kanal: Hilfe bei narzisstischem Missbrauch.

Konfiguration:
- Zielgruppe/Phase: {cfg["stage"]}
- Tonalität: {cfg["tone"]}
- Fokus-Themen (rotierend): Gaslighting, Grenzen, Trauma Bond, Selbstwert, Kontrolle, Schuldumkehr, Heilung
- CTA-Stil: {cfg["cta"]}
- No-Gos: {cfg["no_gos"]}
- Optionaler Kontext: {cfg["extra_context"]}

Liefere valides JSON im Schema:
{{
  "week_theme": "Titel",
  "days": [
    {{
      "day": "Tag 1",
      "goal": "Ziel",
      "topic": "Thema",
      "hook": "max 8 Wörter",
      "slides_outline": ["Slide1 Idee", "Slide2 Idee", "Slide3 Idee", "… max 6"],
      "interaction": "Umfrage/Frage/Quiz/Slider Vorschlag",
      "cta": "kurzer CTA"
    }}
  ],
  "safety_note": "1 Satz"
}}
""".strip()

    resp = client.chat.completions.create(
        model=model,
        temperature=creativity,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": build_system_prompt()},
            {"role": "user", "content": plan_prompt},
        ],
    )
    text = resp.choices[0].message.content or "{}"
    data = safe_json_loads(text)
    return data, text

if generate:
    with st.spinner("Generiere Content…"):
        if batch_mode:
            data, raw = generate_week_plan()
        else:
            data, raw = generate_single_story()

    if not data:
        st.error("Konnte JSON nicht sauber lesen. Unten ist die Roh-Ausgabe (du kannst sie manuell prüfen).")
        st.code(raw)
        st.stop()

    if batch_mode:
        st.subheader("📅 Wochenplan (7 Story-Ideen)")
        st.markdown(f"**Wochenthema:** {data.get('week_theme','')}")
        for d in data.get("days", []):
            with st.expander(f"{d.get('day','Tag')} – {d.get('hook','')}"):
                st.write(f"**Ziel:** {d.get('goal','')}")
                st.write(f"**Thema:** {d.get('topic','')}")
                st.write("**Slides Outline:**")
                for s in d.get("slides_outline", []):
                    st.write(f"- {s}")
                st.write(f"**Interaktion:** {d.get('interaction','')}")
                st.write(f"**CTA:** {d.get('cta','')}")
        st.info(data.get("safety_note", "Keine Diagnose. Bei akuter Gefahr Hilfe holen."))
        export_text = json.dumps(data, ensure_ascii=False, indent=2)
        st.download_button(
            "⬇️ Export (JSON)",
            data=export_text.encode("utf-8"),
            file_name=f"ig_story_weekplan_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        render_story(data)

        export_text = make_export_text(data)
        st.download_button(
            "⬇️ Export (TXT)",
            data=export_text.encode("utf-8"),
            file_name=f"ig_story_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain",
            use_container_width=True
        )

        st.download_button(
            "⬇️ Export (JSON)",
            data=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"),
            file_name=f"ig_story_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json",
            use_container_width=True
        )

st.divider()
with st.expander("ℹ️ Sicherheit & Verantwortung (kurz)"):
    st.write(
        "Diese App generiert Social-Media-Content und ersetzt keine Beratung, Therapie oder rechtliche Einschätzung. "
        "Bitte vermeide Diagnosen/Labels als Tatsachen. Bei akuter Gefahr: lokale Notrufnummern kontaktieren."
    )
import os
import json
import textwrap
from datetime import datetime
import streamlit as st
from openai import OpenAI

# -----------------------------
# App Config
# -----------------------------
st.set_page_config(
    page_title="📱 IG Story Generator – Narzissmus-Hilfe [PRO]",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Caching & Performance
# -----------------------------
@st.cache_data(ttl=300)
def get_api_key() -> str:
    """Cached API key retrieval"""
    try:
        if "OPENAI_API_KEY" in st.secrets:
            return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    
    env_key = os.getenv("OPENAI_API_KEY", "")
    return env_key

@st.cache_data(ttl=3600)
def get_available_models():
    """Return available models"""
    return {
        "Kosteneffizient": ["gpt-4o-mini", "gpt-4.1-mini"],
        "Hochwertig": ["gpt-4o", "gpt-4.1"],
        "Schnell": ["gpt-3.5-turbo"]
    }

def safe_json_loads(text: str):
    """Robust JSON parsing with fallback"""
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown code blocks
        import re
        json_match = re.search(r'```(?:json)?\n?(.*?)\n?```', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except:
                pass
        return None

# -----------------------------
# Enhanced Prompts
# -----------------------------
def build_system_prompt():
    return textwrap.dedent("""
    Du bist ein hochkarätiger Social-Media-Content-Spezialist mit Expertise in Trauma-informierter Kommunikation.
    
    DEINE ROLLE:
    - Erstellst viralen, hoch-engagierenden Content für Instagram Stories
    - Formulierst sofort süchtig machende Hooks & emotional packende Texte
    - Nutzt psychologische Trigger für maximale Interaktion (Neugier, Identifikation, Empowerment)
    - Bleibst absolut sicher: Keine Diagnosen, keine Eskalationstipps
    
    DEINE SUPER-SKILLS:
    🔥 EMOTIONAL HOOKS: Jede Story beginnt mit einem "Aha-Moment"
    💥 SCROLL-STOPPER: Texte, die zum Stehenbleiben zwingen
    📈 ENGAGEMENT-BOOSTER: Fragen, die zur Interaktion einladen
    🎯 ZIELGRUPPEN-TREFFER: Exakt auf Phase & Bedürfnisse abgestimmt
    
    FORMAT-RICHTLINIEN:
    - Jede Slide hat einen klaren Mehrwert
    - Emotionale Achterbahn: Problem → Einsicht → Lösung → Aktion
    - Storytelling mit persönlicher Note (ohne zu privat zu sein)
    - Zahlen, Emojis und kurze Zeilen für bessere Lesbarkeit
    
    SICHERHEIT:
    - Sprache: "narzisstische Dynamiken", "toxische Muster", "emotionaler Schutz"
    - Immer empowernd, nie entmündigend
    - Bei Hoch-Sensibilität: Sanfter Ton + Hilfsangebote
    """).strip()

def build_viral_prompt_template(cfg: dict) -> str:
    """Optimized prompt for viral content"""
    return textwrap.dedent(f"""
    ERSTELLE VIRALE INSTAGRAM-STORY CONTENT mit maximalem Engagement-Potential!
    
    🔥 VIRALE STRATEGIE:
    - Slide 1: EMOTIONALER HOOK (muss zum Weiterscrollen zwingen)
    - Slide 2-3: PROBLEM-VERSTÄNDNIS (Identifikation schaffen)
    - Slide 4-5: LÖSUNGS-IMPULS (klarer Mehrwert)
    - Slide 6+: INTERAKTIONS-PUSH (Community-Bindung)
    
    📊 CONTENT-KONFIGURATION:
    • Ziel: {cfg["goal"]} + Engagement-Boost
    • Format: {cfg["text_type"]} 
    • Ton: {cfg["tone"]} + emotionale Tiefe
    • Zielgruppe: {cfg["stage"]} (genau treffen!)
    • Fokus: {cfg["topic"]}
    • Sensibilität: {cfg["sensitivity"]} (entsprechend anpassen)
    • Slides: {cfg["num_slides"]} (jede muss Wert liefern)
    • CTA: {cfg["cta"]} (maximale Interaktion)
    
    🚀 VIRALE ELEMENTE EINBAUEN:
    1. KURIOSITÄTSLÜCKEN (Curiosity Gaps)
    2. EMOTIONALE IDENTIFIKATION ("Kennst du das?")
    3. ÜBERRASCHUNGS-MOMENTE (unerwartete Einsichten)
    4. GEMEINSCHAFTSGEFÜHL ("Wir sind viele")
    5. KLARE HANDLUNGSIMPULSE (mikro-Aktionen)
    
    ⚠️ TABUS: {cfg["no_gos"]}
    
    💡 STYLE-TIPPS: {cfg["extra_context"] or "Emojis sinnvoll einsetzen • Kurze Zeilen • Direkte Ansprache • Konkrete Beispiele"}
    
    📝 OUTPUT-FORMAT (STRENG EINHALTEN):
    {{
      "title_hook": "🔥 Emotionaler Hook (max 6 Wörter, muss neugierig machen)",
      "viral_score": 85,  # 1-100 wie viral der Content ist
      "slides": [
        {{
          "slide_no": 1,
          "headline": "📌 Scroll-Stopper (max 5 Wörter)",
          "body": "Max {cfg['slide_length']} Zeichen. Emotional • Persönlich • Wertvoll",
          "engagement_tip": "Warum diese Slide interaktionsstark ist",
          "sticker_suggestion": "Interaktiver Sticker + genaue Formulierung",
          "visual_suggestion": "Hintergrund-Farbe • Symbol • Bild-Idee"
        }}
      ],
      "caption_variants": [
        "🔥 Caption mit Hook + CTA + Frage",
        "💫 Alternative mit Storytelling"
      ],
      "cta_options": [
        "📍 Dringender Handlungsimpuls",
        "🤝 Community-Frage",
        "💡 Wissens-CTA"
      ],
      "poll_or_question": {{
        "type": "poll|question|quiz|slider|emoji_slider",
        "prompt": "Ultra-interaktive Frageformulierung",
        "options": ["Emotional Option A", "Überraschende Option B", "Tiefe Option C"]
      }},
      "hashtags": ["Deutsch • Thematisch • Viral • Community"],
      "viral_techniques": ["Liste der verwendeten Viral-Techniken"],
      "safety_note": "🔒 Sicherheitshinweis + Empowerment"
    }}
    
    JETZT: Erstelle den engagiertesten Content, den Instagram je gesehen hat!
    """).strip()

# -----------------------------
# Enhanced UI Components
# -----------------------------
def init_session_state():
    """Initialize session state"""
    if 'generated_content' not in st.session_state:
        st.session_state.generated_content = None
    if 'export_format' not in st.session_state:
        st.session_state.export_format = 'txt'
    if 'api_usage' not in st.session_state:
        st.session_state.api_usage = 0

def render_viral_sidebar():
    """Enhanced sidebar with viral tips"""
    with st.sidebar:
        st.header("🚀 Viral-Optimierung")
        
        col1, col2 = st.columns(2)
        with col1:
            urgency = st.slider("Dringlichkeit", 1, 10, 7, 
                              help="Wie dringlich/aktuell ist die Message?")
        with col2:
            emotion = st.slider("Emotion", 1, 10, 8,
                              help="Emotionale Tiefe (1=sachlich, 10=tief emotional)")
        
        st.divider()
        
        viral_elements = st.multiselect(
            "🔥 Viral-Elemente einbauen:",
            [
                "Curiosity Gap (Neugier wecken)",
                "Social Proof (Community zeigen)",
                "Controversy (sanfte Provokation)",
                "Storytelling (persönliche Geschichte)",
                "Surprise (Überraschungseffekt)",
                "Utility (praktischer Nutzen)",
                "Inspiration (Motivationsboost)"
            ],
            default=["Curiosity Gap", "Utility", "Storytelling"]
        )
        
        st.info("💡 **Viral-Tipp:** Kombiniere 2-3 Elemente für maximalen Impact!")
        
        st.divider()
        st.subheader("📈 Performance-Tracking")
        st.metric("API Calls", st.session_state.api_usage)
        
        return {
            "urgency": urgency,
            "emotion": emotion,
            "viral_elements": viral_elements
        }

# -----------------------------
# Enhanced Content Generation
# -----------------------------
def generate_viral_story(client, model, creativity, cfg, viral_cfg):
    """Generate viral-optimized content"""
    
    base_prompt = build_viral_prompt_template(cfg)
    
    # Add viral configuration to prompt
    viral_addition = f"""
    ZUSÄTZLICHE VIRAL-KONFIG:
    • Dringlichkeit: {viral_cfg['urgency']}/10
    • Emotion: {viral_cfg['emotion']}/10
    • Viral-Elemente: {', '.join(viral_cfg['viral_elements'])}
    
    FOKUS: {cfg['goal']} mit {cfg['topic']} für Zielgruppe in {cfg['stage']}
    
    MACH DIESEN CONTENT UNVERGESSLICH!
    """
    
    full_prompt = base_prompt + "\n\n" + viral_addition
    
    try:
        response = client.chat.completions.create(
            model=model,
            temperature=creativity,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": build_system_prompt()},
                {"role": "user", "content": full_prompt}
            ],
            max_tokens=2000
        )
        
        st.session_state.api_usage += 1
        text = response.choices[0].message.content or "{}"
        
        # Enhanced JSON parsing with retry
        data = safe_json_loads(text)
        if not data:
            # Try to fix common JSON issues
            text = text.replace("'", '"').replace("True", "true").replace("False", "false")
            data = json.loads(text)
        
        return data, text
        
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None, None

# -----------------------------
# Enhanced Content Display
# -----------------------------
def render_viral_story(data):
    """Display content with viral metrics"""
    
    if not data:
        st.error("Keine Daten zum Anzeigen")
        return
    
    # Header with viral score
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown(f"## 🔥 {data.get('title_hook', '')}")
    with col2:
        score = data.get('viral_score', 0)
        color = "green" if score > 80 else "orange" if score > 60 else "red"
        st.metric("Viral Score", f"{score}/100", delta_color="off")
    with col3:
        st.caption(f"📊 {len(data.get('slides', []))} Slides • ⏱️ ~{len(data.get('slides', []))*5}s Lesezeit")
    
    st.divider()
    
    # Slides with engagement tips
    st.subheader("🎬 Story Slides (optimiert für Engagement)")
    
    slides = data.get("slides", [])
    if slides:
        for i in range(0, len(slides), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(slides):
                    slide = slides[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            st.markdown(f"### Slide {slide.get('slide_no', i+j+1)}")
                            st.markdown(f"**{slide.get('headline', '')}**")
                            st.write(slide.get("body", ""))
                            
                            if slide.get("engagement_tip"):
                                with st.expander("💡 Engagement-Tipp"):
                                    st.info(slide.get("engagement_tip"))
                            
                            col_a, col_b = st.columns(2)
                            with col_a:
                                st.caption(f"**Sticker:** {slide.get('sticker_suggestion', '')}")
                            with col_b:
                                st.caption(f"**Visual:** {slide.get('visual_suggestion', '')}")
    
    # Captions & CTAs
    tab1, tab2, tab3, tab4 = st.tabs(["📝 Captions", "🎯 CTAs", "📊 Interaktion", "🏷️ Hashtags"])
    
    with tab1:
        for idx, caption in enumerate(data.get("caption_variants", [])):
            st.write(f"**Variante {idx+1}:** {caption}")
            if idx == 0:
                st.caption("⭐ **Empfohlene Variante für maximale Reichweite**")
    
    with tab2:
        for cta in data.get("cta_options", []):
            st.write(f"• {cta}")
    
    with tab3:
        pq = data.get("poll_or_question", {})
        if pq:
            col_x, col_y = st.columns([1, 2])
            with col_x:
                st.metric("Typ", pq.get('type', ''))
            with col_y:
                st.write(f"**Frage:** {pq.get('prompt', '')}")
                if pq.get("options"):
                    st.write("**Optionen:**")
                    for opt in pq.get("options"):
                        st.write(f"  - {opt}")
    
    with tab4:
        hashtags = data.get("hashtags", [])
        hashtag_string = " ".join([f"#{h.strip('#')}" for h in hashtags])
        st.code(hashtag_string, language=None)
        st.caption("📋 Zum Kopieren")
    
    # Viral techniques
    if data.get("viral_techniques"):
        st.divider()
        with st.expander("🔍 Verwendete Viral-Techniken"):
            for tech in data.get("viral_techniques", []):
                st.write(f"• {tech}")
    
    # Safety note
    st.info(data.get("safety_note", "🔒 Sicherheitshinweis: Dieser Content ersetzt keine professionelle Beratung."))

# -----------------------------
# Enhanced Export
# -----------------------------
def make_enhanced_export(data, format_type='txt'):
    """Create export in various formats"""
    
    if format_type == 'txt':
        lines = []
        lines.append("=" * 50)
        lines.append("🔥 VIRAL INSTAGRAM STORY - EXPORT")
        lines.append("=" * 50)
        lines.append(f"\n🎯 HOOK: {data.get('title_hook','')}")
        lines.append(f"📈 VIRAL SCORE: {data.get('viral_score', 'N/A')}/100")
        
        lines.append("\n" + "=" * 30)
        lines.append("🎬 STORY SLIDES")
        lines.append("=" * 30)
        
        for slide in data.get("slides", []):
            lines.append(f"\n--- SLIDE {slide.get('slide_no','')} ---")
            lines.append(f"📌 {slide.get('headline','')}")
            lines.append(f"{slide.get('body','')}")
            lines.append(f"🎯 Engagement-Tipp: {slide.get('engagement_tip','')}")
            lines.append(f"🔄 Sticker: {slide.get('sticker_suggestion','')}")
            lines.append(f"🎨 Visual: {slide.get('visual_suggestion','')}")
        
        lines.append("\n" + "=" * 30)
        lines.append("📝 CAPTION VARIANTS")
        lines.append("=" * 30)
        for i, caption in enumerate(data.get("caption_variants", [])):
            lines.append(f"\nVariante {i+1}: {caption}")
        
        lines.append("\n" + "=" * 30)
        lines.append("🎯 CTA OPTIONS")
        lines.append("=" * 30)
        for cta in data.get("cta_options", []):
            lines.append(f"• {cta}")
        
        return "\n".join(lines)
    
    elif format_type == 'json':
        return json.dumps(data, ensure_ascii=False, indent=2)
    
    elif format_type == 'csv':
        import csv
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write slides
        writer.writerow(["Slide", "Headline", "Body", "Sticker", "Visual"])
        for slide in data.get("slides", []):
            writer.writerow([
                slide.get('slide_no', ''),
                slide.get('headline', ''),
                slide.get('body', ''),
                slide.get('sticker_suggestion', ''),
                slide.get('visual_suggestion', '')
            ])
        
        return output.getvalue()

# -----------------------------
# Main App
# -----------------------------
def main():
    # Initialize
    init_session_state()
    
    # Header
    st.title("🚀 IG Story Generator – Viral Edition")
    st.markdown("**Erstelle hoch-engagierenden Content für maximale Reichweite & Community-Bindung**")
    
    # API Key
    api_key = get_api_key()
    
    # Enhanced Sidebar
    with st.sidebar:
        st.header("🔑 API & Model")
        
        if not api_key:
            api_key = st.text_input(
                "OpenAI API Key",
                type="password",
                help="Wird lokal zwischengespeichert",
                key="api_key_input"
            )
        
        model_groups = get_available_models()
        model_category = st.selectbox(
            "Modell-Kategorie",
            list(model_groups.keys()),
            index=0
        )
        
        model = st.selectbox(
            "Modell",
            model_groups[model_category],
            index=0,
            help="gpt-4o-mini: kosteneffizient • gpt-4o: beste Qualität"
        )
        
        creativity = st.slider(
            "Kreativität & Variation",
            0.0, 1.0, 0.7, 0.05,
            help="0.7 = optimaler Mix aus Konsistenz & Kreativität"
        )
    
    # Viral Configuration
    viral_cfg = render_viral_sidebar()
    
    # Main Content Configuration
    st.header("🎯 Content-Konfiguration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        goal = st.selectbox(
            "Primäres Ziel",
            [
                "🔥 Maximale Interaktion (Likes, Shares, Comments)",
                "💬 Community-Aufbau & Bindung",
                "📈 Reichweite steigern (viral Potential)",
                "🤝 Vertrauen & Glaubwürdigkeit",
                "🎯 Konkrete Aktionen (Downloads, DMs, Saves)",
                "💡 Aufklärung & Awareness",
                "❤️ Emotionale Verbindung"
            ],
            index=0
        )
        
        text_type = st.selectbox(
            "Content-Format",
            [
                "🚀 Viral Carousel (3-7 ultra-engagierende Slides)",
                "💥 Emotionaler One-Liner (Scroll-Stopper)",
                "📚 Mini-Guide (Wertvoll + Teilbar)",
                "🎯 Interaktive Checkliste",
                "📖 Storytelling (Persönlich + Relatable)",
                "🧠 Mindshift (Perspektivenwechsel)",
                "🔄 Transformations-Story (Vorher/Nachher)",
                "❓ Quiz/Test (hohe Interaktion)"
            ],
            index=0
        )
        
        tone = st.selectbox(
            "Ton & Stimme",
            [
                "🔥 Leidenschaftlich & Mitreißend",
                "💫 Empathisch & Tief",
                "🎯 Direkt & Klar",
                "✨ Inspirierend & Motivierend",
                "🤝 Vertrauensvoll & Autoritativ",
                "😊 Freundlich & Gemeinschaftlich"
            ],
            index=0
        )
        
        stage = st.selectbox(
            "Zielgruppen-Phase",
            [
                "🌀 Verwirrung & Selbstzweifel",
                "⚡ Erkenntnis & Schock",
                "💔 Trennung & Schmerz",
                "🛡️ Schutz & Distanzierung",
                "🌱 Heilung & Wachstum",
                "🚀 Transformation & Neuanfang"
            ],
            index=0
        )
    
    with col2:
        topic = st.selectbox(
            "Fokus-Thema",
            [
                "🔥 Gaslighting erkennen & benennen",
                "💔 Emotionale Erpressung durchbrechen",
                "🛡️ Grenzen setzen ohne Schuldgefühle",
                "🌀 Trauma-Bond verstehen & lösen",
                "🎯 Selbstwert aufbauen trotz Abwertung",
                "✨ Innere Freiheit gewinnen",
                "🤝 Gesunde Beziehungen nach toxischen",
                "💪 Empowerment & Selbstwirksamkeit"
            ],
            index=0
        )
        
        sensitivity = st.selectbox(
            "Sensibilitäts-Level",
            ["🌱 Sanft & Vorsichtig", "🎯 Klar & Direkt", "🔥 Intensiv & Tief"],
            index=1
        )
        
        slide_length = st.select_slider(
            "Zeichen pro Slide",
            options=[80, 120, 160, 200, 240],
            value=120,
            help="Kürzer = besser für Mobile"
        )
        
        num_slides = st.slider(
            "Anzahl Slides",
            min_value=3, max_value=12, value=6,
            help="6-8 Slides = optimale Engagement-Länge"
        )
        
        cta = st.selectbox(
            "Interaktions-Typ",
            [
                "🔥 Frage-Sticker (hohe Reply-Rate)",
                "📊 Umfrage (instant Engagement)",
                "💬 DM-Trigger (Community-Building)",
                "💾 Save-Sticker (Langzeit-Engagement)",
                "🎯 Quiz/Test (spielerisch)",
                "✨ Emoji-Slider (einfach & effektiv)",
                "🔄 Share-Prompt (Virality)"
            ],
            index=0
        )
    
    # Advanced Settings
    with st.expander("⚙️ Erweiterte Einstellungen"):
        col_a, col_b = st.columns(2)
        
        with col_a:
            no_gos = st.text_area(
                "Tabu-Wörter",
                value="diagnose, narzisst, therapie, konfrontation, rache, opfer",
                help="Kommagetrennte Liste"
            )
            
            target_demographic = st.multiselect(
                "Ziel-Demographie",
                ["Frauen 25-45", "Männer 30-50", "Junge Erwachsene", "Berufstätige", "Eltern"],
                default=["Frauen 25-45"]
            )
        
        with col_b:
            extra_context = st.text_area(
                "Style-Guide & Besonderheiten",
                placeholder="z.B.: 'Du-Form • Emojis sparsam • Konkrete Beispiele • Action-words • Positiver Abschluss'",
                height=100
            )
            
            posting_time = st.selectbox(
                "Optimale Posting-Zeit",
                ["⏰ Flexibel", "🌅 Morgens (7-9)", "☕ Mittag (12-14)", "🌇 Abend (18-20)", "🌙 Spät (20-22)"]
            )
    
    # Generate Button
    st.divider()
    
    col_gen1, col_gen2, col_gen3 = st.columns([2, 1, 1])
    
    with col_gen1:
        if st.button(
            "🚀 JETZT VIRALEN CONTENT GENERIEREN",
            type="primary",
            use_container_width=True,
            help="Erstellt hoch-optimierten Content für maximale Reichweite"
        ):
            if not api_key:
                st.error("Bitte API-Key eingeben!")
                st.stop()
            
            # Build configuration
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
                "extra_context": f"{extra_context} | Ziel: {target_demographic} | Zeit: {posting_time}",
            }
            
            # Initialize client
            client = OpenAI(api_key=api_key)
            
            # Generate content
            with st.spinner("🔥 Erstelle viral-optimierten Content..."):
                data, raw = generate_viral_story(client, model, creativity, cfg, viral_cfg)
                
                if data:
                    st.session_state.generated_content = data
                    st.session_state.raw_output = raw
                    st.success("✅ Content erfolgreich generiert!")
                else:
                    st.error("❌ Fehler bei der Generierung")
    
    with col_gen2:
        batch_mode = st.toggle(
            "📅 Wochenplan",
            help="Generiert 7 Tage Content auf einmal"
        )
    
    with col_gen3:
        st.session_state.export_format = st.selectbox(
            "Export",
            ["txt", "json", "csv"],
            index=0,
            label_visibility="collapsed"
        )
    
    # Display Generated Content
    if st.session_state.generated_content:
        st.divider()
        render_viral_story(st.session_state.generated_content)
        
        # Export Options
        st.divider()
        st.subheader("📤 Export")
        
        col_exp1, col_exp2, col_exp3 = st.columns(3)
        
        export_data = st.session_state.generated_content
        
        with col_exp1:
            txt_export = make_enhanced_export(export_data, 'txt')
            st.download_button(
                "📄 TXT Export",
                data=txt_export.encode('utf-8'),
                file_name=f"viral_ig_story_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain",
                use_container_width=True
            )
        
        with col_exp2:
            json_export = make_enhanced_export(export_data, 'json')
            st.download_button(
                "📊 JSON Export",
                data=json_export.encode('utf-8'),
                file_name=f"viral_ig_story_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col_exp3:
            if export_data.get('slides'):
                csv_export = make_enhanced_export(export_data, 'csv')
                st.download_button(
                    "📈 CSV Export",
                    data=csv_export.encode('utf-8'),
                    file_name=f"viral_slides_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    # Footer & Info
    st.divider()
    with st.expander("ℹ️ Best Practices & Tipps"):
        st.markdown("""
        ### 🚀 Viral Content Strategien
        
        **🔥 HOOK FORMEL:**
        - Emotion + Neugier + Relevanz = Perfekter Hook
        - Beispiel: "Das hat mich aus der Opferrolle geholt..."
        
        **💥 ENGAGEMENT-BOOSTER:**
        1. **Erste Slide:** Emotionale Identifikation
        2. **Mittlere Slides:** Wert + Einsicht
        3. **Letzte Slide:** Interaktion + Community
        
        **🎯 OPTIMIERUNGEN:**
        - **Mobile-first:** Kurze Zeilen, große Schrift
        - **Emojis:** 2-3 pro Slide für visuelle Führung
        - **Farben:** Hoher Kontrast für bessere Lesbarkeit
        - **CTA:** Immer konkret & einfach umsetzbar
        
        **📈 ALGORITHMUS-TIPPS:**
        - Interaktion in ersten 60 Minuten ist entscheidend
        - Saves & Shares zählen mehr als Likes
        - DMs sind der stärkste Engagement-Signal
        - Story-Replies erhöhen die Reichweite
        """)
    
    with st.expander("🔒 Sicherheit & Ethik"):
        st.info("""
        Diese App generiert Content für Betroffene von toxischen Beziehungsmustern.
        
        **Unsere Grundsätze:**
        1. **Empowerment statt Pathologisierung:** Wir geben keine Diagnosen
        2. **Sicherheit vor Eskalation:** Keine Konfrontations-Tipps
        3. **Professionalität:** Immer Hinweis auf professionelle Hilfe
        4. **Respekt:** Wertschätzende Sprache, keine Stigmatisierung
        
        **Bei akuter Krise:**
        • Telefonseelsorge: 0800 111 0 111
        • Hilfetelefon Gewalt: 08000 116 016
        • Ärztlicher Notdienst: 116 117
        """)

# -----------------------------
# Run App
# -----------------------------
if __name__ == "__main__":
    main()
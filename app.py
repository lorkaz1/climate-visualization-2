"""
Klimadaten im Kontext – Refinement (Streamlit, 100 % lokal)
===========================================================

Phase 2 (Refinement) zum Baseline-"Data Dump".
Die App ist gezielt entlang der drei Aufgaben-Achsen optimiert:

  1) TYPOGRAFIE          – klare Typo-Hierarchie, Lesbarkeit (siehe CSS unten)
  2) FARBLEITSYSTEM      – jede Variable hat EINE feste, semantische Farbe
  3) INFORMATIONSARCHITEKTUR – Shneiderman-Mantra in 5 Tabs

Zusätzlich: Narrativ, Drill-downs, Tooltips, Barrierefreiheit.
Wo ein Prinzip greift, steht im Code ein [Tag]. Übersicht im Tab "Usability".
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------- #
# Grundkonfiguration  [ISO 9241-110: Erwartungskonformität]
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="Klimadaten im Kontext",
    page_icon=":material/public:",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
# Individualisierbarkeit: Hell-/Dunkel-Modus
# [ISO 9241-110: Individualisierbarkeit / Anpassbarkeit durch den Nutzer]
# Muss vor CSS & Plotly-Template stehen, damit beide darauf reagieren.
# --------------------------------------------------------------------------- #
dark = st.sidebar.toggle(
    ":material/dark_mode: Dunkler Modus", value=False,
    help="Schaltet die gesamte Oberfläche auf ein dunkles, kontrastgeprüftes Farbschema um.",
)

# --------------------------------------------------------------------------- #
# 1) TYPOGRAFIE – zentrales Typo-/Spacing-System per CSS
#    [Grafikdesign: Schrifthierarchie] [Lesbarkeit: Zeilenhöhe, Laufweite]
#    [Tufte: ruhiges, konsistentes Layout]
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Source+Serif+4:opsz,wght@8..60,600;700&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0');

    /* ---- Farb-Tokens des eigenen Designs ----
       Alle Text/Hintergrund-Paare auf WCAG-AA-Kontrast (>=4.5:1) geprueft. */
    :root {
        --c-ink:#0f2733;            /* 15:1 auf hell  */
        --c-muted:#475a67;          /* 7.2:1 auf weiss, 6.4:1 auf Tab-Grau */
        --c-teal:#15803d;           /* helleres Gruen; weiss darauf 5.0:1 */
        --c-warm:#d55e00;
        --c-line:#e4ecef; --c-card:#ffffff; --c-bg:#f7f9fb; --c-tabbg:#eef3f4;
        --radius:16px; --shadow:0 1px 2px rgba(15,39,51,.04), 0 8px 24px rgba(15,39,51,.06);
    }

    html, body, [class*="css"], .stMarkdown, .stMetric, p, li, span, label, input, select {
        font-family:'Inter', system-ui, sans-serif;
    }
    /* Sanfter Verlaufs-Hintergrund statt flachem Weiss */
    [data-testid="stAppViewContainer"] {
        background:
          radial-gradient(1100px 480px at 12% -8%, #e6f3f1 0%, rgba(230,243,241,0) 60%),
          radial-gradient(900px 420px at 100% 0%, #fdeee3 0%, rgba(253,238,227,0) 55%),
          var(--c-bg);
    }
    .block-container { padding-top:1.4rem; max-width:1180px; }

    /* ---- Typografie / Hierarchie ---- */
    h1 { font-family:'Source Serif 4', Georgia, serif !important; }
    h2 { font-weight:800 !important; font-size:1.5rem !important; letter-spacing:-.2px;
         color:var(--c-ink); }
    h3 { font-weight:700 !important; font-size:1.18rem !important; color:var(--c-teal); }
    h4, h5 { color:var(--c-ink) !important; }
    p, li { font-size:1.02rem; line-height:1.62; color:var(--c-ink); }
    .stCaption, [data-testid="stCaptionContainer"] p {
        color:var(--c-muted) !important; font-size:.9rem !important; line-height:1.5; }

    /* ---- Hero-Kopf (eigenes Branding) ---- */
    /* Helleres Gruen; weisser Text bleibt >=5:1 ueber den GESAMTEN Verlauf
       (Stopps #0e7a4a 5.4:1, #15803d 5.0:1). */
    .hero {
        background:linear-gradient(120deg, #0e7a4a 0%, #15803d 60%, #0e7a4a 100%);
        color:#fff; border-radius:var(--radius); padding:30px 34px; margin:.2rem 0 1.3rem;
        box-shadow:var(--shadow); position:relative; overflow:hidden;
    }
    .hero:after {
        content:"public"; font-family:'Material Symbols Outlined'; font-weight:normal;
        position:absolute; right:24px; top:50%; transform:translateY(-50%);
        font-size:150px; opacity:.14; line-height:1;
    }
    .hero h1 { color:#fff !important; font-size:2.3rem !important; margin:0 0 .35rem;
        font-weight:700 !important; letter-spacing:-.5px; }
    /* Fliesstext voll deckend weiss -> sichere AA-Lesbarkeit */
    .hero p { color:#ffffff; font-size:1.06rem; margin:0; max-width:760px; }
    .hero .eyebrow { text-transform:uppercase; letter-spacing:2px; font-size:.74rem;
        font-weight:700; color:rgba(255,255,255,.95); margin-bottom:.5rem; }

    /* ---- Kennzahl-Karten [Restorff] ---- */
    [data-testid="stMetric"] {
        background:var(--c-card); border:1px solid var(--c-line); border-radius:14px;
        padding:16px 18px; box-shadow:var(--shadow);
        border-left:4px solid var(--c-teal);
    }
    [data-testid="stMetricValue"] { font-weight:800; font-variant-numeric:tabular-nums;
        color:var(--c-ink); }
    [data-testid="stMetricLabel"] { font-weight:600; color:var(--c-muted); }

    /* ---- Tabs als Pills ---- */
    .stTabs [data-baseweb="tab-list"] { gap:8px; border-bottom:none; flex-wrap:wrap; }
    .stTabs [data-baseweb="tab"] {
        background:var(--c-tabbg); border-radius:999px; padding:9px 18px; font-weight:600;
        font-size:1rem; border:1px solid transparent;
    }
    /* Nicht ausgewaehlt = dunkelgrauer Text, ausgewaehlt = weisser Text.
       * + !important, damit auch die inneren Text-/Icon-Elemente folgen. */
    .stTabs [data-baseweb="tab"] * { color:var(--c-muted) !important; }
    .stTabs [aria-selected="true"] {
        background:var(--c-teal) !important;
        box-shadow:0 4px 12px rgba(21,128,61,.28);
    }
    .stTabs [aria-selected="true"] * { color:#ffffff !important; }
    .stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] { display:none; }

    /* ---- Sidebar ---- (etwas heller; heller Text bleibt AA-konform >= 7:1) */
    [data-testid="stSidebar"] {
        background:linear-gradient(180deg,#1c4456 0%, #234e61 100%);
    }
    [data-testid="stSidebar"] * { color:#e7eef0 !important; }
    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h1 { color:#fff !important; }
    /* Hilfe-"?"-Icons in der Sidebar deutlich sichtbar (hell + volle Deckkraft) */
    [data-testid="stSidebar"] [data-testid="stTooltipIcon"],
    [data-testid="stSidebar"] [data-testid="stTooltipIcon"] * {
        color:#bfe6f5 !important; fill:#bfe6f5 !important; opacity:1 !important;
    }
    /* Umschalter (Dunkler Modus / Glätten) mit mehr Kontrast: heller Ring um den
       Schalter, damit er sich klar vom helleren Sidebar-Hintergrund abhebt. */
    [data-testid="stSidebar"] label[data-baseweb="checkbox"] > div:first-child,
    [data-testid="stSidebar"] label[data-baseweb="checkbox"] > span:first-child {
        box-shadow:0 0 0 2px rgba(255,255,255,.75) !important; border-radius:999px;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] { background:rgba(255,255,255,.04); }
    /* Expander-Ueberschrift in der dunklen Sidebar immer hell halten (auch ohne Hover) */
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary * { color:#e7eef0 !important; }
    /* Kopfzeile + Inhalt duerfen NICHT weiss werden (Streamlit setzt sonst die
       weisse Sekundaerfarbe) -> transparent, damit die dunkle Sidebar durchscheint */
    [data-testid="stSidebar"] [data-testid="stExpander"],
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] details,
    [data-testid="stSidebar"] [data-testid="stExpander"] details > div {
        background:transparent !important;
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
    [data-testid="stSidebar"] .stCaption { color:#c7d2d8 !important; }

    /* ---- Buttons ---- */
    .stButton>button, .stDownloadButton>button {
        border-radius:10px; font-weight:600; border:1px solid var(--c-teal);
        background:var(--c-teal); color:#fff; transition:transform .05s ease, filter .15s ease;
    }
    .stButton>button:hover, .stDownloadButton>button:hover { filter:brightness(1.08); }
    .stButton>button:active { transform:translateY(1px); }
    /* Alle Buttons (Primary, Download, Feedback …): Text UND Icons immer weiss,
       da sie alle einen gruenen Hintergrund haben. */
    .stButton > button, .stButton > button *,
    .stDownloadButton > button, .stDownloadButton > button * {
        color:#ffffff !important;
    }

    /* ---- Auswahlfelder deutlich abheben (Rand + Schatten) ---- */
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
        background:#fff; border:1.5px solid #c4d0d6; border-radius:10px;
        box-shadow:0 2px 8px rgba(15,39,51,.12); min-height:42px;
    }
    [data-testid="stSelectbox"] div[data-baseweb="select"] > div:hover,
    [data-testid="stMultiSelect"] div[data-baseweb="select"] > div:hover {
        border-color:var(--c-teal); box-shadow:0 3px 12px rgba(21,128,61,.20);
    }
    /* Auswahlfelder in der dunklen Sidebar lesbar halten */
    [data-testid="stSidebar"] div[data-baseweb="select"] > div { color:var(--c-ink) !important; }
    [data-testid="stSidebar"] div[data-baseweb="select"] * { color:var(--c-ink) !important; }

    /* ---- Karten-Optik für Expander & Info-Boxen ---- */
    [data-testid="stExpander"] { border:1px solid var(--c-line); border-radius:12px;
        box-shadow:var(--shadow); }
    [data-testid="stNotification"] { border-radius:12px; }
    hr { border-color:var(--c-line); }
    /* Streamlit-Kopfleiste (oben) in beiden Modi transparent statt weiss */
    [data-testid="stHeader"] { background:transparent !important; }

    /* ---- Barrierefreiheit: sichtbarer Tastatur-Fokus [WCAG: Operable] ---- */
    a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible,
    [role="tab"]:focus-visible, [data-baseweb="select"]:focus-within,
    [data-testid="stSlider"] [role="slider"]:focus-visible {
        outline:3px solid #1d9bf0 !important; outline-offset:2px !important;
        border-radius:6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Dunkles Farbschema: nur die Tokens & wenige Flächen ueberschreiben (spaeter im
# CSS -> gewinnt). Kontraste dunkel ebenfalls AA-konform (heller Text auf dunkel).
if dark:
    st.markdown(
        """
        <style>
        :root {
            --c-ink:#e7eef2; --c-muted:#aab8c2; --c-line:#26323d;
            --c-card:#16212b; --c-bg:#0f1720; --c-tabbg:#1c2935;
        }
        [data-testid="stAppViewContainer"] {
            background:
              radial-gradient(1100px 480px at 12% -8%, #11343a 0%, rgba(17,52,58,0) 60%),
              radial-gradient(900px 420px at 100% 0%, #2a1c12 0%, rgba(42,28,18,0) 55%),
              var(--c-bg);
        }
        /* Auswahlfelder im Dunkelmodus dunkel statt grellweiss */
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div {
            background:#16212b; border-color:#33414d;
        }
        [data-testid="stSelectbox"] div[data-baseweb="select"] *,
        [data-testid="stMultiSelect"] div[data-baseweb="select"] * { color:#e7eef2 !important; }

        /* Dunkler Modus: dunkle Schrift im Hauptbereich aufhellen
           (Widget-Labels, Checkbox/Radio/Slider, Expander-Ueberschriften). */
        [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"],
        [data-testid="stAppViewContainer"] [data-testid="stWidgetLabel"] *,
        [data-testid="stAppViewContainer"] [data-baseweb="checkbox"],
        [data-testid="stAppViewContainer"] [data-baseweb="checkbox"] *,
        [data-testid="stAppViewContainer"] [data-baseweb="radio"] *,
        [data-testid="stAppViewContainer"] [data-testid="stTickBar"] *,
        [data-testid="stAppViewContainer"] [data-testid="stExpander"] summary,
        [data-testid="stAppViewContainer"] [data-testid="stExpander"] summary * {
            color:#e7eef2 !important;
        }

        /* Dunkler Modus: Diagramme als dunkle, abgerundete Karten statt
           grellweisser, eckiger Flaechen (Plotly-Hintergrund ist transparent
           -> der Karten-Hintergrund scheint durch). */
        [data-testid="stPlotlyChart"] {
            background:#16212b; border:1px solid #2b3a45; border-radius:14px;
            padding:8px; box-shadow:0 6px 18px rgba(0,0,0,.35);
        }

        /* Dunkler Modus: Unterueberschriften (z. B. "Das grosse Bild") helleres
           Gruen fuer ausreichenden Kontrast auf dunklem Grund. */
        [data-testid="stAppViewContainer"] h3 { color:#4ade80 !important; }

        /* Dunkler Modus: Willkommens-Box mit hellem Rahmen (per key gezielt). */
        [data-testid="stAppViewContainer"] .st-key-welcome {
            border-color:#c4d0d6 !important;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

# Eigener Plotly-Stil, damit Diagramme zum Design passen (transparenter
# Hintergrund -> der Seiten-Verlauf scheint durch; einheitliche Schrift/Farben).
# Schriftfarbe & Gitter folgen dem Hell-/Dunkel-Modus.
import plotly.io as pio
_fg = "#e7eef2" if dark else "#0f2733"
_grid = "#2b3a45" if dark else "#e4ecef"
pio.templates["clima"] = go.layout.Template(layout=dict(
    font=dict(family="Inter, sans-serif", color=_fg, size=13),
    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
    title=dict(font=dict(family="Inter, sans-serif", size=15)),
    xaxis=dict(gridcolor=_grid), yaxis=dict(gridcolor=_grid),
))
pio.templates.default = "plotly_white+clima"

# --------------------------------------------------------------------------- #
# 2) FARBLEITSYSTEM – eine feste, semantische Farbe je Variable, überall gleich.
#    [Grafikdesign: Farbleitsystem/Color Coding] [Erwartungskonformität]
#    Palette = Okabe-Ito (farbenblind-sicher). Doppelkodierung über Linienstil.
#    [WCAG: Farbe nie alleiniger Informationsträger]
# --------------------------------------------------------------------------- #
COLORS = {
    "Temp": "#d55e00",     # vermilion – Temperatur (Wärme = warmer Farbton, semantisch)
    "CO2": "#0072b2",      # blau – CO2
    "CH4": "#009e73",      # grün – Methan
    "N2O": "#cc79a7",      # rosa – Lachgas
    "CFC-11": "#56b4e9",   # hellblau
    "CFC-12": "#e69f00",   # gold
    "MEI": "#999999",      # grau – natürliche Schwankung
    "Aerosols": "#8c564b", # braun – Vulkan
    "TSI": "#f0e442",      # gelb – Sonne
}
DASHES = {
    "Temp": "solid", "CO2": "dash", "CH4": "dot", "N2O": "dashdot",
    "CFC-11": "longdash", "CFC-12": "longdashdot", "MEI": "dot",
    "Aerosols": "dash", "TSI": "dashdot",
}
# Semantische Signalfarben (divergierend): wärmer vs. kühler
WARM, COOL, NEUTRAL = "#d55e00", "#0072b2", "#828c99"

VARIABLES = {
    "Temperaturanomalie (°C)": "Temp",
    "CO₂ – Kohlendioxid (ppm)": "CO2",
    "CH₄ – Methan (ppb)": "CH4",
    "N₂O – Lachgas (ppb)": "N2O",
    "CFC-11 (ppt)": "CFC-11",
    "CFC-12 (ppt)": "CFC-12",
    "MEI – El-Niño-Index": "MEI",
    "Aerosole (vulkanisch)": "Aerosols",
    "TSI – Sonneneinstrahlung (W/m²)": "TSI",
}
COL_TO_LABEL = {v: k for k, v in VARIABLES.items()}
UNITS = {"Temp": "°C", "CO2": "ppm", "CH4": "ppb", "N2O": "ppb", "CFC-11": "ppt",
         "CFC-12": "ppt", "MEI": "Index", "Aerosols": "", "TSI": "W/m²"}
INFO = {
    "Temp": "Abweichung der globalen Temperatur vom langjährigen Mittel. Positiv = wärmer.",
    "CO2": "Wichtigstes menschengemachtes Treibhausgas (Verbrennung fossiler Energie).",
    "CH4": "Methan – starkes Treibhausgas (Landwirtschaft, Gaslecks).",
    "N2O": "Lachgas – langlebiges Treibhausgas (v. a. Düngung).",
    "CFC-11": "FCKW-11 – Treibhausgas & Ozonkiller, durch Montreal-Protokoll rückläufig.",
    "CFC-12": "FCKW-12 – wie CFC-11.",
    "MEI": "El-Niño/La-Niña-Index – natürliche Schwankung, treibt kurzfristige Ausschläge.",
    "Aerosols": "Vulkanische Schwebeteilchen – kühlen kurzfristig ab.",
    "TSI": "Gesamte Sonneneinstrahlung – natürlicher Antrieb, hier nahezu konstant.",
}


# --------------------------------------------------------------------------- #
# Daten  [Doherty Threshold: Caching -> Antwort < 400 ms]
# --------------------------------------------------------------------------- #
@st.cache_data
def load_data():
    df = pd.read_csv("data/climate_change.csv")
    df["Date"] = pd.to_datetime(df[["Year", "Month"]].assign(Day=1))
    df["Decade"] = (df["Year"] // 10 * 10).astype(int)
    return df


def annualize(df):
    """Jahresmittel – glättet das monatliche Rauschen (Tufte: Signal statt Lärm)."""
    num = [c for c in df.columns if c not in ("Date",)]
    out = df.groupby("Year", as_index=False)[num].mean(numeric_only=True)
    out["Date"] = pd.to_datetime(out["Year"].astype(int).astype(str) + "-07-01")
    return out


try:
    df = load_data()
except FileNotFoundError:
    # [Robustheit gegen Benutzerfehler] [Nielsen: hilfreiche Fehlermeldung]
    st.error("Datei `data/climate_change.csv` nicht gefunden. Bitte im Projektordner starten.")
    st.stop()

NUMERIC = ["Temp", "CO2", "CH4", "N2O", "CFC-11", "CFC-12", "MEI", "Aerosols", "TSI"]
MONTHS_DE = ["Jan", "Feb", "Mär", "Apr", "Mai", "Jun", "Jul", "Aug", "Sep", "Okt", "Nov", "Dez"]


# --------------------------------------------------------------------------- #
# Kopf – Narrativ / Leitfrage  [Storytelling]
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Klima-Dashboard</div>
        <h1>Klimadaten im Kontext</h1>
        <p><strong>Leitfrage: Womit hängt die globale Erwärmung zusammen?</strong>
        Dieses Dashboard stellt die Temperatur in Beziehung zu CO₂ und anderen
        Treibern – damit Zusammenhänge sichtbar werden, nicht bloß Einzelwerte.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# --------------------------------------------------------------------------- #
# Onboarding fuer Erstnutzer (einmalig, schliessbar)
# [Lernfoerderlichkeit] [Cognitive Walkthrough: findet der neue Nutzer die Aktion?]
# --------------------------------------------------------------------------- #
if not st.session_state.get("intro_gesehen", False):
    with st.container(border=True, key="welcome"):
        st.markdown("#### :material/waving_hand: Willkommen! In 3 Schritten startklar")
        st.markdown(
            "1. **Zeitraum wählen** – mit dem Regler links; er steuert *alle* Diagramme.\n"
            "2. **Durch die Tabs gehen** – von *Überblick* über *Zusammenhänge* bis *Erkenntnisse*.\n"
            "3. **Maus über Kurven/Punkte** – zeigt genaue Werte (Tooltips)."
        )
        if st.button(":material/check: Los geht's", type="primary"):
            st.session_state.intro_gesehen = True
            st.rerun()

# --------------------------------------------------------------------------- #
# Sidebar = globale Steuerung
# [Shneiderman: Zoom & Filter] [Steuerbarkeit] [Hick: wenige Elemente]
# --------------------------------------------------------------------------- #
st.sidebar.header(":material/tune: Filter & Steuerung")
year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
year_range = st.sidebar.slider(
    "Zeitraum (Jahre)", year_min, year_max, (year_min, year_max), step=1,
    help="Schränkt ALLE Diagramme gemeinsam ein (Brushing & Linking).",
)
glaetten = st.sidebar.toggle(
    "Auf Jahresmittel glätten", value=True,
    help="Mittelt die 12 Monate je Jahr – zeigt den Trend statt des Rauschens.",
)
if st.sidebar.button(":material/restart_alt: Filter zurücksetzen", use_container_width=True):
    st.rerun()

df_f = df[(df["Year"] >= year_range[0]) & (df["Year"] <= year_range[1])].copy()
view = annualize(df_f) if glaetten else df_f

# [Robustheit / Fehlertoleranz] einheitlicher Leerzustand statt kaputter Diagramme
if df_f.empty:
    st.warning("Für den gewählten Zeitraum liegen keine Daten vor. "
               "Bitte den Zeitraum-Regler links anpassen.", icon=":material/info:")
    st.stop()
# Reichen die Punkte für eine belastbare Korrelation? (sonst spaeter Hinweis)
genug_daten = len(df_f) >= 24

# [Nielsen: Sichtbarkeit des Systemstatus]
st.sidebar.success(
    f"Aktiv: {year_range[0]}–{year_range[1]} · {len(df_f)} Monate · "
    f"{'Jahresmittel' if glaetten else 'Monatswerte'}"
)

# Sichtbares Farbleitsystem (Legende) in der Sidebar
# [Farbleitsystem transparent] [Erlernbarkeit] [Recognition over recall]
with st.sidebar.expander(":material/palette: Farbleitsystem", expanded=False):
    st.caption("Jede Größe hat im gesamten Dashboard EINE feste Farbe:")
    swatches = "".join(
        f"<div style='display:flex;align-items:center;margin:3px 0;'>"
        f"<span style='width:14px;height:14px;border-radius:3px;background:{COLORS[c]};"
        f"display:inline-block;margin-right:8px;border:1px solid #0002;'></span>"
        f"<span style='font-size:0.85rem;'>{COL_TO_LABEL[c]}</span></div>"
        for c in NUMERIC
    )
    st.markdown(swatches, unsafe_allow_html=True)
    st.caption("Farbenblind-sicher (Okabe-Ito) + Linienstil als Doppelkodierung.")


def styled_line(fig, col, yaxis="y", width=2.5):
    """Linie mit fester Farbe + Linienstil + reichem Tooltip."""
    fig.add_trace(go.Scatter(
        x=view["Date"], y=view[col], name=COL_TO_LABEL.get(col, col),
        mode="lines", yaxis=yaxis,
        line=dict(color=COLORS.get(col, "#333"), dash=DASHES.get(col, "solid"), width=width),
        # [Tooltip] sprechend, mit Einheit
        hovertemplate=f"<b>{COL_TO_LABEL.get(col, col)}</b><br>"
                      f"%{{x|%b %Y}}<br>%{{y:.3f}} {UNITS.get(col,'')}<extra></extra>",
    ))


# --------------------------------------------------------------------------- #
# 3) INFORMATIONSARCHITEKTUR
#    [Shneiderman-Mantra] Überblick -> Zusammenhänge -> Explorer/Drill-down ->
#    Details. [Miller/Chunking] 5 Tabs.
# --------------------------------------------------------------------------- #
tab_overview, tab_context, tab_explore, tab_data, tab_insights = st.tabs(
    [":material/dashboard: Überblick", ":material/hub: Zusammenhänge",
     ":material/explore: Selbst erkunden", ":material/table_chart: Daten",
     ":material/lightbulb: Erkenntnisse"]
)

# =========================================================================== #
# TAB 1 – ÜBERBLICK
# =========================================================================== #
with tab_overview:
    st.subheader("Das große Bild")
    st.markdown(":material/arrow_forward: **Hier siehst du auf einen Blick:** Wie stark "
                "sich die Erde erwärmt hat – und dass CO₂ und Temperatur gemeinsam steigen.")
    first, last = df_f.iloc[0], df_f.iloc[-1]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Temperaturanomalie", f"{last['Temp']:.2f} °C",
              f"{last['Temp'] - first['Temp']:+.2f} °C",
              help="Änderung vom Anfang bis zum Ende des gewählten Zeitraums.")
    c2.metric("CO₂", f"{last['CO2']:.0f} ppm", f"{last['CO2'] - first['CO2']:+.0f} ppm")
    c3.metric("Methan (CH₄)", f"{last['CH4']:.0f} ppb", f"{last['CH4'] - first['CH4']:+.0f} ppb")
    r_co2 = df_f["Temp"].corr(df_f["CO2"])
    c4.metric("Korrelation Temp–CO₂", f"r = {r_co2:.2f}",
              help="1 = perfekter Gleichlauf, 0 = kein Zusammenhang.")

    st.divider()
    st.markdown("#### CO₂ und Temperatur im Gleichlauf")
    # [Data-Viz: Annotationsebene / Storytelling] markante Ereignisse + Referenzlinie
    annot = st.checkbox("Ereignisse & Referenzlinie anzeigen", value=True,
                        help="Blendet bekannte Klima-Ereignisse und die Null-Linie der "
                             "Temperaturanomalie ein.")
    fig = go.Figure()
    styled_line(fig, "CO2", yaxis="y", width=3)
    styled_line(fig, "Temp", yaxis="y2", width=3)
    fig.update_layout(
        height=470, hovermode="x unified", xaxis_title="Jahr",
        yaxis=dict(title=dict(text="CO₂ (ppm)", font=dict(color=COLORS["CO2"])),
                   tickfont=dict(color=COLORS["CO2"])),
        yaxis2=dict(title=dict(text="Temperaturanomalie (°C)", font=dict(color=COLORS["Temp"])),
                    tickfont=dict(color=COLORS["Temp"]), overlaying="y", side="right"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        margin=dict(t=40), plot_bgcolor="rgba(0,0,0,0)",
    )
    fig.update_xaxes(showgrid=True, gridcolor="#eef1f4")
    if annot:
        # Referenzlinie: Temperatur-Anomalie = 0 (langjähriges Mittel) auf der 2. Achse
        fig.add_shape(type="line", xref="paper", x0=0, x1=1, yref="y2", y0=0, y1=0,
                      line=dict(color="#888", width=1, dash="dot"))
        fig.add_annotation(xref="paper", x=0.01, yref="y2", y=0, yshift=8,
                           text="Temp-Mittel (0 °C)", showarrow=False,
                           font=dict(size=11, color="#888"))
        # Markante Ereignisse, nur wenn im gewählten Zeitraum
        EREIGNISSE = [(1991, "Jun", "Vulkan Pinatubo"), (1998, "Feb", "Starkes El Niño")]
        for jahr, _m, txt in EREIGNISSE:
            if year_range[0] <= jahr <= year_range[1]:
                fig.add_vline(x=pd.Timestamp(f"{jahr}-06-01").timestamp() * 1000,
                              line=dict(color="#888", width=1, dash="dash"))
                fig.add_annotation(x=pd.Timestamp(f"{jahr}-06-01"), yref="paper", y=1,
                                   text=txt, showarrow=False, font=dict(size=11, color="#888"),
                                   bgcolor="rgba(255,255,255,0)")
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Beide Kurven steigen gemeinsam: mehr CO₂ geht mit höheren Temperaturen einher. "
        "Zwei Achsen, weil die Einheiten verschieden sind – vergleichbar bleibt die *Form*."
    )
    # [Recht & Ethik: ehrliche Darstellung, keine Täuschung]
    st.info("**Korrelation ist nicht automatisch Kausalität.** Der enge Gleichlauf ist ein "
            "starkes Indiz; die Erklärung liefert die Physik des Treibhauseffekts.",
            icon=":material/info:")

# =========================================================================== #
# TAB 2 – ZUSAMMENHÄNGE
# =========================================================================== #
with tab_context:
    st.subheader("Womit hängt die Temperatur zusammen?")
    st.markdown(":material/arrow_forward: **Hier findest du heraus:** Welche Faktoren sich "
                "gemeinsam mit der Temperatur verändern – und welche kaum. Je länger der "
                "Balken, desto stärker der Zusammenhang.")
    if not genug_daten:
        st.info("Der gewählte Zeitraum ist sehr kurz (< 2 Jahre) – die Korrelationen "
                "sind dann nur eingeschränkt aussagekräftig.", icon=":material/info:")
    corr_temp = (df_f[NUMERIC].corr()["Temp"].drop("Temp")
                 .sort_values(key=lambda s: s.abs(), ascending=True))
    bar = go.Figure(go.Bar(
        x=corr_temp.values, y=[COL_TO_LABEL.get(i, i) for i in corr_temp.index],
        orientation="h",
        marker_color=[COOL if v >= 0 else WARM for v in corr_temp.values],
        text=[f"{v:+.2f}" for v in corr_temp.values], textposition="outside",
        hovertemplate="%{y}<br>r = %{x:.2f}<extra></extra>",
    ))
    bar.update_layout(height=420, xaxis_title="Korrelation mit der Temperatur (r)",
                      xaxis_range=[-1, 1], margin=dict(t=30), plot_bgcolor="rgba(0,0,0,0)")
    bar.add_vline(x=0, line_color="#888")
    st.plotly_chart(bar, use_container_width=True)
    st.caption("Blau = gleichläufig, Orange = gegenläufig. Länge = Stärke des Zusammenhangs. "
               "Treibhausgase liegen vorne, die Sonne (TSI) kaum.")

    st.divider()
    st.markdown("#### Zwei Größen direkt vergleichen")
    cc1, cc2 = st.columns(2)
    x_lab = cc1.selectbox("X-Achse", list(VARIABLES.keys()),
                          index=list(VARIABLES.values()).index("CO2"),
                          help="Diese Größe wird waagerecht (links↔rechts) aufgetragen.")
    y_lab = cc2.selectbox("Y-Achse", list(VARIABLES.keys()),
                          index=list(VARIABLES.values()).index("Temp"),
                          help="Diese Größe wird senkrecht (unten↕oben) aufgetragen.")
    xcol, ycol = VARIABLES[x_lab], VARIABLES[y_lab]
    fig_sc = px.scatter(df_f, x=xcol, y=ycol, color="Year",
                        color_continuous_scale="Cividis", trendline="ols",
                        trendline_color_override=WARM,
                        labels={xcol: x_lab, ycol: y_lab}, height=460)
    fig_sc.update_traces(marker=dict(size=6, opacity=0.6),
                         hovertemplate=f"{x_lab}: %{{x}}<br>{y_lab}: %{{y}}<extra></extra>")
    fig_sc.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    st.plotly_chart(fig_sc, use_container_width=True)
    r = df_f[xcol].corr(df_f[ycol])
    staerke = ("sehr starken" if abs(r) > .8 else "starken" if abs(r) > .6
               else "mittleren" if abs(r) > .3 else "schwachen")
    richtung = ("Steigt das eine, steigt meist auch das andere."
                if r > 0 else "Steigt das eine, sinkt meist das andere.")
    st.caption(f"Kurzfassung: **{staerke} Zusammenhang** (r = {r:.2f}). {richtung}")

    # Ausführliche Lesehilfe hinter einem Fragezeichen [Hilfe & Dokumentation]
    with st.expander(":material/help: Wie lese ich dieses Diagramm?"):
        steigend = "nach oben" if r > 0 else "nach unten"
        gemeinsam = "gemeinsam hoch" if r > 0 else "gegenläufig"
        st.markdown(
            f"""
Dieses Streudiagramm zeigt, ob zwei Größen miteinander **zusammenhängen**.

**Jeder Punkt steht für einen Monat.** Seine Lage verrät zwei Werte auf einmal:
waagerecht den Wert von {x_lab}, senkrecht den Wert von {y_lab}. Die **Farbe**
gibt das Jahr an (dunkel = früher, hell = später), sodass man auch erkennt, wie
sich die Werte über die Zeit verschoben haben.

Wie **stark** der Zusammenhang ist, sieht man an der Streuung: Liegen die Punkte
**eng beieinander**, ist er stark; sind sie **breit verteilt**, ist er schwach.
Die Zahl **r** fasst das in einem Wert zusammen – nahe **±1** bedeutet sehr
stark, nahe **0** bedeutet kaum ein Zusammenhang.

:material/lightbulb: **Tipp:** Fahre mit der Maus über einen Punkt, um die genauen Werte zu sehen.
            """
        )
        st.markdown("**Wie entsteht die orange Linie?**")
        st.markdown(
            f"""
Die orange Linie ist eine sogenannte **Trend- oder Regressionsgerade**. Sie wird
nicht von Hand gezogen, sondern **berechnet**: Der Computer sucht genau die eine
Gerade, die **insgesamt am dichtesten an allen Punkten** liegt. Dafür wird der
senkrechte Abstand jedes Punktes zur Linie gemessen, **quadriert und
aufsummiert** – die Gerade mit der **kleinsten Summe** gewinnt (Methode der
*kleinsten Quadrate*).

Sie zeigt den groben **„roten Faden"** durch die Punktwolke: Hier verläuft sie
**{steigend}**, die beiden Größen gehen also **{gemeinsam}**. Je enger die Punkte
an der Linie liegen, desto **verlässlicher** beschreibt sie den Zusammenhang.
            """
        )
    with st.expander(":material/menu_book: Was bedeuten diese Variablen?"):  # [Hilfe & Dokumentation]
        for col in NUMERIC:
            st.markdown(f"- **{COL_TO_LABEL[col]}** — {INFO[col]}")

# =========================================================================== #
# TAB 3 – EXPLORER & DRILL-DOWN
# =========================================================================== #
with tab_explore:
    st.subheader("Eigene Zeitreihen vergleichen")
    st.markdown(":material/arrow_forward: **Hier bist du dran:** Wähle selbst aus, welche "
                "Werte du im Zeitverlauf vergleichen willst. Weiter unten kannst du eine "
                "einzelne Größe genauer untersuchen.")
    sel = st.multiselect("Variablen auswählen", list(VARIABLES.keys()),
                         default=["Temperaturanomalie (°C)", "CO₂ – Kohlendioxid (ppm)"],
                         help="Werte mit verschiedenen Einheiten lassen sich standardisieren.")
    if not sel:
        st.warning("Bitte mindestens eine Variable auswählen.")  # [Robustheit]
    else:
        normieren = st.checkbox("Kurven vergleichbar machen",
                                value=len(sel) > 1,
                                help="Bringt alle Linien auf dieselbe Skala, damit man trotz "
                                     "verschiedener Einheiten den Verlauf vergleichen kann "
                                     "(statistisch: z-Standardisierung).")
        fig_e = go.Figure()
        for lab in sel:
            col = VARIABLES[lab]
            y = view[col]
            if normieren:
                y = (y - y.mean()) / y.std()
            fig_e.add_trace(go.Scatter(
                x=view["Date"], y=y, name=lab, mode="lines",
                line=dict(color=COLORS.get(col, "#333"), dash=DASHES.get(col, "solid"), width=2.5),
                hovertemplate=f"<b>{lab}</b><br>%{{x|%b %Y}}<br>%{{y:.3f}}<extra></extra>"))
        fig_e.update_layout(height=460, xaxis_title="Jahr",
                            yaxis_title="z-Wert" if normieren else "Originalwert",
                            legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
                            margin=dict(t=40), plot_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig_e, use_container_width=True)
        # [A11y: Textalternative] beschreibt das Diagramm in Worten
        st.caption("Liniendiagramm der gewählten Größen über die Zeit"
                   + (" (standardisiert auf eine gemeinsame Skala)." if normieren else ".")
                   + " Die vollständigen Werte stehen im Tab „Daten“.")

    st.divider()
    # ---- DRILL-DOWN: von der Übersicht in eine einzelne Größe hineinzoomen ----
    # [Shneiderman: Details on demand] [Drill-down explizit gefordert]
    st.markdown("#### :material/zoom_in: Drill-down: eine Variable im Detail")
    dd_lab = st.selectbox("Variable für die Detailanalyse", list(VARIABLES.keys()),
                          index=list(VARIABLES.values()).index("Temp"), key="drill")
    dd = VARIABLES[dd_lab]
    color = COLORS[dd]
    g1, g2 = st.columns(2)

    # Drill-down A: Dekaden-Mittel (grobe Ebene)
    dec = df_f.groupby("Decade", as_index=False)[dd].mean()
    fig_dec = go.Figure(go.Bar(x=dec["Decade"].astype(str) + "er", y=dec[dd],
                               marker_color=color,
                               hovertemplate="%{x}<br>Ø %{y:.2f} " + UNITS.get(dd, "") + "<extra></extra>"))
    fig_dec.update_layout(height=330, title="Dekaden-Mittel", margin=dict(t=40),
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title=UNITS.get(dd, ""))
    g1.plotly_chart(fig_dec, use_container_width=True)

    # Drill-down B: Saisonfigur (feine Ebene) – Mittel je Monat
    mon = df_f.groupby("Month", as_index=False)[dd].mean()
    fig_mon = go.Figure(go.Scatter(x=[MONTHS_DE[m - 1] for m in mon["Month"]], y=mon[dd],
                                   mode="lines+markers", line=dict(color=color, width=2.5),
                                   hovertemplate="%{x}<br>Ø %{y:.2f} " + UNITS.get(dd, "") + "<extra></extra>"))
    fig_mon.update_layout(height=330, title="Jahresgang (Mittel je Monat)", margin=dict(t=40),
                          plot_bgcolor="rgba(0,0,0,0)", yaxis_title=UNITS.get(dd, ""))
    g2.plotly_chart(fig_mon, use_container_width=True)
    st.caption(f"Drill-down für **{dd_lab}**: links die langfristige Entwicklung über Dekaden, "
               f"rechts das typische Muster innerhalb eines Jahres – vom Groben ins Feine.")

# =========================================================================== #
# TAB 4 – DATEN (Details on demand)
# =========================================================================== #
with tab_data:
    st.subheader("Rohdaten")
    st.markdown(":material/arrow_forward: **Hier liegen die Zahlen dahinter:** die "
                "vollständige Tabelle zum Nachschlagen, Sortieren und Herunterladen.")
    st.caption(f"{len(df_f)} Zeilen im gewählten Zeitraum. Spalten sortierbar, Tabelle durchsuchbar.")
    st.dataframe(df_f.drop(columns=["Decade"]), use_container_width=True, height=420)
    csv = df_f.drop(columns=["Decade"]).to_csv(index=False).encode("utf-8")
    st.download_button("Gefilterte Daten als CSV", csv, "klimadaten_gefiltert.csv",
                       "text/csv", icon=":material/download:")
    with st.expander("Statistische Kurzübersicht"):
        st.dataframe(df_f[NUMERIC].describe().T, use_container_width=True)
    st.caption("Datenquelle: data/climate_change.csv (Climate Change Dataset, "
               "u. a. NOAA/NASA-Reihen). Verwendung zu Studienzwecken.")

# =========================================================================== #
# TAB 5 – ERKENNTNISSE (verständliche Zusammenfassung in Alltagssprache)
# =========================================================================== #
with tab_insights:
    st.subheader("Die wichtigsten Erkenntnisse")
    st.markdown(":material/arrow_forward: **In einfachen Worten:** Das Wichtigste aus den "
                "Daten – automatisch für den gewählten Zeitraum berechnet.")

    # Kennwerte für den aktiven Zeitraum
    temp_delta = df_f["Temp"].iloc[-1] - df_f["Temp"].iloc[0]
    co2_delta = df_f["CO2"].iloc[-1] - df_f["CO2"].iloc[0]
    co2_pct = co2_delta / df_f["CO2"].iloc[0] * 100
    top = (df_f[NUMERIC].corr()["Temp"].drop("Temp")
           .sort_values(key=lambda s: s.abs(), ascending=False))
    top_name = COL_TO_LABEL.get(top.index[0], top.index[0])

    def erkenntnis(titel, text):
        # eigener Block mit etwas Abstand nach unten für bessere Lesbarkeit
        st.markdown(f"##### {titel}")
        st.markdown(text)
        st.markdown("<div style='margin-bottom:1.6rem'></div>", unsafe_allow_html=True)

    erkenntnis(":material/thermostat: Es wird wärmer",
               f"Im Zeitraum {year_range[0]} bis {year_range[1]} ist die Temperatur "
               f"um **{temp_delta:+.2f} °C** gestiegen.")

    erkenntnis(":material/factory: Das CO₂ steigt mit",
               f"Gleichzeitig nahm der CO₂-Gehalt um **{co2_delta:+.0f} ppm** zu "
               f"(das sind {co2_pct:+.1f} %). Temperatur und CO₂ steigen also fast "
               f"im Gleichschritt.")

    erkenntnis(":material/hub: Welcher Faktor passt am besten?",
               f"Von allen menschengemachten Treibern hängt **{top_name}** am "
               f"engsten mit der Temperatur zusammen.")

    erkenntnis(":material/sunny: Die Sonne erklärt es nicht",
               "Die Sonneneinstrahlung schwankt kaum und hängt nur schwach mit der "
               "Temperatur zusammen. Die Erwärmung kommt also nicht „von der Sonne“.")

    st.info("Wichtig: Ein enger Gleichlauf (Korrelation) ist ein **starkes Indiz**, "
            "aber noch kein Beweis für Ursache. Dass CO₂ die Temperatur tatsächlich "
            "antreibt, erklärt die Physik des Treibhauseffekts.", icon=":material/balance:")

    st.divider()
    st.markdown("#### So liest du dieses Dashboard")
    st.markdown(
        "- :material/dashboard: **Überblick** – der schnelle Gesamteindruck.\n"
        "- :material/hub: **Zusammenhänge** – welche Faktoren zusammenhängen.\n"
        "- :material/explore: **Selbst erkunden** – eigene Vergleiche und Detailansichten.\n"
        "- :material/table_chart: **Daten** – die Zahlen zum Nachschlagen und Herunterladen.\n"
        "- Mit dem **Zeitraum-Regler** links änderst du *alle* Diagramme gleichzeitig. "
        "Fahre mit der Maus über eine Kurve, um genaue Werte zu sehen."
    )

st.divider()

# --------------------------------------------------------------------------- #
# Leichtgewichtige Evaluation: Single Ease Question (SEQ)
# [V6 – Evaluation: SEQ] demonstriert den Evaluations-Gedanken; speichert lokal.
# --------------------------------------------------------------------------- #
with st.expander(":material/rate_review: Feedback geben (1 Frage)"):
    seq = st.slider("Wie leicht war die Bedienung insgesamt?", 1, 7, 5,
                    help="1 = sehr schwer · 7 = sehr leicht (Single Ease Question)")
    if st.button(":material/send: Feedback senden"):
        zeile = pd.DataFrame([{"zeitpunkt": pd.Timestamp.now().isoformat(timespec="seconds"),
                               "seq": seq}])
        pfad = "feedback.csv"
        import os
        zeile.to_csv(pfad, mode="a", header=not os.path.exists(pfad), index=False)
        st.success("Danke für dein Feedback!", icon=":material/check_circle:")
    st.caption("Hinweis: Das Feedback wird nur lokal in `feedback.csv` gespeichert – "
               "eine Demonstration des Evaluations-Gedankens, keine echte Datenerhebung.")

st.caption("Refinement vom Baseline-Entwurf · Streamlit & Plotly  ·  Datenquelle: data/climate_change.csv")

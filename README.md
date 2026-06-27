# 🌍 Klimadaten im Kontext

Ein interaktives Dashboard zur Visualisierung von Klimadaten mit **Streamlit** und **Plotly**.

> **Womit hängt die globale Erwärmung zusammen?**

Dabei werden Temperaturentwicklungen gemeinsam mit verschiedenen natürlichen und anthropogenen Einflussgrößen visualisiert, um Zusammenhänge nachvollziehbar zu machen.

---

## Funktionen

### 📈 Interaktive Datenvisualisierung

Das Dashboard ermöglicht die Analyse verschiedener Klimavariablen, darunter:

- Globale Temperaturanomalie
- CO₂-Konzentration
- Methan (CH₄)
- Lachgas (N₂O)
- CFC-11
- CFC-12
- El-Niño-Index (MEI)
- Vulkanische Aerosole
- Sonneneinstrahlung (TSI)

Alle Diagramme reagieren dynamisch auf den ausgewählten Zeitraum.

---

### 🗂 Struktur der Anwendung

Die Anwendung orientiert sich am **Shneiderman-Mantra** („Overview first, zoom and filter, then details on demand“) und ist in fünf Bereiche gegliedert:

1. **Überblick**
   - Entwicklung von Temperatur und CO₂
   - Kennzahlen
   - Zeitreihenvergleich

2. **Zusammenhänge**
   - Korrelationsanalyse
   - Streudiagramme
   - Vergleich verschiedener Einflussgrößen

3. **Selbst erkunden**
   - Eigene Variablenauswahl
   - Vergleich mehrerer Zeitreihen
   - Drill-Down-Analysen

4. **Daten**
   - Vollständige Datentabelle
   - Statistische Kennzahlen
   - CSV-Export

5. **Erkenntnisse**
   - Automatisch erzeugte Zusammenfassung der wichtigsten Ergebnisse
   - Interpretation der Daten in verständlicher Sprache

---

## Installation

Repository klonen:

```bash
git clone <repository-url>
cd <projektordner>
```

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

---
## Anwendung starten

```bash
streamlit run app.py
```

Anschließend öffnet sich die Anwendung automatisch im Browser.

---

## Datengrundlage

Die Anwendung verwendet den Datensatz

**Climate Change Dataset**

mit Zeitreihen zu

- Temperatur
- CO₂
- CH₄
- N₂O
- CFC-11
- CFC-12
- MEI
- Aerosolen
- Sonneneinstrahlung

Die Daten liegen lokal unter

```text
data/climate_change.csv
```



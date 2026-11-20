import streamlit as st
import pandas as pd
from pathlib import Path
import html
import json
import random
import re
import time
from datetime import datetime

st.set_page_config(layout="wide", page_title="SISB Economics · Past Paper Tool")

APP_DIR = Path(__file__).parent
CSV_NAME = "IGCSE Econ P2 Past Papers + MS - Sheet1.csv"
MODEL_ANSWERS_NAME = "model_answers.json"
MONTH_ORDER = {"March": 1, "June": 2, "November": 3}
MINUTES_PER_MARK = 1.5   # 90 marks in 2 h 15 min

# ── Answer-building colours (SISB secondary palette) ─────────────────────────
TAGS = {
    "P": {"name": "Point",       "color": "#597CFF", "ink": "#3451d1", "hint": "The economic idea or definition"},
    "E": {"name": "Explanation", "color": "#37C563", "ink": "#1e7a3c", "hint": "Each link in the chain: because… so… this means…"},
    "A": {"name": "Application", "color": "#FF801D", "ink": "#b4530a", "hint": "Linking to the country or case in the question"},
    "V": {"name": "Evaluation",  "color": "#E171EA", "ink": "#a12aa8", "hint": "The other side: However… this may not happen if…"},
    "C": {"name": "Conclusion",  "color": "#83E3DE", "ink": "#11807a", "hint": "Your judgement: Overall… it depends on…"},
}

def tint(hex_color, alpha=0.16):
    h = hex_color.lstrip("#")
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha})"

for _t in TAGS.values():
    _t["tint"] = tint(_t["color"])

TYPE_INFO = {
    "analyse6": {
        "label": "6-mark Analyse",
        "tags": ["P", "E"],
        "minutes": 9,
        "structure": [("Point 1", "P → E → E → E"), ("Point 2", "P → E → E → E"), ("Point 3", "P → E → E")],
        "frame": [("Point 1 and its chain", ["P", "E"]), ("Point 2 and its chain", ["P", "E"]), ("Point 3 and its chain", ["P", "E"])],
        "tip": "Analyse means explain how or why, step by step. Each sentence should lead to the next, like links in a chain. You only need one side, and no conclusion.",
        "checklist": [
            "I made at least two separate points (three is safer).",
            "Each point is developed into a chain: because… so… this means…",
            "I used economic terms correctly (e.g. total demand, productivity).",
            "I answered the exact question that was asked.",
            "I didn't spend time on evaluation or a conclusion. Analyse doesn't need them.",
        ],
        "levels": None,
    },
    "discuss6": {
        "label": "6-mark Discuss (Question 1)",
        "tags": ["P", "E", "A", "V", "C"],
        "minutes": 9,
        "structure": [("For", "P → E (×2)"), ("Against", "V → E (×2)"), ("Link to the extract", "A"), ("Conclusion", "C")],
        "frame": [("For: point 1", ["P", "E"]), ("For: point 2", ["P", "E"]), ("Against: point 1", ["V", "E"]),
                  ("Against: point 2", ["V", "E"]), ("Conclusion, linked to the country", ["C", "A"])],
        "tip": "Discuss means look at both sides. In Question 1, use the country in the extract to make your points specific.",
        "checklist": [
            "I wrote about both sides: why it might and why it might not.",
            "Each point is explained, not just listed.",
            "I linked at least one point to the country or case in the extract.",
            "I finished with a short conclusion that answers the question.",
        ],
        "levels": None,
    },
    "discuss8": {
        "label": "8-mark Discuss",
        "tags": ["P", "E", "V", "C"],
        "minutes": 12,
        "structure": [("For", "P → E → E (×2)"), ("Against", "V → E → E (×2)"), ("Conclusion", "C: Overall… it depends on…")],
        "frame": [("For: point 1", ["P", "E"]), ("For: point 2", ["P", "E"]), ("Against: point 1", ["V", "E"]),
                  ("Against: point 2", ["V", "E"]), ("Conclusion", ["C"])],
        "tip": "The examiner wants reasoned discussion of both sides. Your 'against' points must be new reasons, not the 'for' points reversed.",
        "checklist": [
            "I wrote at least two developed points on each side.",
            "My points are chains of reasoning, not lists.",
            "My 'against' side is not just my 'for' side reversed.",
            "I used economic terms correctly.",
            "I ended with a judgement: Overall… it depends on…",
        ],
        "levels": [
            ("Level 3", "6–8 marks", "Reasoned discussion examining both sides"),
            ("Level 2", "3–5 marks", "Reasoned discussion, may be one-sided"),
            ("Level 1", "1–2 marks", "Simple attempt"),
        ],
    },
}

STARTERS = {
    "P": ["One reason is…", "A … is… (definition)", "Firstly, …"],
    "E": ["This means that…", "…, so…", "As a result, …", "This leads to…", "…, which causes…"],
    "A": ["In [country], …", "The extract shows that…", "For example, in [country]…"],
    "V": ["However, …", "On the other hand, …", "This may not happen if…"],
    "C": ["Overall, …", "It depends on…", "The most important factor is… because…"],
}

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');
html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
#MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

.app-header { background: #002F6C; border-radius: 12px; padding: 1.4rem 2rem; margin-bottom: 1.8rem;
    display: flex; align-items: center; justify-content: space-between; }
.app-header h1 { font-family: 'Lato', sans-serif !important; font-weight: 900; color: #fff; font-size: 1.7rem; margin: 0; }
.app-header .subtitle { color: #83E3DE; font-size: 0.85rem; margin-top: 3px; }
.header-badge { background: #008BCC; color: #fff; font-size: 0.75rem; font-weight: 700; padding: 5px 14px;
    border-radius: 20px; letter-spacing: 0.06em; text-transform: uppercase; }

.paper-label { background: #e8f4fb; border-left: 4px solid #008BCC; color: #002F6C; padding: 10px 16px;
    border-radius: 0 8px 8px 0; font-size: 0.9rem; font-weight: 700; margin-bottom: 1rem; }
.topic-label { background: #e0f7f6; border-left: 4px solid #83E3DE; color: #002F6C; padding: 10px 16px;
    border-radius: 0 8px 8px 0; font-size: 0.9rem; font-weight: 700; margin-bottom: 1rem; }

.marks-pill { display: inline-flex; align-items: center; gap: 6px; background: #002F6C; color: #fff; font-size: 0.85rem;
    font-weight: 700; padding: 6px 16px; border-radius: 20px; margin-bottom: 1.2rem; }
.count-pill { display: inline-flex; align-items: center; gap: 6px; background: #008BCC; color: #fff; font-size: 0.85rem;
    font-weight: 700; padding: 6px 16px; border-radius: 20px; margin-bottom: 1.2rem; }

.freq-essential { display: inline-flex; background: #fff3cd; color: #7a4800; border: 1px solid #f0c040; font-size: 0.72rem;
    font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em; }
.freq-important { display: inline-flex; background: #e0f0fb; color: #003f7a; border: 1px solid #008BCC; font-size: 0.72rem;
    font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em; }
.freq-worthknowing { display: inline-flex; background: #e6f9f4; color: #1a5c4a; border: 1px solid #37C563; font-size: 0.72rem;
    font-weight: 700; padding: 3px 10px; border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em; }
.freq-info { background: #f0f7ff; border: 1px solid #c5dff5; border-radius: 10px; padding: 12px 16px; font-size: 0.82rem;
    color: #002F6C; margin-bottom: 1.2rem; line-height: 1.6; }

.stimulus-card { background: #fffdf5; border: 1px solid #e8d98a; border-left: 5px solid #FF801D; border-radius: 0 10px 10px 0;
    padding: 1.2rem 1.5rem; font-size: 0.93rem; line-height: 1.7; color: #3d3110; margin-bottom: 1.5rem; }
.stimulus-label { font-size: 0.72rem; font-weight: 700; color: #FF801D; text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px; }

.year-group-header { font-weight: 900; font-size: 1.1rem; color: #002F6C; border-bottom: 2px solid #008BCC;
    padding-bottom: 6px; margin: 1.8rem 0 1rem 0; }
.topic-q-context { font-size: 0.78rem; font-weight: 700; color: #008BCC; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 4px; }
.topic-badge { display: inline-flex; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem; font-weight: 700;
    background: #e0f0fb; color: #002F6C; margin-right: 4px; margin-bottom: 6px; }

.section-rule { border: none; border-top: 1px solid #e2e8f0; margin: 0.6rem 0 1.4rem 0; }
.col-header { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #008BCC;
    padding-bottom: 6px; border-bottom: 2px solid #008BCC; margin-bottom: 0.8rem; }
.part-badge { display: inline-flex; align-items: center; justify-content: center; width: 36px; height: 36px; background: #002F6C;
    color: #fff; font-weight: 900; font-size: 1rem; border-radius: 8px; }
.q-text { font-size: 0.95rem; line-height: 1.65; color: #1e293b; }
.marks-badge { display: inline-flex; align-items: center; justify-content: center; padding: 3px 10px; border-radius: 6px;
    font-size: 0.8rem; font-weight: 700; min-width: 38px; }
.marks-1 { background: #dcfce7; color: #166534; } .marks-2 { background: #fef9c3; color: #854d0e; }
.marks-3 { background: #ffedd5; color: #9a3412; } .marks-4p { background: #fee2e2; color: #991b1b; }
.ms-card { background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #008BCC; border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem; font-size: 0.88rem; line-height: 1.7; color: #1e293b; }
.teacher-tip { margin-top: 10px; padding-top: 10px; border-top: 1px dashed #cbd5e1; font-size: 0.83rem; color: #475569; }
.tip-label { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.07em; color: #008BCC; margin-bottom: 4px; }
.row-divider { border: none; border-top: 1px solid #f1f5f9; margin: 1rem 0; }

/* Technique + practice */
.legend { display: flex; flex-wrap: wrap; gap: 8px; margin: 0.3rem 0 1rem 0; }
.chip { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; border-radius: 999px; font-size: 0.8rem;
    font-weight: 700; color: #1e293b; }
.chip .dot { width: 10px; height: 10px; border-radius: 50%; display: inline-block; }
.model-para { line-height: 2.0; font-size: 0.97rem; margin-bottom: 0.9rem; color: #1e293b; }
.hl { padding: 2px 3px; border-radius: 3px; box-decoration-break: clone; -webkit-box-decoration-break: clone; }
.hl sup { font-size: 0.68rem; font-weight: 900; margin-left: 2px; }
.side-head { font-size: 0.72rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #64748b; margin: 1rem 0 0.3rem 0; }
.q-card { background: #fff; border: 1px solid #c5dff5; border-radius: 10px; padding: 1rem 1.2rem; margin-bottom: 1rem; }
.q-card .q-meta { font-size: 0.75rem; font-weight: 700; color: #008BCC; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 6px; }
.q-card .q-main { font-size: 1.08rem; font-weight: 700; color: #002F6C; line-height: 1.5; }
.guide-row { display: flex; gap: 10px; align-items: baseline; margin: 4px 0; font-size: 0.9rem; }
.guide-row b { min-width: 150px; color: #002F6C; }
.frame-head { display: flex; align-items: center; gap: 8px; margin: 0.8rem 0 0.2rem 0; font-weight: 700; color: #002F6C; font-size: 0.92rem; }
.time-guide { font-size: 0.75rem; color: #64748b; font-weight: 700; }
.student-answer { background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: 0.8rem 1rem; font-size: 0.92rem;
    line-height: 1.6; color: #1e293b; white-space: pre-wrap; min-height: 2.5rem; }
.empty-answer { color: #94a3b8; font-style: italic; }
.score-big { font-size: 3rem; font-weight: 900; color: #002F6C; line-height: 1; }
.score-sub { font-size: 1rem; color: #008BCC; font-weight: 700; }
.result-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #e2e8f0; font-size: 0.95rem; }

[data-testid="stSidebar"] { background: #f0f7ff; border-right: 1px solid #c5dff5; }
@media print {
    section[data-testid='stSidebar'] { display: none !important; }
    .app-header { background: #002F6C !important; -webkit-print-color-adjust: exact; }
    .hl { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
</style>
""", unsafe_allow_html=True)


# ── General helpers ───────────────────────────────────────────────────────────
def safe_str(val, default=""):
    return str(val) if pd.notnull(val) else default

def esc(text):
    return html.escape(safe_str(text)).replace("\n", "<br>")

def marks_class(marks_str):
    try:
        m = float(marks_str)
        if m <= 1: return "marks-1"
        if m == 2: return "marks-2"
        if m == 3: return "marks-3"
        return "marks-4p"
    except Exception:
        return "marks-2"

def part_sort_key(part):
    if part.lower() == "stimulus":
        return (0, "", 0)
    base = part.split("(")[0].strip()
    sub = part[len(base):].strip("() ")
    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6}
    return (1, base, roman.get(sub.lower(), 0))

def month_key(m):
    return MONTH_ORDER.get(m, 9)

def to_marks(val):
    try:
        return int(float(val))
    except Exception:
        return 0

def minutes_for(marks):
    return max(1, round(marks * MINUTES_PER_MARK))

def question_type(text, marks):
    text = safe_str(text).strip().lower()
    if marks == 8:
        return "discuss8"
    if marks == 6:
        return "discuss6" if text.startswith("discuss") else "analyse6"
    return None

def chip_html(tag_code, label=None):
    t = TAGS[tag_code]
    return (f'<span class="chip" style="background:{t["tint"]};border:1.5px solid {t["color"]}">'
            f'<span class="dot" style="background:{t["color"]}"></span>{html.escape(label or t["name"])}</span>')

def legend_html(tag_codes):
    return '<div class="legend">' + "".join(chip_html(c) for c in tag_codes) + "</div>"

def freq_badge(count):
    if count >= 40:
        return '<span class="freq-essential">🔥 Essential</span>'
    if count >= 15:
        return '<span class="freq-important">⭐ Important</span>'
    return '<span class="freq-worthknowing">📚 Worth Knowing</span>'

def freq_label(count):
    if count >= 40:
        return "🔥 Essential"
    if count >= 15:
        return "⭐ Important"
    return "📚 Worth Knowing"

def markscheme_html(ms, explanation):
    tip = f'<div class="teacher-tip"><div class="tip-label">Teacher Tip</div>{esc(explanation)}</div>' if safe_str(explanation) else ""
    return f'<div class="ms-card">{esc(safe_str(ms, "No markscheme available."))}{tip}</div>'

def secrets_get(key):
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return None


# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    file_path = APP_DIR / CSV_NAME
    if not file_path.exists():
        st.error(f"CSV file not found: {file_path}")
        st.stop()
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    required = ["Year", "Month", "Paper", "Question", "Part", "Stimulus / Scenario",
                "Question Text", "Marks", "Markscheme", "Explanation"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.error(f"Missing columns in CSV: {missing}")
        st.stop()
    for col in ["Topic 1", "Topic 2"]:
        if col not in df.columns:
            df[col] = ""
        df[col] = df[col].fillna("")
    df["Part"] = df["Part"].astype(str).str.strip()
    df["is_stim"] = df["Part"].str.lower() == "stimulus"
    df["marks_int"] = df["Marks"].apply(to_marks)
    return df

@st.cache_data
def load_model_answers():
    path = APP_DIR / MODEL_ANSWERS_NAME
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        return json.load(f)

df = load_data()
model_answers = load_model_answers()

def find_row(year, month, paper, question, part):
    r = df[(df["Year"] == year) & (df["Month"] == month) & (df["Paper"] == paper) &
           (df["Question"] == question) & (df["Part"] == str(part))]
    return r.iloc[0] if len(r) else None

def find_stimulus(year, month, paper, question):
    r = df[(df["Year"] == year) & (df["Month"] == month) & (df["Paper"] == paper) &
           (df["Question"] == question) & df["is_stim"]]
    if len(r):
        text = safe_str(r["Stimulus / Scenario"].iloc[0]).strip()
        return text or None
    return None

def model_for(year, month, paper, question, part):
    for m in model_answers:
        if (m["year"] == year and m["month"] == month and m["paper"] == paper
                and m["question"] == question and m["part"] == str(part)):
            return m
    return None

@st.cache_data
def build_topic_counts(_df):
    counts = {}
    q_rows = _df[~_df["is_stim"]]
    for topic in set(list(_df["Topic 1"].unique()) + list(_df["Topic 2"].unique())) - {""}:
        counts[topic] = int(((q_rows["Topic 1"] == topic) | (q_rows["Topic 2"] == topic)).sum())
    return counts

topic_counts = build_topic_counts(df)

def topic_sort_key(t):
    c = topic_counts.get(t, 0)
    return (0 if c >= 40 else 1 if c >= 15 else 2, t)

all_topics = sorted(topic_counts.keys(), key=topic_sort_key)

SIDE_HEAD = re.compile(r"(?:Reasons? why|Why)\b[^:.;]{0,100}:")

def parse_sides(ms):
    """Split a 'Why it might: …; … Why it might not: …' markscheme into two labelled lists."""
    ms = safe_str(ms)
    heads = list(SIDE_HEAD.finditer(ms))
    if len(heads) != 2:
        return None
    def items(chunk):
        out = []
        for x in chunk.split(";"):
            x = x.strip(" .\n")
            if len(x) > 3:
                out.append(x[0].upper() + x[1:])
        return out
    a = items(ms[heads[0].end():heads[1].start()])
    b = items(ms[heads[1].end():])
    if len(a) < 2 or len(b) < 2:
        return None
    labels = [heads[0].group(0).rstrip(":").strip(), heads[1].group(0).rstrip(":").strip()]
    return labels, a, b


# ── Shared rendering ──────────────────────────────────────────────────────────
def render_question_rows(table_data, student_mode):
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)
    if student_mode:
        c1, c2, c3 = st.columns([1, 5, 1])
    else:
        c1, c2, c3, c4 = st.columns([1, 4, 1, 5])
        c4.markdown('<div class="col-header">Markscheme & Explanation</div>', unsafe_allow_html=True)
    c1.markdown('<div class="col-header">Part</div>', unsafe_allow_html=True)
    c2.markdown('<div class="col-header">Question</div>', unsafe_allow_html=True)
    c3.markdown('<div class="col-header">Marks</div>', unsafe_allow_html=True)

    for _, row in table_data.iterrows():
        part, marks = safe_str(row["Part"]), safe_str(row["Marks"])
        if student_mode:
            col1, col2, col3 = st.columns([1, 5, 1])
        else:
            col1, col2, col3, col4 = st.columns([1, 4, 1, 5])
            col4.markdown(markscheme_html(row["Markscheme"], row["Explanation"]), unsafe_allow_html=True)
        col1.markdown(f'<div class="part-badge">({html.escape(part)})</div>', unsafe_allow_html=True)
        col2.markdown(f'<div class="q-text">{esc(row["Question Text"])}</div>', unsafe_allow_html=True)
        col3.markdown(f'<div class="marks-badge {marks_class(marks)}">{html.escape(marks)}</div>', unsafe_allow_html=True)
        st.markdown('<hr class="row-divider">', unsafe_allow_html=True)

def stimulus_card(text, label="📄 Stimulus / Scenario"):
    return f'<div class="stimulus-card"><div class="stimulus-label">{label}</div>{esc(text)}</div>'

def model_answer_html(model, show_sides=True):
    side_names = {"for": "For", "against": "Against", "conclusion": "Conclusion"}
    out, last_side = [], "__start__"
    for para in model["model"]:
        side = para.get("side")
        if show_sides and side and side != last_side:
            out.append(f'<div class="side-head">{side_names.get(side, side)}</div>')
        last_side = side
        spans = []
        for tag, text in para["sentences"]:
            t = TAGS[tag]
            spans.append(f'<span class="hl" style="background:{t["tint"]};border-bottom:2px solid {t["color"]}">'
                         f'{html.escape(text)}<sup style="color:{t["ink"]}">{tag}</sup></span>')
        out.append('<div class="model-para">' + " ".join(spans) + "</div>")
    return "".join(out)

def model_answer_text(model):
    return "\n\n".join(" ".join(s[1] for s in p["sentences"]) for p in model["model"])

def checklist_widget(qtype, key_prefix):
    info = TYPE_INFO[qtype]
    ticked = 0
    for i, item in enumerate(info["checklist"]):
        if st.checkbox(item, key=f"{key_prefix}_chk_{i}"):
            ticked += 1
    if info["levels"]:
        st.markdown("**How 8-mark answers are marked** (levels from the markscheme):")
        for lvl, rng, desc in info["levels"]:
            st.markdown(f"- **{lvl} ({rng})**: {desc}")
    return ticked


# ── Interactive components (embedded HTML/JS) ─────────────────────────────────
COMPONENT_BASE = """
<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@400;700;900&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box}
body{font-family:Lato,sans-serif;margin:0;padding:2px 4px 12px;color:#1e293b;font-size:15px;background:#fff}
.btn{font-family:Lato,sans-serif;font-weight:700;font-size:14px;border-radius:8px;padding:8px 16px;cursor:pointer;border:1.5px solid #008BCC;background:#008BCC;color:#fff;margin:4px 6px 4px 0}
.btn.ghost{background:#fff;color:#008BCC}
.btn:disabled{opacity:.45;cursor:default}
.card{border:1px solid #e2e8f0;border-left:5px solid #cbd5e1;border-radius:0 8px 8px 0;padding:10px 12px;margin:7px 0;background:#fff;line-height:1.55}
.pill{display:inline-flex;align-items:center;gap:5px;border:1.5px solid #cbd5e1;background:#fff;color:#1e293b;border-radius:999px;padding:4px 11px;font-size:12.5px;font-weight:700;cursor:pointer;margin:7px 6px 0 0;font-family:Lato,sans-serif}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.res{font-size:13px;font-weight:700;margin-top:6px}
.ok{color:#15803d}.bad{color:#b91c1c}
.score{font-size:16px;font-weight:900;color:#002F6C;margin:10px 0 4px}
.box{border:1.5px dashed #c5dff5;border-radius:10px;padding:8px 10px;min-height:56px;margin:6px 0 14px;background:#f8fbff}
.box-label{font-size:11.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#64748b;margin-top:6px}
.num{display:inline-flex;width:22px;height:22px;border-radius:50%;background:#002F6C;color:#fff;font-size:12px;font-weight:900;align-items:center;justify-content:center;margin-right:8px;flex-shrink:0}
.row{display:flex;align-items:flex-start}
.clickable{cursor:pointer}
.clickable:hover{box-shadow:0 1px 6px rgba(0,47,108,.15)}
.para-gap{height:10px}
.side{font-size:12px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:#64748b;margin:4px 0}
.hint{font-size:13px;color:#475569;margin:2px 0 8px}
</style></head><body>
<div id="app"></div>
<script>
const TAGS = __TAGS__;
const D = __DATA__;
__SCRIPT__
</script></body></html>
"""

def embed_html(page, height):
    """Embed our own interactive HTML. Uses st.iframe (current Streamlit), falling back for older versions."""
    if hasattr(st, "iframe"):
        st.iframe(page, height=height)
    else:
        import streamlit.components.v1 as components
        components.html(page, height=height, scrolling=True)

def render_component(script, data, height):
    page = (COMPONENT_BASE
            .replace("__TAGS__", json.dumps(TAGS))
            .replace("__DATA__", json.dumps(data).replace("</", "<\\/"))
            .replace("__SCRIPT__", script))
    embed_html(page, height)

SPOT_SCRIPT = r"""
const app = document.getElementById('app');
let items = [];
D.paras.forEach((p, pi) => p.forEach(s => items.push({pi, tag: s[0], text: s[1], pick: null})));
let checked = false;
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function render(){
  let h = '<div class="hint">Click a label under each sentence to say what job it does. Then press <b>Check</b>.</div>';
  let lastP = 0;
  items.forEach((it, i) => {
    if (it.pi !== lastP) { h += '<div class="para-gap"></div>'; lastP = it.pi; }
    const t = it.pick ? TAGS[it.pick] : null;
    const style = t ? `border-left-color:${t.color};background:${t.tint}` : '';
    h += `<div class="card" style="${style}">${esc(it.text)}<div>`;
    D.tags.forEach(code => {
      const tg = TAGS[code]; const on = it.pick === code;
      h += `<button class="pill" data-i="${i}" data-c="${code}" style="border-color:${tg.color};${on ? 'background:'+tg.tint : ''}"><span class="dot" style="background:${tg.color}"></span>${tg.name}</button>`;
    });
    h += '</div>';
    if (checked && it.pick) {
      h += it.pick === it.tag ? '<div class="res ok">✓ Correct</div>'
        : `<div class="res bad">✗ Not quite: this is ${TAGS[it.tag].name.toLowerCase()} (${TAGS[it.tag].hint.toLowerCase()})</div>`;
    }
    h += '</div>';
  });
  const done = items.filter(x => x.pick).length;
  h += `<div class="score" id="score"></div>`;
  h += `<button class="btn" id="check" ${done < items.length ? 'disabled' : ''}>Check (${done}/${items.length} labelled)</button>`;
  h += `<button class="btn ghost" id="retry">Try the wrong ones again</button><button class="btn ghost" id="reset">Start again</button>`;
  app.innerHTML = h;
  if (checked) {
    const right = items.filter(x => x.pick === x.tag).length;
    document.getElementById('score').textContent = `Score: ${right} / ${items.length}` + (right === items.length ? '  🎉 Perfect!' : '');
  }
  app.querySelectorAll('.pill').forEach(b => b.onclick = () => { items[+b.dataset.i].pick = b.dataset.c; checked = false; render(); });
  document.getElementById('check').onclick = () => { checked = true; render(); };
  document.getElementById('retry').onclick = () => { items.forEach(x => { if (x.pick !== x.tag) x.pick = null; }); checked = false; render(); };
  document.getElementById('reset').onclick = () => { items.forEach(x => x.pick = null); checked = false; render(); };
}
render();
"""

BUILD_SCRIPT = r"""
const app = document.getElementById('app');
let idx = 0, pool = [], placed = [], checked = false, shown = false;
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function seeded(seed){ let s = seed % 2147483647; if (s <= 0) s += 2147483646; return () => (s = s * 16807 % 2147483647) / 2147483647; }
function setup(){
  const n = D.chains[idx].sentences.length;
  const rnd = seeded(D.seed + idx * 97);
  pool = [...Array(n).keys()];
  for (let i = n - 1; i > 0; i--) { const j = Math.floor(rnd() * (i + 1)); [pool[i], pool[j]] = [pool[j], pool[i]]; }
  if (pool.every((v, k) => v === k)) pool.push(pool.shift());
  placed = []; checked = false; shown = false;
}
function card(k, where, pos){
  const s = D.chains[idx].sentences[k]; const t = TAGS[s[0]];
  let mark = '';
  if (checked && where === 'placed') mark = (k === pos) ? ' <span class="ok">✓</span>' : ' <span class="bad">✗</span>';
  const num = where === 'placed' ? `<span class="num">${pos + 1}</span>` : '';
  return `<div class="card clickable row" data-k="${k}" data-w="${where}" style="border-left-color:${t.color};background:${t.tint}">${num}<div>${esc(s[1])}${mark}</div></div>`;
}
function render(){
  const ch = D.chains[idx];
  let h = `<div class="side">Chain ${idx + 1} of ${D.chains.length}${ch.side ? ' · ' + ch.side : ''}</div>`;
  h += '<div class="hint">Click the pieces in the right order to build the chain of reasoning. Click a placed piece to send it back.</div>';
  h += '<div class="box-label">Your chain</div><div class="box">';
  const order = shown ? [...Array(ch.sentences.length).keys()] : placed;
  order.forEach((k, pos) => h += card(k, 'placed', pos));
  if (!order.length) h += '<div class="hint" style="margin:10px 4px">Start with the point…</div>';
  h += '</div>';
  if (!shown) { h += '<div class="box-label">Pieces</div><div class="box">'; pool.forEach(k => h += card(k, 'pool')); if (!pool.length) h += '<div class="hint" style="margin:10px 4px">All placed. Press Check.</div>'; h += '</div>'; }
  if (checked) {
    const right = placed.filter((k, pos) => k === pos).length;
    h += `<div class="score">${right === placed.length ? '🎉 Perfect chain!' : `${right} of ${placed.length} in the right place`}</div>`;
  }
  h += `<button class="btn" id="check" ${pool.length || shown ? 'disabled' : ''}>Check</button>`;
  h += `<button class="btn ghost" id="again">Try again</button><button class="btn ghost" id="show">Show the answer</button>`;
  h += `<button class="btn ghost" id="next" ${D.chains.length < 2 ? 'disabled' : ''}>Next chain →</button>`;
  app.innerHTML = h;
  app.querySelectorAll('.clickable').forEach(el => el.onclick = () => {
    if (shown) return;
    const k = +el.dataset.k;
    if (el.dataset.w === 'pool') { pool = pool.filter(x => x !== k); placed.push(k); }
    else { placed = placed.filter(x => x !== k); pool.push(k); }
    checked = false; render();
  });
  document.getElementById('check').onclick = () => { checked = true; render(); };
  document.getElementById('again').onclick = () => { setup(); render(); };
  document.getElementById('show').onclick = () => { shown = true; checked = false; render(); };
  document.getElementById('next').onclick = () => { idx = (idx + 1) % D.chains.length; setup(); render(); };
}
setup(); render();
"""

SORT_SCRIPT = r"""
const app = document.getElementById('app');
let picks = D.items.map(() => null), checked = false;
const COLS = ['#37C563', '#E171EA'];
const TINTS = ['rgba(55,197,99,0.16)', 'rgba(225,113,234,0.16)'];
function esc(s){const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
function render(){
  let h = '<div class="hint">These points all come from the markscheme. Decide which side each one belongs to.</div>';
  D.items.forEach((it, i) => {
    const p = picks[i];
    const style = p === null ? '' : `border-left-color:${COLS[p]};background:${TINTS[p]}`;
    h += `<div class="card" style="${style}">${esc(it.text)}<div>`;
    [0, 1].forEach(s => h += `<button class="pill" data-i="${i}" data-s="${s}" style="border-color:${COLS[s]};${p === s ? 'background:' + TINTS[s] : ''}"><span class="dot" style="background:${COLS[s]}"></span>${esc(D.labels[s])}</button>`);
    h += '</div>';
    if (checked && p !== null) h += p === it.side ? '<div class="res ok">✓ Correct</div>' : `<div class="res bad">✗ This belongs in "${esc(D.labels[it.side])}"</div>`;
    h += '</div>';
  });
  const done = picks.filter(x => x !== null).length;
  h += '<div class="score" id="score"></div>';
  h += `<button class="btn" id="check" ${done < D.items.length ? 'disabled' : ''}>Check (${done}/${D.items.length} sorted)</button><button class="btn ghost" id="reset">Start again</button>`;
  app.innerHTML = h;
  if (checked) { const r = D.items.filter((it, i) => picks[i] === it.side).length; document.getElementById('score').textContent = `Score: ${r} / ${D.items.length}` + (r === D.items.length ? '  🎉 Perfect!' : ''); }
  app.querySelectorAll('.pill').forEach(b => b.onclick = () => { picks[+b.dataset.i] = +b.dataset.s; checked = false; render(); });
  document.getElementById('check').onclick = () => { checked = true; render(); };
  document.getElementById('reset').onclick = () => { picks = D.items.map(() => null); checked = false; render(); };
}
render();
"""

TIMER_PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<link href="https://fonts.googleapis.com/css2?family=Lato:wght@700;900&display=swap" rel="stylesheet">
<style>body{margin:0;font-family:Lato,sans-serif;background:transparent}
.t{background:#002F6C;color:#fff;border-radius:10px;padding:10px 14px;text-align:center}
.t .l{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:#83E3DE;font-weight:700}
.t .v{font-size:28px;font-weight:900;letter-spacing:.02em}
.t.warn{background:#FF801D}.t.over{background:#b91c1c}</style></head><body>
<div class="t" id="t"><div class="l" id="l"></div><div class="v" id="v"></div></div>
<script>
const START = __START__, END = __END__;
function fmt(s){ s = Math.max(0, Math.floor(s)); const h = Math.floor(s/3600), m = Math.floor(s%3600/60), x = s%60;
  return (h ? h + ':' + String(m).padStart(2,'0') : m) + ':' + String(x).padStart(2,'0'); }
function tick(){
  const now = Date.now(); const box = document.getElementById('t');
  if (END) {
    const left = (END - now) / 1000;
    document.getElementById('l').textContent = left > 0 ? 'Time remaining' : "Time's up";
    document.getElementById('v').textContent = left > 0 ? fmt(left) : '+' + fmt(-left);
    box.className = 't' + (left <= 0 ? ' over' : left < 600 ? ' warn' : '');
  } else {
    document.getElementById('l').textContent = 'Time so far';
    document.getElementById('v').textContent = fmt((now - START) / 1000);
  }
}
tick(); setInterval(tick, 1000);
</script></body></html>
"""

def render_timer(start_ms, end_ms):
    page = TIMER_PAGE.replace("__START__", str(int(start_ms))).replace("__END__", str(int(end_ms) if end_ms else 0))
    embed_html(page, 86)


# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <h1>IGCSE Economics</h1>
        <div class="subtitle">Past Paper Examiner Tool &nbsp;·&nbsp; Paper 2</div>
    </div>
    <div class="header-badge">SISB Nonthaburi</div>
</div>
""", unsafe_allow_html=True)

MODES = ["📋 Paper", "🏷️ Topic", "✍️ Technique", "📝 Practice"]
with st.sidebar:
    st.markdown("#### 🗂️ Mode")
    mode = st.radio("Mode", MODES, label_visibility="collapsed", key="mode")
    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# PAPER MODE
# ══════════════════════════════════════════════════════════════════════════════
def paper_mode():
    with st.sidebar:
        st.markdown("#### 📋 Select Paper")
        years = sorted(df["Year"].dropna().unique(), reverse=True)
        year = st.selectbox("Year", years)
        fy = df[df["Year"] == year]
        month = st.selectbox("Month", sorted(fy["Month"].dropna().unique(), key=month_key))
        fm = fy[fy["Month"] == month]
        paper = st.selectbox("Paper / Variant", sorted(fm["Paper"].dropna().unique()))
        st.markdown("#### ❓ Select Question")
        fp = fm[fm["Paper"] == paper]
        question_num = st.selectbox("Question Number", sorted(fp["Question"].dropna().unique()))
        st.markdown("---")
        st.markdown("#### ⚙️ Options")
        student_mode = st.toggle("🎓 Student Mode", value=False, help="Hides markschemes for self-testing")
        keyword = st.text_input("🔍 Search question text", placeholder="e.g. elasticity, GDP…")

    parts = fp[fp["Question"] == question_num].copy()
    parts["_sort_key"] = parts["Part"].apply(part_sort_key)
    parts = parts.sort_values("_sort_key")
    table_all = parts[~parts["is_stim"]]
    if keyword:
        kw = table_all[table_all["Question Text"].str.contains(keyword, case=False, na=False)]
        table = kw if not kw.empty else table_all
    else:
        table = table_all

    if parts.empty:
        st.warning("No data found for the selected filters.")
        return

    st.markdown(f'<div class="paper-label">Question {question_num} &nbsp;·&nbsp; {month} {year} &nbsp;·&nbsp; Variant {paper}</div>',
                unsafe_allow_html=True)
    st.markdown(f'<div class="marks-pill">📋 Total marks: {int(table["marks_int"].sum())}</div>', unsafe_allow_html=True)

    topics_in_q = sorted({t for col in ["Topic 1", "Topic 2"] for t in table[col] if t})
    if topics_in_q:
        badges = " ".join(f'<span class="topic-badge">{html.escape(t)}</span> {freq_badge(topic_counts.get(t, 0))}' for t in topics_in_q)
        st.markdown(f'<div style="margin-bottom:1rem">{badges}</div>', unsafe_allow_html=True)

    stim = find_stimulus(year, month, paper, question_num)
    if stim:
        st.markdown(stimulus_card(stim), unsafe_allow_html=True)

    render_question_rows(table, student_mode)

    with st.sidebar:
        st.markdown("#### 📥 Export")
        st.download_button("📥 Download as CSV",
                           table.drop(columns=["_sort_key", "is_stim", "marks_int"], errors="ignore").to_csv(index=False).encode("utf-8"),
                           file_name=f"Econ_{year}_{month}_Q{question_num}.csv", mime="text/csv")
        st.caption("💡 Ctrl+P → Save as PDF. The sidebar hides automatically.")


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC MODE
# ══════════════════════════════════════════════════════════════════════════════
def topic_mode():
    with st.sidebar:
        st.markdown("#### 🏷️ Select Topic")
        labels = [f"{t}  —  {freq_label(topic_counts.get(t, 0))}" for t in all_topics]
        idx = st.selectbox("Topic", range(len(all_topics)), format_func=lambda i: labels[i])
        selected_topic = all_topics[idx]
        st.markdown("#### 📅 Filter by Year (optional)")
        year_filter = st.selectbox("Year", ["All years"] + [str(y) for y in sorted(df["Year"].dropna().unique(), reverse=True)])
        st.markdown("---")
        st.markdown("#### ⚙️ Options")
        student_mode = st.toggle("🎓 Student Mode", value=False, help="Hides markschemes for self-testing")

    rows = df[((df["Topic 1"] == selected_topic) | (df["Topic 2"] == selected_topic)) & ~df["is_stim"]].copy()
    if year_filter != "All years":
        rows = rows[rows["Year"] == int(year_filter)]
    count = topic_counts.get(selected_topic, 0)

    st.markdown(f'<div class="topic-label">🏷️ {html.escape(selected_topic)} &nbsp; {freq_badge(count)}</div>', unsafe_allow_html=True)
    if count >= 40:
        msg = f"This topic has appeared in <strong>{count} questions</strong> across past papers. It comes up constantly and should be at the top of your revision list."
    elif count >= 15:
        msg = f"This topic has appeared in <strong>{count} questions</strong> across past papers. It comes up regularly and is well worth revising thoroughly."
    else:
        msg = f"This topic has appeared in <strong>{count} questions</strong> across past papers. It is part of the full syllabus, and understanding it will strengthen your overall performance."
    st.markdown(f'<div class="freq-info">📊 {msg}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="count-pill">📊 {len(rows)} question{"s" if len(rows) != 1 else ""} shown</div>', unsafe_allow_html=True)

    if rows.empty:
        st.info("No questions found for this topic and year combination.")
        return

    rows["_m"] = rows["Month"].apply(month_key)
    rows = rows.sort_values(["Year", "_m", "Paper", "Question"], ascending=[False, True, True, True])
    for year_val, year_group in rows.groupby("Year", sort=False):
        st.markdown(f'<div class="year-group-header">{int(year_val)}</div>', unsafe_allow_html=True)
        for (month_val, paper_val, q_val), q_group in year_group.groupby(["Month", "Paper", "Question"], sort=False):
            t1, t2 = safe_str(q_group.iloc[0]["Topic 1"]), safe_str(q_group.iloc[0]["Topic 2"])
            badges = "".join(f'<span class="topic-badge">{html.escape(t)}</span>' for t in [t1, t2] if t)
            st.markdown(f'<div class="topic-q-context">{month_val} &nbsp;·&nbsp; Variant {paper_val} &nbsp;·&nbsp; Q{int(q_val)}</div>{badges}',
                        unsafe_allow_html=True)
            stim = find_stimulus(year_val, month_val, paper_val, q_val)
            if stim:
                with st.expander("📄 View stimulus for this question"):
                    st.markdown(stimulus_card(stim, "Stimulus / Scenario"), unsafe_allow_html=True)
            q_group = q_group.copy()
            q_group["_sort_key"] = q_group["Part"].apply(part_sort_key)
            render_question_rows(q_group.sort_values("_sort_key"), student_mode)

    with st.sidebar:
        st.markdown("#### 📥 Export")
        fname = selected_topic.replace(" ", "_").replace("/", "-").replace("&", "and")[:40]
        st.download_button("📥 Download topic as CSV",
                           rows.drop(columns=["_m", "is_stim", "marks_int"], errors="ignore").to_csv(index=False).encode("utf-8"),
                           file_name=f"Econ_topic_{fname}.csv", mime="text/csv")
        st.caption("💡 Ctrl+P → Save as PDF. The sidebar hides automatically.")


# ══════════════════════════════════════════════════════════════════════════════
# TECHNIQUE MODE
# ══════════════════════════════════════════════════════════════════════════════
ACTIVITIES = ["👀 See it", "🎯 Spot it", "🔗 Build the chain", "⚖️ Sort the sides", "✏️ Write it"]

def technique_mode():
    if not model_answers:
        st.warning(f"No model answers found. Add **{MODEL_ANSWERS_NAME}** to the same folder as app.py.")
        return

    type_keys = [k for k in TYPE_INFO if any(m["type"] == k for m in model_answers)]
    with st.sidebar:
        st.markdown("#### ✍️ Question type")
        qtype = st.radio("Question type", type_keys, format_func=lambda k: TYPE_INFO[k]["label"],
                         label_visibility="collapsed", key="tq_type")
        options = [m for m in model_answers if m["type"] == qtype]
        options.sort(key=lambda m: (-m["year"], month_key(m["month"])))

        def opt_label(i):
            m = options[i]
            row = find_row(m["year"], m["month"], m["paper"], m["question"], m["part"])
            q = safe_str(row["Question Text"]) if row is not None else ""
            q = re.sub(r"^(Analyse|Discuss)( whether or not| whether)?\s*", "", q).rstrip(".")
            q = q[0].upper() + q[1:] if q else q
            return (q[:62] + "…") if len(q) > 63 else q

        st.markdown("#### ❓ Question")
        qi = st.selectbox("Question", range(len(options)), format_func=opt_label, key=f"tq_q_{qtype}",
                          label_visibility="collapsed")
        st.markdown("#### 🧩 Activity")
        acts = [a for a in ACTIVITIES if not (a.startswith("⚖️") and qtype == "analyse6")]
        activity = st.radio("Activity", acts, label_visibility="collapsed", key=f"tq_act_{qtype}")
        st.caption("Work down the list: see a good answer, take it apart, then write your own.")

    m = options[qi]
    info = TYPE_INFO[qtype]
    row = find_row(m["year"], m["month"], m["paper"], m["question"], m["part"])
    if row is None:
        st.error("This model answer doesn't match a question in the CSV.")
        return
    qkey = f'{m["year"]}_{m["month"]}_{m["paper"]}_{m["question"]}{m["part"]}'
    marks = row["marks_int"]

    st.markdown(f'<div class="topic-label">✍️ Exam technique &nbsp;·&nbsp; {info["label"]}</div>', unsafe_allow_html=True)

    with st.expander(f"🧭 How to answer {'an' if info['label'].startswith('8') else 'a'} {info['label']} question", expanded=(activity == ACTIVITIES[0])):
        st.markdown(info["tip"])
        st.markdown(f"**Time:** about **{info['minutes']} minutes** (1½ minutes per mark).")
        st.markdown("**Structure:**")
        st.markdown("".join(f'<div class="guide-row"><b>{html.escape(a)}</b><span>{html.escape(b)}</span></div>' for a, b in info["structure"]),
                    unsafe_allow_html=True)
        st.markdown("**The colours:**")
        st.markdown("".join(f'<div class="guide-row">{chip_html(c)}<span>{html.escape(TAGS[c]["hint"])}</span></div>' for c in info["tags"]),
                    unsafe_allow_html=True)
        if info["levels"]:
            st.markdown("**How it's marked (levels from the markscheme):**")
            for lvl, rng, desc in info["levels"]:
                st.markdown(f"- **{lvl} ({rng})**: {desc}")

    topics = " ".join(f'<span class="topic-badge">{html.escape(t)}</span>' for t in [row["Topic 1"], row["Topic 2"]] if t)
    st.markdown(f'<div class="q-card"><div class="q-meta">{m["month"]} {m["year"]} · Variant {m["paper"]} · Question {m["question"]}({m["part"]})</div>'
                f'<div class="q-main">{esc(row["Question Text"])} <span class="marks-badge {marks_class(marks)}">{marks}</span></div>'
                f'<div style="margin-top:8px">{topics}</div></div>', unsafe_allow_html=True)
    stim = find_stimulus(m["year"], m["month"], m["paper"], m["question"])
    if stim:
        with st.expander("📄 Stimulus summary for this question"):
            st.markdown(stimulus_card(stim, "Stimulus / Scenario"), unsafe_allow_html=True)

    # ── See it ──
    if activity == ACTIVITIES[0]:
        st.markdown("#### 👀 A colour-coded model answer")
        st.markdown(legend_html(info["tags"]), unsafe_allow_html=True)
        st.markdown(model_answer_html(m), unsafe_allow_html=True)
        st.caption("Notice the pattern: every point is followed by a chain of explanation, never left on its own.")
        with st.expander("📋 Compare with the official markscheme"):
            st.markdown(markscheme_html(row["Markscheme"], row["Explanation"]), unsafe_allow_html=True)

    # ── Spot it ──
    elif activity == ACTIVITIES[1]:
        st.markdown("#### 🎯 Spot it: what job does each sentence do?")
        st.markdown(legend_html(info["tags"]), unsafe_allow_html=True)
        paras = [p["sentences"] for p in m["model"]]
        n = sum(len(p) for p in paras)
        render_component(SPOT_SCRIPT, {"paras": paras, "tags": info["tags"]}, height=min(2400, 170 + n * 84 + len(paras) * 12))

    # ── Build the chain ──
    elif activity == ACTIVITIES[2]:
        st.markdown("#### 🔗 Build the chain")
        st.markdown("Good answers move one step at a time. Put each chain of reasoning back in order.")
        side_names = {"for": "For", "against": "Against", "conclusion": "Conclusion"}
        chains = [{"side": side_names.get(p.get("side"), ""), "sentences": p["sentences"]}
                  for p in m["model"] if len(p["sentences"]) >= 3]
        if not chains:
            chains = [{"side": "", "sentences": [s for p in m["model"] for s in p["sentences"]][:6]}]
        longest = max(len(c["sentences"]) for c in chains)
        seed = sum(ord(c) for c in qkey)
        render_component(BUILD_SCRIPT, {"chains": chains, "seed": seed}, height=300 + longest * 64)

    # ── Sort the sides ──
    elif activity == ACTIVITIES[3]:
        st.markdown("#### ⚖️ Sort the sides")
        pool = df[(~df["is_stim"]) & (df["marks_int"] == marks) &
                  df["Question Text"].str.strip().str.lower().str.startswith("discuss")].copy()
        pool["sides"] = pool["Markscheme"].apply(parse_sides)
        pool = pool[pool["sides"].notna()]
        pool["_m"] = pool["Month"].apply(month_key)
        pool = pool.sort_values(["Year", "_m", "Paper", "Question"], ascending=[False, True, True, True])
        keys = [f'{r.Year}|{r.Month}|{r.Paper}|{r.Question}|{r.Part}' for r in pool.itertuples()]
        if not keys:
            st.info("No questions of this type have a markscheme that can be sorted automatically.")
            return
        this = f'{m["year"]}|{m["month"]}|{m["paper"]}|{m["question"]}|{m["part"]}'
        default = keys.index(this) if this in keys else 0
        labels = {k: f'{mo[:3]} {yr} · {safe_str(qt)[:70]}'
                  for k, mo, yr, qt in zip(keys, pool["Month"], pool["Year"], pool["Question Text"])}
        st.caption(f"This works on any of the {len(keys)} {info['label']} questions in the bank, not just the model answers.")
        pick = st.selectbox("Question to sort", keys, index=default, format_func=lambda k: labels[k], key=f"sort_q_{qtype}")
        prow = pool.iloc[keys.index(pick)]
        side_labels, a, b = prow["sides"]
        if pick != this:
            st.markdown(f'<div class="q-card"><div class="q-main">{esc(prow["Question Text"])}</div></div>', unsafe_allow_html=True)
        items = [{"text": t, "side": 0} for t in a] + [{"text": t, "side": 1} for t in b]
        random.Random(pick).shuffle(items)
        render_component(SORT_SCRIPT, {"items": items, "labels": side_labels}, height=min(2600, 160 + len(items) * 86))
        st.caption("Next step: pick the two strongest points from each side and turn them into chains in ✏️ Write it.")

    # ── Write it ──
    else:
        st.markdown("#### ✏️ Write it")
        st.markdown("Build your answer one block at a time. The colours show what each block needs.")
        store = st.session_state.setdefault("wi_answers", {}).setdefault(qkey, {})
        with st.expander("💬 Sentence starters"):
            for c in info["tags"]:
                st.markdown(f'{chip_html(c)} &nbsp; ' + " · ".join(f"<i>{html.escape(s)}</i>" for s in STARTERS[c]), unsafe_allow_html=True)
        for bi, (title, codes) in enumerate(info["frame"]):
            st.markdown(f'<div class="frame-head">{html.escape(title)} {" ".join(chip_html(c, TAGS[c]["name"]) for c in codes)}</div>',
                        unsafe_allow_html=True)
            wkey = f"wi_{qkey}_{bi}"
            if wkey not in st.session_state:
                st.session_state[wkey] = store.get(bi, "")
            st.text_area(title, key=wkey, height=110, label_visibility="collapsed",
                         placeholder=" → ".join(STARTERS[c][0] for c in codes))
            store[bi] = st.session_state[wkey]

        words = sum(len(v.split()) for v in store.values())
        st.caption(f"{words} words so far")
        reveal_key = f"wi_reveal_{qkey}"
        if st.button("🔍 Compare with the model answer", type="primary"):
            st.session_state[reveal_key] = True
        if st.session_state.get(reveal_key):
            c1, c2 = st.columns(2)
            with c1:
                st.markdown("##### Your answer")
                for bi, (title, codes) in enumerate(info["frame"]):
                    col = TAGS[codes[0]]
                    text = store.get(bi, "").strip()
                    body = esc(text) if text else '<span class="empty-answer">(empty)</span>'
                    st.markdown(f'<div class="student-answer" style="border-left:5px solid {col["color"]};margin-bottom:8px">'
                                f'<b style="color:{col["ink"]}">{html.escape(title)}</b><br>{body}</div>', unsafe_allow_html=True)
            with c2:
                st.markdown("##### Model answer")
                st.markdown(model_answer_html(m), unsafe_allow_html=True)
            st.markdown("##### ✅ Check your own answer")
            ticked = checklist_widget(qtype, f"wi_{qkey}")
            if ticked == len(info["checklist"]):
                st.success("Every box ticked. That's the shape of a strong answer.")
            with st.expander("📋 Official markscheme"):
                st.markdown(markscheme_html(row["Markscheme"], row["Explanation"]), unsafe_allow_html=True)
            full = "\n\n".join(f"{t}:\n{store.get(i, '')}" for i, (t, _) in enumerate(info["frame"]))
            st.download_button("📥 Download my answer", f"{row['Question Text']}\n\n{full}\n\n--- Model answer ---\n{model_answer_text(m)}",
                               file_name=f"My_answer_{qkey}.txt")


# ══════════════════════════════════════════════════════════════════════════════
# PRACTICE MODE
# ══════════════════════════════════════════════════════════════════════════════
def new_attempt():
    return {"phase": "setup", "answers": {}, "marks": {}, "sent": False}

def pp_state():
    if "pp" not in st.session_state:
        st.session_state.pp = new_attempt()
    return st.session_state.pp

def reset_attempt():
    for k in list(st.session_state.keys()):
        if k.startswith(("ppw_", "ppm_", "ppc_")):
            del st.session_state[k]
    st.session_state.pp = new_attempt()

def attempt_parts(pp):
    """All question rows in this attempt, in exam order."""
    y, mth, p = pp["year"], pp["month"], pp["paper"]
    rows = df[(df["Year"] == y) & (df["Month"] == mth) & (df["Paper"] == p) &
              (df["Question"].isin(pp["questions"])) & ~df["is_stim"]].copy()
    rows["_sort_key"] = rows["Part"].apply(part_sort_key)
    return rows.sort_values(["Question", "_sort_key"])

def part_key(r):
    return f'{int(r["Question"])}{r["Part"]}'

def type_bucket(r):
    t = question_type(r["Question Text"], r["marks_int"])
    return TYPE_INFO[t]["label"] if t else "Short answers (1–5 marks)"

def send_to_sheet(pp, rows, name, cls):
    sa = secrets_get("gcp_service_account")
    sheet_id = secrets_get("results_sheet_id")
    if not sa or not sheet_id:
        return False, "Sending results hasn't been set up yet."
    try:
        import gspread
        gc = gspread.service_account_from_dict(dict(sa))
        sh = gc.open_by_key(sheet_id)

        def ws(title, header):
            try:
                w = sh.worksheet(title)
            except gspread.WorksheetNotFound:
                w = sh.add_worksheet(title=title, rows=1000, cols=len(header))
                w.append_row(header)
            return w

        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        paper = f'{pp["month"]} {pp["year"]} Variant {pp["paper"]}'
        qs = ", ".join(f"Q{q}" for q in pp["questions"])
        score = sum(pp["marks"].get(part_key(r), 0) for _, r in rows.iterrows())
        total = int(rows["marks_int"].sum())
        minutes = round((pp["finished_at"] - pp["start_ms"]) / 60000)
        buckets = {}
        for _, r in rows.iterrows():
            b = buckets.setdefault(type_bucket(r), [0, 0])
            b[0] += pp["marks"].get(part_key(r), 0)
            b[1] += r["marks_int"]
        breakdown = "; ".join(f"{k}: {v[0]}/{v[1]}" for k, v in buckets.items())
        ws("Results", ["Timestamp", "Name", "Class", "Paper", "Questions", "Score", "Out of", "Percent", "Minutes", "Breakdown"]).append_row(
            [stamp, name, cls, paper, qs, score, total, round(100 * score / total) if total else 0, minutes, breakdown])
        ws("Answers", ["Timestamp", "Name", "Class", "Paper", "Part", "Marks available", "Self mark", "Question", "Answer"]).append_rows(
            [[stamp, name, cls, paper, part_key(r), int(r["marks_int"]), pp["marks"].get(part_key(r), 0),
              safe_str(r["Question Text"]), pp["answers"].get(part_key(r), "")[:45000]] for _, r in rows.iterrows()])
        return True, "Sent to your teacher."
    except Exception as e:
        return False, f"Couldn't send your results ({type(e).__name__}). Download them instead and show your teacher."

def practice_mode():
    pp = pp_state()

    # ── Setup ──
    if pp["phase"] == "setup":
        with st.sidebar:
            st.markdown("#### 📝 What to practise")
            kind = st.radio("Practice", ["Full paper", "Single question"], label_visibility="collapsed", key="pp_kind")
            years = sorted(df["Year"].dropna().unique(), reverse=True)
            year = st.selectbox("Year", years, key="pp_year")
            fy = df[df["Year"] == year]
            month = st.selectbox("Month", sorted(fy["Month"].dropna().unique(), key=month_key), key="pp_month")
            paper = st.selectbox("Paper / Variant", sorted(fy[fy["Month"] == month]["Paper"].dropna().unique()), key="pp_paper")
            fp = fy[(fy["Month"] == month) & (fy["Paper"] == paper)]
            if kind == "Single question":
                single_q = st.selectbox("Question", sorted(fp["Question"].dropna().unique()), key="pp_single")

        st.markdown(f'<div class="paper-label">📝 Practice &nbsp;·&nbsp; {month} {year} &nbsp;·&nbsp; Variant {paper}</div>', unsafe_allow_html=True)

        def q_summary(q):
            qr = fp[(fp["Question"] == q) & ~fp["is_stim"]]
            ts = sorted({t for c in ["Topic 1", "Topic 2"] for t in qr[c] if t})
            return ", ".join(t.split(" ", 1)[1] for t in ts[:3])

        if kind == "Full paper":
            st.markdown("""
**How this paper works**
- **Section A:** Question 1 is compulsory (30 marks).
- **Section B:** choose **three** of Questions 2–5 (20 marks each).
- **90 marks** in **2 hours 15 minutes**, about 1½ minutes per mark.
""")
            section_b = sorted(q for q in fp["Question"].dropna().unique() if q != 1)
            chosen = st.multiselect("Choose three Section B questions", section_b, max_selections=3,
                                    format_func=lambda q: f"Question {q}: {q_summary(q)}", key="pp_secb")
            questions = [1] + sorted(chosen)
            ready = len(chosen) == 3
            if not ready:
                st.caption("Tip: read all four questions first and pick the three where you can write the best 8-mark answer.")
            timed_default = 135
        else:
            questions = [single_q]
            total_q = int(fp[(fp["Question"] == single_q)]["marks_int"].sum())
            st.markdown(f"**Question {single_q}** ({total_q} marks): {q_summary(single_q)}")
            ready = True
            timed_default = minutes_for(total_q)

        c1, c2 = st.columns(2)
        timed = c1.toggle(f"⏱️ Timed ({timed_default} minutes)", value=True, key="pp_timed")
        frames = c2.toggle("🎨 Show writing frames on 6 and 8 mark questions", value=False, key="pp_frames")
        st.caption("Your answers stay in this browser tab only. Don't refresh the page or close the tab until you've finished.")
        if st.button("▶️ Start", type="primary", disabled=not ready):
            now = time.time() * 1000
            pp.update({"phase": "writing", "kind": kind, "year": year, "month": month, "paper": paper,
                       "questions": questions, "frames": frames, "start_ms": now,
                       "end_ms": now + timed_default * 60000 if timed else 0})
            st.rerun()
        return

    rows = attempt_parts(pp)
    total = int(rows["marks_int"].sum())

    with st.sidebar:
        st.markdown(f"**{pp['month']} {pp['year']} · Variant {pp['paper']}**")
        st.caption(", ".join(f"Question {q}" for q in pp["questions"]))
        if pp["phase"] == "writing":
            render_timer(pp["start_ms"], pp["end_ms"])
            written = sum(1 for _, r in rows.iterrows() if pp["answers"].get(part_key(r), "").strip())
            st.progress(written / len(rows), text=f"{written} of {len(rows)} parts answered")
        elif pp["phase"] == "marking":
            so_far = sum(pp["marks"].get(part_key(r), 0) for _, r in rows.iterrows())
            st.metric("Marks so far", f"{so_far} / {total}")
        st.markdown("---")
        confirm = st.checkbox("I want to start a new attempt", key="pp_confirm_new")
        if st.button("🔄 New attempt", disabled=not confirm):
            reset_attempt()
            st.rerun()

    # ── Writing ──
    if pp["phase"] == "writing":
        st.markdown(f'<div class="paper-label">📝 Writing &nbsp;·&nbsp; {pp["month"]} {pp["year"]} &nbsp;·&nbsp; Variant {pp["paper"]} &nbsp;·&nbsp; {total} marks</div>',
                    unsafe_allow_html=True)
        if pp["end_ms"] and time.time() * 1000 > pp["end_ms"]:
            st.warning("⏰ Time is up. Finish your sentence, then submit.")
        for q, q_rows in rows.groupby("Question", sort=False):
            st.markdown(f'<div class="year-group-header">Question {int(q)} &nbsp;<span style="font-size:0.85rem;color:#008BCC">({int(q_rows["marks_int"].sum())} marks)</span></div>',
                        unsafe_allow_html=True)
            stim = find_stimulus(pp["year"], pp["month"], pp["paper"], q)
            if stim:
                st.markdown(stimulus_card(stim, "📄 Source summary"), unsafe_allow_html=True)
            if int(q) == 1:
                st.warning("📰 This is only a summary. Question 1 uses data and details from the full source, "
                           "so have the printed paper or insert in front of you.")
            for _, r in q_rows.iterrows():
                pk, mk = part_key(r), r["marks_int"]
                qt = question_type(r["Question Text"], mk)
                st.markdown(f'<div style="display:flex;gap:12px;align-items:flex-start;margin-top:0.8rem">'
                            f'<div class="part-badge">({html.escape(r["Part"])})</div>'
                            f'<div style="flex:1"><div class="q-text">{esc(r["Question Text"])} '
                            f'<span class="marks-badge {marks_class(mk)}">{mk}</span></div>'
                            f'<div class="time-guide">⏱ about {minutes_for(mk)} min</div></div></div>', unsafe_allow_html=True)
                if "diagram" in safe_str(r["Question Text"]).lower():
                    st.caption("✏️ Draw the diagram on paper, then describe what it shows in the box.")
                if pp["frames"] and qt:
                    st.markdown('<div style="margin:4px 0 2px 48px">' + " ".join(
                        f'<span style="font-size:0.78rem;font-weight:700;color:#475569">{html.escape(t)}:</span> ' +
                        " ".join(chip_html(c, TAGS[c]["name"]) for c in codes) for t, codes in TYPE_INFO[qt]["frame"][:2]) +
                        ("" if qt == "analyse6" else " …") + '</div>', unsafe_allow_html=True)
                wkey = f"ppw_{pk}"
                if wkey not in st.session_state:
                    st.session_state[wkey] = pp["answers"].get(pk, "")
                height = {1: 70, 2: 90, 4: 150, 5: 170, 6: 240, 8: 300}.get(mk, 120)
                st.text_area(f"Answer {pk}", key=wkey, height=height, label_visibility="collapsed")
                pp["answers"][pk] = st.session_state[wkey]
        st.markdown("---")
        empty = sum(1 for _, r in rows.iterrows() if not pp["answers"].get(part_key(r), "").strip())
        if empty:
            st.caption(f"{empty} part{'s' if empty != 1 else ''} still empty.")
        if st.button("✅ I've finished: show me the markschemes", type="primary"):
            pp["phase"] = "marking"
            pp["finished_at"] = time.time() * 1000
            st.rerun()
        return

    # ── Marking ──
    if pp["phase"] == "marking":
        st.markdown('<div class="paper-label">✅ Mark your own answers</div>', unsafe_allow_html=True)
        st.info("Compare each answer with the markscheme and be strict. Only give a mark if your answer really makes that point. "
                "For 6 and 8 mark questions, use the checklist to help.")
        for q, q_rows in rows.groupby("Question", sort=False):
            st.markdown(f'<div class="year-group-header">Question {int(q)}</div>', unsafe_allow_html=True)
            for _, r in q_rows.iterrows():
                pk, mk = part_key(r), r["marks_int"]
                qt = question_type(r["Question Text"], mk)
                st.markdown(f'<div class="q-text" style="margin-top:0.6rem"><b>({html.escape(r["Part"])})</b> {esc(r["Question Text"])} '
                            f'<span class="marks-badge {marks_class(mk)}">{mk}</span></div>', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                ans = pp["answers"].get(pk, "").strip()
                c1.markdown("**Your answer**")
                c1.markdown(f'<div class="student-answer">{esc(ans) if ans else "<span class=empty-answer>(no answer)</span>"}</div>',
                            unsafe_allow_html=True)
                c2.markdown("**Markscheme**")
                c2.markdown(markscheme_html(r["Markscheme"], r["Explanation"]), unsafe_allow_html=True)
                if qt:
                    with st.expander(f"✅ {TYPE_INFO[qt]['label']} checklist"):
                        checklist_widget(qt, f"ppc_{pk}")
                    mdl = model_for(pp["year"], pp["month"], pp["paper"], int(q), r["Part"])
                    if mdl:
                        with st.expander("🎨 See a colour-coded model answer"):
                            st.markdown(legend_html(TYPE_INFO[qt]["tags"]), unsafe_allow_html=True)
                            st.markdown(model_answer_html(mdl), unsafe_allow_html=True)
                mkey = f"ppm_{pk}"
                if mkey not in st.session_state:
                    st.session_state[mkey] = pp["marks"].get(pk, 0)
                st.number_input(f"Your mark for ({r['Part']}) out of {mk}", min_value=0, max_value=int(mk), step=1, key=mkey)
                pp["marks"][pk] = int(st.session_state[mkey])
                st.markdown('<hr class="row-divider">', unsafe_allow_html=True)
        if st.button("🏁 Finish marking: show my results", type="primary"):
            pp["phase"] = "done"
            st.rerun()
        return

    # ── Results ──
    score = sum(pp["marks"].get(part_key(r), 0) for _, r in rows.iterrows())
    pct = round(100 * score / total) if total else 0
    minutes = round((pp["finished_at"] - pp["start_ms"]) / 60000)
    st.markdown('<div class="paper-label">🏁 Your results</div>', unsafe_allow_html=True)
    c1, c2 = st.columns([1, 2])
    with c1:
        st.markdown(f'<div class="score-big">{score}/{total}</div><div class="score-sub">{pct}% · {minutes} minutes</div>',
                    unsafe_allow_html=True)
    buckets = {}
    for _, r in rows.iterrows():
        b = buckets.setdefault(type_bucket(r), [0, 0])
        b[0] += pp["marks"].get(part_key(r), 0)
        b[1] += r["marks_int"]
    with c2:
        st.markdown("".join(f'<div class="result-row"><span>{html.escape(k)}</span><b>{v[0]} / {v[1]} '
                            f'({round(100 * v[0] / v[1]) if v[1] else 0}%)</b></div>' for k, v in buckets.items()),
                    unsafe_allow_html=True)
    long_types = {k: v for k, v in buckets.items() if k != "Short answers (1–5 marks)" and v[1]}
    if long_types:
        weakest = min(long_types, key=lambda k: long_types[k][0] / long_types[k][1])
        if long_types[weakest][0] / long_types[weakest][1] < 0.7:
            st.info(f"💡 Your best next step: practise **{weakest}** questions in ✍️ Technique mode.")
        else:
            st.success("Strong work on the longer questions. Keep practising full papers to build speed.")
    if pp["end_ms"] and pp["finished_at"] > pp["end_ms"]:
        st.caption(f"You went over the time limit by {round((pp['finished_at'] - pp['end_ms']) / 60000)} minutes. In the real exam, time management matters as much as content.")

    lines = [f"IGCSE Economics Paper 2 practice: {pp['month']} {pp['year']} Variant {pp['paper']}",
             f"Score: {score}/{total} ({pct}%) in {minutes} minutes", ""]
    for _, r in rows.iterrows():
        pk = part_key(r)
        lines += [f"Q{pk} [{pp['marks'].get(pk, 0)}/{r['marks_int']}] {safe_str(r['Question Text'])}",
                  pp["answers"].get(pk, "").strip() or "(no answer)", ""]
    st.download_button("📥 Download my answers and marks", "\n".join(lines),
                       file_name=f"Practice_{pp['year']}_{pp['month']}_{pp['paper']}.txt")

    st.markdown("#### 📤 Send to your teacher (optional)")
    if secrets_get("gcp_service_account") and secrets_get("results_sheet_id"):
        if pp["sent"]:
            st.success("✅ Already sent to your teacher.")
        else:
            c1, c2 = st.columns(2)
            name = c1.text_input("Your name", key="pp_name")
            cls = c2.text_input("Your class", key="pp_class", placeholder="e.g. G10")
            if st.button("📤 Send my results", disabled=not (name.strip() and cls.strip())):
                ok, msg = send_to_sheet(pp, rows, name.strip(), cls.strip())
                if ok:
                    pp["sent"] = True
                    st.success("✅ " + msg)
                else:
                    st.error(msg)
            st.caption("Your teacher sees your score, your marks for each part, and your answers.")
    else:
        st.caption("Sending results to your teacher isn't switched on yet. Download your answers instead if your teacher asks for them.")


# ── Dispatch ──────────────────────────────────────────────────────────────────
if mode == MODES[0]:
    paper_mode()
elif mode == MODES[1]:
    topic_mode()
elif mode == MODES[2]:
    technique_mode()
else:
    practice_mode()

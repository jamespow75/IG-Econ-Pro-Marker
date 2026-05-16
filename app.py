import streamlit as st
import pandas as pd
from pathlib import Path
import html

st.set_page_config(layout="wide", page_title="SISB Economics · Past Paper Tool")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lato:wght@300;400;700;900&display=swap');

html, body, [class*="css"] { font-family: 'Lato', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

/* ── Header ── */
.app-header {
    background: #002F6C;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.app-header h1 {
    font-family: 'Lato', sans-serif;
    font-weight: 900;
    color: #ffffff;
    font-size: 1.7rem;
    margin: 0;
    letter-spacing: -0.01em;
}
.app-header .subtitle { color: #83E3DE; font-size: 0.85rem; margin-top: 3px; font-weight: 400; }
.header-badge {
    background: #008BCC;
    color: #ffffff;
    font-size: 0.75rem;
    font-weight: 700;
    padding: 5px 14px;
    border-radius: 20px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
}

/* ── Paper label ── */
.paper-label {
    background: #e8f4fb;
    border-left: 4px solid #008BCC;
    color: #002F6C;
    padding: 10px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* ── Topic label ── */
.topic-label {
    background: #e0f7f6;
    border-left: 4px solid #83E3DE;
    color: #002F6C;
    padding: 10px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 1rem;
}

/* ── Pills ── */
.marks-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #002F6C; color: #fff; font-size: 0.85rem; font-weight: 700;
    padding: 6px 16px; border-radius: 20px; margin-bottom: 1.2rem;
}
.count-pill {
    display: inline-flex; align-items: center; gap: 6px;
    background: #008BCC; color: #fff; font-size: 0.85rem; font-weight: 700;
    padding: 6px 16px; border-radius: 20px; margin-bottom: 1.2rem;
}

/* ── Frequency badges ── */
.freq-essential {
    display: inline-flex; align-items: center; gap: 5px;
    background: #fff3cd; color: #7a4800; border: 1px solid #f0c040;
    font-size: 0.72rem; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em;
}
.freq-important {
    display: inline-flex; align-items: center; gap: 5px;
    background: #e0f0fb; color: #003f7a; border: 1px solid #008BCC;
    font-size: 0.72rem; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em;
}
.freq-worthknowing {
    display: inline-flex; align-items: center; gap: 5px;
    background: #e6f9f4; color: #1a5c4a; border: 1px solid #37C563;
    font-size: 0.72rem; font-weight: 700; padding: 3px 10px;
    border-radius: 20px; text-transform: uppercase; letter-spacing: 0.06em;
}

/* ── Frequency info box ── */
.freq-info {
    background: #f0f7ff;
    border: 1px solid #c5dff5;
    border-radius: 10px;
    padding: 12px 16px;
    font-size: 0.82rem;
    color: #002F6C;
    margin-bottom: 1.2rem;
    line-height: 1.6;
}

/* ── Stimulus ── */
.stimulus-card {
    background: #fffdf5; border: 1px solid #e8d98a; border-left: 5px solid #FF801D;
    border-radius: 0 10px 10px 0; padding: 1.2rem 1.5rem; font-size: 0.93rem;
    line-height: 1.7; color: #3d3110; margin-bottom: 1.5rem;
}
.stimulus-label {
    font-size: 0.72rem; font-weight: 700; color: #FF801D;
    text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 8px;
}

/* ── Year group header ── */
.year-group-header {
    font-family: 'Lato', sans-serif; font-weight: 900;
    font-size: 1.1rem; color: #002F6C;
    border-bottom: 2px solid #008BCC;
    padding-bottom: 6px; margin: 1.8rem 0 1rem 0;
}
.topic-q-context {
    font-size: 0.78rem; font-weight: 700; color: #008BCC;
    text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 4px;
}
.topic-badge {
    display: inline-flex; align-items: center; padding: 2px 8px; border-radius: 4px;
    font-size: 0.72rem; font-weight: 700; background: #e0f0fb; color: #002F6C;
    margin-right: 4px; margin-bottom: 6px;
}

/* ── Table ── */
.section-rule { border: none; border-top: 1px solid #e2e8f0; margin: 0.6rem 0 1.4rem 0; }
.col-header {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.08em; color: #008BCC; padding-bottom: 6px;
    border-bottom: 2px solid #008BCC; margin-bottom: 0.8rem;
}
.part-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 36px; height: 36px; background: #002F6C; color: #fff;
    font-family: 'Lato', sans-serif; font-weight: 900;
    font-size: 1rem; border-radius: 8px;
}
.q-text { font-size: 0.95rem; line-height: 1.65; color: #1e293b; }
.marks-badge {
    display: inline-flex; align-items: center; justify-content: center;
    padding: 3px 10px; border-radius: 6px; font-size: 0.8rem;
    font-weight: 700; min-width: 38px;
}
.marks-1  { background: #dcfce7; color: #166534; }
.marks-2  { background: #fef9c3; color: #854d0e; }
.marks-3  { background: #ffedd5; color: #9a3412; }
.marks-4p { background: #fee2e2; color: #991b1b; }
.ms-card {
    background: #f8fafc; border: 1px solid #e2e8f0; border-left: 4px solid #008BCC;
    border-radius: 0 10px 10px 0; padding: 1rem 1.2rem; font-size: 0.88rem;
    line-height: 1.7; color: #1e293b;
}
.teacher-tip {
    margin-top: 10px; padding-top: 10px; border-top: 1px dashed #cbd5e1;
    font-size: 0.83rem; color: #475569;
}
.tip-label {
    font-size: 0.72rem; font-weight: 700; text-transform: uppercase;
    letter-spacing: 0.07em; color: #008BCC; margin-bottom: 4px;
}
.row-divider { border: none; border-top: 1px solid #f1f5f9; margin: 1rem 0; }

/* ── Sidebar ── */
[data-testid="stSidebar"] { background: #f0f7ff; border-right: 1px solid #c5dff5; }

@media print {
    section[data-testid='stSidebar'] { display: none !important; }
    .app-header { background: #002F6C !important; -webkit-print-color-adjust: exact; }
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────
def safe_str(val, default=""):
    return str(val) if pd.notnull(val) else default

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
    sub  = part[len(base):].strip("() ")
    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6}
    return (1, base, roman.get(sub.lower(), 0))

def freq_badge(count):
    if count >= 40:
        return '<span class="freq-essential">🔥 Essential</span>'
    elif count >= 15:
        return '<span class="freq-important">⭐ Important</span>'
    else:
        return '<span class="freq-worthknowing">📚 Worth Knowing</span>'

def freq_label(count):
    if count >= 40:
        return "🔥 Essential"
    elif count >= 15:
        return "⭐ Important"
    else:
        return "📚 Worth Knowing"

def render_question_rows(table_data, student_mode):
    st.markdown('<hr class="section-rule">', unsafe_allow_html=True)
    if student_mode:
        c1, c2, c3 = st.columns([1, 5, 1])
        c1.markdown('<div class="col-header">Part</div>', unsafe_allow_html=True)
        c2.markdown('<div class="col-header">Question</div>', unsafe_allow_html=True)
        c3.markdown('<div class="col-header">Marks</div>', unsafe_allow_html=True)
    else:
        c1, c2, c3, c4 = st.columns([1, 4, 1, 5])
        c1.markdown('<div class="col-header">Part</div>', unsafe_allow_html=True)
        c2.markdown('<div class="col-header">Question</div>', unsafe_allow_html=True)
        c3.markdown('<div class="col-header">Marks</div>', unsafe_allow_html=True)
        c4.markdown('<div class="col-header">Markscheme & Explanation</div>', unsafe_allow_html=True)

    for _, row in table_data.iterrows():
        part        = safe_str(row["Part"])
        q_text      = safe_str(row["Question Text"])
        marks       = safe_str(row["Marks"])
        ms          = safe_str(row["Markscheme"], "No markscheme available.")
        explanation = safe_str(row["Explanation"])
        ms_safe     = html.escape(ms).replace("\n", "<br>")
        expl_safe   = html.escape(explanation).replace("\n", "<br>")
        mclass      = marks_class(marks)

        if student_mode:
            col1, col2, col3 = st.columns([1, 5, 1])
            col1.markdown(f'<div class="part-badge">({part})</div>', unsafe_allow_html=True)
            col2.markdown(f'<div class="q-text">{html.escape(q_text)}</div>', unsafe_allow_html=True)
            col3.markdown(f'<div class="marks-badge {mclass}">{marks}</div>', unsafe_allow_html=True)
        else:
            col1, col2, col3, col4 = st.columns([1, 4, 1, 5])
            col1.markdown(f'<div class="part-badge">({part})</div>', unsafe_allow_html=True)
            col2.markdown(f'<div class="q-text">{html.escape(q_text)}</div>', unsafe_allow_html=True)
            col3.markdown(f'<div class="marks-badge {mclass}">{marks}</div>', unsafe_allow_html=True)
            tip_html = f'<div class="teacher-tip"><div class="tip-label">Teacher Tip</div>{expl_safe}</div>' if explanation else ""
            col4.markdown(f'<div class="ms-card">{ms_safe}{tip_html}</div>', unsafe_allow_html=True)

        st.markdown('<hr class="row-divider">', unsafe_allow_html=True)


# ── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "IGCSE Econ P2 Past Papers + MS - Sheet1.csv"
    if not file_path.exists():
        st.error(f"CSV file not found: {file_path}")
        st.stop()
    df = pd.read_csv(file_path)
    df.columns = df.columns.str.strip()
    required_columns = [
        "Year", "Month", "Paper", "Question", "Part",
        "Stimulus / Scenario", "Question Text", "Marks", "Markscheme", "Explanation"
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns in CSV: {missing}")
        st.stop()
    for col in ["Topic 1", "Topic 2"]:
        if col not in df.columns:
            df[col] = ""
    df["Topic 1"] = df["Topic 1"].fillna("")
    df["Topic 2"] = df["Topic 2"].fillna("")
    return df

df = load_data()

# ── Build topic frequency map ─────────────────────────────────────────────────
@st.cache_data
def build_topic_counts(df):
    counts = {}
    q_rows = df[df["Part"].astype(str).str.lower() != "stimulus"]
    for topic in set(list(df["Topic 1"].unique()) + list(df["Topic 2"].unique())) - {""}:
        n = ((q_rows["Topic 1"] == topic) | (q_rows["Topic 2"] == topic)).sum()
        counts[topic] = int(n)
    return counts

topic_counts = build_topic_counts(df)

# Sort topics: Essential first, then Important, then Worth Knowing, alpha within each tier
def topic_sort_key(t):
    c = topic_counts.get(t, 0)
    if c >= 40: tier = 0
    elif c >= 15: tier = 1
    else: tier = 2
    return (tier, t)

all_topics = sorted(topic_counts.keys(), key=topic_sort_key)


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


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("#### 🗂️ Browse Mode")
    browse_mode = st.radio(
        "Browse by",
        ["📋 Paper", "🏷️ Topic"],
        label_visibility="collapsed"
    )
    st.markdown("---")

    if browse_mode == "📋 Paper":
        st.markdown("#### 📋 Select Paper")
        available_years = sorted(df["Year"].dropna().unique(), reverse=True)
        year = st.selectbox("Year", available_years)
        filtered_year = df[df["Year"] == year]
        available_months = sorted(filtered_year["Month"].dropna().unique())
        month = st.selectbox("Month", available_months)
        filtered_month = filtered_year[filtered_year["Month"] == month]
        available_papers = sorted(filtered_month["Paper"].dropna().unique())
        paper = st.selectbox("Paper / Variant", available_papers)
        st.markdown("#### ❓ Select Question")
        filtered_paper = filtered_month[filtered_month["Paper"] == paper]
        available_questions = sorted(filtered_paper["Question"].dropna().unique())
        question_num = st.selectbox("Question Number", available_questions)

    else:
        st.markdown("#### 🏷️ Select Topic")

        # Format topic options with frequency label
        topic_display = {t: f"{t}  —  {freq_label(topic_counts.get(t,0))}" for t in all_topics}
        topic_options = list(topic_display.keys())
        topic_labels  = list(topic_display.values())

        selected_idx = st.selectbox(
            "Topic",
            range(len(topic_options)),
            format_func=lambda i: topic_labels[i]
        )
        selected_topic = topic_options[selected_idx]

        st.markdown("#### 📅 Filter by Year (optional)")
        year_options = ["All years"] + [str(y) for y in sorted(df["Year"].dropna().unique(), reverse=True)]
        selected_year_filter = st.selectbox("Year", year_options)

    st.markdown("---")
    st.markdown("#### ⚙️ Options")
    student_mode = st.toggle("🎓 Student Mode", value=False, help="Hides markschemes for self-testing")
    if browse_mode == "📋 Paper":
        keyword = st.text_input("🔍 Search question text", placeholder="e.g. elasticity, GDP…")

    st.markdown("#### 📥 Export")


# ══════════════════════════════════════════════════════════════════════════════
# PAPER MODE
# ══════════════════════════════════════════════════════════════════════════════
if browse_mode == "📋 Paper":
    mask = (
        (df["Year"] == year) &
        (df["Month"] == month) &
        (df["Paper"] == paper) &
        (df["Question"] == question_num)
    )
    result_all_parts = df[mask].copy()
    result_all_parts["Part"] = result_all_parts["Part"].astype(str)
    result_all_parts["_sort_key"] = result_all_parts["Part"].apply(part_sort_key)
    result_all_parts = result_all_parts.sort_values(by="_sort_key")

    table_data_all = result_all_parts[result_all_parts["Part"].str.lower() != "stimulus"].copy()
    if keyword:
        filtered_kw = table_data_all[table_data_all["Question Text"].str.contains(keyword, case=False, na=False)]
        table_data = filtered_kw if not filtered_kw.empty else table_data_all
    else:
        table_data = table_data_all

    if not result_all_parts.empty:
        st.markdown(
            f'<div class="paper-label">Question {question_num} &nbsp;·&nbsp; {month} {year} &nbsp;·&nbsp; Variant {paper}</div>',
            unsafe_allow_html=True
        )
        total = pd.to_numeric(table_data["Marks"], errors="coerce").sum()
        total_str = str(int(total)) if total == int(total) else str(total)
        st.markdown(f'<div class="marks-pill">📋 Total marks: {total_str}</div>', unsafe_allow_html=True)

        # Show topic badges with frequency for this question
        topics_in_q = set()
        for _, r in table_data.iterrows():
            if r["Topic 1"]: topics_in_q.add(r["Topic 1"])
            if r["Topic 2"]: topics_in_q.add(r["Topic 2"])
        if topics_in_q:
            badges = " ".join([
                f'<span class="topic-badge">{html.escape(t)}</span> {freq_badge(topic_counts.get(t,0))}'
                for t in sorted(topics_in_q)
            ])
            st.markdown(f'<div style="margin-bottom:1rem">{badges}</div>', unsafe_allow_html=True)

        stimulus = result_all_parts[result_all_parts["Part"].str.lower() == "stimulus"]
        if not stimulus.empty:
            stim_text = html.escape(stimulus["Stimulus / Scenario"].fillna("").iloc[0]).replace("\n", "<br>")
            st.markdown(f'<div class="stimulus-card"><div class="stimulus-label">📄 Stimulus / Scenario</div>{stim_text}</div>', unsafe_allow_html=True)

        render_question_rows(table_data, student_mode)

        with st.sidebar:
            csv_data = table_data.drop(columns=["_sort_key"], errors="ignore").to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download as CSV",
                data=csv_data,
                file_name=f"Econ_{year}_{month}_Q{question_num}.csv",
                mime="text/csv",
            )
            st.caption("💡 Ctrl+P → Save as PDF. Sidebar hides automatically.")
    else:
        st.warning("No data found for the selected filters.")


# ══════════════════════════════════════════════════════════════════════════════
# TOPIC MODE
# ══════════════════════════════════════════════════════════════════════════════
else:
    topic_mask = (df["Topic 1"] == selected_topic) | (df["Topic 2"] == selected_topic)
    topic_rows = df[topic_mask & (df["Part"].astype(str).str.lower() != "stimulus")].copy()

    if selected_year_filter != "All years":
        topic_rows = topic_rows[topic_rows["Year"] == int(selected_year_filter)]

    count = topic_counts.get(selected_topic, 0)

    st.markdown(
        f'<div class="topic-label">🏷️ {selected_topic} &nbsp; {freq_badge(count)}</div>',
        unsafe_allow_html=True
    )

    # Frequency info box
    if count >= 40:
        msg = f"This topic has appeared in <strong>{count} questions</strong> across past papers — it comes up constantly and should be at the top of your revision list."
    elif count >= 15:
        msg = f"This topic has appeared in <strong>{count} questions</strong> across past papers — it comes up regularly and is well worth revising thoroughly."
    else:
        msg = f"This topic has appeared in <strong>{count} questions</strong> across past papers — it is part of the full syllabus and understanding it will strengthen your overall performance."

    st.markdown(f'<div class="freq-info">📊 {msg}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="count-pill">📊 {len(topic_rows)} question{"s" if len(topic_rows) != 1 else ""} shown</div>', unsafe_allow_html=True)

    if topic_rows.empty:
        st.info("No questions found for this topic and year combination.")
    else:
        grouped = topic_rows.sort_values(["Year", "Month", "Paper", "Question"], ascending=[False, True, True, True])

        for year_val, year_group in grouped.groupby("Year", sort=False):
            st.markdown(f'<div class="year-group-header">{int(year_val)}</div>', unsafe_allow_html=True)

            for (month_val, paper_val, q_val), q_group in year_group.groupby(["Month", "Paper", "Question"], sort=False):
                t1 = safe_str(q_group.iloc[0]["Topic 1"])
                t2 = safe_str(q_group.iloc[0]["Topic 2"])
                topic_badges = f'<span class="topic-badge">{html.escape(t1)}</span>' if t1 else ""
                if t2:
                    topic_badges += f'<span class="topic-badge">{html.escape(t2)}</span>'

                st.markdown(
                    f'<div class="topic-q-context">{month_val} &nbsp;·&nbsp; Variant {paper_val} &nbsp;·&nbsp; Q{int(q_val)}</div>{topic_badges}',
                    unsafe_allow_html=True
                )

                stim_row = df[
                    (df["Year"] == year_val) &
                    (df["Month"] == month_val) &
                    (df["Paper"] == paper_val) &
                    (df["Question"] == q_val) &
                    (df["Part"].astype(str).str.lower() == "stimulus")
                ]
                if not stim_row.empty:
                    stim_text = html.escape(stim_row["Stimulus / Scenario"].fillna("").iloc[0]).replace("\n", "<br>")
                    if stim_text.strip():
                        with st.expander("📄 View stimulus for this question"):
                            st.markdown(f'<div class="stimulus-card" style="margin-bottom:0"><div class="stimulus-label">Stimulus / Scenario</div>{stim_text}</div>', unsafe_allow_html=True)

                q_group = q_group.copy()
                q_group["Part"] = q_group["Part"].astype(str)
                q_group["_sort_key"] = q_group["Part"].apply(part_sort_key)
                q_group = q_group.sort_values("_sort_key")

                render_question_rows(q_group, student_mode)

        with st.sidebar:
            csv_data = topic_rows.to_csv(index=False).encode("utf-8")
            fname = selected_topic.replace(" ", "_").replace("/", "-").replace("&", "and")[:40]
            st.download_button(
                label="📥 Download topic as CSV",
                data=csv_data,
                file_name=f"Econ_topic_{fname}.csv",
                mime="text/csv",
            )
            st.caption("💡 Ctrl+P → Save as PDF. Sidebar hides automatically.")

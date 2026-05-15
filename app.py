import streamlit as st
import pandas as pd
from pathlib import Path
import html

st.set_page_config(layout="wide", page_title="Teacher James · IGCSE Economics")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display&family=DM+Sans:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }

.app-header {
    background: #1a2e44;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.8rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.app-header h1 {
    font-family: 'DM Serif Display', serif;
    color: #ffffff;
    font-size: 1.7rem;
    margin: 0;
    letter-spacing: -0.01em;
}
.app-header .subtitle {
    color: #7fa8c9;
    font-size: 0.85rem;
    margin-top: 3px;
}
.header-badge {
    background: #2e7d52;
    color: #c6f0d8;
    font-size: 0.75rem;
    font-weight: 600;
    padding: 5px 12px;
    border-radius: 20px;
    letter-spacing: 0.04em;
    text-transform: uppercase;
}

.paper-label {
    background: #e8f5ee;
    border-left: 4px solid #2e7d52;
    color: #1a4d32;
    padding: 10px 16px;
    border-radius: 0 8px 8px 0;
    font-size: 0.9rem;
    font-weight: 500;
    margin-bottom: 1rem;
}

.marks-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #1a2e44;
    color: #fff;
    font-size: 0.85rem;
    font-weight: 600;
    padding: 6px 16px;
    border-radius: 20px;
    margin-bottom: 1.2rem;
}

.stimulus-card {
    background: #fffdf5;
    border: 1px solid #e8d98a;
    border-left: 5px solid #c9a227;
    border-radius: 0 10px 10px 0;
    padding: 1.2rem 1.5rem;
    font-size: 0.93rem;
    line-height: 1.7;
    color: #3d3110;
    margin-bottom: 1.5rem;
}
.stimulus-label {
    font-size: 0.72rem;
    font-weight: 600;
    color: #c9a227;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 8px;
}

.section-rule {
    border: none;
    border-top: 1px solid #e2e8f0;
    margin: 0.6rem 0 1.4rem 0;
}

.col-header {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    padding-bottom: 6px;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 0.8rem;
}

.part-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 36px;
    height: 36px;
    background: #1a2e44;
    color: #fff;
    font-family: 'DM Serif Display', serif;
    font-size: 1rem;
    border-radius: 8px;
}

.q-text {
    font-size: 0.95rem;
    line-height: 1.65;
    color: #1e293b;
}

.marks-badge {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 3px 10px;
    border-radius: 6px;
    font-size: 0.8rem;
    font-weight: 600;
    min-width: 38px;
}
.marks-1  { background: #dcfce7; color: #166534; }
.marks-2  { background: #fef9c3; color: #854d0e; }
.marks-3  { background: #ffedd5; color: #9a3412; }
.marks-4p { background: #fee2e2; color: #991b1b; }

.ms-card {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-left: 4px solid #3b82f6;
    border-radius: 0 10px 10px 0;
    padding: 1rem 1.2rem;
    font-size: 0.88rem;
    line-height: 1.7;
    color: #1e293b;
}
.ms-card .teacher-tip {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px dashed #cbd5e1;
    font-size: 0.83rem;
    color: #475569;
}
.ms-card .tip-label {
    font-size: 0.72rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.07em;
    color: #3b82f6;
    margin-bottom: 4px;
}

.row-divider {
    border: none;
    border-top: 1px solid #f1f5f9;
    margin: 1rem 0;
}

[data-testid="stSidebar"] {
    background: #f8fafc;
    border-right: 1px solid #e2e8f0;
}

@media print {
    section[data-testid='stSidebar'] { display: none !important; }
    .app-header { background: #1a2e44 !important; -webkit-print-color-adjust: exact; }
}
</style>
""", unsafe_allow_html=True)


# ── Helper ────────────────────────────────────────────────────────────────────
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
        "Stimulus / Scenario", "Question Text",
        "Marks", "Markscheme", "Explanation"
    ]
    missing = [col for col in required_columns if col not in df.columns]
    if missing:
        st.error(f"Missing columns in CSV: {missing}")
        st.stop()
    return df

df = load_data()


# ── Header Banner ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="app-header">
    <div>
        <h1>IGCSE Economics</h1>
        <div class="subtitle">Past Paper Examiner Tool &nbsp;·&nbsp; Paper 2</div>
    </div>
    <div class="header-badge">Teacher James</div>
</div>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
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

    st.markdown("#### ⚙️ Options")
    student_mode = st.toggle("🎓 Student Mode", value=False, help="Hides markschemes for self-testing")
    keyword = st.text_input("🔍 Search question text", placeholder="e.g. elasticity, GDP…")

    st.markdown("#### 📥 Export")


# ── Filter ────────────────────────────────────────────────────────────────────
mask = (
    (df["Year"] == year) &
    (df["Month"] == month) &
    (df["Paper"] == paper) &
    (df["Question"] == question_num)
)
result_all_parts = df[mask].copy()
result_all_parts["Part"] = result_all_parts["Part"].astype(str)

def part_sort_key(part):
    if part.lower() == "stimulus":
        return (0, "", 0)
    base = part.split("(")[0].strip()
    sub  = part[len(base):].strip("() ")
    roman = {"i": 1, "ii": 2, "iii": 3, "iv": 4, "v": 5, "vi": 6}
    return (1, base, roman.get(sub.lower(), 0))

result_all_parts["_sort_key"] = result_all_parts["Part"].apply(part_sort_key)
result_all_parts = result_all_parts.sort_values(by="_sort_key")

table_data_all = result_all_parts[result_all_parts["Part"].str.lower() != "stimulus"].copy()

if keyword:
    filtered_kw = table_data_all[table_data_all["Question Text"].str.contains(keyword, case=False, na=False)]
    table_data = filtered_kw if not filtered_kw.empty else table_data_all
else:
    table_data = table_data_all


# ── Main Display ──────────────────────────────────────────────────────────────
if not result_all_parts.empty:

    st.markdown(
        f'<div class="paper-label">Question {question_num} &nbsp;·&nbsp; {month} {year} &nbsp;·&nbsp; Variant {paper}</div>',
        unsafe_allow_html=True
    )

    total = pd.to_numeric(table_data["Marks"], errors="coerce").sum()
    total_str = str(int(total)) if total == int(total) else str(total)
    st.markdown(
        f'<div class="marks-pill">📋 Total marks: {total_str}</div>',
        unsafe_allow_html=True
    )

    # Stimulus
    stimulus = result_all_parts[result_all_parts["Part"].str.lower() == "stimulus"]
    if not stimulus.empty:
        stim_text = html.escape(stimulus["Stimulus / Scenario"].fillna("").iloc[0]).replace("\n", "<br>")
        st.markdown(f"""
        <div class="stimulus-card">
            <div class="stimulus-label">📄 Stimulus / Scenario</div>
            {stim_text}
        </div>
        """, unsafe_allow_html=True)

    # Column headers
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

    # Question rows
    for _, row in table_data.iterrows():
        part        = safe_str(row["Part"])
        q_text      = safe_str(row["Question Text"])
        marks       = safe_str(row["Marks"])
        ms          = safe_str(row["Markscheme"], "No markscheme available.")
        explanation = safe_str(row["Explanation"])

        ms_safe   = html.escape(ms).replace("\n", "<br>")
        expl_safe = html.escape(explanation).replace("\n", "<br>")
        mclass    = marks_class(marks)

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

            tip_html = f"""
                <div class="teacher-tip">
                    <div class="tip-label">Teacher Tip</div>
                    {expl_safe}
                </div>""" if explanation else ""

            col4.markdown(f"""
            <div class="ms-card">
                {ms_safe}
                {tip_html}
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<hr class="row-divider">', unsafe_allow_html=True)

    # Sidebar export
    with st.sidebar:
        csv_data = table_data.drop(columns=["_sort_key"], errors="ignore").to_csv(index=False).encode("utf-8")
        st.download_button(
            label="📥 Download as CSV",
            data=csv_data,
            file_name=f"Econ_{year}_{month}_Q{question_num}.csv",
            mime="text/csv",
        )
        st.caption("💡 To save as PDF: Ctrl+P → Save as PDF. The sidebar hides automatically.")

else:
    st.warning("No data found for the selected filters.")

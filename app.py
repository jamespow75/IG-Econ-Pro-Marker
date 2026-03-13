import streamlit as st
import pandas as pd
from pathlib import Path
import html

# Page setup must come before other Streamlit commands
st.set_page_config(layout="wide", page_title="Teacher James Examiner Tool")

st.title("🎓 IGCSE Economics Examiner Tool")

# Load your CSV
@st.cache_data
def load_data():
    file_path = Path("IGCSE Econ P2 Past Papers + MS - Sheet1.csv")
    if not file_path.exists():
        st.error(f"CSV file not found: {file_path}")
        st.stop()

    df = pd.read_csv(file_path)

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

# Sidebar Filters
st.sidebar.header("Step 1: Select Paper")

available_years = sorted(df["Year"].dropna().unique(), reverse=True)
year = st.sidebar.selectbox("Year", available_years)

filtered_year = df[df["Year"] == year]
available_months = sorted(filtered_year["Month"].dropna().unique())
month = st.sidebar.selectbox("Month", available_months)

filtered_month = filtered_year[filtered_year["Month"] == month]
available_papers = sorted(filtered_month["Paper"].dropna().unique())
paper = st.sidebar.selectbox("Paper/Variant", available_papers)

st.sidebar.header("Step 2: Select Question")

filtered_paper = filtered_month[filtered_month["Paper"] == paper]
available_questions = sorted(filtered_paper["Question"].dropna().unique())
question_num = st.sidebar.selectbox("Question Number", available_questions)

# Final filter
mask = (
    (df["Year"] == year) &
    (df["Month"] == month) &
    (df["Paper"] == paper) &
    (df["Question"] == question_num)
)

result_all_parts = df[mask].copy()

# Optional: safer sort if Part contains strings
result_all_parts["Part"] = result_all_parts["Part"].astype(str)
result_all_parts = result_all_parts.sort_values(by="Part")

if not result_all_parts.empty:
    st.success(f"Displaying Question {question_num} from {month} {year} (Variant {paper})")

    # Stimulus section
    stimulus = result_all_parts[result_all_parts["Part"] == "Stimulus"]
    if not stimulus.empty:
        with st.expander("📝 View Question Stimulus / Scenario", expanded=True):
            stim_text = stimulus["Stimulus / Scenario"].fillna("").iloc[0]
            st.info(stim_text)

    # Main table rows excluding stimulus
    table_data = result_all_parts[result_all_parts["Part"] != "Stimulus"].copy()

    st.write("---")

    h1, h2, h3, h4 = st.columns([1, 4, 1, 6])
    h1.subheader("Part")
    h2.subheader("Question Text")
    h3.subheader("Marks")
    h4.subheader("Markscheme & Explanation")

    st.write("---")

    for _, row in table_data.iterrows():
        c1, c2, c3, c4 = st.columns([1, 4, 1, 6])

        part = str(row["Part"]) if pd.notnull(row["Part"]) else ""
        q_text = str(row["Question Text"]) if pd.notnull(row["Question Text"]) else ""
        marks = str(row["Marks"]) if pd.notnull(row["Marks"]) else ""
        ms = str(row["Markscheme"]) if pd.notnull(row["Markscheme"]) else "No markscheme available."
        explanation = str(row["Explanation"]) if pd.notnull(row["Explanation"]) else ""

        c1.markdown(f"### ({part})")
        c2.write(q_text)
        c3.markdown(f"**[{marks}]**")

        # Escape HTML-sensitive characters to avoid rendering glitches
        ms_safe = html.escape(ms).replace("\n", "<br>")
        expl_safe = html.escape(explanation).replace("\n", "<br>")

        teacher_tip = f"<br><br><strong>Teacher Tip:</strong> {expl_safe}" if explanation else ""

        c4.markdown(
            f"""
            <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; color: #1f1f1f;">
                {ms_safe}{teacher_tip}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.write("---")

    # Export options
    st.sidebar.write("---")
    st.sidebar.header("Step 3: Export")

    csv_data = table_data.to_csv(index=False).encode("utf-8")
    st.sidebar.download_button(
        label="📥 Download Question as CSV",
        data=csv_data,
        file_name=f"Econ_{year}_{month}_Q{question_num}.csv",
        mime="text/csv",
    )

    st.sidebar.info("💡 To save as PDF: Press Ctrl+P or Cmd+P and choose 'Save as PDF'.")

else:
    st.warning("No data found. Please adjust your filters in the sidebar.")

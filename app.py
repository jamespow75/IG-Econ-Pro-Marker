import streamlit as st
import pandas as pd

# Load your CSV
@st.cache_data
def load_data():
    df = pd.read_csv('IGCSE Econ P2 Past Papers + MS - Sheet1.csv')
    return df

df = load_data()

# Page Setup
st.set_page_config(layout="wide", page_title="Teacher James Examiner Tool")
st.title("🎓 IGCSE Economics Examiner Tool")

# Sidebar Filters
st.sidebar.header("Step 1: Select Paper")
year = st.sidebar.selectbox("Year", sorted(df['Year'].unique(), reverse=True))
month = st.sidebar.selectbox("Month", df['Month'].unique())
paper = st.sidebar.selectbox("Paper/Variant", sorted(df['Paper'].unique()))

st.sidebar.header("Step 2: Select Question")
question_num = st.sidebar.selectbox("Question Number", sorted(df['Question'].unique()))

# Filter Data
mask = (df['Year'] == year) & (df['Month'] == month) & (df['Paper'] == paper) & (df['Question'] == question_num)
result_all_parts = df[mask].sort_values(by='Part')

if not result_all_parts.empty:
    st.success(f"Displaying Question {question_num} from {month} {year} (Variant {paper})")
    
    # 1. Stimulus Section
    stimulus = result_all_parts[result_all_parts['Part'] == 'Stimulus']
    if not stimulus.empty:
        with st.expander("📝 View Question Stimulus / Scenario", expanded=True):
            st.info(stimulus['Stimulus / Scenario'].values[0])

    # 2. Table Layout
    table_data = result_all_parts[result_all_parts['Part'] != 'Stimulus'].copy()

    st.write("---")
    # Custom Header for the Table
    h1, h2, h3, h4 = st.columns([1, 4, 1, 6])
    h1.subheader("Part")
    h2.subheader("Question Text")
    h3.subheader("Marks")
    h4.subheader("Markscheme & Explanation")
    st.write("---")

    # Rows
    for index, row in table_data.iterrows():
        c1, c2, c3, c4 = st.columns([1, 4, 1, 6])
        
        c1.write(f"### **({row['Part']})**")
        c2.write(row['Question Text'])
        c3.write(f"**[{row['Marks']}]**")
        
        # Combine MS and Explanation
        ms = str(row['Markscheme']) if pd.notnull(row['Markscheme']) else "No markscheme available."
        expl = f"\n\n**Teacher Tip:** {row['Explanation']}" if pd.notnull(row['Explanation']) else ""
        c4.markdown(f'<div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px;">{ms}{expl}</div>', unsafe_allow_status=True, unsafe_allow_html=True)
        
        st.write("---")

    # 3. Export Options
    st.sidebar.write("---")
    st.sidebar.header("Step 3: Export")
    
    # Create a CSV version of just this question for the student to download
    csv_data = table_data.to_csv(index=False).encode('utf-8')
    st.sidebar.download_button(
        label="📥 Download Question as CSV",
        data=csv_data,
        file_name=f"Econ_{year}_{month}_Q{question_num}.csv",
        mime='text/csv',
    )
    
    st.sidebar.info("💡 To save as PDF: Press **Ctrl+P** (Windows) or **Cmd+P** (Mac) and select 'Save as PDF'.")

else:
    st.warning("No data found. Please adjust your filters in the sidebar.")

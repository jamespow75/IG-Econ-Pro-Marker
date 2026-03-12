import streamlit as st
import pandas as pd

# Load your CSV
@st.cache_data
def load_data():
    df = pd.read_csv('IGCSE Econ P2 Past Papers + MS - Sheet1.csv')
    return df

df = load_data()

st.title("🎓 IGCSE Economics Revision Tool")
st.write("Find your question and mark scheme below to paste into Teacher James.")

# Sidebar Filters
st.sidebar.header("Filter by Question")
year = st.sidebar.selectbox("Year", sorted(df['Year'].unique()))
month = st.sidebar.selectbox("Month", df['Month'].unique())
paper = st.sidebar.selectbox("Paper/Variant", sorted(df['Paper'].unique()))
question = st.sidebar.selectbox("Question Number", sorted(df['Question'].unique()))
part = st.sidebar.selectbox("Part", sorted(df['Part'].unique()))

# Filter Data
result = df[(df['Year'] == year) & 
            (df['Month'] == month) & 
            (df['Paper'] == paper) & 
            (df['Question'] == question) & 
            (df['Part'] == part)]

if not result.empty:
    st.success("Question Found!")
    st.subheader("Question Text")
    st.write(result['Question Text'].values[0])
    st.subheader("Official Markscheme")
    st.write(result['Markscheme'].values[0])
    
    # Helper to copy
    st.info("💡 Copy the text above and paste it into Teacher James along with your answer!")
else:
    st.warning("No data found for this combination.")
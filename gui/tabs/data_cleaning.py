import streamlit as st

def render(manager):
    st.header("🧹 Data Import & Cleaning")
    st.info("Goal: Upload raw CSVs, map columns, clean text, and split into Train/Test.")

    st.markdown("""
    ### 🚧 TODO:
    1. **Import:** Add file uploader for Training & Test datasets.
    2. **Mapping:** Add selectors to identify 'Text', 'Label', and 'ID' columns.
    3. **Cleaning:** Add checkboxes for cleaning rules (URLs, Mentions, Stopwords).
    4. **Split:** Add slider for Train/Test ratio (default 80/20).
    5. **Preview:** Show 'Before vs After' dataframe snippets.
    """)
    st.write("---")
    st.write("*(Build the cleaning pipeline controls here)*")
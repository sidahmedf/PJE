import streamlit as st

def render(manager):
    st.header("📍 Algorithm: KNN")
    st.info("Goal: K-Nearest Neighbors classification.")

    st.markdown("""
        ### 🚧 TODO:
        - **Develop algorithm** in the most modular way possible.
        - **Configuration:** Make it possible to configure params (e.g., dictionary source, threshold).
        - **Actions:** Train (fit), Type a tweet and get a prediction on that tweet.
        - **Metrics:** Show metrics (accuracy, stats specific to algorithm, and comparison of different params).
        """)
    st.write("---")
    st.write("*(Build Knn specific widgets here)*")
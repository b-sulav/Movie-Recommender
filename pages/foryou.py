import streamlit as st
st.title("Recommended for you")
if st.button("Main Menu"):
    st.session_state.user_table = st.session_state.movies.sample(15)
    st.session_state.count = 0
    st.switch_page("main.py")
import streamlit as st

#  initial value
if 'count' not in st.session_state:
    st.session_state.count = 0
    
# show movies poster and title one after another
def change_movie():
    st.session_state.count += 1

st.title("Swipe to Like or Dislike")
if st.session_state.count >=15:
    st.switch_page("pages/foryou.py")
st.image(st.session_state.user_table.iloc[st.session_state.count]['poster_url'])
st.subheader(st.session_state.user_table.iloc[st.session_state.count]['title'])
st.button("Next", on_click = change_movie)
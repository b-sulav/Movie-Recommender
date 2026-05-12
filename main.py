import pandas as pd
import streamlit as st 

# load the csv file
st.session_state.movies = pd.read_csv("Movies.csv")

# initial value
if 'user_table' not in st.session_state:
    st.session_state.user_table = st.session_state.movies.sample(15)
    
st.title("Movie Recommender")  
if st.button("Start"):
    st.switch_page("pages/discover.py")
    


   






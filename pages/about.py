import streamlit as st

st.title("about :rainbow[SignOut]")

with st.sidebar:
    st.header(':rainbow[Navigation]')
    st.page_link('SignOut.py', label=':blue[Home]')
    st.page_link('pages/signup.py', label=':orange[Signup]')
    st.page_link('pages/view.py', label=':violet[Login]')
    st.page_link('pages/about.py', label=':violet-background[About]')

st.write(":orange[SignOut] is an application that brings light to the traditional signout style among graduating students in Nigeria, Africa and the uttermost part of the earth.")
st.write(":blue[SignOut] creates a lightburdensome method of celebrating time spent in learning institutions with friends by eliminating the necessity of getting the white shirt (signout traditional merchandise), which is usually at a cost for concerened graduates.")
st.write(":violet[Signout] brings about a more inclusive way of celebrating end of educational pursuit by making it available to people of all age, tribe, nations and economy.")
st.write('Contact admin @ https://x.com/mercy_mts')
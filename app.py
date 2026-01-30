import streamlit as st

if "page" not in st.session_state:
    st.session_state.page = 1

def next_page():
    st.session_state.page += 1

st.title("Streamlit Wizard Test")

if st.session_state.page == 1:
    st.write("Page 1")
    st.button("Next", on_click=next_page)

elif st.session_state.page == 2:
    st.write("Page 2")
    st.button("Next", on_click=next_page)

elif st.session_state.page == 3:
    st.write("Page 3 – Done")


import streamlit as st

st.set_page_config(layout="centered")

# ---------- INIT ----------
if "screen" not in st.session_state:
    st.session_state.screen = "screen_a"
    st.session_state.action = None
    st.session_state.undo_stack = []

def goto(screen):
    st.session_state.undo_stack.append(st.session_state.screen)
    st.session_state.screen = screen
    st.session_state.action = None

def undo():
    if st.session_state.undo_stack:
        st.session_state.screen = st.session_state.undo_stack.pop()
    st.session_state.action = None

# ---------- ACTION HANDLER ----------
if st.session_state.action == "NEXT":
    goto("screen_b")

elif st.session_state.action == "UNDO":
    undo()

# ---------- UI ----------
st.title("Single-Tap Test")

if st.session_state.screen == "screen_a":
    st.subheader("Screen A")

    if st.button("Go Next", use_container_width=True):
        st.session_state.action = "NEXT"
        st.rerun()

elif st.session_state.screen == "screen_b":
    st.subheader("Screen B")

    if st.button("Undo", use_container_width=True):
        st.session_state.action = "UNDO"
        st.rerun()

import streamlit as st

# =========================
# Session State Init (ONCE)
# =========================
if "page" not in st.session_state:
    st.session_state.page = "round"

if "round" not in st.session_state:
    st.session_state.round = {}

if "hole_index" not in st.session_state:
    st.session_state.hole_index = 1

if "hole" not in st.session_state:
    st.session_state.hole = {}

if "shot" not in st.session_state:
    st.session_state.shot = {}


# =========================
# Navigation Helper
# =========================
def go(page):
    st.session_state.page = page


# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker – Round Setup")

    st.session_state.round["player"] = st.text_input("Player Name")
    st.session_state.round["course"] = st.text_input("Course Name")
    st.session_state.round["holes_played"] = st.number_input(
        "Holes Played", 1, 18, 18
    )
    st.session_state.round["course_par"] = st.number_input(
        "Course Par", 9, 90, st.session_state.round["holes_played"] * 4
    )
    st.session_state.round["holes"] = []

    st.button(
        "Start Round",
        use_container_width=True,
        on_click=lambda: go("hole_setup")
    )


# =========================
# HOLE SETUP
# =========================
elif st.session_state.page == "hole_setup":
    st.title(f"Hole {st.session_state.hole_index} Setup")

    st.session_state.hole = {
        "hole_number": st.session_state.hole_index,
        "par": st.number_input("Hole Par", 3, 5, 4),
        "yardage": st.number_input("Hole Yardage (yards)", 50, 800, 400),
        "shots":


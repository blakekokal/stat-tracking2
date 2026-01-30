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


# =========================
# Navigation Helpers
# =========================
def go(page):
    st.session_state.page = page


# =========================
# ROUND SETUP PAGE
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
# HOLE SETUP PAGE
# =========================
elif st.session_state.page == "hole_setup":
    st.title(f"Hole {st.session_state.hole_index} Setup")

    st.session_state.hole["par"] = st.number_input("Hole Par", 3, 5, 4)
    st.session_state.hole["yardage"] = st.number_input(
        "Hole Yardage (yards)", 50, 800, 400
    )

    def start_hole():
        st.session_state.hole["shots"] = []
        go("confirm_hole")

    st.button(
        "Confirm Hole",
        use_container_width=True,
        on_click=start_hole
    )


# =========================
# CONFIRM PAGE (DEBUG)
# =========================
elif st.session_state.page == "confirm_hole":
    st.title("Hole Created ✅")

    st.write("Round:")
    st.json(st.session_state.round)

    st.write("Current Hole:")
    st.json(st.session_state.hole)

    st.button(
        "Proceed to Shots (next step)",
        use_container_width=True,
        on_click=lambda: go("done")
    )


# =========================
# DONE PLACEHOLDER
# =========================
elif st.session_state.page == "done":
    st.title("Step 1 Complete 🎉")
    st.write("Round and hole setup are working.")

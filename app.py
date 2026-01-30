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
        "shots": []
    }

    st.button(
        "Confirm Hole",
        use_container_width=True,
        on_click=lambda: go("shot_distance")
    )


# =========================
# SHOT DISTANCE
# =========================
elif st.session_state.page == "shot_distance":
    shot_number = len(st.session_state.hole["shots"]) + 1

    st.title(f"Hole {st.session_state.hole_index} – Shot {shot_number}")

    st.session_state.shot = {
        "number": shot_number,
        "distance": st.number_input(
            "How far did the shot go? (yards)",
            min_value=0,
            max_value=400,
            value=150,
            step=1
        )
    }

    st.button(
        "Confirm Distance",
        use_container_width=True,
        on_click=lambda: go("shot_result")
    )


# =========================
# SHOT RESULT (NEW)
# =========================
elif st.session_state.page == "shot_result":
    st.title("Where did the ball go?")

    cols = st.columns(2)
    options = ["Fairway", "Rough", "Bunker", "Water", "Green", "Hole"]

    for i, opt in enumerate(options):
        def make_handler(choice=opt):
            st.session_state.shot["result"] = choice.lower()
            go("confirm_shot")

        cols[i % 2].button(
            opt,
            use_container_width=True,
            on_click=make_handler
        )


# =========================
# CONFIRM SHOT (DEBUG)
# =========================
elif st.session_state.page == "confirm_shot":
    st.title("Shot Saved ✅")

    st.session_state.hole["shots"].append(st.session_state.shot)

    st.write("Current Hole:")
    st.json(st.session_state.hole)

    st.button(
        "Continue (next step)",
        use_container_width=True,
        on_click=lambda: go("done")
    )


# =========================
# DONE PLACEHOLDER
# =========================
elif st.session_state.page == "done":
    st.title("Step 3 Complete 🎉")
    st.write("Shot distance + result entry works.")

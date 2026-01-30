import streamlit as st

# =========================
# Session State Init
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


def save_shot_and_continue():
    st.session_state.hole["shots"].append(st.session_state.shot)
    go("shot_distance")


# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker – Round Setup")

    st.session_state.round["player"] = st.text_input("Player Name")
    st.session_state.round["course"] = st.text_input("Course Name")
    st.session_state.round["holes_played"] = st.number_input("Holes Played", 1, 18, 18)
    st.session_state.round["course_par"] = st.number_input(
        "Course Par", 9, 90, st.session_state.round["holes_played"] * 4
    )
    st.session_state.round["holes"] = []

    st.button("Start Round", use_container_width=True, on_click=lambda: go("hole_setup"))


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

    st.button("Confirm Hole", use_container_width=True, on_click=lambda: go("shot_distance"))


# =========================
# SHOT DISTANCE
# =========================
elif st.session_state.page == "shot_distance":
    shot_number = len(st.session_state.hole["shots"]) + 1

    st.title(f"Hole {st.session_state.hole_index} – Shot {shot_number}")

    st.session_state.shot = {
        "number": shot_number,
        "distance": st.number_input(
            "How far did the shot go? (yards)", 0, 400, 150, step=1
        )
    }

    st.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT RESULT (AUTO-ADVANCE)
# =========================
elif st.session_state.page == "shot_result":
    st.title("Where did the ball go?")

    cols = st.columns(2)
    options = ["Fairway", "Rough", "Bunker", "Water", "Green", "Hole"]

    for i, opt in enumerate(options):
        def handler(choice=opt):
            st.session_state.shot["result"] = choice.lower()

            if choice.lower() == "green":
                go("putt_distance")
            elif choice.lower() in ["rough", "bunker", "water"]:
                go("shot_direction")
            elif choice.lower() == "hole":
                save_shot_and_continue()
            else:  # fairway
                save_shot_and_continue()

        cols[i % 2].button(
            opt,
            use_container_width=True,
            on_click=handler
        )


# =========================
# SHOT DIRECTION
# =========================
elif st.session_state.page == "shot_direction":
    st.title("Which direction?")

    cols = st.columns(2)
    for i, d in enumerate(["Left", "Right", "Short", "Long"]):
        def handler(direction=d):
            st.session_state.shot["direction"] = direction.lower()
            save_shot_and_continue()

        cols[i % 2].button(
            d,
            use_container_width=True,
            on_click=handler
        )


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.title("Putting")

    st.session_state.shot["putt_distance"] = st.number_input(
        "How far from the hole? (feet)", 0, 100, 15, step=1
    )

    st.button(
        "Confirm Putt",
        use_container_width=True,
        on_click=save_shot_and_continue
    )

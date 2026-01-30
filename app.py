import streamlit as st

# =========================
# Session State Init
# =========================
if "page" not in st.session_state:
    st.session_state.page = "round"

if "round" not in st.session_state:
    st.session_state.round = {"holes": []}

if "hole_index" not in st.session_state:
    st.session_state.hole_index = 1

if "hole" not in st.session_state:
    st.session_state.hole = {}

if "shot" not in st.session_state:
    st.session_state.shot = {}

if "on_green" not in st.session_state:
    st.session_state.on_green = False


# =========================
# Helpers
# =========================
def go(page):
    st.session_state.page = page


def save_shot():
    st.session_state.hole["shots"].append(st.session_state.shot)


def finish_hole():
    st.session_state.round["holes"].append(st.session_state.hole)
    st.session_state.hole_index += 1
    st.session_state.on_green = False

    if st.session_state.hole_index > st.session_state.round["holes_played"]:
        go("summary")
    else:
        go("hole_setup")


def shot_number():
    return len(st.session_state.hole.get("shots", [])) + 1


def progress():
    return f"Hole {st.session_state.hole_index} of {st.session_state.round['holes_played']} • Shot {shot_number()}"


def back():
    transitions = {
        "approach_distance": "shot_result",
        "shot_direction": "shot_result",
        "putt_distance": "shot_result",
        "putt_result": "putt_distance",
    }
    go(transitions.get(st.session_state.page, "shot_result"))


# =========================
# ROUND SETUP
# =========================
if st.session_state.page == "round":
    st.title("Golf Stat Tracker")

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
    st.subheader(f"Hole {st.session_state.hole_index} Setup")

    st.session_state.hole = {
        "hole_number": st.session_state.hole_index,
        "par": st.number_input("Hole Par", 3, 5, 4),
        "yardage": st.number_input("Hole Yardage (yards)", 50, 800, 400),
        "shots": []
    }

    st.button("Confirm Hole", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT RESULT
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())
    st.subheader("Where did the ball end up?")

    options = [
        "Fairway",
        "Fairway Bunker",
        "Rough",
        "Bunker",
        "Greenside Bunker",
        "Water",
        "Green",
        "Hole",
    ]

    cols = st.columns(2)
    for i, opt in enumerate(options):
        def handler(choice=opt):
            key = choice.lower().replace(" ", "_")
            st.session_state.shot = {
                "shot_number": shot_number(),
                "result": key
            }

            if key == "green":
                st.session_state.on_green = True
                go("putt_distance")

            elif key in ["rough", "bunker", "fairway_bunker", "water"]:
                go("shot_direction")

            elif key == "greenside_bunker":
                # NOT on the green → still needs distance
                save_shot()
                go("approach_distance")

            elif key == "hole":
                save_shot()
                finish_hole()

            else:  # fairway
                save_shot()
                go("approach_distance")

        cols[i % 2].button(opt, use_container_width=True, on_click=handler)

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# APPROACH DISTANCE
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())
    st.subheader(f"Shot {shot_number()} – distance to hole")

    st.session_state.shot = {
        "shot_number": shot_number(),
        "distance_to_hole": st.number_input("Yards", 0, 400, 50, step=1)
    }

    col1, col2 = st.columns(2)
    col1.button("⬅ Back", use_container_width=True, on_click=back)
    col2.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT DIRECTION
# =========================
elif st.session_state.page == "shot_direction":
    st.caption(progress())
    st.subheader("Which direction?")

    cols = st.columns(2)
    for i, d in enumerate(["Left", "Right", "Short", "Long"]):
        def handler(direction=d):
            st.session_state.shot["direction"] = direction.lower()
            save_shot()
            go("approach_distance")

        cols[i % 2].button(d, use_container_width=True, on_click=handler)

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# PUTTING DISTANCE (ONLY AFTER GREEN)
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())
    st.subheader("Putting – distance to hole")

    st.session_state.shot = {
        "shot_number": shot_number(),
        "putt_distance": st.number_input("Feet", 0, 100, 15, step=1)
    }

    col1, col2 = st.columns(2)
    col1.button("⬅ Back", use_container_width=True, on_click=back)
    col2.button("Next", use_container_width=True, on_click=lambda: go("putt_result"))


# =========================
# PUTT RESULT
# =========================
elif st.session_state.page == "putt_result":
    st.caption(progress())
    st.subheader("Where did the putt go?")

    cols = st.columns(2)
    for i, opt in enumerate(["Left", "Right", "Short", "Long", "Hole"]):
        def handler(choice=opt):
            st.session_state.shot["result"] = choice.lower()
            save_shot()

            if choice.lower() == "hole":
                finish_hole()
            else:
                go("putt_distance")

        cols[i % 2].button(opt, use_container_width=True, on_click=handler)

    st.button("⬅ Back", use_container_width=True, on_click=back)


# =========================
# SUMMARY
# =========================
elif st.session_state.page == "summary":
    st.title("Round Complete 🏁")
    st.json(st.session_state.round)

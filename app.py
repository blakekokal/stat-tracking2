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

if "history" not in st.session_state:
    st.session_state.history = []


# =========================
# Helpers
# =========================
def go(page):
    st.session_state.history.append(st.session_state.page)
    st.session_state.page = page


def back():
    if st.session_state.history:
        st.session_state.page = st.session_state.history.pop()


def save_shot():
    st.session_state.hole["shots"].append(st.session_state.shot)


def finish_hole():
    st.session_state.round["holes"].append(st.session_state.hole)
    st.session_state.hole_index += 1

    if st.session_state.hole_index > st.session_state.round["holes_played"]:
        st.session_state.page = "summary"
    else:
        st.session_state.page = "hole_setup"


def progress():
    return f"Hole {st.session_state.hole_index} of {st.session_state.round['holes_played']} • Shot {len(st.session_state.hole.get('shots', [])) + 1}"


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

    st.button("Confirm Hole", use_container_width=True, on_click=lambda: go("shot_distance"))


# =========================
# SHOT DISTANCE
# =========================
elif st.session_state.page == "shot_distance":
    st.caption(progress())
    st.subheader("How far did the shot go?")

    st.session_state.shot = {
        "distance": st.number_input("Yards", 0, 400, 150, step=1)
    }

    col1, col2 = st.columns(2)
    col1.button("Back", use_container_width=True, on_click=back)
    col2.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT RESULT
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())
    st.subheader("Where did the ball go?")

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
                save_shot()
                finish_hole()
            else:
                save_shot()
                go("shot_distance")

        cols[i % 2].button(opt, use_container_width=True, on_click=handler)


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
            go("shot_distance")

        cols[i % 2].button(d, use_container_width=True, on_click=handler)


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())
    st.subheader("Putting")

    st.session_state.shot["putt_distance"] = st.number_input(
        "Feet from hole", 0, 100, 15, step=1
    )

    col1, col2 = st.columns(2)
    col1.button("Back", use_container_width=True, on_click=back)
    col2.button(
        "Confirm Putt",
        use_container_width=True,
        on_click=lambda: (save_shot(), go("shot_distance"))
    )


# =========================
# SUMMARY (BASIC STATS)
# =========================
elif st.session_state.page == "summary":
    st.title("Round Summary 🏁")

    total_strokes = sum(len(h["shots"]) for h in st.session_state.round["holes"])
    score_vs_par = total_strokes - st.session_state.round["course_par"]

    putts = sum(
        1 for h in st.session_state.round["holes"]
        for s in h["shots"] if "putt_distance" in s
    )

    fairways = sum(
        1 for h in st.session_state.round["holes"]
        if h["shots"] and h["shots"][0]["result"] == "fairway"
    )

    gir = 0
    for h in st.session_state.round["holes"]:
        for i, s in enumerate(h["shots"], start=1):
            if s["result"] == "green" and i <= h["par"] - 2:
                gir += 1
                break

    st.metric("Total Strokes", total_strokes)
    st.metric("Score vs Par", score_vs_par)
    st.metric("Total Putts", putts)
    st.metric("Fairways Hit", fairways)
    st.metric("Greens in Regulation", gir)

    st.json(st.session_state.round)

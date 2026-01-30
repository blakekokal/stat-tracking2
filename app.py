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
# SHOT RESULT (TEE OR OFF-GREEN)
# =========================
elif st.session_state.page == "shot_result":
    st.caption(progress())
    st.subheader("Where did the ball end up?")

    cols = st.columns(2)
    options = ["Fairway", "Rough", "Bunker", "Water", "Green", "Hole"]

    for i, opt in enumerate(options):
        def handler(choice=opt):
            st.session_state.shot = {
                "shot_number": shot_number(),
                "result": choice.lower()
            }

            if choice.lower() == "green":
                st.session_state.on_green = True
                go("putt_distance")

            elif choice.lower() in ["rough", "bunker", "water"]:
                go("shot_direction")

            elif choice.lower() == "hole":
                save_shot()
                finish_hole()

            else:  # fairway
                save_shot()
                go("approach_distance")

        cols[i % 2].button(opt, use_container_width=True, on_click=handler)


# =========================
# APPROACH DISTANCE (SHOT 2+)
# =========================
elif st.session_state.page == "approach_distance":
    st.caption(progress())
    st.subheader(f"Shot {shot_number()} – distance to hole")

    st.session_state.shot = {
        "shot_number": shot_number(),
        "distance_to_hole": st.number_input("Yards", 0, 400, 150, step=1)
    }

    st.button("Next", use_container_width=True, on_click=lambda: go("shot_result"))


# =========================
# SHOT DIRECTION (MISSES)
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


# =========================
# PUTTING DISTANCE
# =========================
elif st.session_state.page == "putt_distance":
    st.caption(progress())
    st.subheader("Putting")

    st.session_state.shot = {
        "shot_number": shot_number(),
        "putt_distance": st.number_input("Feet from hole", 0, 100, 15, step=1)
    }

    st.button("Next", use_container_width=True, on_click=lambda: go("putt_result"))


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


# =========================
# SUMMARY / STATS
# =========================
elif st.session_state.page == "summary":
    st.title("Round Stats Recap 📊")

    holes = st.session_state.round["holes"]
    holes_played = len(holes)

    # ---------- FAIRWAYS (Par 4 & 5) ----------
    fw_holes = [h for h in holes if h["par"] in (4, 5)]
    fw_total = len(fw_holes)
    fw_hit = 0
    fw_miss = {"left": 0, "right": 0, "short": 0, "long": 0}

    for h in fw_holes:
        tee = h["shots"][0]
        if tee["result"] == "fairway":
            fw_hit += 1
        else:
            for d in fw_miss:
                if d in tee.get("direction", ""):
                    fw_miss[d] += 1

    st.subheader("Fairways Hit (Par 4s & 5s)")
    st.write(f"**{fw_hit}/{fw_total}**")
    if fw_total:
        st.write(f"Hit %: {fw_hit/fw_total:.1%}")
        for d in fw_miss:
            st.write(f"{d.title()} %: {fw_miss[d]/fw_total:.1%}")

    # ---------- GREENS IN REGULATION ----------
    gir = 0
    gir_holes = set()
    gir_miss = {"left": 0, "right": 0, "short": 0, "long": 0}

    for h in holes:
        par = h["par"]
        green_shot = None

        for i, s in enumerate(h["shots"], start=1):
            if s.get("result") == "green":
                green_shot = i
                break

        if green_shot and green_shot <= par - 2:
            gir += 1
            gir_holes.add(h["hole_number"])
        else:
            last = h["shots"][-1]
            for d in gir_miss:
                if d in last.get("direction", ""):
                    gir_miss[d] += 1

    st.subheader("Greens in Regulation")
    st.write(f"**{gir}/{holes_played}**")
    if holes_played:
        st.write(f"GIR %: {gir/holes_played:.1%}")
        for d in gir_miss:
            st.write(f"{d.title()} %: {gir_miss[d]/holes_played:.1%}")

    # ---------- PUTTING ----------
    total_putts = 0
    first_putts = []
    first_putts_gir = []
    first_putts_no_gir = []

    for h in holes:
        putts = [s for s in h["shots"] if "putt_distance" in s]
        total_putts += len(putts)

        if putts:
            first = putts[0]["putt_distance"]
            first_putts.append(first)

            if h["hole_number"] in gir_holes:
                first_putts_gir.append(first)
            else:
                first_putts_no_gir.append(first)

    putts_per_hole = total_putts / holes_played if holes_played else 0
    putts_per_gir = total_putts / len(gir_holes) if gir_holes else 0

    st.subheader("Putting")
    st.write(f"Total Putts: **{total_putts}**")
    st.write(f"Putts per Hole: **{putts_per_hole:.2f}**")
    st.write(f"Putts per GIR: **{putts_per_gir:.2f}**")

    if first_putts:
        st.write(f"Avg First Putt Distance: **{sum(first_putts)/len(first_putts):.1f} ft**")
    if first_putts_gir:
        st.write(f"Avg First Putt Distance (GIR): **{sum(first_putts_gir)/len(first_putts_gir):.1f} ft**")
    if first_putts_no_gir:
        st.write(f"Avg First Putt Distance (No GIR): **{sum(first_putts_no_gir)/len(first_putts_no_gir):.1f} ft**")

    # ---------- DISTANCE STATS ----------
    par4_approach = []
    par3_tee = []
    par5_approach = []

    for h in holes:
        shots = h["shots"]

        if h["par"] == 4 and len(shots) >= 2:
            d = shots[1].get("distance_to_hole")
            if d is not None:
                par4_approach.append(d)

        if h["par"] == 3 and shots:
            d = shots[0].get("distance_to_hole")
            if d is not None:
                par3_tee.append(d)

        if h["par"] == 5:
            for s in shots[1:]:
                if "distance_to_hole" in s:
                    par5_approach.append(s["distance_to_hole"])
                    break

    st.subheader("Distance Averages")
    if par4_approach:
        st.write(f"Avg 2nd Shot (Par 4): **{sum(par4_approach)/len(par4_approach):.1f} yds**")
    if par3_tee:
        st.write(f"Avg Tee Shot (Par 3): **{sum(par3_tee)/len(par3_tee):.1f} yds**")
    if par5_approach:
        st.write(f"Avg Approach (Par 5): **{sum(par5_approach)/len(par5_approach):.1f} yds**")

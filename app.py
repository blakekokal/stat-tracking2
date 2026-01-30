import streamlit as st
from dataclasses import dataclass, field
from typing import List, Optional
import pandas as pd

# ------------------------------
# Data Models
# ------------------------------
@dataclass
class Shot:
    shot_number: int
    distance: Optional[int]  # yards
    start_lie: str
    end_lie: str
    distance_to_hole: Optional[int] = None  # for putts

    def is_putt(self):
        return self.start_lie == "green"

    def category(self):
        if self.is_putt():
            return "putting"
        if self.shot_number == 1:
            return "tee"
        if self.distance and self.distance > 100:
            return "approach"
        return "short_game"

    def direction(self):
        for d in ["left", "right", "short", "long"]:
            if d in self.end_lie:
                return d
        if self.end_lie in ["fairway", "green"]:
            return "center"
        if self.end_lie == "hole":
            return "hole"
        return "unknown"

@dataclass
class Hole:
    hole_number: int
    par: int
    yardage: int
    shots: List[Shot] = field(default_factory=list)

    def strokes(self):
        return len(self.shots)

    def putts(self):
        return sum(s.is_putt() for s in self.shots)

    def fairway_result(self):
        if self.par < 4 or len(self.shots) == 0:
            return None
        return self.shots[0].direction()

    def gir(self):
        for i, s in enumerate(self.shots):
            if s.end_lie == "green":
                return (i + 1) <= (self.par - 2)
        return False

@dataclass
class Round:
    player_name: str
    course_name: str
    holes_played: int
    course_par: int
    holes: List[Hole] = field(default_factory=list)

    def total_score(self):
        return sum(h.strokes() for h in self.holes)

    def score_vs_par(self):
        return self.total_score() - self.course_par

    def total_putts(self):
        return sum(h.putts() for h in self.holes)

    def fairway_stats(self):
        results = [h.fairway_result() for h in self.holes if h.fairway_result()]
        return pd.Series(results).value_counts()

    def gir_stats(self):
        hits = sum(h.gir() for h in self.holes)
        return hits, len(self.holes)

    def directional_bias(self):
        dirs = []
        for h in self.holes:
            for s in h.shots:
                d = s.direction()
                if d not in ["center", "hole"]:
                    dirs.append(d)
        return pd.Series(dirs).value_counts()

    def strokes_by_category(self):
        buckets = {"tee":0,"approach":0,"short_game":0,"putting":0}
        for h in self.holes:
            for s in h.shots:
                buckets[s.category()] +=1
        return buckets

    def to_dataframe(self):
        rows = []
        for h in self.holes:
            for s in h.shots:
                rows.append([
                    self.player_name,
                    self.course_name,
                    h.hole_number,
                    h.par,
                    h.yardage,
                    s.shot_number,
                    s.distance,
                    s.start_lie,
                    s.end_lie,
                    s.distance_to_hole,
                    s.category(),
                    s.direction()
                ])
        return pd.DataFrame(rows, columns=[
            "Player","Course","Hole","Par","Hole_Yardage",
            "Shot#","Distance","Start_Lie","End_Lie",
            "Distance_to_Hole","Category","Direction"
        ])

# ------------------------------
# Initialize session state
# ------------------------------
for key, default in [
    ("round", None),
    ("current_hole", 1),
    ("current_shot", 1),
    ("current_hole_obj", None),
    ("hole_pars", {}),
    ("hole_yardages", {})
]:
    if key not in st.session_state:
        st.session_state[key] = default

# ------------------------------
# App UI
# ------------------------------
st.title("Golf Stat Tracker - Stepwise Shot Entry")
MAIN_LIES = ["fairway", "rough", "bunker", "water", "green", "hole"]

# ------------------------------
# Round Setup
# ------------------------------
if st.session_state.round is None:
    st.header("Round Setup")
    player = st.text_input("Player Name", key="player")
    course = st.text_input("Course Name", key="course")
    holes_played = st.number_input("Holes Played", min_value=1, max_value=18, value=18, step=1)
    course_par = st.number_input("Course Par", min_value=9, max_value=72, value=holes_played*4, step=1)

    if player and course:
        st.session_state.round = Round(player, course, holes_played, course_par)

# ------------------------------
# Hole & Shot Entry
# ------------------------------
elif st.session_state.current_hole <= st.session_state.round.holes_played:
    rnd = st.session_state.round
    hole_num = st.session_state.current_hole

    # Hole setup
    if st.session_state.current_hole_obj is None:
        st.subheader(f"Hole {hole_num} Setup")
        par = st.number_input(f"Hole {hole_num} Par", min_value=3, max_value=5, step=1, key=f"par{hole_num}")
        yardage = st.number_input(f"Hole {hole_num} Yardage", min_value=50, max_value=800, step=1, key=f"yard{hole_num}")
        if st.button("Start Hole"):
            st.session_state.current_hole_obj = Hole(hole_num, par, yardage)
            st.session_state.current_shot = 1
            st.experimental_rerun()

    # Shot entry with buttons
    else:
        shot_num = st.session_state.current_shot
        st.subheader(f"Hole {hole_num} - Shot {shot_num}")
        start_lie = "tee" if shot_num==1 else st.session_state.current_hole_obj.shots[-1].end_lie

        # Distance for non-putts
        distance = None
        if start_lie != "green":
            distance = st.number_input("Shot distance (yards)", min_value=0, step=1, format="%d", key=f"dist_{hole_num}_{shot_num}")

        # Shot buttons
        st.write("Where did the ball go?")
        cols = st.columns(len(MAIN_LIES))
        clicked_lie = None
        for i, lie in enumerate(MAIN_LIES):
            if cols[i].button(lie.capitalize(), key=f"btn_{hole_num}_{shot_num}_{lie}"):
                clicked_lie = lie

        if clicked_lie:
            end_lie = clicked_lie
            distance_to_hole = None

            # Stepwise side selection
            if end_lie == "rough":
                side = st.radio("Which rough?", ["left rough","right rough","short rough","long rough"], key=f"rough_{hole_num}_{shot_num}")
                end_lie = side
            elif end_lie == "bunker":
                side = st.radio("Which bunker?", ["left bunker","right bunker","fairway bunker"], key=f"bunker_{hole_num}_{shot_num}")
                end_lie = side
            elif end_lie == "water":
                side = st.radio("Which water?", ["left water","right water","long water"], key=f"water_{hole_num}_{shot_num}")
                end_lie = side
            elif end_lie == "green":
                distance_to_hole = st.number_input("Distance from hole (ft)", min_value=0, step=1, format="%d", key=f"puttdist_{hole_num}_{shot_num}")

            # Save shot
            st.session_state.current_hole_obj.shots.append(
                Shot(shot_num, distance, start_lie, end_lie, distance_to_hole)
            )

            # Move to next shot or hole
            if end_lie == "hole":
                rnd.holes.append(st.session_state.current_hole_obj)
                st.session_state.current_hole += 1
                st.session_state.current_shot = 1
                st.session_state.current_hole_obj = None
            else:
                st.session_state.current_shot += 1

            st.experimental_rerun()

# ------------------------------
# Round Summary & Export
# ------------------------------
elif st.session_state.current_hole > st.session_state.round.holes_played:
    rnd = st.session_state.round
    st.header("🏁 Round Summary")

    fw = rnd.fairway_stats()
    gir_hit, gir_total = rnd.gir_stats()
    bias = rnd.directional_bias()
    sg = rnd.strokes_by_category()

    # Score
    st.subheader("Score")
    st.metric("Total Score", rnd.total_score())
    st.metric("Score vs Par", rnd.score_vs_par())

    # Fairways
    st.subheader("Fairways")
    st.write(f"Hit (Center): {fw.get('center',0)}, Left: {fw.get('left',0)}, Right: {fw.get('right',0)}")

    # GIR
    st.subheader("Greens in Regulation")
    st.write(f"{gir_hit}/{gir_total} ({round((gir_hit/gir_total)*100,1)}%)")

    # Putting
    st.subheader("Putting")
    st.write(f"Total Putts: {rnd.total_putts()}")
    st.write(f"Putts per Hole: {round(rnd.total_putts()/len(rnd.holes),2) if len(rnd.holes) else 0}")
    st.write(f"Putts per GIR: {round(rnd.total_putts()/gir_hit,2) if gir_hit else 'N/A'}")

    # Miss tendency
    st.subheader("Miss Tendency")
    st.write(bias if not bias.empty else "No misses")

    # Shots by category
    st.subheader("Shots by Category")
    st.write(sg)

    # Export
    st.subheader("Export Round Data")
    df = rnd.to_dataframe()
    excel_file = "round.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file,"rb") as f:
        st.download_button("Download Excel", data=f, file_name="round.xlsx")
    csv_file = "round.csv"
    df.to_csv(csv_file, index=False)
    with open(csv_file,"rb") as f:
        st.download_button("Download CSV", data=f, file_name="round.csv")

    st.success("Round complete! Download your Excel or CSV file above.")

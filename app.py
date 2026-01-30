# ------------------------------
# Round Summary and Export
# ------------------------------

if st.session_state.round is not None and st.session_state.current_hole > st.session_state.round.holes_played:
    rnd = st.session_state.round

    st.header("🏁 Round Summary")
    
    # Fairways and GIR
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
    
    # Strokes by category
    st.subheader("Shots by Category")
    st.write(sg)
    
    # ------------------------------
    # Export
    # ------------------------------
    st.subheader("Export Round Data")
    df = rnd.to_dataframe()
    
    # Export Excel
    excel_file = "round.xlsx"
    df.to_excel(excel_file, index=False)
    with open(excel_file, "rb") as f:
        st.download_button("Download Excel", data=f, file_name="round.xlsx")
    
    # Optionally, export CSV (good for Google Sheets offline import)
    csv_file = "round.csv"
    df.to_csv(csv_file, index=False)
    with open(csv_file, "rb") as f:
        st.download_button("Download CSV", data=f, file_name="round.csv")
    
    st.success("Round complete! Download your Excel or CSV file above.")

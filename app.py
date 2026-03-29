import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go 

base_df = pd.read_csv("prospects.csv")
base_df.columns = base_df.columns.str.strip()
base_df = base_df.rename(columns={"College": "School"})


st.set_page_config(page_title="Vikings Draft Hub", layout="wide")
# -------------------------
# HEADER + TOP RIGHT MENU
# -------------------------
header_left, header_right = st.columns([6,1])

with header_left:
    st.title("Minnesota Vikings Draft Hub")

with header_right:
    page = st.selectbox(
        "",
        ["Main App", "Vikings Depth Chart", "Community Forum", "Why This Model Works"]
    )

# Sample prospect dataset (can be replaced by upload)
default_data = [
    {"Player": "Mansoor Delane", "Position": "CB", "College": "Colorado", "Grade": 94,
     "Size": 85, "Speed": 82, "Versatility": 93, "Pressure": 60},
    {"Player": "Fernando Mendoza", "Position": "QB", "College": "North Carolina", "Grade": 92,
     "Size": 90, "Speed": 83, "Versatility": 85, "Pressure": 50},
    {"Player": "Peter Woods", "Position": "DT", "College": "Illinois", "Grade": 90,
     "Size": 95, "Speed": 72, "Versatility": 78, "Pressure": 92},
    {"Player": "David Bailey", "Position": "EDGE", "College": "Alabama", "Grade": 93,
     "Size": 86, "Speed": 94, "Versatility": 88, "Pressure": 95},
    {"Player": "Jermod McCoy", "Position": "CB", "College": "Alabama", "Grade": 91,
     "Size": 84, "Speed": 92, "Versatility": 90, "Pressure": 65},
]

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Draft Index", "Big Board", "Player Fits", "Draft Simulator", "Build Draft Model", "Player Comparison"])

# ---------------- TAB 1 ----------------
with tab1: 
    st.title(" Vikings Draft Analytics Lab") 

    st.write("""
    Welcome to the **Vikings Draft Site**, a scouting and analytics platform built to evaluate how NFL draft prospects fit 
    with the Minnesota Vikings' under **Kevin O'Connell** and **Brian Flores**. 

    This project blends  **statistical modeling**, and **custom fit scores** to create an advanced
    way to think about the draft beyond just mock boards.
    """)

    st.subheader("Vikings Draft Guide") 

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Prospects Tracked", 150)
        st.write("Custom scouting database with positional traits and analytics.")

    with col2:
        st.metric("KOC & Flo Fit Models", 3) 
        st.write("Scheme-based scoring for offense and defense.")

    with col3:
        st.metric("Draft Tools", 5)
        st.write("Big board, comparisons, simulators, and filters.")

    st.subheader("Scouting Process") 

    st.write("""
    Instead of ranking players only by hype, this site focuses on **scheme fit**, **versatility**, and **impact traits**.

    For defense, Brian Flores values **positional versatility, athleticism, pressure ability, and football IQ**.   
    For offense, Kevin O'Connell emphasizes **separation, processing, and situational awareness**.

    Each prospect has a **custom fit score** based on how well they fit under the Minnesota Vikings' system. 
    """)

    st.subheader("Explore") 

    st.write("""
    Use the tabs above to:
    - View the **Vikings Big Board**
    - Customize the **Flores Fit Model**
    - Compare prospects across positions
    - Simulate draft strategies
    """)
    
# ---------------- TAB 2 ----------------
with tab2:

    import pandas as pd
    import streamlit as st

    st.header("Big Board")

    df = base_df.copy()

    # -------------------------
    # FIX NUMERIC COLUMNS
    # -------------------------
    df["Rank"] = pd.to_numeric(df["Rank"], errors="coerce")
    df["Grade"] = pd.to_numeric(df["Grade"], errors="coerce")
    df["Athleticism"] = pd.to_numeric(df["Athleticism"], errors="coerce")
    df["Production"] = pd.to_numeric(df["Production"], errors="coerce")
    df["Weight"] = pd.to_numeric(df["Weight"], errors="coerce")

    # -------------------------
    # FIX HEIGHT CONVERSION
    # -------------------------
    def convert_height(height_val):

        if pd.isna(height_val):
            return ""

        height_str = str(height_val).strip()

        if "'" in height_str:
            return height_str

        month_map = {
            "Jan":1,"Feb":2,"Mar":3,"Apr":4,
            "May":5,"Jun":6,"Jul":7,"Aug":8,
            "Sep":9,"Oct":10,"Nov":11,"Dec":12
        }

        try:
            if "-" in height_str:

                part1, part2 = height_str.split("-")

                feet = month_map.get(part1, part1)

                feet = int(feet)
                inches = int(part2)

                return f"{feet}'{inches}\""

        except:
            return height_str

        return height_str


    df["Height"] = df["Height"].apply(convert_height)

    # -------------------------
    # SORT BY YOUR ORIGINAL RANK
    # -------------------------
    df = df.sort_values("Rank")

    # -------------------------
    # FILTER LAYOUT (YOUR ORIGINAL STYLE)
    # -------------------------
    col1, col2, col3 = st.columns(3)

    with col1:
        pos_filter = st.multiselect(
            "Filter by Position",
            options=sorted(df["Position"].dropna().unique()),
            default=[]
        )

    with col2:
        grade_slider = st.slider(
            "Minimum Grade",
            min_value=0.0,
            max_value=100.0,
            value=70.0,
            step=0.1
        )

    with col3:
        search = st.text_input("Search Player")


    # -------------------------
    # APPLY FILTERS
    # -------------------------
    filtered_df = df.copy()

    if pos_filter:
        filtered_df = filtered_df[
            filtered_df["Position"].isin(pos_filter)
        ]

    filtered_df = filtered_df[
        filtered_df["Grade"] >= grade_slider
    ]

    if search:
        filtered_df = filtered_df[
            filtered_df["Player"].str.contains(search, case=False, na=False)
        ]


    # -------------------------
    # DISPLAY TABLE
    # -------------------------
    st.dataframe(

        filtered_df[
            [
                "Rank",
                "Player",
                "Position",
                "School",
                "Height",
                "Weight",
                "Athleticism",
                "Production",
                "Grade"
            ]
        ],

        use_container_width=True,
        hide_index=True

    )

    st.caption(f"Showing {len(filtered_df)} players")
# ---------------- TAB 3 ----------------
with tab3:

    st.header("Minnesota Vikings Scheme Fits")

    offense_df = pd.read_csv("kocreal.csv")
    defense_df = pd.read_csv("flores.csv")

    off_tab, def_tab = st.tabs(["KOC Offense", "Flores Defense"])

    # ---------------- OFFENSE ---------------- #

    with off_tab:

        st.subheader("Kevin O'Connell Offensive Scheme Fits")

        st.write(
        "O'Connell's offense values athleticism, explosiveness, intelligence, and versatility."
        )

        offense_df["Scheme_Fit"] = (
            offense_df["Athleticism"] * 0.25 +
            offense_df["Explosiveness"] * 0.25 +
            offense_df["Skill"] * 0.25 +
            offense_df["IQ"] * 0.15 +
            offense_df["Versatility"] * 0.10
        )

        offense_df = offense_df.sort_values("Scheme_Fit", ascending=False)

        offense_df = offense_df.reset_index(drop=True)
        offense_df.index = offense_df.index + 1

        board = st.dataframe(
            (offense_df[["Player","Position","School","Scheme_Fit"]]
            .rename(columns={"Scheme_Fit":"Scheme Fit"})),
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if board.selection.rows:

            row_index = board.selection.rows[0]
            player_data = offense_df.iloc[row_index]

            @st.dialog(player_data["Player"])
            def offense_player_profile():

                position = player_data["Position"]

                st.markdown(f"### {player_data['Player']} — {position}")

                traits = {
                    "Athleticism": player_data["Athleticism"],
                    "Explosiveness": player_data["Explosiveness"],
                    "Skill": player_data["Skill"],
                    "IQ": player_data["IQ"],
                    "Versatility": player_data["Versatility"]
                }

                cols = st.columns(len(traits))

                for col,(trait,value) in zip(cols,traits.items()):
                    col.metric(trait,f"{value}")

                labels = list(traits.keys())
                values = list(traits.values())

                # Normalize traits so radar charts differ more
                max_val = max(values)
                values = [(v/max_val)*100 for v in values]

                labels.append(labels[0])
                values.append(values[0])

                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    fillcolor='rgba(79,38,131,0.35)',
                    line=dict(width=2)
                ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0,100],
                            tickvals=[20,40,60,80,100]
                        )
                    ),
                    showlegend=False
                )

                st.plotly_chart(fig,use_container_width=True)

            offense_player_profile()


    # ---------------- DEFENSE ---------------- #

    with def_tab:

        st.subheader("Brian Flores Defensive Scheme Fits")

        st.write(
        "Flores' defense emphasizes versatility, pressure ability, football IQ, and tackling."
        )

        def calculate_flores_fit(row):

            if row["Position"] in ["CB","SAF"]:

                score = (
                    row["Versatility"] * 0.25 +
                    row["Run Defense"] * 0.15 +
                    row["Football IQ"] * 0.25 +
                    row["Zone Cov."] * 0.25 +
                    row["Man Cov."] * 0.10
                )

            else:

                score = (
                    row["Versatility"] * 0.35 +
                    row["Pressure Ability"] * 0.20 +
                    row["Run Defense"] * 0.20 +
                    row["Football IQ"] * 0.25
                )

            return round(score,2)

        defense_df["Scheme_Fit"] = defense_df.apply(calculate_flores_fit,axis=1)

        defense_df = defense_df.sort_values("Scheme_Fit",ascending=False)

        defense_df = defense_df.reset_index(drop=True)
        defense_df.index = defense_df.index + 1

        board = st.dataframe(
            (defense_df[["Player","Position","School","Scheme_Fit"]]
            .rename(columns={"Scheme_Fit":"Scheme Fit"})),
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if board.selection.rows:

            row_index = board.selection.rows[0]
            player_data = defense_df.iloc[row_index]

            @st.dialog(player_data["Player"])
            def defense_player_profile():

                position = player_data["Position"]

                st.markdown(f"### {player_data['Player']} — {position}")

                if position in ["CB","SAF"]:

                    traits = {
                        "Versatility": player_data["Versatility"],
                        "Run Defense": player_data["Run Defense"],
                        "Football IQ": player_data["Football IQ"],
                        "Zone Cov.": player_data["Zone Cov."],
                        "Man Cov.": player_data["Man Cov."]
                    }

                else:

                    traits = {
                        "Versatility": player_data["Versatility"],
                        "Pressure Ability": player_data["Pressure Ability"],
                        "Run Defense": player_data["Run Defense"],
                        "Football IQ": player_data["Football IQ"]
                    }

                cols = st.columns(len(traits))

                for col,(trait,value) in zip(cols,traits.items()):
                    col.metric(trait,f"{value}")

                labels = list(traits.keys())
                values = list(traits.values())

                max_val = max(values)
                values = [(v/max_val)*100 for v in values]

                labels.append(labels[0])
                values.append(values[0])

                fig = go.Figure()

                fig.add_trace(go.Scatterpolar(
                    r=values,
                    theta=labels,
                    fill='toself',
                    fillcolor='rgba(79,38,131,0.35)',
                    line=dict(width=2)
                ))

                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(
                            visible=True,
                            range=[0,100],
                            tickvals=[20,40,60,80,100]
                        )
                    ),
                    showlegend=False
                )

                st.plotly_chart(fig,use_container_width=True)

            defense_player_profile()


with tab4:

    st.header("Vikings Draft Strategy Simulator")

    offense_df = pd.read_csv("kocreal.csv")
    defense_df = pd.read_csv("flores.csv")

    # -------------------------
    # COLLEGE LOGOS
    # -------------------------

    college_logos = {
        "Oregon": "https://a.espncdn.com/i/teamlogos/ncaa/500/2483.png",
        "Clemson": "https://a.espncdn.com/i/teamlogos/ncaa/500/228.png",
        "Toledo": "https://a.espncdn.com/i/teamlogos/ncaa/500/2649.png",
        "Arizona State": "https://a.espncdn.com/i/teamlogos/ncaa/500/9.png",
        "Notre Dame": "https://a.espncdn.com/i/teamlogos/ncaa/500/87.png",
        "Oklahoma": "https://a.espncdn.com/i/teamlogos/ncaa/500/201.png",
        "Texas Tech": "https://a.espncdn.com/i/teamlogos/ncaa/500/2641.png",
        "San Diego State": "https://a.espncdn.com/i/teamlogos/ncaa/500/21.png",
        "LSU": "https://a.espncdn.com/i/teamlogos/ncaa/500/99.png",
        "Auburn": "https://a.espncdn.com/i/teamlogos/ncaa/500/2.png",
        "USC": "https://a.espncdn.com/i/teamlogos/ncaa/500/30.png",
        "Kansas State": "https://a.espncdn.com/i/teamlogos/ncaa/500/2306.png",
        "UConn": "https://a.espncdn.com/i/teamlogos/ncaa/500/41.png",
        "Iowa": "https://a.espncdn.com/i/teamlogos/ncaa/500/2294.png",
        "North Dakota State": "https://a.espncdn.com/i/teamlogos/ncaa/500/2449.png",
        "Florida": "https://a.espncdn.com/i/teamlogos/ncaa/500/57.png",
        "Penn State": "https://a.espncdn.com/i/teamlogos/ncaa/500/213.png"
    }

    # -------------------------
    # TEAM NEED GRID
    # -------------------------

    st.subheader("Team Needs")

    team_needs = {
        "DT":9,"OC":9,"SAF":8,"RB":8,"WR":7,"CB":7,
        "OT":6,"TE":6,"EDGE":4,"LB":3,"OG":3,"QB":2
    }

    def need_color(score):
        if score >= 8:
            return "#ff4d4d"
        elif score >= 5:
            return "#ffd24d"
        else:
            return "#66cc66"

    positions = sorted(team_needs, key=lambda x: team_needs[x], reverse=True)

    row1 = st.columns(6)
    row2 = st.columns(6)

    for i, pos in enumerate(positions[:6]):
        row1[i].markdown(
            f"""<div style="background:{need_color(team_needs[pos])};
            padding:8px;text-align:center;border-radius:8px;
            font-weight:bold;font-size:13px;">{pos}</div>""",
            unsafe_allow_html=True
        )

    for i, pos in enumerate(positions[6:]):
        row2[i].markdown(
            f"""<div style="background:{need_color(team_needs[pos])};
            padding:8px;text-align:center;border-radius:8px;
            font-weight:bold;font-size:13px;">{pos}</div>""",
            unsafe_allow_html=True
        )

    # -------------------------
    # SCHEME FIT
    # -------------------------

    offense_df["Scheme_Fit"] = (
        offense_df["Athleticism"]*0.25 +
        offense_df["Explosiveness"]*0.25 +
        offense_df["Skill"]*0.25 +
        offense_df["IQ"]*0.15 +
        offense_df["Versatility"]*0.10
    )

    def flores_fit(row):
        if row["Position"] in ["CB","SAF"]:
            return (
                row["Versatility"]*0.25 +
                row["Run Defense"]*0.15 +
                row["Football IQ"]*0.25 +
                row["Zone Cov."]*0.25 +
                row["Man Cov."]*0.10
            )
        else:
            return (
                row["Versatility"]*0.35 +
                row["Pressure Ability"]*0.20 +
                row["Run Defense"]*0.20 +
                row["Football IQ"]*0.25
            )

    defense_df["Scheme_Fit"] = defense_df.apply(flores_fit, axis=1)

    prospects = pd.concat([offense_df, defense_df], ignore_index=True)

    prospects["Need_Score"] = prospects["Position"].map(team_needs).fillna(3)

    # -------------------------
    # RECOMMENDED PLAYERS
    # -------------------------

    recommended_players = {
        18: ["Dillon Thieneman", "Avieon Terrell", "Emmanuel McNeil-Warren", "Peter Woods", "Jordyn Tyson"],
        49: ["Jadarian Price", "Gracen Halton", "Lee Hunter", "Chris Johnson", "AJ Haulcy"],
        82: ["Connor Lew", "Ja'Kobi Lane", "Sam Hecht", "Skyler Bell", "Antonio Williams"],
        97: ["Logan Jones", "Bryce Lance", "Jake Slaughter", "VJ Payne", "Zakee Wheatley"]
    }

    # -------------------------
    # PICK BUTTONS (STATE FIX)
    # -------------------------

    if "selected_pick" not in st.session_state:
        st.session_state.selected_pick = 18

    pick_cols = st.columns(4)

    if pick_cols[0].button("18"): st.session_state.selected_pick = 18
    if pick_cols[1].button("49"): st.session_state.selected_pick = 49
    if pick_cols[2].button("82"): st.session_state.selected_pick = 82
    if pick_cols[3].button("97"): st.session_state.selected_pick = 97

    selected_pick = st.session_state.selected_pick

    st.subheader(f"Recommended Players at Pick {selected_pick}")

    # -------------------------
    # PLAYER DISPLAY (WITH LOGOS)
    # -------------------------

    cols = st.columns(5)

    for col, player_name in zip(cols, recommended_players[selected_pick]):

        player_row = prospects[prospects["Player"] == player_name]

        if player_row.empty:
            col.warning("Missing Data")
            continue

        player_row = player_row.iloc[0]

        logo = college_logos.get(player_row["School"], None)

        inner = col.columns([1,3])

        if logo:
            inner[0].image(logo, width=40)

        inner[1].markdown(f"""
        **{player_row['Player']}**  
        {player_row['Position']} | {player_row['School']}
        """)

        col.markdown(f"""
        Scheme Fit: {round(player_row['Scheme_Fit'],1)}  
        Team Need: {player_row['Need_Score']}
        """)

        # Profile button with unique key
        if col.button("Profile", key=f"{player_name}_{selected_pick}"):

            st.session_state["selected_player"] = player_name

    # -------------------------
    # POPUP PROFILE (ONLY ONE)
    # -------------------------

    if "selected_player" in st.session_state:

        player_name = st.session_state["selected_player"]
        player_row = prospects[prospects["Player"] == player_name].iloc[0]

        @st.dialog(player_name)
        def show_profile():

            st.markdown(f"### {player_row['Player']} — {player_row['Position']}")

            if player_row["Position"] in ["CB","SAF"]:
                traits = {
                    "Versatility": player_row["Versatility"],
                    "Run Defense": player_row["Run Defense"],
                    "Football IQ": player_row["Football IQ"],
                    "Zone Cov.": player_row["Zone Cov."],
                    "Man Cov.": player_row["Man Cov."]
                }
            else:
                traits = {
                    "Versatility": player_row.get("Versatility",0),
                    "Pressure Ability": player_row.get("Pressure Ability",0),
                    "Run Defense": player_row.get("Run Defense",0),
                    "Football IQ": player_row.get("Football IQ",0)
                }

            cols_traits = st.columns(len(traits))
            for c,(t,v) in zip(cols_traits,traits.items()):
                c.metric(t,v)

            labels = list(traits.keys())
            values = list(traits.values())

            labels.append(labels[0])
            values.append(values[0])

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=labels,
                fill='toself'
            ))

            fig.update_layout(
                polar=dict(radialaxis=dict(range=[0,100])),
                showlegend=False
            )

            st.plotly_chart(fig, use_container_width=True)

            if st.button("Close"):
                del st.session_state["selected_player"]

        show_profile()

with tab5:
    
    st.header("Vikings Draft Model")

    # -------------------------
    # LOAD DATA
    # -------------------------
    offense_df = pd.read_csv("kocreal.csv")
    defense_df = pd.read_csv("flores.csv")

    # -------------------------
    # CREATE UNIVERSAL VIKINGS FIT (FOR ALL PLAYERS)
    # -------------------------
    base = base_df.copy()

    base["Athleticism"] = pd.to_numeric(base["Athleticism"], errors="coerce").fillna(70)
    base["Production"] = pd.to_numeric(base["Production"], errors="coerce").fillna(70)

    # 🔥 THIS FIXES YOUR PROBLEM → applies to ALL 150 players
    base["Vikings_Fit"] = (
        base["Athleticism"] * 0.6 +
        base["Production"] * 0.4
    )

    # -------------------------
    # SEARCH BAR (🔥 BIG FEATURE)
    # -------------------------
    st.subheader("Search Any Prospect")

    search = st.text_input("Enter player name")

    if search:
        result = base[base["Player"].str.contains(search, case=False, na=False)]

        if not result.empty:
            player = result.iloc[0]

            st.markdown(f"### {player['Player']} ({player['Position']})")

            c1, c2, c3 = st.columns(3)

            c1.metric("Vikings Fit", round(player["Vikings_Fit"], 1))
            c2.metric("Athleticism", player["Athleticism"])
            c3.metric("Production", player["Production"])

        else:
            st.warning("Player not found")

    st.markdown("---")

    # -------------------------
    # TEAM NEEDS
    # -------------------------
    team_needs = {
        "DT":9,"OC":9,"SAF":8,"RB":8,"WR":7,"CB":7,
        "OT":6,"TE":6,"EDGE":4,"LB":3,"OG":3,"QB":2
    }

    base["Need_Score"] = base["Position"].map(team_needs).fillna(3)

    # -------------------------
    # BIG BOARD BASELINE
    # -------------------------
    base = base.reset_index(drop=True)
    base["BigBoard"] = len(base) - base.index

    # -------------------------
    # MODEL TYPES (NO SLIDERS)
    # -------------------------
    st.subheader("Model Type")

    c1, c2, c3 = st.columns(3)

    if "weights" not in st.session_state:
        st.session_state.weights = {"fit":50,"need":20,"board":30}

    if c1.button("Best Player Available"):
        st.session_state.weights = {"fit":60,"need":10,"board":30}

    if c2.button("Scheme Fit Focus"):
        st.session_state.weights = {"fit":70,"need":20,"board":10}

    if c3.button("Team Need Focus"):
        st.session_state.weights = {"fit":40,"need":50,"board":10}

    fit_w = st.session_state.weights["fit"]
    need_w = st.session_state.weights["need"]
    board_w = st.session_state.weights["board"]

    # -------------------------
    # NORMALIZATION (🔥 FIXES HUGE SCORES)
    # -------------------------
    base["Fit_N"] = base["Vikings_Fit"] / 100
    base["Need_N"] = base["Need_Score"] / 10
    base["Board_N"] = base["BigBoard"] / len(base)

    # -------------------------
    # FINAL SCORE
    # -------------------------
    base["Final_Score"] = (
        base["Fit_N"] * fit_w +
        base["Need_N"] * need_w +
        base["Board_N"] * board_w
    )

    base = base.sort_values("Final_Score", ascending=False).reset_index(drop=True)
    base.index += 1

    # -------------------------
    # VALUE TAG (🔥 COOL FEATURE)
    # -------------------------
    pos_avg = base.groupby("Position")["Final_Score"].mean().to_dict()

    def value_tag(pos):
        v = pos_avg.get(pos,0)
        if v > 0.65:
            return " High Value"
        elif v > 0.5:
            return "Solid"
        else:
            return "Low"

    base["Value"] = base["Position"].apply(value_tag)

    # -------------------------
    # FINAL BOARD (ALL 150 PLAYERS)
    # -------------------------
    st.subheader("Full Draft Board")

    st.dataframe(
        base[["Player","Position","School","Final_Score","Value"]],
        use_container_width=True
    )
with tab6:

    st.header("Player Comparison Tool")

    df = base_df.copy()

    df["Athleticism"] = pd.to_numeric(df["Athleticism"], errors="coerce").fillna(70)
    df["Production"] = pd.to_numeric(df["Production"], errors="coerce").fillna(70)

    df["Vikings_Fit"] = (
        df["Athleticism"] * 0.6 +
        df["Production"] * 0.4
    )

    team_needs = {
        "DT":9,"OC":9,"SAF":8,"RB":8,"WR":7,"CB":7,
        "OT":6,"TE":6,"EDGE":4,"LB":3,"OG":3,"QB":2
    }

    df["Need_Score"] = df["Position"].map(team_needs).fillna(3)

    col1, col2 = st.columns(2)

    with col1:
        p1_name = st.text_input("Player 1")

    with col2:
        p2_name = st.text_input("Player 2")

    def get_player(name):
        res = df[df["Player"].str.contains(name, case=False, na=False)]
        return res.iloc[0] if not res.empty else None

    p1 = get_player(p1_name) if p1_name else None
    p2 = get_player(p2_name) if p2_name else None

    if p1 is not None and p2 is not None:

        c1, c2 = st.columns(2)

        for col, p in zip([c1, c2], [p1, p2]):

            col.markdown(f"### {p['Player']}")
            col.write(f"{p['Position']} | {p['School']}")

            col.metric("Vikings Fit", round(p["Vikings_Fit"],1))
            col.metric("Team Need", p["Need_Score"])

            col.metric("Athleticism", p["Athleticism"])
            col.metric("Production", p["Production"])

        def find_comp(player, df):

            df["distance"] = (
                (df["Athleticism"] - player["Athleticism"])**2 +
                (df["Production"] - player["Production"])**2
            )

            comp = df.sort_values("distance").iloc[1]
            return comp["Player"]

        st.markdown("---")
        st.subheader("Closest Player Comparison")

        st.write(f"{p1['Player']} → {find_comp(p1, df)}")
        st.write(f"{p2['Player']} → {find_comp(p2, df)}")
    

if page == "Vikings Depth Chart":

    st.header("Minnesota Vikings Depth Chart")
    # ------------------------
    # DEPTH CHART (4 SLOTS)
    # ------------------------
    depth_data = [
        ["QB","Kyler Murray","J.J. McCarthy","Carson Wentz","Max Brosmer"],
        ["RB","Aaron Jones","Jordan Mason","Zavier Scott",""],

        ["WR","Justin Jefferson","Jeshaun Jones","",""],
        ["WR","Jordan Addison","Myles Price","",""],
        ["WR","Tai Felton","","",""],

        ["TE","T.J. Hockenson","Josh Oliver","Ben Yurosek","Gavin Bartholomew"],

        ["LT","Christian Darrisaw","Ryan Van Demark","",""],
        ["LG","Donovan Jackson","Joe Huber","",""],
        ["C","Michael Jurgens","Blake Brandel","",""],
        ["RG","Will Fries","","",""],
        ["RT","Brian O'Neill","Walter Rouse","",""],

        ["DT","Jalen Redmond","Tyrion Ingram-Dawkins","",""],
        ["DT","Levi Drake Rodriguez","Taki Taimani","",""],
       

        ["EDGE","Jonathan Greenard","Dallas Turner",""],
        ["EDGE","Andrew Van Ginkel","Bo Richter","",""],

        ["LB","Blake Cashman","Ivan Pace Jr.","",""],
        ["LB","Eric Wilson","","",""],

        ["CB","Isaiah Rodgers","Dwight McGlothern","",""],
        ["CB","James Pierre","","",""],
        ["CB","Byron Murphy Jr","","",""],

        ["SAF","Harrison Smith","Theo Jackson",""],
        ["SAF","Josh Metellus","","",""]
    ]

    depth_df = pd.DataFrame(depth_data)
    depth_df.columns = ["Position","","","",""]

    position_strength = {
        "QB": 8, "RB": 6, "WR": 10, "TE": 8,
        "LT": 9, "LG": 6, "C": 5, "RG": 5, "RT": 9,
        "DT": 3, "EDGE": 7, "LB": 7, "CB": 4, "SAF": 3
    }

    def color_position(pos):
        score = position_strength.get(pos, 5)
        if score <= 4:
            return f"<span style='color:red; font-weight:bold'>{pos}</span>"
        elif score <= 6:
            return f"<span style='color:orange; font-weight:bold'>{pos}</span>"
        else:
            return f"<span style='color:green; font-weight:bold'>{pos}</span>"

    depth_df["Position"] = depth_df["Position"].apply(color_position)

    left, right = st.columns([3,2])

    with left:
        st.markdown(
            depth_df.to_html(escape=False, index=False),
            unsafe_allow_html=True
        )

    with right:
        st.subheader("Draft Targets")

        if "selected_position" not in st.session_state:
            st.session_state.selected_position = None

        row1 = st.columns(4)
        row2 = st.columns(4)
        row3 = st.columns(4)

        positions_layout = [
            ["QB","RB","WR","TE"],
            ["OT","OG","OC","EDGE"],
            ["DT","LB","CB","SAF"]
        ]

        rows = [row1, row2, row3]

        for r_idx, row in enumerate(rows):
            for c_idx, col in enumerate(row):
                pos = positions_layout[r_idx][c_idx]
                with col:
                    if st.button(pos):
                        st.session_state.selected_position = pos

        st.markdown("---")

        pos = st.session_state.selected_position

        if pos is None:
            st.write("Select a position")
        else:
            st.write(f"Top 5 Prospects at {pos}")

            if "base_df" in globals():
                if pos == "OT":
                    filtered = base_df[base_df["Position"].isin(["LT","RT"])]
                elif pos == "OG":
                    filtered = base_df[base_df["Position"].isin(["LG","RG"])]
                elif pos == "OC":
                    filtered = base_df[base_df["Position"] == "C"]
                else:
                    filtered = base_df[base_df["Position"] == pos]

                if "Rating" in filtered.columns:
                    filtered = filtered.sort_values("Rating", ascending=False)

                top5 = filtered.head(5)

                for _, row in top5.iterrows():
                    st.write(f"- {row['Player']}")
            else:
                st.write("Big board not connected")

elif page == "Community Forum":

    st.header("Community")

    poll = st.radio(
        "What should the Vikings prioritize?",
        ["Defensive Line", "Secondary", "Offensive Line", "Best Player Available"]
    )

    if st.button("Submit Vote"):
        st.success(f"You voted for: {poll}")

    comment = st.text_input("Leave a comment")

    if st.button("Post"):
        st.write(f"User: {comment}")


elif page == "Why This Model Works":

    st.header("Why This Model Works")

    st.write("""
    This project simulates real NFL front office decision-making.

    The model combines:
    - Vikings Fit
    - Team Needs
    - Big Board ranking
    """)

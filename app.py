import streamlit as st
import pandas as pd
import pydeck as pdk

# --------------------
# Page config
# --------------------
st.set_page_config(
    page_title="AI Inference Readiness Map — Africa",
    layout="wide"
)

st.title("AI Inference Readiness Map — Africa (v0)")
st.caption(
    "Founder-facing decision-support tool showing where AI inference workloads "
    "can realistically be deployed across Africa today."
)

# --------------------
# Load data
# --------------------
df = pd.read_csv("data/ai_inference_readiness_africa_v0.csv")

# --------------------
# Map readiness to colors
# --------------------
color_map = {
    "Viable": [26, 150, 65],
    "Emerging": [253, 174, 97],
    "Emerging (Early)": [215, 25, 28],
}

df["color"] = df["ai_inference_readiness"].map(color_map)

# --------------------
# Country detail panel
# --------------------
st.subheader("Country-level AI inference details")

selected_country = st.selectbox(
    "Select a country:",
    sorted(df["country"].unique()),
    index=0
)

# --------------------
# Africa map (DOTS – PyDeck)
# --------------------
st.subheader("AI Inference Readiness — Geographic View")

MAPBOX_TOKEN = st.secrets["MAPBOX_TOKEN"]

# --------------------
# Dynamic view state (cinematic zoom)
# --------------------
if selected_country:
    selected_row = df[df["country"] == selected_country].iloc[0]

    view_state = pdk.ViewState(
        latitude=selected_row["latitude"],
        longitude=selected_row["longitude"],
        zoom=4.5,
        transition_duration=1200,
    )
else:
    view_state = pdk.ViewState(
        latitude=0,
        longitude=20,
        zoom=2.5,
    )

layer = pdk.Layer(
    "ScatterplotLayer",
    data=df,
    get_position=["longitude", "latitude"],
    get_color="color",
    get_radius=180000,
    pickable=True,
)

st.pydeck_chart(
    pdk.Deck(
        map_style="mapbox://styles/mapbox/light-v11",
        api_keys={"mapbox": MAPBOX_TOKEN},
        layers=[layer],
        initial_view_state=view_state,
        tooltip={
            "html": "<b>{country}</b><br/>Readiness: {ai_inference_readiness}",
            "style": {
                "backgroundColor": "rgba(255,255,255,0.95)",
                "color": "black",
                "border": "1px solid #ddd",
            },
        },
    ),
    use_container_width=True,
)

country = df[df["country"] == selected_country].iloc[0]

col1, col2 = st.columns(2)

with col1:
    st.markdown(f"### {selected_country}")
    st.markdown(f"**AI Inference Readiness:** {country['ai_inference_readiness']}")
    st.markdown(f"**Active Data Centers:** {country['active_data_centers']}")
    st.markdown(f"**DC Pipeline:** {country['dc_pipeline']}")
    st.markdown(f"**AI Compute Availability:** {country['ai_compute_availability']}")
    st.markdown(f"**Cloud Maturity:** {country['cloud_maturity']}")

with col2:
    st.markdown("### Infrastructure Context")
    st.markdown(f"**Connectivity Role:** {country['connectivity_role']}")
    st.markdown(f"**Power Reliability:** {country['power_reliability']}")
    st.markdown(f"**Ops Friction:** {country['ops_friction']}")
    st.markdown(f"**Data Residency Constraint:** {country['data_residency_constraint']}")

st.markdown("### Founder Insight")
st.info(country["founder_insight"])

st.markdown("---")
st.caption(
    "v0 focuses on AI inference feasibility (not training capacity). "
    "Data is directional and intended to support early-stage deployment decisions."
)
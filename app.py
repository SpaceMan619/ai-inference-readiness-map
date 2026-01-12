import streamlit as st
import pandas as pd
import plotly.express as px

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
# Map readiness to numeric scale (for colors)
# --------------------
readiness_map = {
    "Viable": 3,
    "Emerging": 2,
    "Emerging (Early)": 1
}
df["readiness_score"] = df["ai_inference_readiness"].map(readiness_map)

# --------------------
# Africa choropleth map
# --------------------
fig = px.choropleth(
    df,
    locations="country",
    locationmode="country names",
    color="readiness_score",
    hover_name="country",
    color_continuous_scale=["#d7191c", "#fdae61", "#1a9641"],
    range_color=(1, 3),
)

fig.update_layout(
    margin=dict(l=0, r=0, t=0, b=0),
    coloraxis_colorbar=dict(
        title="AI Inference Readiness",
        tickvals=[1, 2, 3],
        ticktext=["Emerging (Early)", "Emerging", "Viable"]
    )
)

st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# --------------------
# Country detail panel
# --------------------
st.subheader("Country-level AI inference details")

selected_country = st.selectbox(
    "Select a country:",
    df["country"].unique()
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

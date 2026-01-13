import streamlit as st
import pandas as pd
import pydeck as pdk

# --------------------
# 1. Page Configuration
# --------------------
st.set_page_config(
    page_title="AI Inference Readiness Map — Africa",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --------------------
# 2. Styling (CSS Tooltips & Legend)
# --------------------
st.markdown("""
<style>
    .block-container {padding-top: 1rem; padding-bottom: 2rem;}
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 0.75rem;
        padding: 1.5rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        height: 100%;
        position: relative; /* Context for tooltip positioning */
    }
    .metric-label {
        font-size: 0.875rem; 
        color: #6b7280; 
        font-weight: 500; 
        display: flex; 
        align-items: center; 
        gap: 6px;
    }
    .metric-value {
        font-size: 1.5rem; 
        color: #111827; 
        font-weight: 700; 
        margin-top: 0.25rem;
    }
    
    /* CSS Tooltip Implementation */
    .tooltip-container {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    .info-icon {
        color: #9ca3af;
        font-size: 0.85rem;
        transition: color 0.2s;
    }
    .tooltip-container:hover .info-icon {
        color: #3b82f6;
    }
    .tooltip-text {
        visibility: hidden;
        width: 220px;
        background-color: #1f2937; /* Dark Gray */
        color: #f9fafb;
        text-align: left;
        border-radius: 6px;
        padding: 8px 12px;
        font-size: 0.75rem;
        line-height: 1.4;
        font-weight: normal;
        
        /* Positioning */
        position: absolute;
        z-index: 10;
        bottom: 135%; /* Above the icon */
        left: 50%;
        margin-left: -110px; /* Center it */
        
        opacity: 0;
        transition: opacity 0.2s;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        pointer-events: none;
    }
    .tooltip-text::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: #1f2937 transparent transparent transparent;
    }
    .tooltip-container:hover .tooltip-text {
        visibility: visible;
        opacity: 1;
    }

    /* Legend Strip Styling */
    .legend-strip {
        display: flex;
        flex-wrap: wrap;
        gap: 20px;
        background: white;
        padding: 15px 20px;
        border-radius: 10px;
        border: 1px solid #e5e7eb;
        margin-bottom: 20px;
        margin-top: 20px;
        align-items: center;
        justify-content: space-around;
    }
    .legend-item {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.9rem;
        color: #374151;
    }
    .legend-icon {
        font-size: 1.2rem;
    }

    /* Insight Box */
    .insight-box {
        background-color: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        border-radius: 0 0.5rem 0.5rem 0;
        color: #334155;
        font-style: italic;
    }

    /* Badges */
    .badge {
        padding: 4px 10px;
        border-radius: 9999px;
        font-weight: 600;
        font-size: 0.75rem;
        display: inline-block;
    }
    .badge-viable {background-color: #dcfce7; color: #166534;}
    .badge-emerging {background-color: #fef3c7; color: #92400e;}
    .badge-early {background-color: #fee2e2; color: #991b1b;}
    .badge-strong {background-color: #1e40af; color: #eff6ff;} /* Deep Blue for Policy */
    .badge-unclear {background-color: #9ca3af; color: #f3f4f6;} 
    
    /* Mode Toggle Container */
    .mode-toggle-container {
        display: flex;
        justify-content: center;
        margin-bottom: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# --------------------
# 3. Data Loading
# --------------------
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("data/ai_inference_readiness_africa_v0.csv")
        # Clean column names to avoid KeyErrors from trailing spaces
        df.columns = df.columns.str.strip()

        # 1. Sanitize Coordinates
        df['latitude'] = pd.to_numeric(df['latitude'], errors='coerce')
        df['longitude'] = pd.to_numeric(df['longitude'], errors='coerce')
        df = df.dropna(subset=['latitude', 'longitude'])

        # ---------------------------
        # FALLBACK FOR MISSING V2 DATA
        # ---------------------------
        # Ensure v2 columns exist even if CSV is outdated, to prevent app crash
        v2_defaults = {
            'ai_policy_signal': 'Unclear',
            'ai_data_governance_posture': 'Unclear',
            'ai_compute_policy_commitment': 'Absent',
            'cross_border_ai_alignment': 'Unclear'
        }
        for col, default_val in v2_defaults.items():
            if col not in df.columns:
                df[col] = default_val

        # ---------------------------
        # FALLBACK FOR MISSING FOUNDER DATA (non-destructive)
        # ---------------------------
        founder_defaults = {
            'primary_inference_route': 'Unclear',
            'ai_compute_availability': 'Unclear',
            'power_reliability': 'Unclear',
            'cloud_maturity': 'Unclear',
            'ops_friction': 'Unclear',
            'founder_insight': 'Founder insight pending.',
        }
        for col, default_val in founder_defaults.items():
            if col not in df.columns:
                df[col] = default_val
            else:
                df[col] = df[col].fillna(default_val)

        # ---------------------------
        # COLOR MAPPING LOGIC
        # ---------------------------
        # 1. Founder Mode Colors (Readiness)
        founder_colors = {
            "Viable": [26, 150, 65],      # Green
            "Emerging": [253, 174, 97],   # Orange
            "Emerging (Early)": [215, 25, 28], # Red
        }
        # 2. Policy Mode Colors (Signal) - DIFFERENT PALETTE (Blues/Purples)
        policy_colors = {
            "Strong": [30, 64, 175],      # Strong Blue
            "Emerging": [96, 165, 250],   # Light Blue
            "Unclear": [156, 163, 175],   # Gray
        }
        # 3. Opacity
        opacities = {"Viable": 230, "Emerging": 190, "Emerging (Early)": 150}

        def get_founder_rgba(readiness):
            rgb = founder_colors.get(readiness, [128, 128, 128])
            alpha = opacities.get(readiness, 150)
            return rgb + [alpha]

        def get_policy_rgba(signal):
            rgb = policy_colors.get(signal, [128, 128, 128])
            # Policy mode: Make strong signals more opaque
            alpha = 240 if signal == "Strong" else (180 if signal == "Emerging" else 100)
            return rgb + [alpha]

        df["color_founder"] = df["ai_inference_readiness"].apply(get_founder_rgba)
        df["color_policy"] = df["ai_policy_signal"].apply(get_policy_rgba)
        # 4. Radius Mapping
        radius_map = {"Viable": 220000, "Emerging": 170000, "Emerging (Early)": 130000}
        df["radius"] = df["ai_inference_readiness"].map(radius_map).fillna(120000)
        return df
    except FileNotFoundError:
        return None
import numpy as np

def safe(val, fallback="Unclear"):
    import pandas as pd
    return val if pd.notna(val) and str(val).strip() != "" else fallback

df = load_data()

if df is None:
    st.error("⚠️ CSV Not Loaded. Please check data path.")
    st.stop()

# --------------------
# 4. Session State & Logic
# --------------------
if 'selected_country' not in st.session_state:
    st.session_state.selected_country = sorted(df["country"].unique())[0]

# --------------------
# 5. Header & Mode Switch
# --------------------
st.title("AI Inference Flow Map — Africa (v2)")
st.caption("Visual decision-support tool for AI inference paths (local, regional, offshore).")

# Mode Toggle
col_mode_spacer, col_mode, col_mode_spacer2 = st.columns([3, 2, 3])
with col_mode:
    view_mode = st.radio(
        "Layer View:",
        ["Founder Mode", "Policy Mode"],
        horizontal=True,
        label_visibility="collapsed"
    )

is_policy_mode = view_mode == "Policy Mode"

# Top Level Metrics - DYNAMIC based on mode
m1, m2, m3 = st.columns(3)

def render_summary_card(col, label, value, subtext):
    with col:
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <div style="color: #6b7280; font-size: 0.875rem; font-weight: 500; margin-bottom: 0.5rem;">
                {label}
            </div>
            <div style="color: #111827; font-size: 2.25rem; font-weight: 700; line-height: 1;">
                {value}
            </div>
            <div style="color: #9ca3af; font-size: 0.75rem; margin-top: 0.5rem;">
                {subtext}
            </div>
        </div>
        """, unsafe_allow_html=True)

if is_policy_mode:
    # Policy Metrics
    strong_policy = len(df[df['ai_policy_signal'] == 'Strong'])
    data_open = len(df[df['ai_data_governance_posture'] == 'Flexible'])
    explicit_compute = len(df[df['ai_compute_policy_commitment'] == 'Explicit'])
    
    render_summary_card(m1, "Markets w/ AI Strategy", strong_policy, "Official strategy + execution signals")
    render_summary_card(m2, "Flexible Data Governance", data_open, "Supportive of AI data flows")
    render_summary_card(m3, "Compute Commitment", explicit_compute, "Explicit state-backed infrastructure")
else:
    # Founder Metrics (v1)
    viable_mkts = len(df[df['ai_inference_readiness'] == 'Viable'])
    gpu_mkts = len(df[df['ai_compute_availability'].str.contains('GPU', case=False, na=False)])
    render_summary_card(m1, "Tracked Markets", len(df), "Total African markets analyzed")
    render_summary_card(m2, "Viable Inference Hubs", viable_mkts, "Ready for immediate deployment")
    render_summary_card(m3, "Markets w/ Local GPU", gpu_mkts, "Confirmed H100/A100 availability")

st.markdown("---")

# --------------------
# 6. Main Content: Map + Selector
# --------------------
col_map, col_details = st.columns([2, 1])

with col_details:
    st.subheader("Select Market")

    country_list = sorted(df["country"].unique())

    # Dropdown logic
    selected_country_name = st.selectbox(
        "Choose a country:",
        country_list,
        index=country_list.index(st.session_state.selected_country)
    )

    if selected_country_name != st.session_state.selected_country:
        st.session_state.selected_country = selected_country_name
        st.rerun()

    country_data = df[df["country"] == st.session_state.selected_country].iloc[0]

    # Details Panel - Dynamic Content
    if is_policy_mode:
        status_label = "Policy Signal"
        status_value = country_data['ai_policy_signal']
        badge_style = "badge-strong" if status_value == "Strong" else ("badge-unclear" if status_value == "Unclear" else "badge-emerging")
        insight_label = "Policy Insight"
        # Dynamic insight text based on data points since separate column missing
        insight_text = f"National policy signal is {status_value} with {country_data['ai_data_governance_posture'].lower()} data governance frameworks."
    else:
        status_label = "Readiness Status"
        status_value = safe(country_data.get('ai_inference_readiness'))
        badge_style = "badge-viable" if "Viable" in status_value else ("badge-early" if "Early" in status_value else "badge-emerging")
        insight_label = "Founder Insight"
        insight_text = safe(country_data.get('founder_insight'), "Founder insight not yet documented.")

    st.markdown(f"""
        <div style="margin-top: 20px; padding: 20px; border: 1px solid #e2e8f0; border-radius: 12px; background: white;">
            <div class="metric-label">{status_label}</div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:5px;">
                <h2 style="margin:0; color: #0f172a;">{st.session_state.selected_country}</h2>
                <span class="badge {badge_style}">{status_value}</span>
            </div>
            <hr style="margin: 15px 0;">
            <div class="metric-label" style="margin-bottom:4px;">{insight_label}</div>
            <div class="insight-box">"{insight_text}"</div>
        </div>
    """, unsafe_allow_html=True)

with col_map:
    # -- Map Logic --
    MAPBOX_TOKEN = st.secrets.get("MAPBOX_TOKEN", None)
    map_style = "mapbox://styles/mapbox/light-v11" if MAPBOX_TOKEN else None

    view_state = pdk.ViewState(
        latitude=float(country_data["latitude"]), 
        longitude=float(country_data["longitude"]),
        zoom=5.2, pitch=45.0, bearing=0
    )

    # 1. Path Layer (Same for both modes, context useful in both)
    EU_HUB = {"lat": 43.0, "lon": 3.0}
    REGIONAL_HUBS = {
        "East": {"lat": -1.286389, "lon": 36.817223},
        "West": {"lat": 6.524379, "lon": 3.379206},
        "Southern": {"lat": -33.9249, "lon": 18.4241},
        "North": {"lat": 30.0444, "lon": 31.2357},
    }
    paths = []
    for _, row in df.iterrows():
        start = [row["longitude"], row["latitude"]]
        route = str(row.get("primary_inference_route", ""))
        if route == "Regional-Tethered":
            hub = REGIONAL_HUBS.get(row["region"])
            if hub: paths.append({"path": [start, [hub["lon"], hub["lat"]]]})
        elif route == "Hybrid-Edge":
            paths.append({"path": [start, [EU_HUB["lon"], EU_HUB["lat"]]]})
    
    path_layer = pdk.Layer(
        "PathLayer", data=pd.DataFrame(paths),
        get_path="path", get_width=4,
        get_color=[60, 120, 216], opacity=0.5, pickable=False
    )

    # 2. Base Scatter Layer - COLOR SWAPS HERE
    active_color_col = "color_policy" if is_policy_mode else "color_founder"
    
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        id="base-scatter",
        data=df,
        get_position=["longitude", "latitude"],
        get_fill_color=active_color_col, # Dynamic Color Column
        get_radius="radius",
        get_line_color=[255, 255, 255],
        get_line_width=2,
        pickable=True, 
        stroked=True,
        auto_highlight=True,
        radius_min_pixels=10,
        radius_max_pixels=45,
    )

    # 3. Highlight Layer
    highlight_df = df[df['country'] == st.session_state.selected_country]
    halo_layer = pdk.Layer(
        "ScatterplotLayer",
        id="highlight-halo",
        data=highlight_df,
        get_position=["longitude", "latitude"],
        get_radius="radius",
        get_fill_color=[0, 0, 0, 0], 
        get_line_color=[0, 200, 255], 
        get_line_width=8000, 
        stroked=True, filled=False,
        radius_scale=1.2, radius_min_pixels=15, pickable=False
    )

    tooltip_html = "<b>{country}</b><br/>Policy Signal: {ai_policy_signal}" if is_policy_mode else "<b>{country}</b><br/>Status: {ai_inference_readiness}"

    deck = pdk.Deck(
        map_style=map_style,
        api_keys={"mapbox": MAPBOX_TOKEN} if MAPBOX_TOKEN else None,
        layers=[path_layer, scatter_layer, halo_layer],
        initial_view_state=view_state,
        tooltip={"html": tooltip_html},
    )
    
    event = st.pydeck_chart(
        deck,
        width="stretch",
        selection_mode="single-object", 
        on_select="rerun",
        key=f"map_{st.session_state.selected_country}_{view_mode}" # Add view_mode to key to force refresh on toggle
    )
    
    # Handle Map Selection
    if event.selection and "base-scatter" in event.selection.indices:
        indices = event.selection.indices["base-scatter"]
        if len(indices) > 0:
            clicked_index = indices[0]
            clicked_country = df.iloc[clicked_index]["country"]
            if clicked_country != st.session_state.selected_country:
                st.session_state.selected_country = clicked_country
                st.rerun()

# --------------------
# 7. Legend (Dynamic)
# --------------------
if is_policy_mode:
    legend_html = """
    <div class="legend-strip">
        <div class="legend-item">
            <span class="legend-icon" style="color: #1e40af;">🔵</span>
            <div><strong>Strong Signal</strong><br><span style="font-size:0.8em; color:#6b7280;">Explicit AI Strategy</span></div>
        </div>
        <div class="legend-item">
            <span class="legend-icon" style="color: #60a5fa;">💠</span>
            <div><strong>Emerging</strong><br><span style="font-size:0.8em; color:#6b7280;">Drafts / Task Forces</span></div>
        </div>
        <div class="legend-item">
            <span class="legend-icon">⭕</span>
            <div><strong>Selection</strong><br><span style="font-size:0.8em; color:#6b7280;">Cyan Ring = Active</span></div>
        </div>
    </div>
    """
else:
    legend_html = """
    <div class="legend-strip">
        <div class="legend-item">
            <span class="legend-icon">🟢</span>
            <div><strong>Readiness</strong><br><span style="font-size:0.8em; color:#6b7280;">Dot Size & Color</span></div>
        </div>
        <div class="legend-item">
            <span class="legend-icon">🔵</span>
            <div><strong>Routing</strong><br><span style="font-size:0.8em; color:#6b7280;">Blue Lines = Data Flow</span></div>
        </div>
        <div class="legend-item">
            <span class="legend-icon">⭕</span>
            <div><strong>Selection</strong><br><span style="font-size:0.8em; color:#6b7280;">Cyan Ring = Active</span></div>
        </div>
    </div>
    """
st.markdown(legend_html, unsafe_allow_html=True)

# --------------------
# 8. Deep Dive Grid
# --------------------
st.markdown("### 🔍 Infrastructure Deep Dive")

# Combined Definitions
definitions = {
    # Founder Mode
    "Inference Route": "Where the AI model actually runs. 'Local' means it runs in-country. 'Hybrid' routes to a regional hub.",
    "Latency to Europe": "Round-trip time (RTT) to major EU cloud hubs. Critical for real-time voice/video AI.",
    "Compute Availability": "Local availability of GPU capacity (H100/A100s) versus CPU-only infrastructure.",
    "Readiness Status": "Overall score combining power, compute, and policy for deployment feasibility.",
    "Active Data Centers": "Number of operational, enterprise-grade facilities (Tier III equivalent).",
    "Power Reliability": "Grid stability. Frequent outages force reliance on diesel, increasing inference costs.",
    "Cloud Maturity": "Presence of Hyperscalers (AWS/Azure) or strong local cloud providers.",
    "Ops Friction": "Difficulty of doing business: payments, cross-border data laws, or support.",
    # Policy Mode
    "AI Policy Signal": "Directional strength of national AI strategy. Strong = Clear framework; Unclear = No visible posture.",
    "Data Governance": "Legal treatment of AI data. Flexible = Innovation friendly; Restricted = Sovereignty focused.",
    "Compute Commitment": "Whether the state treats AI compute as strategic national infrastructure.",
    "Cross-Border Alignment": "Openness to cross-border data flows essential for regional inference."
}

with st.container():
    def render_card(col, label, value, subtext=None):
        tooltip_text = definitions.get(label, "No definition available.")
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">
                    {label} 
                    <div class="tooltip-container">
                        <span class="info-icon">ⓘ</span>
                        <span class="tooltip-text">{tooltip_text}</span>
                    </div>
                </div>
                <div class="metric-value" style="font-size: 1.1rem;">{value}</div>
                {f'<div style="font-size:0.75rem; color:#9ca3af; margin-top:4px;">{subtext}</div>' if subtext else ''}
            </div>
            """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    
    if is_policy_mode:
        # Policy Mode Cards
        render_card(c1, "AI Policy Signal", country_data['ai_policy_signal'])
        render_card(c2, "Data Governance", country_data['ai_data_governance_posture'])
        render_card(c3, "Compute Commitment", country_data['ai_compute_policy_commitment'])
        render_card(c4, "Cross-Border Alignment", country_data['cross_border_ai_alignment'])

        st.write("") # Row Break
        # Just 4 cards for Policy Mode v2 for now, or repeat relevant ones
        c5, c6, c7, c8 = st.columns(4)
        render_card(c5, "Active Data Centers", country_data['active_data_centers'], "(Context)")
        render_card(c6, "Power Reliability", safe(country_data.get('power_reliability')), "(Context)")
        render_card(c7, "Cloud Maturity", safe(country_data.get('cloud_maturity')), "(Context)")
        render_card(c8, "Ops Friction", safe(country_data.get('ops_friction')), "(Context)")
    else:
        # Founder Mode Cards (v1)
        render_card(c1, "Inference Route", safe(country_data.get('primary_inference_route')))
        render_card(c2, "Latency to Europe (RTT)", f"{safe(country_data.get('est_rtt_to_europe_ms'), 'N/A')} ms")
        render_card(c3, "Compute Availability", safe(country_data.get('ai_compute_availability')))
        render_card(c4, "Readiness Status", safe(country_data.get('ai_inference_readiness')))

        st.write("")
        c5, c6, c7, c8 = st.columns(4)
        render_card(c5, "Active Data Centers", country_data['active_data_centers'], f"Pipeline: {country_data['dc_pipeline']}")
        render_card(c6, "Power Reliability", safe(country_data.get('power_reliability')))
        render_card(c7, "Cloud Maturity", safe(country_data.get('cloud_maturity')))
        render_card(c8, "Ops Friction", safe(country_data.get('ops_friction')))

st.markdown("---")
caption_text = "v2 Policy Mode: Signals are directional and based on public strategy documents." if is_policy_mode else "v1 Founder Mode: Focuses on deployment reality and infrastructure readiness."
st.caption(caption_text)
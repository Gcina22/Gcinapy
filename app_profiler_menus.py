import os
import re
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# -------------------------------
# Page Setup
# -------------------------------
st.set_page_config(
    page_title="Gcina Mdizwa | Spectral Signature Dashboard",
    layout="wide"
)

# -------------------------------
# Session state
# -------------------------------
if "menu" not in st.session_state:
    st.session_state.menu = "Welcome"

menu = st.session_state.menu

# -------------------------------
# Global button styling (matches welcome page)
# -------------------------------
st.markdown(
    """
    <style>
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #1b5e20, #2e7d32);
        color: white;
        border-radius: 12px;
        font-weight: 700;
        padding: 0.7rem;
        border: none;
    }
    div.stButton > button:hover {
        background: linear-gradient(135deg, #174d1c, #256628);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------
# Hide sidebar on Welcome page + Welcome styling
# -------------------------------
if menu == "Welcome":
    st.markdown(
        """
        <style>
        [data-testid="stSidebar"] { display: none; }

        .stApp {
            background: linear-gradient(180deg, #EAF7E8 0%, #F7FFF6 60%, #FFFFFF 100%);
        }

        .block-container {
            padding-top: 2rem;
            max-width: 1250px;
        }

        .hero {
            margin-top: 20px;
            border-radius: 18px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            background: white;
        }

        .hero-grid {
            display: grid;
            grid-template-columns: 1.1fr 1.4fr;
        }

        .hero-left img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }

        .hero-right {
            padding: 32px;
            background: linear-gradient(135deg, #1b5e20, #2e7d32);
            color: white;
        }

        .hero-title {
            font-size: 52px;
            font-weight: 900;
            margin-bottom: 12px;
        }

        .hero-subtitle {
            font-size: 18px;
            line-height: 1.6;
            max-width: 75ch;
        }

        .pill {
            display: inline-block;
            background: rgba(255,255,255,0.18);
            padding: 8px 14px;
            border-radius: 999px;
            font-weight: 650;
            margin-bottom: 16px;
        }

        .tiles {
            display: grid;
            grid-template-columns: repeat(6, 1fr);
            gap: 12px;
            padding: 16px;
            background: rgba(21, 75, 27, 0.06);
        }

        .tile {
            background: rgba(255,255,255,0.85);
            border-radius: 14px;
            padding: 12px;
            text-align: center;
            font-weight: 700;
            color: #1b5e20;
        }

        .tile span {
            font-size: 22px;
            display: block;
            margin-bottom: 6px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

# -------------------------------
# Sidebar (hidden on welcome)
# -------------------------------
if menu != "Welcome":
    st.sidebar.title("🛰️ Spectral Signature Dashboard")
    st.sidebar.markdown("**Developed by:** Gcina Mdizwa")
    st.sidebar.markdown("MSc Applied GIS & Remote Sensing Student")

    menu = st.sidebar.radio(
        "Go to:",
        ["Spectral Signatures", "Data Preview"]
    )
    st.session_state.menu = menu

# -------------------------------
# Load CSV (absolute path)
# -------------------------------
@st.cache_data
def load_asd_csv():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "ASD_Data.csv")

    if not os.path.exists(path):
        st.error("ASD_Data.csv not found. Place it in the same folder as app.py.")
        st.stop()

    df = pd.read_csv(path, sep=";", decimal=",")
    df.columns = [c.strip() for c in df.columns]
    return df

# -------------------------------
# Helpers
# -------------------------------
def find_wavelength_column(df):
    for c in df.columns:
        if "wave" in c.lower():
            return c
    return df.columns[0]

def normalize_crop_label(label):
    s = re.sub(r"^(healthy|stressed|stress)[_-]*", "", label, flags=re.I)
    s = re.sub(r"_S\d+", "", s, flags=re.I)
    return s.replace("_", " ").title()

def wide_format_maps(df, wl_col):
    healthy, stressed = {}, {}
    for c in df.columns:
        if c == wl_col:
            continue
        name = normalize_crop_label(c)
        if c.lower().startswith("healthy"):
            healthy[name] = c
        elif c.lower().startswith("stressed"):
            stressed[name] = c
    return healthy, stressed

def plot_signatures(title, x, series):
    fig = go.Figure()
    for name, y in series.items():
        fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=name))
    fig.update_layout(
        title=title,
        xaxis_title="Wavelength (nm)",
        yaxis_title="Reflectance",
        hovermode="x unified",
        height=550
    )
    return fig

# -------------------------------
# Welcome Page
# -------------------------------
if menu == "Welcome":

    st.markdown(
        """
        <div class="hero">
          <div class="hero-grid">
            <div class="hero-left">
              <img src="https://images.unsplash.com/photo-1523348837708-15d4a09cfac2?auto=format&fit=crop&w=1200&q=60">
            </div>
            <div class="hero-right">
              <div class="pill">Healthy • Stressed • Spectral Signatures</div>
              <div class="hero-title">ASD SPECTRA</div>
              <div class="hero-subtitle">
                This dashboard supports the analysis and visual interpretation of crop
                spectral signatures derived from field spectroradiometric measurements.
                It enables interactive exploration of reflectance responses across the
                visible, near-infrared, and shortwave infrared regions for crops under
                healthy and stressed conditions, supporting crop stress detection and
                remote sensing–based agricultural research.
              </div>
            </div>
          </div>

          <div style="padding: 22px;">
        """,
        unsafe_allow_html=True
    )

    if st.button("🚀 Get Started"):
        st.session_state.menu = "Spectral Signatures"
        st.rerun()

# -------------------------------
# Spectral Signatures Page
# -------------------------------
elif menu == "Spectral Signatures":

    # 🔙 Back button (matches welcome style)
    if st.button("⬅ Back to Welcome"):
        st.session_state.menu = "Welcome"
        st.rerun()

    st.title("📈 Spectral Signature Analysis")

    df = load_asd_csv()
    wl = find_wavelength_column(df)
    x = pd.to_numeric(df[wl], errors="coerce")

    healthy, stressed = wide_format_maps(df, wl)

    t1, t2, t3 = st.tabs(["🌱 Healthy", "🥀 Stressed", "⚖️ Compare"])

    with t1:
        sel = st.multiselect("Healthy crops", list(healthy.keys()))
        if sel:
            fig = plot_signatures("Healthy Spectral Signatures", x, {k: df[healthy[k]] for k in sel})
            st.plotly_chart(fig, use_container_width=True)

    with t2:
        sel = st.multiselect("Stressed crops", list(stressed.keys()))
        if sel:
            fig = plot_signatures("Stressed Spectral Signatures", x, {k: df[stressed[k]] for k in sel})
            st.plotly_chart(fig, use_container_width=True)

    with t3:
        common = set(healthy) & set(stressed)
        if common:
            crop = st.selectbox("Crop", sorted(common))
            fig = plot_signatures(
                f"Healthy vs Stressed – {crop}",
                x,
                {
                    "Healthy": df[healthy[crop]],
                    "Stressed": df[stressed[crop]]
                }
            )
            st.plotly_chart(fig, use_container_width=True)

# -------------------------------
# Data Preview
# -------------------------------
elif menu == "Data Preview":

    if st.button("⬅ Back to Welcome"):
        st.session_state.menu = "Welcome"
        st.rerun()

    st.title("Dataset Preview")
    df = load_asd_csv()
    st.dataframe(df, use_container_width=True)

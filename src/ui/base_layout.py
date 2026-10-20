import streamlit as st


def style_base_layout():
    """
    Master Design System for SnapClass - Modern Education SaaS Theme.
    Palette:
      - Neutral Background: #F8FAFC (Slate 50), Cards: #FFFFFF
      - Primary Deep Navy: #0F172A / #1E293B / #1E3A8A
      - Accent Indigo/Blue: #2563EB / #3B82F6 / #4F46E5
      - Success Emerald: #10B981 / #059669 / #ECFDF5
      - Border / Subtle: #E2E8F0 / #CBD5E1
      - Text Primary: #0F172A, Secondary: #475569
    """
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=Inter:wght@300;400;500;600;700&display=swap');

        /* Global App Background & Font */
        .stApp {
            background-color: #F8FAFC !important;
            font-family: 'Plus Jakarta Sans', 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
            color: #0F172A !important;
        }

        /* Hide Streamlit default header decoration */
        #MainMenu, footer, header {
            visibility: hidden !important;
            height: 0px !important;
        }

        .block-container {
            padding-top: 1.5rem !important;
            padding-bottom: 3rem !important;
            max-width: 1200px !important;
        }

        /* Typography */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif !important;
            color: #0F172A !important;
            font-weight: 700 !important;
            letter-spacing: -0.02em !important;
        }

        h1 {
            font-size: 2.25rem !important;
            line-height: 1.25 !important;
            margin-bottom: 0.5rem !important;
        }

        h2 {
            font-size: 1.65rem !important;
            line-height: 1.3 !important;
            margin-bottom: 0.5rem !important;
        }

        h3 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            margin-bottom: 0.35rem !important;
        }

        p, span, label, div {
            font-family: 'Inter', sans-serif !important;
            color: #334155;
        }

        /* SaaS Clean Card Containers */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 14px !important;
            border: 1px solid #E2E8F0 !important;
            background-color: #FFFFFF !important;
            box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.04), 0 2px 4px -2px rgba(15, 23, 42, 0.02) !important;
            padding: 1.25rem !important;
        }

        /* Buttons Styling */
        div.stButton > button {
            border-radius: 10px !important;
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.925rem !important;
            padding: 0.55rem 1.25rem !important;
            transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
            letter-spacing: -0.01em !important;
            box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05) !important;
        }

        /* Primary Button */
        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #1E3A8A 0%, #2563EB 100%) !important;
            color: #FFFFFF !important;
            border: 1px solid transparent !important;
        }

        div.stButton > button[kind="primary"]:hover {
            background: linear-gradient(135deg, #172554 0%, #1D4ED8 100%) !important;
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25) !important;
            transform: translateY(-1px) !important;
        }

        /* Secondary Button */
        div.stButton > button[kind="secondary"] {
            background-color: #FFFFFF !important;
            color: #1E293B !important;
            border: 1px solid #CBD5E1 !important;
        }

        div.stButton > button[kind="secondary"]:hover {
            background-color: #F8FAFC !important;
            border-color: #94A3B8 !important;
            color: #0F172A !important;
            transform: translateY(-1px) !important;
        }

        /* Tertiary Button */
        div.stButton > button[kind="tertiary"] {
            background-color: transparent !important;
            color: #475569 !important;
            border: 1px solid #E2E8F0 !important;
        }

        div.stButton > button[kind="tertiary"]:hover {
            background-color: #F1F5F9 !important;
            color: #0F172A !important;
            border-color: #CBD5E1 !important;
        }

        /* Form Inputs & Selectboxes */
        div[data-baseweb="input"] {
            border-radius: 8px !important;
            border: 1px solid #CBD5E1 !important;
            background-color: #FFFFFF !important;
            transition: border-color 0.2s ease !important;
        }

        div[data-baseweb="input"]:focus-within {
            border-color: #2563EB !important;
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15) !important;
        }

        div[data-baseweb="select"] {
            border-radius: 8px !important;
        }

        /* Tabs Styling */
        div[data-testid="stTabs"] {
            margin-top: 0.5rem;
        }

        button[data-baseweb="tab"] {
            font-family: 'Plus Jakarta Sans', sans-serif !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
            color: #64748B !important;
            padding: 0.6rem 1rem !important;
            border-radius: 6px !important;
        }

        button[data-baseweb="tab"][aria-selected="true"] {
            color: #1E3A8A !important;
            border-bottom-color: #2563EB !important;
            border-bottom-width: 2.5px !important;
        }

        /* Metrics */
        div[data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 1rem !important;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.03) !important;
        }

        div[data-testid="stMetricValue"] {
            color: #0F172A !important;
            font-weight: 700 !important;
            font-size: 1.75rem !important;
        }

        div[data-testid="stMetricLabel"] {
            color: #64748B !important;
            font-weight: 500 !important;
            font-size: 0.85rem !important;
        }

        /* Dataframe styling */
        div[data-testid="stDataFrame"] {
            border-radius: 10px !important;
            border: 1px solid #E2E8F0 !important;
            overflow: hidden !important;
            background: #FFFFFF !important;
        }

        /* Custom Badges & SaaS Utility Classes */
        .saas-badge-success {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.775rem;
            font-weight: 600;
            background-color: #ECFDF5;
            color: #059669;
            border: 1px solid #A7F3D0;
        }

        .saas-badge-brand {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.775rem;
            font-weight: 600;
            background-color: #EFF6FF;
            color: #2563EB;
            border: 1px solid #BFDBFE;
        }

        .saas-badge-neutral {
            display: inline-flex;
            align-items: center;
            padding: 0.25rem 0.65rem;
            border-radius: 9999px;
            font-size: 0.775rem;
            font-weight: 500;
            background-color: #F1F5F9;
            color: #475569;
            border: 1px solid #E2E8F0;
        }

        /* Clean Dividers */
        hr {
            margin: 1.5rem 0 !important;
            border: none !important;
            border-top: 1px solid #E2E8F0 !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )


def style_background_home():
    """Clean neutral SaaS background for Home Screen."""
    style_base_layout()


def style_background_dashboard():
    """Consistent clean SaaS background for Dashboard Screens."""
    style_base_layout()
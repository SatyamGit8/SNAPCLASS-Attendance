import streamlit as st


def subject_card(name, code, section, stats=None, footer_callback=None):
    total_val = 0
    attended_val = 0
    if stats:
        for icon, label, value in stats:
            if label.lower() == 'total':
                total_val = value
            elif label.lower() == 'attended':
                attended_val = value

    pct = round((attended_val / total_val * 100), 1) if total_val > 0 else 0.0

    html = f"""
    <div style="background:#FFFFFF; border:1px solid #E2E8F0; border-radius:14px; padding:1.25rem; margin-bottom:1.25rem; box-shadow: 0 1px 3px rgba(15,23,42,0.04); transition: transform 0.2s ease;">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:0.75rem;">
            <div>
                <h4 style="margin:0 0 4px 0; color:#0F172A; font-size:1.15rem; font-weight:700;">{name}</h4>
                <div style="display:flex; align-items:center; gap:8px;">
                    <span style="background-color:#EFF6FF; color:#2563EB; font-size:0.75rem; font-weight:600; padding:2px 8px; border-radius:6px; border:1px solid #BFDBFE;">
                        {code}
                    </span>
                    <span style="font-size:0.8rem; color:#64748B;">Section {section}</span>
                </div>
            </div>
            <div style="text-align:right;">
                <span style="background-color:{'#ECFDF5' if pct >= 75 else ('#FEF3C7' if pct >= 50 else '#FEE2E2')}; color:{'#059669' if pct >= 75 else ('#D97706' if pct >= 50 else '#DC2626')}; font-size:0.8rem; font-weight:700; padding:4px 8px; border-radius:8px;">
                    {pct}% Attendance
                </span>
            </div>
        </div>
        
        <div style="display:flex; gap:10px; margin-top:0.75rem; padding-top:0.75rem; border-top:1px solid #F1F5F9;">
            <div style="flex:1; background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:6px 10px; text-align:center;">
                <span style="display:block; font-size:0.725rem; color:#64748B; font-weight:500;">Total Lectures</span>
                <span style="font-size:1rem; font-weight:700; color:#0F172A;">{total_val}</span>
            </div>
            <div style="flex:1; background:#ECFDF5; border:1px solid #A7F3D0; border-radius:8px; padding:6px 10px; text-align:center;">
                <span style="display:block; font-size:0.725rem; color:#059669; font-weight:500;">Attended</span>
                <span style="font-size:1rem; font-weight:700; color:#047857;">{attended_val}</span>
            </div>
        </div>
    </div>
    """

    st.markdown(html, unsafe_allow_html=True)

    if footer_callback:
        footer_callback()

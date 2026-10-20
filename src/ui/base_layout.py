import streamlit as st



def style_background_home():

    st.markdown("""
        <style>

                .stApp {
                    background: #5865F2 !important;
                }

                .stApp div[data-testid="stColumn"]{
                    background-color:#E0E3FF !important;
                    padding:2.5rem !important;
                    border-radius: 5rem !important;
                    }
        </style>  

                """
            ,unsafe_allow_html=True)
    

def style_background_dashboard():

    st.markdown("""
        <style>

                .stApp {
                    background: #E0E3FF !important;
                }

        </style>  

                """
            ,unsafe_allow_html=True)
    

    

def style_base_layout():
# asdasd
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Climate+Crisis:YEAR@1979&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@100..900&display=swap');

                
         /* Hide Top Bar of streamlit */
                
            #MainMenu, footer, header {
                visibility: hidden;
            }
                
            .block-container {
                padding-top:1.5rem !important;    
            }

            h1 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 3.5rem !important;
                line-height:1.1 1important;
                margin-bottom:0rem !important;
            }
                

            h2 {
                font-family: 'Climate Crisis', sans-serif !important;
                font-size: 2rem !important;
                line-height:0.9 !important;
                margin-bottom:0rem !important;
            }
                
            h3, h4, p {
                font-family: 'Outfit', sans-serif;    
            }
                

            button{
                border-radius: 1.5rem !important;
                background-color: #5865F2 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                transition: all 0.25s ease-in-out !important;
                }

            button[kind="secondary"]{
                border-radius: 1.5rem !important;
                background-color: #5865F2 !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                transition: all 0.25s ease-in-out !important;
                }

            button[kind="tertiary"]{
                border-radius: 1.5rem !important;
                background-color: black !important;
                color: white !important;
                padding: 10px 20px !important;
                border: none !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                transition: all 0.25s ease-in-out !important;
                }

            button:hover, button[kind="secondary"]:hover, button[kind="primary"]:hover{
                background-color: #4752C4 !important;
                transform: scale(1.05) !important;
                box-shadow: 0 4px 14px rgba(88, 101, 242, 0.4) !important;
            }

            /* Custom Tabs styling - Blue Theme (#5865F2) */
            div[data-baseweb="tab-list"] {
                gap: 12px !important;
            }

            [data-baseweb="tab"] {
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                color: #475569 !important;
                transition: all 0.2s ease-in-out !important;
            }

            /* Hover / Movement on tabs -> Blue color */
            [data-baseweb="tab"]:hover {
                color: #5865F2 !important;
            }

            [data-baseweb="tab"]:hover p, [data-baseweb="tab"]:hover span, [data-baseweb="tab"]:hover div {
                color: #5865F2 !important;
            }

            /* Active Tab -> Blue color */
            [data-baseweb="tab"][aria-selected="true"] {
                color: #5865F2 !important;
            }

            [data-baseweb="tab"][aria-selected="true"] p, [data-baseweb="tab"][aria-selected="true"] span, [data-baseweb="tab"][aria-selected="true"] div {
                color: #5865F2 !important;
                font-weight: 700 !important;
            }

            /* Active tab underline bar */
            [data-baseweb="tab-highlight"] {
                background-color: #5865F2 !important;
                height: 3px !important;
                border-radius: 3px !important;
            }

            /* File Uploader button & dropzone */
            [data-testid="stFileUploaderDropzone"] button {
                background-color: #5865F2 !important;
                color: white !important;
                border: none !important;
                border-radius: 1rem !important;
                font-family: 'Outfit', sans-serif !important;
                font-weight: 600 !important;
                transition: all 0.25s ease-in-out !important;
            }

            [data-testid="stFileUploaderDropzone"] button:hover {
                background-color: #4752C4 !important;
                transform: scale(1.03) !important;
            }

            [data-testid="stFileUploaderDropzone"]:hover {
                border-color: #5865F2 !important;
            }

            /* Camera Input Button */
            [data-testid="stCameraInput"] button {
                background-color: #5865F2 !important;
                color: white !important;
                border-radius: 1.5rem !important;
            }

            [data-testid="stCameraInput"] button:hover {
                background-color: #4752C4 !important;
            }

            /* High contrast readable inputs */
            input, textarea {
                color: #0F172A !important;
                background-color: #FFFFFF !important;
                font-family: 'Outfit', sans-serif !important;
            }
            div[data-baseweb="input"] {
                background-color: #FFFFFF !important;
                border-radius: 10px !important;
            }
            div[data-baseweb="select"] {
                background-color: #FFFFFF !important;
                border-radius: 10px !important;
            }
            /* Pink Labels for Input Widgets */
            div[data-testid="stWidgetLabel"],
            div[data-testid="stWidgetLabel"] *,
            label[data-testid="stWidgetLabel"],
            label[data-testid="stWidgetLabel"] *,
            div[data-testid="stTextInput"] label,
            div[data-testid="stTextInput"] label *,
            div[data-testid="stFileUploader"] label,
            div[data-testid="stFileUploader"] label *,
            div[data-testid="stAudioInput"] label,
            div[data-testid="stAudioInput"] label *,
            div[data-testid="stCameraInput"] label,
            div[data-testid="stCameraInput"] label * {
                color: #EB459E !important;
                font-weight: 600 !important;
                font-family: 'Outfit', sans-serif !important;
            }
        </style>  

                """
            ,unsafe_allow_html=True)
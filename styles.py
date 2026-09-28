import streamlit as st


def apply_styles():
    st.markdown(
        """
        <style>

        /* Main page */
        .stApp {
            background:
                radial-gradient(
                    circle at top right,
                    rgba(0, 180, 216, 0.08),
                    transparent 35%
                ),
                #07111F;
        }

        /* Main content width */
        .block-container {
            max-width: 1400px;
            padding-top: 4.25rem;
            padding-bottom: 4rem;
        }

        /* Containers / cards */
        [data-testid="stVerticalBlockBorderWrapper"] {
            background: rgba(14, 27, 43, 0.72);
            border: 1px solid rgba(0, 180, 216, 0.20);
            border-radius: 14px;
        }

        /* Buttons */
        .stButton > button,
        .stFormSubmitButton > button {
            border-radius: 9px;
            border: 1px solid rgba(0, 180, 216, 0.45);
            font-weight: 600;
        }

        .stButton > button:hover,
        .stFormSubmitButton > button:hover {
            border-color: #00B4D8;
            box-shadow: 0 0 14px rgba(0, 180, 216, 0.18);
        }

        /* Inputs */
        [data-baseweb="input"] > div,
        [data-baseweb="select"] > div,
        textarea {
            border-radius: 9px !important;
        }

        /* Horizontal rules */
        hr {
            border-color: rgba(0, 180, 216, 0.16);
        }

        /* Oceanus hero */
        .oceanus-hero {
            margin-top: 0.8rem;
            margin-bottom: 1.6rem;
            padding: 1.4rem 1.6rem;
            background: linear-gradient(
                135deg,
                rgba(0, 180, 216, 0.10),
                rgba(14, 27, 43, 0.72)
            );
            border: 1px solid rgba(0, 180, 216, 0.22);
            border-radius: 16px;
            overflow: visible;
        }

        .oceanus-kicker {
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            color: #48CAE4;
            margin-bottom: 0.35rem;
        }

        .oceanus-title {
            font-size: 2.2rem;
            font-weight: 700;
            line-height: 1.1;
            color: #F1FBFF;
        }

        .oceanus-subtitle {
            margin-top: 0.45rem;
            color: #A8C7D8;
            font-size: 0.95rem;
        }

        /* Dashboard metric cards */
        .metric-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(14, 27, 43, 0.96),
                    rgba(7, 17, 31, 0.96)
                );
            border: 1px solid rgba(0, 180, 216, 0.22);
            border-radius: 16px;
            padding: 1.15rem 1.25rem;
            min-height: 115px;
            transition: all 0.2s ease;
        }

        .metric-card:hover {
            transform: translateY(-2px);
            border-color: rgba(72, 202, 228, 0.55);
            box-shadow: 0 8px 28px rgba(0, 180, 216, 0.08);
        }

        .metric-label {
            color: #8FAFC1;
            font-size: 0.78rem;
            font-weight: 600;
            letter-spacing: 0.04em;
            text-transform: uppercase;
        }

        .metric-value {
            color: #F1FBFF;
            font-size: 2rem;
            font-weight: 750;
            line-height: 1.1;
            margin-top: 0.45rem;
        }

        .metric-accent {
            width: 28px;
            height: 3px;
            background: #00B4D8;
            border-radius: 10px;
            margin-top: 0.7rem;
        }

        /* Expanders */
        [data-testid="stExpander"] {
            background:
                linear-gradient(
                    145deg,
                    rgba(14, 27, 43, 0.92),
                    rgba(7, 17, 31, 0.92)
                );
            border: 1px solid rgba(0, 180, 216, 0.18);
            border-radius: 14px;
            overflow: hidden;
            margin-bottom: 0.7rem;
        }

        [data-testid="stExpander"] details > summary {
            padding: 0.9rem 1rem;
            font-weight: 650;
            color: #EAF7FF;
            transition: all 0.2s ease;
        }

        [data-testid="stExpander"] details > summary:hover {
            background: rgba(0, 180, 216, 0.06);
            color: #48CAE4;
        }

        [data-testid="stExpander"] details[open] > summary {
            border-bottom: 1px solid rgba(0, 180, 216, 0.14);
        }

        /* Forms */
        [data-testid="stForm"] {
            border: none;
            padding: 0.3rem 0 0 0;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stNumberInput"] input,
        [data-testid="stTextArea"] textarea {
            background-color: rgba(10, 24, 39, 0.95);
            border: 1px solid rgba(143, 175, 193, 0.16);
        }

        [data-testid="stTextInput"] input:focus,
        [data-testid="stNumberInput"] input:focus,
        [data-testid="stTextArea"] textarea:focus {
            border-color: #00B4D8;
            box-shadow: 0 0 0 1px rgba(0, 180, 216, 0.20);
        }

        [data-testid="stFormSubmitButton"] button {
            background:
                linear-gradient(
                    135deg,
                    #0077B6,
                    #0096C7
                );
            color: white;
            border: 1px solid rgba(72, 202, 228, 0.40);
            min-height: 2.6rem;
        }

        [data-testid="stFormSubmitButton"] button:hover {
            background:
                linear-gradient(
                    135deg,
                    #0096C7,
                    #00B4D8
                );
            color: white;
            transform: translateY(-1px);
        }

        /* Inventory section */
        .inventory-section-label,
        .activity-section-label {
            margin-top: 2rem;
            margin-bottom: 0.8rem;
            color: #8FAFC1;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.14em;
        }

        [data-testid="stTextInput"] input {
            background: rgba(10, 24, 39, 0.95);
            border: 1px solid rgba(0, 180, 216, 0.16);
            border-radius: 10px;
        }

        [data-testid="stTextInput"] input:hover {
            border-color: rgba(72, 202, 228, 0.35);
        }

        [data-testid="stSelectbox"] > div > div {
            background: rgba(10, 24, 39, 0.95);
            border-radius: 10px;
        }

        [data-testid="stDataFrame"] {
            background: rgba(7, 17, 31, 0.72);
            border: 1px solid rgba(0, 180, 216, 0.18);
            border-radius: 14px;
            overflow: hidden;
        }

        [data-testid="stWidgetLabel"] p {
            color: #A8C7D8;
            font-weight: 550;
        }

        /* Activity cards */
        .activity-card {
            background:
                linear-gradient(
                    145deg,
                    rgba(14, 27, 43, 0.92),
                    rgba(7, 17, 31, 0.92)
                );
            border: 1px solid rgba(0, 180, 216, 0.16);
            border-radius: 14px;
            padding: 0.95rem 1.1rem;
            margin-bottom: 0.65rem;
        }

        .activity-card:hover {
            border-color: rgba(72, 202, 228, 0.35);
        }

        .activity-top {
            display: flex;
            justify-content: space-between;
            gap: 1rem;
            align-items: center;
        }

        .activity-item {
            color: #F1FBFF;
            font-size: 1rem;
            font-weight: 650;
        }

        .activity-action {
            color: #48CAE4;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.08em;
        }

        .activity-meta {
            margin-top: 0.35rem;
            color: #8FAFC1;
            font-size: 0.82rem;
        }

        .activity-details {
            margin-top: 0.35rem;
            color: #B8D1DF;
            font-size: 0.86rem;
        }

        /* Access screen */
        .access-shell {
            max-width: 520px;
            margin: 10vh auto 0 auto;
            padding: 2rem;
            background:
                linear-gradient(
                    145deg,
                    rgba(14, 27, 43, 0.96),
                    rgba(7, 17, 31, 0.96)
                );
            border: 1px solid rgba(0, 180, 216, 0.22);
            border-radius: 18px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.18);
        }

        .access-kicker {
            color: #48CAE4;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 0.16em;
            margin-bottom: 0.4rem;
        }

        .access-title {
            color: #F1FBFF;
            font-size: 2rem;
            font-weight: 700;
            line-height: 1.1;
        }

        .access-subtitle {
            color: #8FAFC1;
            font-size: 0.92rem;
            margin-top: 0.5rem;
            margin-bottom: 1.4rem;
        }

        /* Mobile responsiveness */
        @media (max-width: 768px) {

            .block-container {
                padding-top: 3rem;
                padding-left: 1rem;
                padding-right: 1rem;
            }

            .oceanus-hero {
                padding: 1.1rem 1rem;
            }

            .oceanus-title {
                font-size: 1.7rem;
            }

            .oceanus-subtitle {
                font-size: 0.9rem;
            }

            .oceanus-kicker {
                font-size: 0.65rem;
                letter-spacing: 0.12em;
            }

            .metric-card {
                min-height: 95px;
                padding: 0.9rem 1rem;
            }

            .metric-value {
                font-size: 1.6rem;
            }

            .metric-label {
                font-size: 0.7rem;
            }

            .activity-top {
                align-items: flex-start;
                flex-direction: column;
                gap: 0.25rem;
            }

            .activity-action {
                font-size: 0.68rem;
            }

            .activity-card {
                padding: 0.85rem 0.9rem;
            }

            .access-shell {
                margin-top: 6vh;
                padding: 1.4rem;
            }
        }

        </style>
        """,
        unsafe_allow_html=True
    )
import base64

import streamlit as st


# Layered swells behind the page heading.
_WAVES = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1440 360" preserveAspectRatio="none">
  <defs>
    <linearGradient id="fade" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0.35" stop-color="#fff" stop-opacity="1"/>
      <stop offset="1" stop-color="#fff" stop-opacity="0"/>
    </linearGradient>
    <mask id="m"><rect width="1440" height="360" fill="url(#fade)"/></mask>
  </defs>
  <g mask="url(#m)">
    <path fill="#1C6C94" fill-opacity="0.22"
          d="M0 150 C 180 110 360 190 540 160 S 900 100 1080 140 S 1320 190 1440 150 V360 H0Z"/>
    <path fill="#14557A" fill-opacity="0.28"
          d="M0 210 C 200 170 380 250 600 215 S 960 160 1160 205 S 1360 245 1440 220 V360 H0Z"/>
    <path fill="#0B3A57" fill-opacity="0.45"
          d="M0 270 C 220 240 420 300 640 275 S 1000 230 1220 265 S 1400 290 1440 280 V360 H0Z"/>
  </g>
</svg>
"""

_WAVES_URI = (
    "data:image/svg+xml;base64,"
    + base64.b64encode(_WAVES.encode()).decode()
)


# Base colors live in .streamlit/config.toml. This file adds the ocean
# backdrop, brand bar, cards and summary tiles the theme can't express.
def apply_styles():
    st.html(
        """
        <style>

        /* Deep-water backdrop: light from the surface, swells, then dark */
        .stApp {
            background:
                radial-gradient(
                    ellipse 80% 45% at 50% -5%,
                    rgba(110, 200, 240, 0.16),
                    transparent 70%
                ),
                url("WAVES_URI") top 40px center / 100% 360px no-repeat,
                linear-gradient(
                    180deg,
                    #0B3652 0%,
                    #082A40 280px,
                    #061C2C 620px,
                    #04111B 100%
                );
            background-attachment: scroll, scroll, scroll;
        }

        .block-container {
            max-width: 1180px;
            padding-top: 0;
            padding-bottom: 4rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
            height: 3.5rem;
        }


        /* Full-width brand bar */
        .topbar {
            margin: 0 calc(50% - 50vw) 0;
            background: rgba(3, 16, 26, 0.55);
            border-bottom: 1px solid rgba(140, 200, 235, 0.10);
            backdrop-filter: blur(6px);
        }

        .topbar-inner {
            max-width: 1180px;
            margin: 0 auto;
            padding: 0.85rem 5rem;
            display: flex;
            align-items: center;
            gap: 0.65rem;
        }

        .brand-name {
            color: #FFFFFF;
            font-weight: 700;
            font-size: 1.05rem;
            letter-spacing: 0.01em;
        }

        .brand-divider {
            width: 1px;
            height: 1.1rem;
            background: rgba(255,255,255,0.25);
        }

        .brand-product {
            color: #8FB4CC;
            font-size: 0.95rem;
        }

        /* Page heading */
        .page-heading {
            padding: 1.9rem 0 0.2rem;
        }

        .page-title {
            font-size: 1.75rem;
            font-weight: 700;
            letter-spacing: -0.015em;
            line-height: 1.2;
        }

        .page-subtitle {
            color: #93B3C8;
            font-size: 0.95rem;
            margin-top: 0.3rem;
        }

        /* Summary tiles */
        .stats {
            display: grid;
            grid-template-columns: repeat(5, minmax(0, 1fr));
            gap: 0.75rem;
            margin: 0.4rem 0 0.6rem;
        }

        .stat {
            background: rgba(8, 30, 46, 0.72);
            border: 1px solid rgba(120, 190, 230, 0.14);
            border-radius: 10px;
            padding: 0.85rem 1rem;
            backdrop-filter: blur(6px);
        }

        .stat-label {
            color: #8FB0C6;
            font-size: 0.8rem;
            font-weight: 500;
            display: flex;
            align-items: center;
            gap: 0.4rem;
        }

        .stat-value {
            font-size: 1.6rem;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
            margin-top: 0.15rem;
        }

        .dot {
            width: 7px;
            height: 7px;
            border-radius: 50%;
            display: inline-block;
        }

        /* Cards that hold the table and the activity log */
        .st-key-inventory_card,
        .st-key-activity_card {
            background: rgba(6, 25, 39, 0.82);
            border-color: rgba(120, 190, 230, 0.14);
            border-radius: 12px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
            backdrop-filter: blur(8px);
            padding: 1.1rem 1.2rem 1.2rem;
        }

        /* Bar above the table */
        .st-key-selection_bar {
            background: rgba(47, 164, 217, 0.08);
            border-color: rgba(47, 164, 217, 0.28);
            padding: 0.5rem 0.85rem;
            margin-bottom: 1rem;
        }

        .st-key-selection_bar p {
            margin: 0;
            font-size: 0.92rem;
        }

        .row-count {
            color: #8FB0C6;
            font-size: 0.85rem;
            text-align: right;
        }

        /* Tabs */
        [data-baseweb="tab-list"] {
            gap: 1.25rem;
        }

        [data-baseweb="tab"] p {
            font-size: 0.95rem;
            font-weight: 500;
        }

        /* Sign-in */
        .access-header {
            margin: 10vh 0 1.25rem;
            text-align: center;
        }

        .access-header .page-title {
            margin-top: 0.9rem;
        }

        .logo {
            width: 26px;
            height: 26px;
            display: block;
        }

        .access-header .logo {
            width: 44px;
            height: 44px;
            margin: 0 auto;
        }

        @media (max-width: 900px) {
            .stats {
                grid-template-columns: repeat(3, minmax(0, 1fr));
            }
        }

        @media (max-width: 640px) {
            .topbar-inner {
                padding: 0.75rem 1rem;
            }

            .stats {
                grid-template-columns: repeat(3, minmax(0, 1fr));
                gap: 0.5rem;
            }

            .stat {
                padding: 0.6rem 0.7rem;
            }

            .stat-label {
                font-size: 0.72rem;
            }

            .stat-value {
                font-size: 1.25rem;
            }

            .page-heading {
                padding-top: 1.3rem;
            }

            .page-title {
                font-size: 1.45rem;
            }

            .row-count {
                text-align: left;
            }

            .st-key-inventory_card,
            .st-key-activity_card {
                padding: 0.8rem;
            }

            .access-header {
                margin-top: 6vh;
            }
        }

        </style>
        """.replace("WAVES_URI", _WAVES_URI)
    )

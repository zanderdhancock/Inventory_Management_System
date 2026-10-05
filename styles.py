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


# Sea life drifting behind the page. Silhouettes in a pale blue at low
# opacity, so they read as shapes in the distance and never compete with
# the cards. st.html strips inline <svg>, so each is a data-URI background.
_INK = 'fill="#7FC4E8"'

# ROV hanging from its tether, camera dome facing left
_ROV = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 220 260">
  <path d="M112 0 C 104 60 122 100 110 140" fill="none" stroke="#7FC4E8"
        stroke-width="2.5" stroke-dasharray="7 5"/>
  <g {_INK}>
    <rect x="40" y="140" width="140" height="28" rx="7"/>
    <ellipse cx="72" cy="136" rx="17" ry="6"/>
    <ellipse cx="148" cy="136" rx="17" ry="6"/>
    <rect x="12" y="178" width="26" height="40" rx="9"/>
    <rect x="182" y="178" width="26" height="40" rx="9"/>
    <circle cx="56" cy="198" r="13"/>
  </g>
  <g fill="none" stroke="#7FC4E8" stroke-width="5" stroke-linecap="round">
    <rect x="36" y="168" width="148" height="56" rx="4"/>
    <path d="M36 196 H184 M46 224 V238 M174 224 V238 M30 238 H190"/>
  </g>
</svg>
"""

# Shark cruising left
_SHARK = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 110">
  <path {_INK} d="M8 60 C 30 48 70 38 120 36 L 148 8 L 162 37 C 200 40 234 46
    256 52 L 292 20 L 281 58 L 296 92 L 255 66 C 228 74 190 80 152 80
    L 130 102 L 120 80 C 70 78 32 70 8 60 Z"/>
</svg>
"""

# Diver swimming left: tank on the back, fins trailing
_DIVER = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 260 120">
  <g {_INK}>
    <circle cx="38" cy="56" r="12"/>
    <path d="M50 48 C 80 40 130 42 160 50 L 160 70 C 130 76 80 74 50 66 Z"/>
    <rect x="72" y="34" width="62" height="14" rx="7"/>
    <path d="M236 31 L 258 20 L 252 46 Z M232 80 L 256 97 L 237 101 Z"/>
  </g>
  <g fill="none" stroke="#7FC4E8" stroke-width="9" stroke-linecap="round"
     stroke-linejoin="round">
    <path d="M62 64 L 32 80 L 18 77"/>
    <path d="M158 54 L 204 46 L 238 38"/>
    <path d="M158 66 L 204 72 L 236 88"/>
  </g>
</svg>
"""

# Bubbles rising from the diver
_BUBBLES = """
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 200">
  <g fill="none" stroke="#9FD6F2" stroke-width="1.6">
    <circle cx="20" cy="186" r="5"/>
    <circle cx="12" cy="150" r="4"/>
    <circle cx="24" cy="112" r="6"/>
    <circle cx="16" cy="70" r="3.5"/>
    <circle cx="26" cy="34" r="4.5"/>
    <circle cx="18" cy="8" r="3"/>
  </g>
</svg>
"""


def _svg_uri(svg):
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()


_SEA_LIFE = f"""
<div class="sea-life" aria-hidden="true">
  <div class="sea rov rov-near" style="background-image: url('{_svg_uri(_ROV)}')"></div>
  <div class="sea rov rov-far" style="background-image: url('{_svg_uri(_ROV)}')"></div>
  <div class="sea shark" style="background-image: url('{_svg_uri(_SHARK)}')"></div>
  <div class="sea diver" style="background-image: url('{_svg_uri(_DIVER)}')"></div>
  <div class="sea bubbles" style="background-image: url('{_svg_uri(_BUBBLES)}')"></div>
</div>
"""


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

        /* Sea life behind the page */
        .sea-life {
            position: fixed;
            inset: 0;
            z-index: 0;
            pointer-events: none;
            overflow: hidden;
        }

        [data-testid="stMain"] {
            position: relative;
            z-index: 1;
        }

        .sea {
            position: absolute;
            background: center / contain no-repeat;
        }

        .rov-near {
            left: 2.5vw;
            top: 8vh;
            width: 150px;
            height: 178px;
            opacity: 0.22;
            animation: bob 7s ease-in-out infinite;
        }

        .rov-far {
            right: 6vw;
            top: 14vh;
            width: 92px;
            height: 109px;
            opacity: 0.12;
            transform: scaleX(-1);
            animation: bob-far 9s ease-in-out infinite;
        }

        .shark {
            top: 46vh;
            left: 0;
            width: 260px;
            height: 95px;
            opacity: 0.16;
            animation: cruise 75s linear infinite;
        }

        .diver {
            right: 5vw;
            bottom: 9vh;
            width: 210px;
            height: 97px;
            opacity: 0.18;
            animation: drift 11s ease-in-out infinite;
        }

        .bubbles {
            right: calc(5vw + 168px);
            bottom: calc(9vh + 64px);
            width: 28px;
            height: 140px;
            opacity: 0.35;
            animation: rise 6s ease-in infinite;
        }

        @keyframes bob {
            50% { transform: translateY(12px); }
        }

        @keyframes bob-far {
            0%, 100% { transform: scaleX(-1) translateY(0); }
            50% { transform: scaleX(-1) translateY(8px); }
        }

        @keyframes cruise {
            from { transform: translateX(105vw); }
            to { transform: translateX(-300px); }
        }

        @keyframes drift {
            50% { transform: translate(-14px, 6px); }
        }

        @keyframes rise {
            from { transform: translateY(0); opacity: 0.35; }
            to { transform: translateY(-60px); opacity: 0; }
        }

        @media (prefers-reduced-motion: reduce) {
            .sea {
                animation: none;
            }

            .shark {
                transform: translateX(70vw);
            }
        }

        @media (max-width: 640px) {
            .rov-far,
            .diver,
            .bubbles {
                display: none;
            }

            .rov-near {
                width: 96px;
                height: 114px;
                opacity: 0.16;
            }

            .shark {
                width: 170px;
                height: 62px;
                opacity: 0.12;
            }
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
        .st-key-projects_card,
        .st-key-activity_card,
        .st-key-admin_card {
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

        .bar-text {
            font-size: 0.92rem;
            line-height: 1.4;
        }

        .row-count {
            color: #8FB0C6;
            font-size: 0.85rem;
            text-align: right;
        }


        /* Summary tiles are clickable: an invisible button covers each one */
        .st-key-stats [data-testid="stHorizontalBlock"] {
            flex-wrap: wrap;
            gap: 0.75rem;
        }

        .st-key-stats [data-testid="stColumn"] {
            min-width: 150px;
        }

        [class*="st-key-tile_"] {
            position: relative;
            gap: 0;
        }

        [class*="st-key-tile_"] [data-testid="stElementContainer"]:has(.stButton) {
            position: absolute;
            inset: 0;
            z-index: 2;
            width: 100% !important;
            height: 100%;
        }

        [class*="st-key-tile_"] .stButton {
            width: 100%;
            height: 100%;
        }

        /* Clicks pass through the tile's text to the button underneath */
        [class*="st-key-tile_"] [data-testid="stElementContainer"]:not(:has(.stButton)) {
            pointer-events: none;
        }

        [class*="st-key-tile_"] .stButton button {
            width: 100%;
            height: 100%;
            opacity: 0;
            cursor: pointer;
        }

        [class*="st-key-tile_"]:hover .stat {
            border-color: rgba(120, 190, 230, 0.35);
            background: rgba(10, 38, 58, 0.85);
        }

        .stat-active {
            border-color: rgba(47, 164, 217, 0.65) !important;
            box-shadow: inset 0 0 0 1px rgba(47, 164, 217, 0.35);
        }

        /* Keep the table's hover toolbar inside the table header */
        [data-testid="stElementToolbar"] {
            top: 0.35rem;
            right: 0.35rem;
        }

        /* Projects */
        .project-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
            gap: 0.75rem;
            margin-bottom: 0.5rem;
        }

        .project-card {
            background: rgba(10, 36, 54, 0.75);
            border: 1px solid rgba(120, 190, 230, 0.14);
            border-radius: 10px;
            padding: 0.85rem 1rem;
        }

        .project-name {
            font-weight: 600;
        }

        .project-meta {
            color: #8FB0C6;
            font-size: 0.85rem;
            margin-top: 0.2rem;
        }

        .project-flag {
            color: #F3C55C;
            font-size: 0.8rem;
            margin-top: 0.35rem;
        }

        .muted {
            color: #8FB0C6;
            font-size: 0.88rem;
        }

        /* Credits footer */
        .app-footer {
            margin-top: 3rem;
            padding: 1.25rem 0 0.5rem;
            border-top: 1px solid rgba(120, 190, 230, 0.12);
            display: flex;
            flex-wrap: wrap;
            justify-content: space-between;
            gap: 1rem 2rem;
            font-size: 0.85rem;
        }

        .footer-brand {
            display: flex;
            align-items: center;
            gap: 0.7rem;
        }

        .footer-title {
            font-weight: 600;
        }

        .footer-text {
            color: #8FB0C6;
        }

        .footer-credits {
            text-align: right;
            line-height: 1.6;
        }

        .app-footer a {
            color: #6FC3EC;
            text-decoration: none;
        }

        .app-footer a:hover {
            text-decoration: underline;
        }

        @media (max-width: 640px) {
            .footer-credits {
                text-align: left;
            }
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


        @media (max-width: 640px) {
            .topbar-inner {
                padding: 0.75rem 1rem;
            }

            .st-key-stats [data-testid="stHorizontalBlock"] {
                gap: 0.5rem;
            }

            .st-key-stats [data-testid="stColumn"] {
                min-width: calc(33% - 0.5rem);
                flex: 1 1 calc(33% - 0.5rem);
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

            /* Keep Edit / Delete / History on one row on phones */
            .st-key-bar_actions [data-testid="stHorizontalBlock"] {
                flex-wrap: nowrap;
                gap: 0.5rem;
            }

            .st-key-bar_actions [data-testid="stColumn"] {
                min-width: 0;
                flex: 1 1 0;
            }

            .st-key-inventory_card,
            .st-key-projects_card,
            .st-key-activity_card,
            .st-key-admin_card {
                padding: 0.8rem;
            }

            .access-header {
                margin-top: 6vh;
            }
        }

        </style>
        """.replace("WAVES_URI", _WAVES_URI)
        + _SEA_LIFE
    )

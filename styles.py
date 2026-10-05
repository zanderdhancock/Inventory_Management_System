import streamlit as st


# Colors live in .streamlit/config.toml. This file covers the branded
# top bar, cards and summary tiles the theme can't express.
def apply_styles():
    st.html(
        """
        <style>

        .block-container {
            max-width: 1180px;
            padding-top: 0;
            padding-bottom: 4rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
            height: 3.5rem;
        }

        [data-testid="stHeader"] button,
        [data-testid="stHeader"] svg {
            color: #FFFFFF;
        }

        /* Full-width brand bar */
        .topbar {
            margin: 0 calc(50% - 50vw) 0;
            background:
                linear-gradient(180deg, rgba(255,255,255,0.04), transparent),
                #0C2A47;
            border-bottom: 1px solid #0A2239;
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
            color: #A9C3DB;
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
            color: #5B6B7B;
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
            background: #FFFFFF;
            border: 1px solid #E1E6EC;
            border-radius: 10px;
            padding: 0.85rem 1rem;
            box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        }

        .stat-label {
            color: #5B6B7B;
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
            background: #FFFFFF;
            border-color: #E1E6EC;
            border-radius: 12px;
            box-shadow: 0 1px 3px rgba(16, 24, 40, 0.06);
            padding: 1.1rem 1.2rem 1.2rem;
        }

        /* Bar above the table */
        .st-key-selection_bar {
            background: #F3F7FB;
            border-color: #D6E3F0;
            padding: 0.5rem 0.85rem;
            margin-bottom: 1rem;
        }

        .st-key-selection_bar p {
            margin: 0;
            font-size: 0.92rem;
        }

        .row-count {
            color: #5B6B7B;
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
        """
    )

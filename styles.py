import streamlit as st


# Colors live in .streamlit/config.toml. This file only covers layout
# details the theme can't express.
def apply_styles():
    st.html(
        """
        <style>

        .block-container {
            max-width: 1200px;
            padding-top: 2.5rem;
            padding-bottom: 3rem;
        }

        [data-testid="stHeader"] {
            background: transparent;
        }

        /* Header */
        .app-title {
            font-size: 1.5rem;
            font-weight: 600;
            letter-spacing: -0.01em;
            line-height: 1.2;
        }

        .app-subtitle {
            color: #8A939C;
            font-size: 0.9rem;
            margin-top: 0.15rem;
        }

        .access-header {
            margin: 18vh 0 1.25rem;
        }

        /* Summary numbers */
        .stats {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem 2.5rem;
            padding: 1rem 0 0.25rem;
            border-top: 1px solid #262C33;
            margin-top: 0.5rem;
        }

        .stat-value {
            font-size: 1.35rem;
            font-weight: 600;
            font-variant-numeric: tabular-nums;
            line-height: 1.2;
        }

        .stat-label {
            color: #8A939C;
            font-size: 0.8rem;
        }

        /* Bar above the table */
        .st-key-selection_bar {
            background: #171B20;
            padding: 0.55rem 0.9rem;
        }

        .st-key-selection_bar {
            margin-bottom: 0.6rem;
        }

        .st-key-selection_bar p {
            margin: 0;
        }

        .row-count {
            color: #8A939C;
            font-size: 0.85rem;
            text-align: right;
        }

        @media (max-width: 640px) {
            .block-container {
                padding-top: 1.5rem;
            }

            .stats {
                gap: 0.5rem 1.5rem;
            }

            .row-count {
                text-align: left;
            }

            .access-header {
                margin-top: 8vh;
            }
        }

        </style>
        """
    )

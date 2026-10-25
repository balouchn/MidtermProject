"""Interactive scientific storytelling dashboard for renewable electricity."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from data_prep import (
    COUNTRY_CSV,
    REGION_CSV,
    TECHNOLOGY_COLUMNS,
    available_years,
    filter_observations,
    gdp_share_complete_cases,
    load_datasets,
    rank_countries,
)


st.set_page_config(
    page_title="Powering the Future",
    page_icon="⚡",
    layout="wide",
)

COLORS = {
    "Renewable share": "#65051F",
    "Hydro": "#426A80",
    "Wind": "#78618C",
    "Solar": "#D08A28",
    "Other renewables": "#64806A",
}
COUNTRY_PALETTE = [
    "#65051F",
    "#426A80",
    "#D08A28",
    "#C66C86",
    "#64806A",
    "#78618C",
    "#9A6D43",
    "#58656D",
]
TIMELINE_PALETTE = [
    "#FF9EAA",
    "#75C7E8",
    "#FFC66D",
    "#E9A0FF",
    "#95D7A7",
    "#D7A7FF",
    "#F6B68A",
    "#B7CBD8",
]
PLOT_CONFIG = {"displaylogo": False, "responsive": True}


@st.cache_data(show_spinner="Loading and checking the local CSV files…")
def load_data():
    return load_datasets(COUNTRY_CSV, REGION_CSV)


def safe_plot(
    fig: go.Figure,
    *,
    key: str,
    height: int = 450,
    margin: dict[str, int] | None = None,
    dark: bool = False,
) -> None:
    plot_bgcolor = "#350D1C" if dark else "#FFFFFF"
    paper_bgcolor = "#2B0914" if dark else "rgba(0,0,0,0)"
    font_color = "#FFF4F0" if dark else "#30272A"
    grid_color = "rgba(255, 236, 237, .14)" if dark else "#E9E0E2"
    axis_color = "#F6DCE2" if dark else "#4A373D"
    fig.update_layout(
        template="plotly_white",
        height=height,
        margin=margin or dict(l=28, r=28, t=62, b=34),
        legend_title_text="",
        font=dict(family="Arial, sans-serif", color=font_color),
        title_font=dict(color="#FFF4F0" if dark else "#800020"),
        paper_bgcolor=paper_bgcolor,
        plot_bgcolor=plot_bgcolor,
        hoverlabel=dict(
            bgcolor="#48051A",
            bordercolor="#48051A",
            font=dict(color="#FFFFFF", family="Arial, sans-serif"),
        ),
    )
    fig.update_xaxes(
        gridcolor=grid_color,
        linecolor=axis_color,
        zerolinecolor=grid_color,
        title_font=dict(color=axis_color),
        tickfont=dict(color=axis_color),
    )
    fig.update_yaxes(
        gridcolor=grid_color,
        linecolor=axis_color,
        zerolinecolor=grid_color,
        title_font=dict(color=axis_color),
        tickfont=dict(color=axis_color),
    )
    st.plotly_chart(fig, width="stretch", config=PLOT_CONFIG, key=key)


def add_anchor(anchor: str) -> None:
    st.markdown(f'<div id="{anchor}" class="section-anchor"></div>', unsafe_allow_html=True)


def country_rows(frame: pd.DataFrame, country: str, start: int, end: int) -> pd.DataFrame:
    return filter_observations(
        frame, countries=[country], year_range=(start, end)
    ).sort_values("year")


def line_chart(
    frame: pd.DataFrame,
    *,
    x: str,
    y: str,
    color: str,
    title: str,
    y_title: str,
    key: str,
    color_map: dict[str, str] | None = None,
    hover_data: dict[str, bool] | None = None,
) -> None:
    if frame.empty:
        st.info("No observations are available for this selection.")
        return
    fig = px.line(
        frame,
        x=x,
        y=y,
        color=color,
        line_dash=(
            "Technology"
            if color == "country" and "Technology" in frame.columns
            else None
        ),
        title=title,
        color_discrete_map=color_map,
        markers=True,
        hover_data=hover_data,
    )
    fig.update_traces(connectgaps=False)
    fig.update_xaxes(title="Year", dtick=5 if x == "year" else None)
    fig.update_yaxes(title=y_title)
    safe_plot(fig, key=key)


try:
    bundle = load_data()
except (OSError, ValueError, KeyError) as exc:
    st.error(f"Could not load or validate the local renewable-energy data: {exc}")
    st.info(
        "Check that both original CSV files are present in the project's data/ folder "
        "and have not been edited."
    )
    st.stop()

data = bundle.country
region = bundle.region
share_years = available_years(data, "renewables_share_elec")
generation_years = available_years(data, "renewables_electricity")
gdp_years = sorted(set(available_years(data, "gdp")) & set(share_years))
countries = sorted(data["country"].dropna().unique().tolist())
country_labels = data[["country", "iso_code"]].drop_duplicates("country")
map_countries = country_labels.dropna(subset=["iso_code"])
map_countries = map_countries[
    map_countries["iso_code"].str.fullmatch(r"[A-Z]{3}", na=False)
]
map_share_years = sorted(share_years)
country_diag = bundle.diagnostics["country"]
available_2022 = int(
    data.loc[
        (data["year"] == 2022) & data["renewables_share_elec"].notna(),
        "country",
    ].nunique()
)

st.markdown(
    """
    <style>
    :root {
        --wine: #65051F;
        --wine-dark: #48051A;
        --ivory: #FCF8F5;
        --blush: #F2E3E7;
        --rose: #C66C86;
        --coral: #E95D62;
        --ink: #34272B;
        --muted: #786B70;
        --border: #E8D9DC;
    }
    .stApp,
    [data-testid="stAppViewContainer"] {
        background: var(--ivory);
        color: var(--ink);
    }
    html { scroll-behavior: smooth; }
    [data-testid="stHeader"] {
        background: rgba(252, 248, 245, 0.97);
    }
    [data-testid="stSidebar"] { display: none; }
    .block-container {
        padding-top: 0.75rem;
        padding-bottom: 3rem;
        max-width: 1440px;
    }
    h1, h2, h3, h4 {
        color: var(--wine-dark) !important;
    }
    h2 {
        font-family: Georgia, "Times New Roman", serif !important;
        font-size: clamp(2rem, 3.6vw, 3.3rem) !important;
        letter-spacing: -0.045em !important;
        line-height: 1.02 !important;
        margin-bottom: 0.25rem !important;
    }
    p, li, label, [data-testid="stWidgetLabel"] p {
        color: var(--ink) !important;
    }
    a, a:visited { color: var(--wine) !important; }
    [data-testid="stCaptionContainer"] p {
        color: #66575D !important;
    }
    [data-testid="stMetric"] {
        background: transparent;
        border: 0;
        padding: 0.45rem 0;
        border-radius: 0;
        box-shadow: none;
    }
    [data-testid="stMetricLabel"] p { color: var(--muted) !important; }
    [data-testid="stMetricValue"] {
        color: var(--wine-dark) !important;
    }
    [data-baseweb="select"] > div,
    [data-baseweb="input"] > div,
    [data-baseweb="textarea"] > div {
        background: #FFFFFF !important;
        border-color: #B99DA5 !important;
        color: var(--ink) !important;
        box-shadow: none !important;
    }
    [data-testid="stSelectbox"] [role="group"],
    [data-testid="stMultiSelect"] [role="group"] {
        background: #FFFFFF !important;
        border: 1px solid #B99DA5 !important;
        border-radius: 0.55rem !important;
        color: var(--ink) !important;
        box-shadow: none !important;
    }
    [data-baseweb="select"] input,
    [data-baseweb="select"] [role="combobox"],
    [data-baseweb="select"] [data-testid="stMarkdownContainer"],
    [data-testid="stSelectbox"] input,
    [data-testid="stMultiSelect"] input,
    [data-baseweb="select"] span,
    [data-baseweb="input"] input,
    [data-baseweb="textarea"] textarea {
        color: var(--ink) !important;
        -webkit-text-fill-color: var(--ink) !important;
        background: transparent !important;
    }
    [data-baseweb="tag"] {
        background: var(--blush) !important;
        border: 1px solid #D8B9C2 !important;
        border-radius: 0.45rem !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag] {
        background: var(--blush) !important;
        color: var(--wine-dark) !important;
        border: 1px solid #D8B9C2 !important;
        border-radius: 0.4rem !important;
    }
    [data-testid="stMultiSelectTagsContainer"] [data-tag] span,
    [data-testid="stMultiSelectTagsContainer"] [data-tag] button {
        color: var(--wine-dark) !important;
        -webkit-text-fill-color: var(--wine-dark) !important;
    }
    [data-baseweb="tag"] span,
    [data-baseweb="tag"] [role="presentation"] {
        color: var(--wine-dark) !important;
        -webkit-text-fill-color: var(--wine-dark) !important;
    }
    [data-baseweb="popover"] > div,
    [data-baseweb="menu"],
    [role="listbox"] {
        background: #FFFFFF !important;
        color: var(--ink) !important;
    }
    [role="option"] {
        background: #FFFFFF !important;
        color: var(--ink) !important;
    }
    [role="option"]:hover,
    [role="option"][aria-selected="true"] {
        background: var(--blush) !important;
        color: var(--wine-dark) !important;
    }
    [data-baseweb="select"] svg { color: var(--wine) !important; fill: var(--wine) !important; }
    input, textarea { color: var(--ink) !important; }
    [data-testid="stAlert"] {
        background: #F2E3E7 !important;
        border: 1px solid #D8B9C2 !important;
        border-left: 4px solid #E95D62 !important;
        border-radius: 0.75rem !important;
    }
    [data-testid="stAlert"] p { color: #34272B !important; }
    [data-testid="stButton"] button {
        min-height: 2.55rem;
        border-radius: 0.6rem;
        color: var(--wine-dark) !important;
        border: 1px solid #B99DA5;
        background: #FFFFFF;
        transition: background 140ms ease, color 140ms ease, border-color 140ms ease;
    }
    [data-testid="stButton"] button:hover {
        color: #FFFFFF !important;
        border-color: var(--wine);
        background: var(--wine);
    }
    [data-testid="stButton"] button:focus-visible,
    [data-baseweb="select"] > div:focus-within,
    [data-baseweb="input"] > div:focus-within {
        outline: 3px solid rgba(198, 108, 134, 0.42) !important;
        outline-offset: 2px;
    }
    [data-testid="stSlider"] [role="slider"] {
        border-color: var(--wine) !important;
        background: #FFFFFF !important;
    }
    [data-testid="stSlider"] [data-baseweb="slider"] div[role="presentation"] {
        background: var(--rose);
    }
    [data-testid="stRadio"] label p { color: var(--ink) !important; }
    [data-testid="stRadio"] [role="radio"][aria-checked="true"] > div:first-child {
        border-color: var(--wine) !important;
        background: var(--wine) !important;
    }
    [data-testid="stPlotlyChart"] {
        background: transparent;
        border: 0;
        border-radius: 0;
        padding: 0;
        box-shadow: none;
    }
    .st-key-world_map [data-testid="stPlotlyChart"] {
        background: #FBF3F0;
        border: 1px solid #E8D9DC;
        border-radius: 1.1rem;
        overflow: hidden;
    }
    .st-key-share_time_series {
        background:
            radial-gradient(ellipse at 86% 0%, rgba(198,108,134,.22), transparent 34%),
            linear-gradient(135deg, #260812 0%, #420B20 58%, #2B0A16 100%);
        border: 1px solid rgba(242, 227, 231, .16);
        border-radius: 1.15rem;
        padding: 0.5rem 1rem 0.35rem;
        box-shadow: 0 22px 56px rgba(48, 7, 22, .18);
    }
    .st-key-share_time_series [data-testid="stPlotlyChart"] {
        background: transparent;
        border: 0;
        box-shadow: none;
    }
    .st-key-share_time_series [data-testid="stToolbar"] {
        filter: invert(1) hue-rotate(180deg);
    }
    .st-key-share_time_series [data-testid="stCaptionContainer"] p {
        color: #F2DDE3 !important;
    }
    .st-key-share_time_series [data-testid="stButton"] button {
        color: #48051A !important;
        background: #FFF8F4 !important;
        border-color: #F0CDD5 !important;
    }
    .st-key-share_time_series [data-testid="stButton"] button:hover {
        background: #EFB1BD !important;
    }
    .st-key-timeline-controls {
        padding: .85rem 1rem .45rem;
        margin: .4rem 0 0;
        border: 1px solid rgba(242, 227, 231, .15);
        border-bottom: 0;
        border-radius: 1rem 1rem 0 0;
        background: linear-gradient(115deg, #260812, #420B20);
    }
    .st-key-timeline-controls [data-testid="stWidgetLabel"] p,
    .st-key-timeline-controls [data-testid="stCaptionContainer"] p {
        color: #F2DDE3 !important;
    }
    .st-key-timeline-controls [data-testid="stSlider"] p {
        color: #F2DDE3 !important;
    }
    [data-testid="stHorizontalBlock"] { gap: 1.15rem; }
    .section-anchor,
    [data-testid="stPlotlyChart"] { scroll-margin-top: 5.5rem; }
    .story-nav {
        position: sticky;
        top: 0.4rem;
        z-index: 100;
        display: flex;
        flex-wrap: nowrap;
        gap: 0.25rem;
        padding: 0.55rem 0.65rem;
        margin: 0.35rem 0 1.1rem;
        border-top: 1px solid var(--border);
        border-bottom: 1px solid var(--border);
        background: rgba(252,248,245,.97);
        overflow-x: auto;
    }
    .story-nav a {
        display: inline-block;
        flex: 0 0 auto;
        padding: 0.5rem 0.72rem;
        border-radius: 0.35rem;
        color: #514047 !important;
        text-decoration: none !important;
        font-size: 0.78rem;
        font-weight: 720;
        letter-spacing: .025em;
        transition: background 160ms ease, color 160ms ease;
    }
    .story-nav a:hover,
    .story-nav a:focus-visible {
        background: var(--wine);
        color: #FFFFFF !important;
        outline: none;
    }
    body:has(#world-map:target) .story-nav a[href="#world-map"],
    body:has(#over-time:target) .story-nav a[href="#over-time"],
    body:has(#energy-mix:target) .story-nav a[href="#energy-mix"],
    body:has(#gdp:target) .story-nav a[href="#gdp"],
    body:has(#rankings:target) .story-nav a[href="#rankings"],
    body:has(#comparisons:target) .story-nav a[href="#comparisons"] {
        background: var(--wine);
        color: #FFFFFF !important;
    }
    .closing-note {
        display: grid;
        grid-template-columns: 1fr auto;
        align-items: center;
        gap: 1rem;
        padding: 1.35rem 1.5rem;
        margin: 1.8rem 0 1.1rem;
        border-left: 4px solid #EF8E91;
        background: linear-gradient(105deg, #300A18, #55102B);
        color: #FFF5F0;
    }
    .closing-note strong {
        display: block;
        color: #FFFFFF;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.45rem;
        line-height: 1.2;
    }
    .closing-note span {
        display: block;
        margin-top: .3rem;
        color: #F1D9DE;
        font-size: .88rem;
    }
    .closing-value {
        color: #FFC1B4;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1.5rem, 3vw, 2.4rem);
        font-variant-numeric: tabular-nums;
        white-space: nowrap;
    }
    .section-anchor { scroll-margin-top: 5.2rem; }
    [data-testid="stElementContainer"]:has(.section-anchor) {
        margin-top: 1.35rem;
    }
    .st-key-exploration-bar {
        padding: .8rem 1.1rem .25rem;
        margin: 0 0 .7rem;
        border-top: 1px solid #DFC9CF;
        border-bottom: 1px solid #DFC9CF;
        background: linear-gradient(100deg, #F8ECEE, #FFF9F5);
    }
    .st-key-exploration-bar [data-testid="stMetricLabel"] p {
        color: #66575D !important;
        font-size: .72rem;
    }
    .st-key-exploration-bar [data-testid="stMetricValue"] {
        color: #48051A !important;
        font-size: 1.55rem;
        font-variant-numeric: tabular-nums;
    }
    .section-kicker {
        display: flex;
        align-items: center;
        gap: .65rem;
        margin: 0 0 .35rem;
        color: #9B5268;
        font-size: .72rem;
        font-weight: 850;
        letter-spacing: .16em;
        text-transform: uppercase;
    }
    .section-kicker::after {
        content: "";
        width: 2.5rem;
        height: 1px;
        background: #C66C86;
    }
    .section-intro {
        max-width: 52rem;
        margin: 0 0 1rem;
        color: #66575D;
        line-height: 1.55;
    }
    .hero {
        position: relative;
        display: grid;
        grid-template-columns: minmax(0, 1.25fr) minmax(280px, .75fr);
        align-items: center;
        gap: 1.2rem;
        overflow: hidden;
        min-height: 355px;
        padding: clamp(1.45rem, 3.4vw, 2.8rem);
        margin: 0.2rem 0 1rem;
        border: 1px solid rgba(255, 232, 237, .17);
        border-radius: 0.45rem;
        color: #FFF8F4;
        background:
            radial-gradient(ellipse at 80% 50%, rgba(233,93,98,.15), transparent 34%),
            linear-gradient(112deg, #260812 0%, #48051A 56%, #6B1634 100%);
        box-shadow: 0 22px 58px rgba(48, 7, 22, .19);
    }
    .hero::before {
        content: "FIELD NOTES  /  ENERGY TRANSITIONS";
        position: absolute;
        right: 1.35rem;
        top: 1rem;
        color: rgba(255, 239, 240, .52);
        font-size: .6rem;
        font-weight: 750;
        letter-spacing: .16em;
    }
    .hero-eyebrow {
        color: #F1A9B5;
        font-size: 0.7rem;
        font-weight: 800;
        letter-spacing: 0.18em;
        text-transform: uppercase;
    }
    .hero h1 {
        max-width: 12ch;
        margin: 0.55rem 0 0.35rem;
        color: #FFF8F4 !important;
        font-family: Georgia, "Times New Roman", serif !important;
        font-size: clamp(3.2rem, 6.5vw, 6.35rem);
        line-height: .88;
        letter-spacing: -.065em;
        text-wrap: balance;
    }
    .hero-subtitle {
        margin: 1rem 0 0.6rem;
        color: #F4C3C9;
        font-family: Georgia, "Times New Roman", serif;
        font-size: clamp(1rem, 1.65vw, 1.35rem);
        font-weight: 500;
    }
    .hero-copy {
        max-width: 39rem;
        color: #F4E6E6;
        font-size: .95rem;
        line-height: 1.55;
    }
    .hero-action {
        display: inline-block;
        margin-top: 0.85rem;
        padding: 0.76rem 1.05rem;
        border: 1px solid #F8C4C9;
        border-radius: 0.25rem;
        background: #A72F50 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        text-decoration: none !important;
        font-weight: 750;
        transition: transform 160ms ease, background 160ms ease;
    }
    .hero-action:hover {
        background: #7F1734 !important;
        color: #FFFFFF !important;
        -webkit-text-fill-color: #FFFFFF !important;
        transform: translateY(-2px);
    }
    .hero-art {
        position: relative;
        display: grid;
        min-height: 275px;
        place-items: center;
        isolation: isolate;
    }
    .hero-globe {
        position: relative;
        z-index: 1;
        width: min(22vw, 250px);
        min-width: 190px;
        aspect-ratio: 1;
        border: 1px solid rgba(255, 213, 220, .58);
        border-radius: 50%;
        overflow: hidden;
        background:
            radial-gradient(circle at 32% 24%, rgba(255,216,200,.98), transparent 4%),
            radial-gradient(circle at 38% 33%, #F3A5A8 0%, #C95372 28%, #671536 70%, #300A1A 100%);
        box-shadow:
            inset -28px -8px 38px rgba(24, 5, 14, .66),
            inset 10px 6px 26px rgba(255, 235, 221, .28),
            0 0 40px rgba(233, 93, 98, .26),
            0 0 0 15px rgba(240, 142, 145, .07);
    }
    .hero-globe::before,
    .hero-globe::after {
        content: "";
        position: absolute;
        inset: 9% -5%;
        border: 1px solid rgba(255, 221, 220, .56);
        border-radius: 50%;
    }
    .hero-globe::before { transform: scaleX(.42); }
    .hero-globe::after {
        inset: 25% -4%;
        transform: rotate(-18deg);
        border-left-color: transparent;
        border-right-color: transparent;
    }
    .hero-orbit {
        position: absolute;
        z-index: 2;
        width: min(29vw, 340px);
        height: 112px;
        border: 1px solid rgba(250, 205, 212, .58);
        border-radius: 50%;
        transform: rotate(-27deg);
        pointer-events: none;
    }
    .hero-orbit.orbit-two {
        width: min(31vw, 370px);
        height: 155px;
        border-color: rgba(240, 142, 145, .32);
        transform: rotate(34deg);
    }
    .hero-star {
        position: absolute;
        z-index: 3;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        background: #FFD08A;
        box-shadow: 0 0 20px 5px rgba(255, 190, 124, .5);
    }
    .hero-star.one { top: 19%; right: 16%; }
    .hero-star.two { bottom: 17%; left: 16%; width: 7px; height: 7px; }
    .hero-facts {
        display: flex;
        flex-wrap: wrap;
        gap: 1.3rem;
        margin-top: 1.45rem;
    }
    .hero-fact {
        padding: 0;
        color: #F4DDE1;
        font-size: 0.73rem;
        letter-spacing: .025em;
    }
    .hero-fact strong {
        display: block;
        color: #FFF8F4;
        font-family: Georgia, "Times New Roman", serif;
        font-size: 1.45rem;
        letter-spacing: -.04em;
    }
    .hero-source-note {
        margin-top: 0.7rem;
        color: #D8BCC4;
        font-size: 0.71rem;
    }
    @media (max-width: 760px) {
        .hero { grid-template-columns: 1fr; }
        .hero { min-height: 0; }
        .hero-art { min-height: 190px; }
        .hero-globe { width: 168px; min-width: 168px; }
        .hero-orbit { width: 250px; height: 82px; }
        .hero-orbit.orbit-two { width: 275px; height: 105px; }
        .story-nav { top: 0; }
        .hero::before { font-size: .52rem; }
        .hero-facts { gap: .85rem; }
        .hero-fact strong { font-size: 1.2rem; }
        .closing-note { grid-template-columns: 1fr; }
        .closing-value { font-size: 1.7rem; }
    }
    @media (prefers-reduced-motion: reduce) {
        html { scroll-behavior: auto; }
        *, *::before, *::after {
            animation-duration: .01ms !important;
            transition-duration: .01ms !important;
        }
    }
    [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p {
        color: #67585E !important;
        font-size: 0.82rem;
        line-height: 1.45;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <section class="hero" id="overview">
      <div>
        <div class="hero-eyebrow">Energy transitions · data explorer</div>
        <h1>Powering<br>the Future</h1>
        <div class="hero-subtitle">One planet. Different paths to renewable electricity.</div>
        <div class="hero-copy">
          Explore how renewable electricity changes across countries and time,
          and how different sources shape each country's power mix.
        </div>
        <a class="hero-action" href="#world-map">Explore the atlas <span aria-hidden="true">↘</span></a>
        <div class="hero-facts">
          <span class="hero-fact"><strong>{len(countries)}</strong> country & territory labels</span>
          <span class="hero-fact"><strong>{available_2022}</strong> observed shares · 2022</span>
          <span class="hero-fact"><strong>{min(share_years)}—{max(share_years)}</strong> share years</span>
        </div>
        <div class="hero-source-note">
          {len(data):,} country-year records · counts are observations, not estimates
        </div>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="hero-orbit orbit-two"></div>
        <div class="hero-orbit"></div>
        <div class="hero-globe"></div>
        <span class="hero-star one"></span>
        <span class="hero-star two"></span>
      </div>
    </section>
    """,
    unsafe_allow_html=True,
)

if "focus_country" not in st.session_state:
    st.session_state["focus_country"] = (
        "United States" if "United States" in countries else countries[0]
    )
focus_country = st.session_state["focus_country"]
if "share_countries" not in st.session_state:
    st.session_state["share_countries"] = [focus_country]
if "technology_country" not in st.session_state:
    st.session_state["technology_country"] = focus_country

def update_shared_country() -> None:
    selected = st.session_state["focus_country"]
    st.session_state["share_countries"] = [selected]
    st.session_state["technology_country"] = selected

with st.container(key="exploration-bar"):
    explore_col, value_col, note_col = st.columns([1.15, 0.9, 1.25], vertical_alignment="center")
    with explore_col:
        focus_country = st.selectbox(
            "Your country",
            countries,
            key="focus_country",
            on_change=update_shared_country,
        )
    selected_country_rows = data.loc[data["country"] == focus_country]
    selected_share_rows = selected_country_rows.dropna(subset=["renewables_share_elec"])
    with value_col:
        if not selected_share_rows.empty:
            latest_observation = selected_share_rows.sort_values("year").iloc[-1]
            st.metric(
                f"{focus_country} · {int(latest_observation['year'])}",
                f"{latest_observation['renewables_share_elec']:.1f}%",
            )
        else:
            st.metric(f"{focus_country} · renewable share", "No observation")
    with note_col:
        st.caption(
            "Latest available record; coverage changes by year. This country follows "
            "you into the trend and technology chapters."
        )

with st.expander("Research question & data boundaries"):
    st.markdown(
        "**Question:** How have renewable electricity generation and its share changed "
        "across countries, and how do country renewable electricity mixes differ?"
    )
    st.caption(
        "Blank values remain missing, never zero. Share data spans "
        f"{min(share_years)}–{max(share_years)}; generation begins in "
        f"{min(generation_years)}; GDP ends in 2022. 2025 coverage is sparse. "
        "Country and regional observations stay separate."
    )

st.markdown(
    """
    <nav class="story-nav" aria-label="Story sections">
      <a href="#world-map"><span>01</span> &nbsp;Global picture</a>
      <a href="#over-time"><span>02</span> &nbsp;Race through time</a>
      <a href="#energy-mix"><span>03</span> &nbsp;Energy mix</a>
      <a href="#gdp"><span>04</span> &nbsp;Wealth & electricity</a>
      <a href="#rankings"><span>05</span> &nbsp;Who leads?</a>
      <a href="#comparisons"><span>06</span> &nbsp;Different paths</a>
    </nav>
    """,
    unsafe_allow_html=True,
)

add_anchor("world-map")
st.markdown('<div class="section-kicker">01 — World atlas</div>', unsafe_allow_html=True)
st.header("The global picture")
st.markdown(
    '<div class="section-intro">Compare observed renewable electricity shares across '
    'countries. Uncolored locations are unavailable or unmapped, never zero.</div>',
    unsafe_allow_html=True,
)
default_map_year = 2022 if 2022 in map_share_years else map_share_years[-1]
map_select_col, map_info_col = st.columns([3.6, 1.15], gap="large")
with map_info_col:
    map_year = st.select_slider(
        "Map year",
        options=map_share_years,
        value=default_map_year,
        key="map_year",
    )
map_year_rows = data.loc[
    (data["year"] == map_year) & data["renewables_share_elec"].notna()
].copy()
map_data = map_year_rows.merge(
    map_countries, on="country", suffixes=("", "_map"), how="inner"
)
map_data["iso_code"] = map_data["iso_code"].fillna(map_data["iso_code_map"])
map_data = map_data.drop(columns=["iso_code_map"], errors="ignore")
map_valid_ids = map_data["iso_code"].str.fullmatch(r"[A-Z]{3}", na=False)
map_data = map_data.loc[map_valid_ids]
map_country_options = sorted(map_data["country"].unique().tolist())
if not map_country_options:
    map_country_options = [focus_country]
if st.session_state.get("map_country") not in map_country_options:
    st.session_state["map_country"] = (
        focus_country if focus_country in map_country_options else map_country_options[0]
    )
with map_select_col:
    if map_data.empty:
        st.info("No mappable country share observations are available for this year.")
    else:
        fig = px.choropleth(
            map_data,
            locations="iso_code",
            locationmode="ISO-3",
            color="renewables_share_elec",
            hover_name="country",
            hover_data={
                "year": True,
                "renewables_share_elec": ":.2f",
            },
            color_continuous_scale=["#F2E3E7", "#D9A4B1", "#C66C86", "#65051F"],
            range_color=(0, 100),
            labels={"renewables_share_elec": "Renewable share (%)"},
            title=f"Renewable electricity share by country · {map_year}",
        )
        fig.update_geos(
            showframe=False,
            showcoastlines=False,
            showland=True,
            landcolor="#F5ECEA",
            showocean=True,
            oceancolor="#FCF8F5",
            showcountries=True,
            countrycolor="#CDB9BE",
            countrywidth=0.55,
            bgcolor="#FCF8F5",
            projection_type="natural earth",
        )
        fig.update_layout(
            coloraxis_colorbar=dict(
                title=dict(text="Share (%)", font=dict(color="#34272B")),
                tickfont=dict(color="#34272B"),
                outlinecolor="#D8C9CD",
                bgcolor="#FFFFFF",
            ),
            margin=dict(l=8, r=8, t=52, b=8),
        )
        safe_plot(fig, key="world_map", height=500, margin=dict(l=4, r=4, t=48, b=4))
with map_info_col:
    st.caption("Color = share of electricity generation. Pale land has no mapped observation.")
    st.metric(
        "Observed / mapped",
        f"{len(map_year_rows)} / {len(map_data)}",
        help=f"Observed share rows / rows with a valid three-letter map code in {map_year}.",
    )
    selected_map_country = st.selectbox(
        "Inspect a mapped country",
        map_country_options,
        key="map_country",
    )
    selected_value = map_data.loc[
        map_data["country"] == selected_map_country, "renewables_share_elec"
    ]
    if not selected_value.empty:
        st.metric(
            f"{selected_map_country} · {map_year}",
            f"{selected_value.iloc[0]:.2f}%",
        )
    else:
        st.info(f"No mapped share observation for {selected_map_country} in {map_year}.")
    st.caption("Unmapped country rows remain available in the other views.")

add_anchor("over-time")
st.markdown('<div class="section-kicker">02 — Time travel</div>', unsafe_allow_html=True)
st.header("The race through time")
st.markdown(
    '<div class="section-intro">Follow each country’s renewable electricity share '
    'through the years. Gaps remain visible where observations are missing.</div>',
    unsafe_allow_html=True,
)
share_select = st.multiselect(
    "Countries for share trend",
    countries,
    key="share_countries",
)
share_start, share_end = st.slider(
    "Share-trend year range",
    min_value=min(share_years),
    max_value=max(share_years),
    value=(2000, 2022) if min(share_years) <= 2000 and max(share_years) >= 2022 else (min(share_years), max(share_years)),
    key="share_range",
)
share_subset = filter_observations(
    data,
    countries=share_select,
    year_range=(share_start, share_end),
    value_column="renewables_share_elec",
).sort_values(["country", "year"])
if share_subset.empty:
    st.info("Select at least one country with renewable-share observations in this range.")
else:
    share_colors = {
        country: TIMELINE_PALETTE[countries.index(country) % len(TIMELINE_PALETTE)]
        for country in share_select
    }
    animation_end_key = "share_animation_endpoint"
    if animation_end_key not in st.session_state:
        st.session_state[animation_end_key] = share_end
    endpoint_options = list(range(share_start, share_end + 1))
    st.session_state[animation_end_key] = min(
        max(int(st.session_state[animation_end_key]), share_start), share_end
    )

    def step_animation() -> None:
        values = list(range(st.session_state["share_range"][0], st.session_state["share_range"][1] + 1))
        current = st.session_state.get("share_animation_endpoint", values[0])
        st.session_state["share_animation_endpoint"] = values[
            min(values.index(current) + 1, len(values) - 1)
        ]

    def reset_animation() -> None:
        st.session_state["share_animation_endpoint"] = st.session_state["share_range"][1]

    with st.container(key="timeline-controls"):
        animation_controls = st.columns([1.5, 1.7, 5.8])
        animation_controls[0].button(
            "Step forward →", on_click=step_animation, key="animation_step",
            help="Advance the selected animation endpoint by one year.",
        )
        animation_controls[1].button(
            "Reset endpoint", on_click=reset_animation, key="animation_reset",
        )
        endpoint = st.select_slider(
            "Animation endpoint",
            options=endpoint_options,
            key=animation_end_key,
            help="Use Plotly's Play/Pause controls, Step forward, or choose an endpoint.",
        )
        st.caption(
            "Year range sets the available window; the endpoint sets the initial frame; "
            "Playback year and Play/Pause browse the cumulative frames."
        )
    animated = go.Figure()
    country_frame = share_subset.pivot(
        index="year", columns="country", values="renewables_share_elec"
    ).reindex(range(share_start, share_end + 1))
    all_years = list(country_frame.index.astype(int))
    for country in share_select:
        if country in country_frame:
            animated.add_trace(
                go.Scatter(
                    x=all_years,
                    y=country_frame[country].where(
                        country_frame.index <= endpoint
                    ).tolist(),
                    name=country,
                    mode="lines+markers",
                    connectgaps=False,
                    line=dict(color=share_colors[country]),
                    hovertemplate=(
                        f"{country}<br>Year: %{{x}}<br>"
                        "Renewable share: %{y:.2f}%<extra></extra>"
                    ),
                )
            )
    frames = []
    for frame_year in all_years:
        frames.append(
            go.Frame(
                name=str(frame_year),
                data=[
                    go.Scatter(
                        x=all_years,
                        y=country_frame[country]
                        .where(country_frame.index <= frame_year)
                        .tolist(),
                    )
                    for country in share_select
                    if country in country_frame
                ],
            )
        )
    animated.frames = frames
    animated.update_layout(
        title=f"Renewable electricity share · observations through {endpoint}",
        xaxis_title="Year",
        yaxis_title="Share of electricity generation (%)",
        yaxis=dict(rangemode="tozero"),
        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 0.02,
                "y": -0.32,
                "xanchor": "left",
                "yanchor": "top",
                "pad": {"t": 4, "r": 5},
                "bgcolor": "#FFF8F4",
                "bordercolor": "#E8BFC9",
                "font": {"color": "#48051A", "size": 12},
                "buttons": [
                    {
                        "label": "Play",
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "frame": {"duration": 350, "redraw": True},
                                "transition": {"duration": 150},
                                "fromcurrent": True,
                            },
                        ],
                    },
                    {
                        "label": "Pause",
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "frame": {"duration": 0, "redraw": False},
                                "mode": "immediate",
                            },
                        ],
                    },
                ],
            }
        ],
        sliders=[
            {
                "x": 0.25,
                "len": 0.73,
                "y": -0.17,
                "yanchor": "top",
                "active": all_years.index(endpoint),
                "currentvalue": {
                    "prefix": "Playback year: ",
                "font": {"color": "#FFF1F0", "size": 12},
                },
                "font": {"color": "#FFF1F0", "size": 10},
                "bgcolor": "rgba(255,255,255,.08)",
                "bordercolor": "rgba(255,255,255,.18)",
                "activebgcolor": "#E97C8E",
                "steps": [
                    {
                        "label": str(year),
                        "method": "animate",
                        "args": [
                            [str(year)],
                            {
                                "mode": "immediate",
                                "frame": {"duration": 0, "redraw": True},
                                "transition": {"duration": 0},
                            },
                        ],
                    }
                    for year in all_years
                ],
            }
        ],
        transition={"duration": 0},
    )
    safe_plot(
        animated,
        key="share_time_series",
        height=500,
        margin=dict(l=52, r=30, t=74, b=116),
        dark=True,
    )
    st.caption(
        f"Selected countries: {', '.join(share_select) if share_select else 'none'} · "
        f"range: {share_start}–{share_end} · displayed through {endpoint}. "
        "Missing years remain gaps."
    )

add_anchor("energy-mix")
st.markdown('<div class="section-kicker">03 — Sources & generation</div>', unsafe_allow_html=True)
st.header("Meet the energy mix")
st.markdown(
    '<div class="section-intro">Compare observed generation by source. Lines are '
    'separate TWh measures—not a stacked total.</div>',
    unsafe_allow_html=True,
)
tech_country = st.selectbox(
    "Country for technology trends",
    countries,
    key="technology_country",
)
tech_options = list(TECHNOLOGY_COLUMNS.keys())
tech_selected = st.multiselect(
    "Technologies to show",
    tech_options,
    default=tech_options,
    key="technologies",
)
tech_start, tech_end = st.slider(
    "Technology year range",
    min_value=min(generation_years),
    max_value=max(generation_years),
    value=(2000, 2022) if min(generation_years) <= 2000 and max(generation_years) >= 2022 else (min(generation_years), max(generation_years)),
    key="technology_range",
)
tech_frames = []
for technology in tech_selected:
    column = TECHNOLOGY_COLUMNS[technology]
    part = country_rows(data, tech_country, tech_start, tech_end)[
        ["year", column]
    ].rename(columns={column: "Generation (TWh)"})
    part["Technology"] = technology
    tech_frames.append(part)
if not tech_frames:
    st.info("Choose one or more technology indicators.")
else:
    tech_data = pd.concat(tech_frames, ignore_index=True)
    line_chart(
        tech_data,
        x="year",
        y="Generation (TWh)",
        color="Technology",
        title=f"Observed renewable generation by technology · {tech_country}",
        y_title="Electricity generation (TWh)",
        key="technology_trends",
        color_map=COLORS,
        hover_data={"Technology": True, "Generation (TWh)": ":.3f"},
    )
    tech_coverage = {
        label: int(country_rows(data, tech_country, tech_start, tech_end)[column].notna().sum())
        for label, column in TECHNOLOGY_COLUMNS.items()
        if label in tech_selected
    }
    st.caption(
        "Observed points in the selected window: "
        + "; ".join(f"{name}: {count}" for name, count in tech_coverage.items())
        + ". Different sources may have different coverage; no values are imputed."
    )

add_anchor("gdp")
st.markdown('<div class="section-kicker">04 — An exploratory lens</div>', unsafe_allow_html=True)
st.header("Wealth and clean electricity")
st.markdown(
    '<div class="section-intro">Each point has both GDP and renewable-share data for '
    'the selected year. The pattern is observational, not causal.</div>',
    unsafe_allow_html=True,
)
if not gdp_years:
    st.info("There are no years with both GDP and renewable-share observations.")
else:
    gdp_default_year = 2022 if 2022 in gdp_years else gdp_years[-1]
    gdp_year = st.selectbox(
        "GDP comparison year",
        gdp_years,
        index=gdp_years.index(gdp_default_year),
        key="gdp_year",
    )
    gdp_cases = gdp_share_complete_cases(data, gdp_year)
    gdp_countries = st.multiselect(
        "Countries to include (leave empty for all complete cases)",
        countries,
        default=[],
        key="gdp_countries",
    )
    if gdp_countries:
        gdp_cases = gdp_cases[gdp_cases["country"].isin(gdp_countries)]
    log_gdp = st.checkbox(
        "Use logarithmic GDP axis",
        value=True,
        help="GDP values span several orders of magnitude. A log scale makes smaller and larger economies easier to inspect together.",
        key="gdp_log_scale",
    )
    nonpositive_gdp_count = int((gdp_cases["gdp"] <= 0).sum()) if log_gdp else 0
    plotted_gdp_cases = (
        gdp_cases.loc[gdp_cases["gdp"] > 0].copy() if log_gdp else gdp_cases.copy()
    )
    st.caption(
        f"{len(plotted_gdp_cases)} complete country observations plotted for {gdp_year}; "
        f"{data.loc[data['year'] == gdp_year, 'country'].nunique()} country records "
        "exist that year. Missing GDP or share excludes a point only from this chart."
    )
    if log_gdp and nonpositive_gdp_count:
        st.caption(
            f"{nonpositive_gdp_count} complete-case observation(s) with nonpositive GDP "
            "are omitted because they cannot appear on a logarithmic axis."
        )
    if plotted_gdp_cases.empty:
        if gdp_cases.empty:
            st.info("No countries have both required values for this selection.")
        else:
            st.info(
                "No positive GDP values are available for a logarithmic plot. "
                "Turn off the log scale to view these complete cases."
            )
    else:
        fig = px.scatter(
            plotted_gdp_cases,
            x="gdp",
            y="renewables_share_elec",
            hover_name="country",
            hover_data={
                "year": True,
                "gdp": ":,.0f",
                "renewables_share_elec": ":.2f",
            },
            labels={
                "gdp": (
                    "GDP (2011 international-$, log scale)"
                    if log_gdp
                    else "GDP (2011 international-$)"
                ),
                "renewables_share_elec": "Renewable share of electricity (%)",
            },
            title=f"GDP and renewable electricity share · {gdp_year}",
            color_discrete_sequence=[COLORS["Renewable share"]],
        )
        if log_gdp:
            fig.update_xaxes(type="log", tickformat=".1s")
        fig.update_yaxes(rangemode="tozero")
        safe_plot(fig, key="gdp_scatter")
        with st.expander(
            "Show complete cases (including any omitted from the log-scale plot)"
        ):
            st.dataframe(
                gdp_cases[
                    ["country", "year", "gdp", "renewables_share_elec"]
                ].sort_values("country"),
                hide_index=True,
                width="stretch",
            )

add_anchor("rankings")
st.markdown('<div class="section-kicker">05 — A year in focus</div>', unsafe_allow_html=True)
st.header("Who leads the transition?")
st.markdown(
    '<div class="section-intro">Rank only countries with observed values in the '
    'selected year. Ties share a rank; names order tied bars.</div>',
    unsafe_allow_html=True,
)
ranking_year = st.selectbox(
    "Ranking year",
    share_years,
    index=share_years.index(default_map_year),
    key="ranking_year",
)
ranking_direction = st.radio(
    "Countries to display",
    ["Highest shares", "Lowest shares"],
    horizontal=True,
    key="ranking_direction",
)
ranking_limit = st.slider(
    "Number of countries",
    min_value=5,
    max_value=30,
    value=15,
    key="ranking_limit",
)
ranking_ascending = ranking_direction == "Lowest shares"
ranked = rank_countries(
    data, ranking_year, ascending=ranking_ascending, limit=ranking_limit
)
rank_total = int(
    data.loc[
        (data["year"] == ranking_year) & data["renewables_share_elec"].notna(),
        "country",
    ].nunique()
)
st.caption(
    f"{rank_total} countries have valid values in {ranking_year}; showing "
    f"{len(ranked)} {ranking_direction.lower()}."
)
if ranked.empty:
    st.info("No countries have a valid share value for this year.")
else:
    ranking_display = ranked.sort_values(
        ["renewables_share_elec", "country"],
        ascending=[True, True],
        kind="stable",
    ).copy()
    fig = px.bar(
        ranking_display,
        x="renewables_share_elec",
        y="country",
        orientation="h",
        text="renewables_share_elec",
        hover_data={"rank": True, "renewables_share_elec": ":.2f"},
        labels={
            "renewables_share_elec": "Renewable share of electricity (%)",
            "country": "Country",
            "rank": "Rank (ties share the same rank)",
        },
        title=f"{ranking_direction} · {ranking_year}",
        color_discrete_sequence=[
            "#C66C86" if ranking_ascending else COLORS["Renewable share"]
        ],
    )
    fig.update_traces(
        texttemplate="%{x:.1f}%",
        textposition="outside",
        cliponaxis=False,
    )
    fig.update_xaxes(range=[0, 112], ticksuffix="%")
    fig.update_yaxes(
        categoryorder="array",
        categoryarray=ranking_display["country"].tolist(),
        automargin=True,
    )
    safe_plot(
        fig,
        key="country_rankings",
        height=max(390, min(650, 22 * len(ranked) + 80)),
        margin=dict(l=155, r=80, t=58, b=46),
    )
    with st.expander("Show ranking values and ranks"):
        st.dataframe(
            ranked[["rank", "country", "renewables_share_elec"]].rename(
                columns={"renewables_share_elec": "Share (%)"}
            ),
            hide_index=True,
            width="stretch",
        )

add_anchor("comparisons")
st.markdown('<div class="section-kicker">06 — Side by side</div>', unsafe_allow_html=True)
st.header("Different paths, one transition")
st.markdown(
    '<div class="section-intro">Compare two to four countries over the same period. '
    'Share (%) and generation (TWh) stay on separate charts.</div>',
    unsafe_allow_html=True,
)
default_transition = [focus_country]
for candidate in ("China", "Denmark", "Brazil", "United States"):
    if candidate in countries and candidate not in default_transition:
        default_transition.append(candidate)
    if len(default_transition) == 3:
        break
if "transition_countries" not in st.session_state:
    st.session_state["transition_countries"] = default_transition
if "transition_range" not in st.session_state:
    st.session_state["transition_range"] = (2000, 2022)

def reset_transition() -> None:
    st.session_state["transition_countries"] = default_transition
    st.session_state["transition_range"] = (
        max(1985, min(share_years)),
        min(2022, max(share_years)),
    )

st.button("Reset country comparison", on_click=reset_transition, key="transition_reset")
transition_countries = st.multiselect(
    "Choose 2–4 countries",
    countries,
    max_selections=4,
    key="transition_countries",
)
transition_min = max(1985, min(share_years))
transition_max = min(2022, max(share_years))
if transition_min >= transition_max:
    transition_min, transition_max = min(share_years), max(share_years)
current_transition_range = st.session_state["transition_range"]
if (
    current_transition_range[0] < transition_min
    or current_transition_range[1] > transition_max
):
    st.session_state["transition_range"] = (transition_min, transition_max)
transition_range = st.slider(
    "Comparison year range",
    min_value=transition_min,
    max_value=transition_max,
    key="transition_range",
)
transition_techs = st.multiselect(
    "Generation technologies to compare",
    tech_options,
    default=["Hydro", "Wind", "Solar"],
    key="transition_technologies",
)
if len(transition_countries) < 2:
    st.info("Choose at least two countries to compare their transitions.")
else:
    transition_share = filter_observations(
        data,
        countries=transition_countries,
        year_range=transition_range,
    ).dropna(subset=["renewables_share_elec"])
    line_chart(
        transition_share,
        x="year",
        y="renewables_share_elec",
        color="country",
        title="Renewable electricity share across selected countries",
        y_title="Share of electricity generation (%)",
        key="transition_share",
        color_map={
            country: COUNTRY_PALETTE[index % len(COUNTRY_PALETTE)]
            for index, country in enumerate(countries)
        },
        hover_data={"renewables_share_elec": ":.2f"},
    )
    technology_parts = []
    for country in transition_countries:
        observed = country_rows(
            data, country, transition_range[0], transition_range[1]
        )
        for technology in transition_techs:
            column = TECHNOLOGY_COLUMNS[technology]
            part = observed[["year", column]].rename(
                columns={column: "Generation (TWh)"}
            )
            part["country"] = country
            part["Technology"] = technology
            technology_parts.append(part)
    if not transition_techs:
        st.info("Choose at least one generation technology.")
    else:
        transition_technology = pd.concat(technology_parts, ignore_index=True)
        transition_country_colors = {
            country: COUNTRY_PALETTE[countries.index(country) % len(COUNTRY_PALETTE)]
            for country in transition_countries
        }
        line_chart(
            transition_technology,
            x="year",
            y="Generation (TWh)",
            color="country",
            title="Technology generation (separate TWh series)",
            y_title="Electricity generation (TWh)",
            key="transition_technology",
            color_map=transition_country_colors,
            hover_data={
                "country": True,
                "Technology": True,
                "Generation (TWh)": ":.3f",
            },
        )
        st.caption(
            "Series share a common TWh scale. Blanks are gaps; countries and "
            "technologies with sparse records may have shorter lines."
        )

selected_latest_share = (
    selected_share_rows.sort_values("year").iloc[-1]
    if not selected_share_rows.empty
    else None
)
if selected_latest_share is not None:
    st.markdown(
        f"""
        <div class="closing-note">
          <div>
            <strong>Your next question starts with one country.</strong>
            <span>{focus_country} has an observed renewable-electricity share in
            {int(selected_latest_share['year'])}. Compare its timeline, generation mix,
            and country peers above; missing years remain gaps.</span>
          </div>
          <div class="closing-value">
            {selected_latest_share['renewables_share_elec']:.1f}%<br>
            <span>{int(selected_latest_share['year'])} observed share</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.divider()
add_anchor("data-notes")
st.markdown('<div class="section-kicker">Sources & methods</div>', unsafe_allow_html=True)
st.header("Data notes")
with st.expander("Data checks, limitations, and source notes"):
    st.markdown(
        f"""
        **Preparation checks:** the country file has {country_diag['rows']:,} rows,
        {country_diag['exact_duplicate_rows']} exact duplicate rows, and
        {country_diag['duplicate_country_year_rows']} repeated country-year keys.
        The three repeated source headers were checked cell by cell and are identical;
        the duplicate copies are excluded from analysis after that check. Invalid
        numeric conversions: {sum(country_diag['invalid_numeric_conversions'].values())}.

        **Map limitation:** only records with a three-letter ISO-style code are drawn.
        Plotly's built-in ISO-3 map may not resolve every code. The country selector
        lists mapped observations and makes values inspectable.

        **Regional file:** {len(region):,} regional rows and {region['country'].nunique()}
        labels are kept separately. Regional labels can overlap (for example, multiple
        Africa definitions), so they are not summed or merged with country rows.

        **Provenance:** supplied Kaggle files:
        [Global Renewable Energy by Country (1900–2025)](
        https://www.kaggle.com/datasets/riyagarg0314/global-renewable-energy-by-country-1900-2025).
        Variable definitions and units were checked against the
        [Our World in Data Energy codebook](
        https://github.com/owid/energy-data/blob/master/owid-energy-codebook.csv)
        and its [energy-data documentation](https://github.com/owid/energy-data).
        The exact archived Kaggle export/version is not identified inside these CSVs.

        **Measures and units:** renewable electricity share is the percentage of total
        electricity generated. Renewable, hydro, solar, wind, and other-renewable
        electricity fields are generation in TWh. GDP is in inflation- and
        purchasing-power-adjusted 2011 international dollars. `renewables_share_energy`
        is primary energy share, not the electricity-share field.

        **Coverage:** share observations are available in {min(share_years)}–{max(share_years)};
        generation observations in {min(generation_years)}–{max(generation_years)};
        GDP observations end in 2022. Counts vary by variable and year. Blank values are
        retained as missing; no zeros or interpolated values are created.

        **GDP comparison:** the scatter uses rows with both GDP and share observed in
        the selected year. It is descriptive and does not demonstrate causality.
        """
    )

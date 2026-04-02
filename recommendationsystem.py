import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import streamlit as st

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="CinemaScout",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@500;700&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.stApp {
    background-color: #0d0d0d;
    color: #e8e2d9;
}

/* Hide default Streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 3rem; }

h1, h2, h3 { font-family: 'Playfair Display', serif !important; }

/* Hero */
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    font-weight: 700;
    color: #f5ede0;
    text-align: center;
    margin-bottom: 0;
    line-height: 1.1;
}
.hero-title span { color: #c9a96e; }
.hero-sub {
    text-align: center;
    font-size: 0.75rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #4a4540;
    margin-bottom: 2rem;
    font-weight: 300;
}

/* Movie card */
.movie-card {
    background: #161410;
    border: 1px solid #2a2420;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 0.75rem;
    transition: border-color 0.2s;
}
.movie-card:hover { border-color: #5a4a30; }
.card-title {
    font-family: 'Playfair Display', serif;
    font-size: 1rem;
    font-weight: 500;
    color: #f0e8d8;
    margin-bottom: 4px;
}
.card-meta {
    font-size: 0.72rem;
    color: #5a5550;
    margin-bottom: 6px;
}
.badge {
    display: inline-block;
    font-size: 0.65rem;
    font-weight: 500;
    background: #1e1a16;
    border: 1px solid #3a3025;
    border-radius: 4px;
    padding: 2px 7px;
    color: #9a8060;
    letter-spacing: 0.3px;
    margin-bottom: 8px;
}

/* Score bar */
.score-wrap { margin-top: 6px; }
.score-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.65rem;
    color: #4a4540;
    margin-bottom: 2px;
}
.score-track {
    height: 3px;
    background: #2a2420;
    border-radius: 2px;
    overflow: hidden;
    margin-bottom: 4px;
}
.score-fill-gold { height: 100%; background: #c9a96e; border-radius: 2px; }
.score-fill-dim  { height: 100%; background: #6a5a3a; border-radius: 2px; }

/* Tab styling override */
[data-baseweb="tab-list"] {
    background: #161410 !important;
    border: 1px solid #2a2420 !important;
    border-radius: 10px !important;
    gap: 0 !important;
    padding: 2px !important;
}
[data-baseweb="tab"] {
    background: transparent !important;
    color: #6b6560 !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    border-radius: 8px !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: #1e1a16 !important;
    color: #c9a96e !important;
}

/* Input / button overrides */
.stTextInput input, .stSelectbox select {
    background: #161410 !important;
    border: 1px solid #2a2420 !important;
    color: #e8e2d9 !important;
    border-radius: 8px !important;
    font-family: 'DM Sans', sans-serif !important;
}
.stTextInput input:focus { border-color: #5a4a30 !important; }

.stButton > button {
    background: #c9a96e !important;
    border: none !important;
    border-radius: 8px !important;
    color: #0d0d0d !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.8rem !important;
    font-weight: 600 !important;
    padding: 0.5rem 1.5rem !important;
    letter-spacing: 0.2px !important;
}
.stButton > button:hover { background: #dab97e !important; }

/* Section label */
.results-label {
    font-size: 0.65rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #4a4540;
    margin-bottom: 0.75rem;
    font-weight: 500;
}

/* Genre chip */
.genre-chip {
    display: inline-block;
    background: #161410;
    border: 1px solid #2a2420;
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.75rem;
    color: #7a7068;
    margin: 3px;
    cursor: pointer;
}

/* AI response box */
.ai-box {
    background: #161410;
    border: 1px solid #2a2420;
    border-left: 3px solid #c9a96e;
    border-radius: 8px;
    padding: 1rem 1.25rem;
    font-size: 0.875rem;
    color: #c8bfb0;
    line-height: 1.7;
}

/* Empty state */
.empty-state {
    text-align: center;
    padding: 3rem 1rem;
    color: #4a4540;
    font-size: 0.875rem;
}

div[data-testid="stVerticalBlock"] > div { background: transparent; }
</style>
""", unsafe_allow_html=True)


# ── Data ───────────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    movies = [
        {"Film":"Zack and Miri Make a Porno","Genre":"Romance","Studio":"The Weinstein Company","Audience":70,"Profit":1.76,"RT":64,"Gross":41.94,"Year":2008},
        {"Film":"Youth in Revolt","Genre":"Comedy","Studio":"The Weinstein Company","Audience":52,"Profit":1.09,"RT":68,"Gross":19.62,"Year":2009},
        {"Film":"You Will Meet a Tall Dark Stranger","Genre":"Comedy","Studio":"Sony","Audience":35,"Profit":1.21,"RT":43,"Gross":26.69,"Year":2010},
        {"Film":"When in Rome","Genre":"Comedy","Studio":"Disney","Audience":44,"Profit":0.00,"RT":15,"Gross":43.04,"Year":2010},
        {"Film":"What Happens in Vegas","Genre":"Comedy","Studio":"Fox","Audience":72,"Profit":6.27,"RT":28,"Gross":219.37,"Year":2008},
        {"Film":"Water For Elephants","Genre":"Drama","Studio":"Fox","Audience":72,"Profit":3.08,"RT":60,"Gross":117.09,"Year":2011},
        {"Film":"Waitress","Genre":"Romance","Studio":"Fox","Audience":67,"Profit":11.08,"RT":89,"Gross":22.16,"Year":2007},
        {"Film":"Twilight","Genre":"Romance","Studio":"Summit Entertainment","Audience":82,"Profit":10.18,"RT":49,"Gross":376.66,"Year":2008},
        {"Film":"The Ugly Truth","Genre":"Comedy","Studio":"Sony","Audience":68,"Profit":5.34,"RT":14,"Gross":205.30,"Year":2009},
        {"Film":"The Proposal","Genre":"Comedy","Studio":"Disney","Audience":74,"Profit":7.80,"RT":45,"Gross":314.70,"Year":2009},
        {"Film":"The Bounty Hunter","Genre":"Romance","Studio":"Sony","Audience":54,"Profit":3.42,"RT":10,"Gross":136.10,"Year":2010},
        {"Film":"Tangled","Genre":"Animation","Studio":"Disney","Audience":88,"Profit":4.00,"RT":89,"Gross":591.79,"Year":2010},
        {"Film":"Superbad","Genre":"Comedy","Studio":"Sony","Audience":91,"Profit":7.64,"RT":88,"Gross":169.90,"Year":2007},
        {"Film":"She's Out of My League","Genre":"Comedy","Studio":"Paramount/Dreamworks","Audience":64,"Profit":3.70,"RT":57,"Gross":48.80,"Year":2010},
        {"Film":"Sex Drive","Genre":"Comedy","Studio":"Summit Entertainment","Audience":68,"Profit":1.10,"RT":72,"Gross":38.74,"Year":2008},
        {"Film":"Remember Me","Genre":"Drama","Studio":"Summit Entertainment","Audience":70,"Profit":2.90,"RT":27,"Gross":55.70,"Year":2010},
        {"Film":"Rachel Getting Married","Genre":"Drama","Studio":"Sony","Audience":61,"Profit":3.10,"RT":85,"Gross":12.77,"Year":2008},
        {"Film":"Precious","Genre":"Drama","Studio":"Lionsgate","Audience":68,"Profit":4.05,"RT":91,"Gross":47.54,"Year":2009},
        {"Film":"Our Family Wedding","Genre":"Comedy","Studio":"Fox","Audience":52,"Profit":0.00,"RT":18,"Gross":21.37,"Year":2010},
        {"Film":"Nick and Norah's Infinite Playlist","Genre":"Comedy","Studio":"Sony","Audience":67,"Profit":3.00,"RT":73,"Gross":31.50,"Year":2008},
        {"Film":"My Week with Marilyn","Genre":"Drama","Studio":"The Weinstein Company","Audience":84,"Profit":2.10,"RT":83,"Gross":14.59,"Year":2011},
        {"Film":"Monte Carlo","Genre":"Romance","Studio":"Fox","Audience":65,"Profit":3.20,"RT":21,"Gross":38.88,"Year":2011},
        {"Film":"Mamma Mia!","Genre":"Comedy","Studio":"Universal","Audience":76,"Profit":9.48,"RT":54,"Gross":609.47,"Year":2008},
        {"Film":"Love & Other Drugs","Genre":"Romance","Studio":"Fox","Audience":60,"Profit":2.40,"RT":49,"Gross":98.24,"Year":2010},
        {"Film":"Life as We Know It","Genre":"Comedy","Studio":"Warner Bros.","Audience":70,"Profit":2.80,"RT":28,"Gross":96.50,"Year":2010},
        {"Film":"Letters to Juliet","Genre":"Romance","Studio":"Summit Entertainment","Audience":63,"Profit":2.80,"RT":40,"Gross":79.17,"Year":2010},
        {"Film":"Killers","Genre":"Action","Studio":"Lionsgate","Audience":56,"Profit":3.30,"RT":11,"Gross":98.16,"Year":2010},
        {"Film":"It's Complicated","Genre":"Romance","Studio":"Universal","Audience":63,"Profit":4.25,"RT":56,"Gross":219.10,"Year":2009},
        {"Film":"Hereafter","Genre":"Drama","Studio":"Warner Bros.","Audience":61,"Profit":3.10,"RT":47,"Gross":104.03,"Year":2010},
        {"Film":"He's Just Not That Into You","Genre":"Comedy","Studio":"Warner Bros.","Audience":60,"Profit":5.90,"RT":42,"Gross":178.84,"Year":2009},
        {"Film":"Going the Distance","Genre":"Romance","Studio":"Warner Bros.","Audience":57,"Profit":0.70,"RT":53,"Gross":42.05,"Year":2010},
        {"Film":"Gnomeo and Juliet","Genre":"Animation","Studio":"Disney","Audience":54,"Profit":5.70,"RT":56,"Gross":193.97,"Year":2011},
        {"Film":"Four Christmases","Genre":"Comedy","Studio":"Warner Bros.","Audience":62,"Profit":4.00,"RT":25,"Gross":161.83,"Year":2008},
        {"Film":"Failure to Launch","Genre":"Romance","Studio":"Paramount","Audience":47,"Profit":5.30,"RT":24,"Gross":128.52,"Year":2006},
        {"Film":"Enchanted","Genre":"Animation","Studio":"Disney","Audience":80,"Profit":5.40,"RT":93,"Gross":340.49,"Year":2007},
        {"Film":"Dear John","Genre":"Drama","Studio":"Sony","Audience":66,"Profit":4.00,"RT":30,"Gross":114.97,"Year":2010},
        {"Film":"Country Strong","Genre":"Drama","Studio":"Sony","Audience":64,"Profit":2.50,"RT":36,"Gross":20.16,"Year":2011},
        {"Film":"Confessions of a Shopaholic","Genre":"Comedy","Studio":"Disney","Audience":56,"Profit":2.00,"RT":24,"Gross":108.34,"Year":2009},
        {"Film":"Catch and Release","Genre":"Romance","Studio":"Sony","Audience":55,"Profit":2.00,"RT":27,"Gross":16.70,"Year":2007},
        {"Film":"Bride Wars","Genre":"Comedy","Studio":"Fox","Audience":57,"Profit":3.30,"RT":10,"Gross":114.72,"Year":2009},
        {"Film":"Bolt","Genre":"Animation","Studio":"Disney","Audience":73,"Profit":4.40,"RT":86,"Gross":309.98,"Year":2008},
        {"Film":"Blades of Glory","Genre":"Comedy","Studio":"Paramount/Dreamworks","Audience":71,"Profit":4.00,"RT":69,"Gross":145.74,"Year":2007},
        {"Film":"Big Eyes","Genre":"Drama","Studio":"The Weinstein Company","Audience":68,"Profit":1.90,"RT":72,"Gross":24.62,"Year":2014},
        {"Film":"Bedtime Stories","Genre":"Comedy","Studio":"Disney","Audience":64,"Profit":3.50,"RT":25,"Gross":212.87,"Year":2008},
        {"Film":"Because I Said So","Genre":"Romance","Studio":"Universal","Audience":55,"Profit":1.50,"RT":9,"Gross":42.65,"Year":2007},
        {"Film":"P.S. I Love You","Genre":"Romance","Studio":"Warner Bros.","Audience":68,"Profit":2.70,"RT":22,"Gross":156.84,"Year":2007},
        {"Film":"Atonement","Genre":"Drama","Studio":"Universal","Audience":72,"Profit":2.60,"RT":83,"Gross":129.35,"Year":2007},
    ]
    df = pd.DataFrame(movies)
    df['features'] = (
        df['Genre'] + ' ' + df['Studio'] + ' ' +
        df['Audience'].astype(str) + ' ' + df['Profit'].astype(str) + ' ' +
        df['RT'].astype(str) + ' ' + df['Gross'].astype(str) + ' ' +
        df['Year'].astype(str)
    )
    return df

@st.cache_data
def build_similarity(df):
    tfidf = TfidfVectorizer(stop_words='english')
    matrix = tfidf.fit_transform(df['features'])
    return linear_kernel(matrix, matrix)

def get_recommendations(title, df, cosine_sim, n=6):
    matches = df[df['Film'].str.lower() == title.strip().lower()]
    if matches.empty:
        return None
    idx = matches.index[0]
    scores = list(enumerate(cosine_sim[idx]))
    scores = sorted(scores, key=lambda x: x[1], reverse=True)[1:n+1]
    return df.iloc[[i[0] for i in scores]]

def score_bar_html(label, pct, dim=False):
    fill_class = "score-fill-dim" if dim else "score-fill-gold"
    return f"""
    <div class="score-wrap">
      <div class="score-label"><span>{label}</span><span>{pct}%</span></div>
      <div class="score-track"><div class="{fill_class}" style="width:{pct}%"></div></div>
    </div>"""

def movie_card_html(row):
    return f"""
    <div class="movie-card">
      <div class="card-title">{row['Film']}</div>
      <div class="card-meta">{row['Year']} &middot; {row['Studio'].split('/')[0]}</div>
      <span class="badge">{row['Genre']}</span>
      {score_bar_html('Audience', row['Audience'])}
      {score_bar_html('Critics', row['RT'], dim=True)}
    </div>"""


# ── Load ───────────────────────────────────────────────────────────────────────
df = load_data()
cosine_sim = build_similarity(df)
genres = sorted(df['Genre'].unique())

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown('<h1 class="hero-title">Cinema<span>Scout</span></h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">AI-powered movie discovery</p>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🎭  By Genre", "🔍  Similar Films", "✨  Ask AI"])

# ── Tab 1: Genre ───────────────────────────────────────────────────────────────
with tab1:
    st.markdown("<br>", unsafe_allow_html=True)
    selected_genre = st.selectbox(
        "Choose a genre",
        ["— Select —"] + genres,
        label_visibility="collapsed"
    )

    if selected_genre != "— Select —":
        results = df[df['Genre'] == selected_genre]
        st.markdown(f'<div class="results-label">{len(results)} films found</div>', unsafe_allow_html=True)
        cols = st.columns(3)
        for i, (_, row) in enumerate(results.iterrows()):
            with cols[i % 3]:
                st.markdown(movie_card_html(row), unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state">Select a genre above to browse films</div>', unsafe_allow_html=True)

# ── Tab 2: Similar ─────────────────────────────────────────────────────────────
with tab2:
    st.markdown("<br>", unsafe_allow_html=True)
    col_in, col_btn = st.columns([5, 1])
    with col_in:
        film_input = st.text_input(
            "Movie title",
            placeholder="e.g. Twilight, Superbad, Tangled...",
            label_visibility="collapsed"
        )
    with col_btn:
        search_clicked = st.button("Find", use_container_width=True)

    if search_clicked or film_input:
        if film_input:
            similar = get_recommendations(film_input, df, cosine_sim)
            if similar is None:
                st.markdown('<div class="empty-state">Movie not found. Try: Twilight, Superbad, Tangled...</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="results-label">6 films similar to "{film_input}"</div>', unsafe_allow_html=True)
                cols = st.columns(3)
                for i, (_, row) in enumerate(similar.iterrows()):
                    with cols[i % 3]:
                        st.markdown(movie_card_html(row), unsafe_allow_html=True)
    else:
        st.markdown('<div class="empty-state">Enter a movie title to find similar films</div>', unsafe_allow_html=True)

# ── Tab 3: Ask AI ──────────────────────────────────────────────────────────────
with tab3:
    st.markdown("<br>", unsafe_allow_html=True)
    col_q, col_ask = st.columns([5, 1])
    with col_q:
        ai_query = st.text_input(
            "Ask about movies",
            placeholder="e.g. Best comedies with high audience scores...",
            label_visibility="collapsed"
        )
    with col_ask:
        ask_clicked = st.button("Ask", use_container_width=True)

    if ask_clicked and ai_query:
        sample = df.head(20).apply(
            lambda r: f"{r['Film']} ({r['Genre']}, {r['Year']}, RT:{r['RT']}%, Audience:{r['Audience']}%, Profit:{r['Profit']:.1f}x, Gross:${r['Gross']}M)",
            axis=1
        ).tolist()
        dataset_text = "\n".join(sample)

        try:
            import anthropic
            client = anthropic.Anthropic()
            with st.spinner("Thinking..."):
                message = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=1024,
                    messages=[{
                        "role": "user",
                        "content": (
                            f"You are a helpful movie recommendation assistant.\n"
                            f"Dataset (sample of 20 films):\n{dataset_text}\n\n"
                            f"User: {ai_query}\n\n"
                            f"Answer helpfully and concisely in 3-5 sentences or a short list."
                        )
                    }]
                )
            response_text = message.content[0].text
            st.markdown(f'<div class="ai-box">{response_text}</div>', unsafe_allow_html=True)
        except ImportError:
            # Fallback: rule-based answers without API
            query_lower = ai_query.lower()
            if any(w in query_lower for w in ['best', 'top', 'highest']):
                if 'audience' in query_lower:
                    top = df.nlargest(5, 'Audience')[['Film', 'Audience', 'Genre']]
                    answer = "Top films by audience score:<br>" + "<br>".join(
                        f"• {r['Film']} ({r['Genre']}) — {r['Audience']}%" for _, r in top.iterrows()
                    )
                elif 'profit' in query_lower:
                    top = df.nlargest(5, 'Profit')[['Film', 'Profit', 'Genre']]
                    answer = "Most profitable films:<br>" + "<br>".join(
                        f"• {r['Film']} ({r['Genre']}) — {r['Profit']:.1f}x" for _, r in top.iterrows()
                    )
                elif 'critic' in query_lower or 'rotten' in query_lower:
                    top = df.nlargest(5, 'RT')[['Film', 'RT', 'Genre']]
                    answer = "Top films by critic score:<br>" + "<br>".join(
                        f"• {r['Film']} ({r['Genre']}) — {r['RT']}%" for _, r in top.iterrows()
                    )
                else:
                    top = df.nlargest(5, 'Audience')[['Film', 'Audience', 'Genre']]
                    answer = "Top films by audience score:<br>" + "<br>".join(
                        f"• {r['Film']} ({r['Genre']}) — {r['Audience']}%" for _, r in top.iterrows()
                    )
            elif any(g.lower() in query_lower for g in genres):
                matched_genre = next(g for g in genres if g.lower() in query_lower)
                top = df[df['Genre'] == matched_genre].nlargest(5, 'Audience')[['Film', 'Audience']]
                answer = f"Top {matched_genre} films:<br>" + "<br>".join(
                    f"• {r['Film']} — {r['Audience']}% audience" for _, r in top.iterrows()
                )
            else:
                answer = (
                    "Install the Anthropic library for AI-powered answers: "
                    "<code>pip install anthropic</code>. "
                    "Then set your API key: <code>ANTHROPIC_API_KEY=your_key</code>. "
                    "For now, try queries like 'best comedies' or 'top drama films'."
                )
            st.markdown(f'<div class="ai-box">{answer}</div>', unsafe_allow_html=True)
    elif not ask_clicked:
        st.markdown('<div class="empty-state">Ask anything about the movies in this dataset</div>', unsafe_allow_html=True)
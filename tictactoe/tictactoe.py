import streamlit as st
import time

st.set_page_config(page_title="Tic-Tac-Toe — Minimax AI", page_icon="❌", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Nunito:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp { background: #0f0e17; color: #fffffe; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem; padding-bottom: 2rem; max-width: 480px; }

h1 {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 3.2rem;
    letter-spacing: 0.12em;
    text-align: center;
    background: linear-gradient(90deg, #ff6b6b, #4ecdc4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.subtitle {
    text-align: center;
    color: #a7a9be;
    font-size: 0.72rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    margin-bottom: 1.2rem;
}

/* Scoreboard */
.scoreboard {
    display: flex;
    gap: 10px;
    justify-content: center;
    margin-bottom: 1rem;
}
.score-card {
    background: #1a1826;
    border: 1px solid #2d2b3d;
    border-radius: 14px;
    padding: 10px 22px;
    text-align: center;
    min-width: 100px;
    transition: border-color 0.3s, box-shadow 0.3s;
}
.score-card.win-x { border-color: #ff6b6b; box-shadow: 0 0 20px rgba(255,107,107,0.25); }
.score-card.win-o { border-color: #4ecdc4; box-shadow: 0 0 20px rgba(78,205,196,0.25); }
.score-label { font-size: 0.62rem; letter-spacing: 0.15em; text-transform: uppercase; color: #a7a9be; }
.score-val-x { font-size: 2rem; font-weight: 800; color: #ff6b6b; line-height: 1.1; }
.score-val-d { font-size: 1.3rem; font-weight: 800; color: #a7a9be; padding-top: 6px; line-height: 1.1; }
.score-val-o { font-size: 2rem; font-weight: 800; color: #4ecdc4; line-height: 1.1; }
.ai-badge {
    display: inline-block;
    background: rgba(78,205,196,0.1);
    border: 1px solid rgba(78,205,196,0.3);
    color: #4ecdc4;
    font-size: 0.55rem;
    padding: 2px 6px;
    border-radius: 8px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    margin-left: 4px;
    vertical-align: middle;
}

/* Status */
.status-bar {
    text-align: center;
    font-size: 0.9rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    color: #ffe66d;
    margin-bottom: 1rem;
    min-height: 24px;
}

/* Board cells */
.cell-btn {
    width: 100%;
    aspect-ratio: 1;
    background: #1a1826;
    border: 2px solid #2d2b3d;
    border-radius: 16px;
    font-family: 'Bebas Neue', sans-serif;
    font-size: 2.8rem;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
}
.cell-x { color: #ff6b6b; border-color: rgba(255,107,107,0.35); }
.cell-o { color: #4ecdc4; border-color: rgba(78,205,196,0.35); }
.cell-empty:hover { border-color: #ffe66d; background: #1f1d2e; }
.cell-win { background: rgba(255,230,109,0.1) !important; border-color: #ffe66d !important; }

/* Mode toggle */
.mode-wrap {
    display: flex;
    gap: 8px;
    justify-content: center;
    margin-bottom: 1rem;
}
.mode-card {
    background: #1a1826;
    border: 1px solid #2d2b3d;
    border-radius: 10px;
    padding: 7px 20px;
    font-size: 0.75rem;
    font-weight: 700;
    color: #a7a9be;
    cursor: pointer;
    letter-spacing: 0.05em;
}
.mode-card-active {
    background: #4ecdc4;
    border-color: #4ecdc4;
    color: #0f0e17;
}

/* Buttons */
.stButton > button {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    border-radius: 10px !important;
    border: none !important;
    transition: all 0.2s !important;
}
.stButton > button:hover { transform: translateY(-2px) !important; opacity: 0.9 !important; }

div[data-testid="column"] > div > div > div > .stButton > button {
    width: 100%;
    height: 90px;
    font-family: 'Bebas Neue', sans-serif !important;
    font-size: 2.8rem !important;
    background: #1a1826!important;
    border: 2px solid #2d2b3d !important;
    border-radius: 16px !important;
    color: #a7a9be !important;
    letter-spacing: 0.05em !important;
    transition: all 0.15s !important;
}
</style>
""", unsafe_allow_html=True)

# ── Session state init ─────────────────────────────────────────────────────────
def init_state():
    defaults = {
        'board': [''] * 9,
        'current': 'X',
        'game_over': False,
        'winner': None,
        'win_line': [],
        'scores': {'X': 0, 'O': 0, 'D': 0},
        'mode': 'ai',
        'status': 'Your turn — play X',
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ── Game logic ─────────────────────────────────────────────────────────────────
WIN_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def check_win(b):
    for line in WIN_LINES:
        a, c, d = line
        if b[a] and b[a] == b[c] == b[d]:
            return line
    return None

def minimax(b, player, alpha, beta):
    win = check_win(b)
    if win:
        prev = 'O' if player == 'X' else 'X'
        return {'score': 10 if prev == 'O' else -10}
    if all(b):
        return {'score': 0}

    best = {'score': -float('inf')} if player == 'O' else {'score': float('inf')}
    for i in range(9):
        if b[i]:
            continue
        b[i] = player
        result = minimax(b[:], 'X' if player == 'O' else 'O', alpha, beta)
        b[i] = ''
        result['index'] = i
        if player == 'O':
            if result['score'] > best['score']:
                best = result
            alpha = max(alpha, best['score'])
        else:
            if result['score'] < best['score']:
                best = result
            beta = min(beta, best['score'])
        if beta <= alpha:
            break
    return best

def ai_move():
    b = st.session_state.board[:]
    result = minimax(b, 'O', -float('inf'), float('inf'))
    if 'index' in result:
        do_move(result['index'], 'O')

def do_move(i, player):
    st.session_state.board[i] = player
    win = check_win(st.session_state.board)
    if win:
        st.session_state.game_over = True
        st.session_state.winner = player
        st.session_state.win_line = list(win)
        st.session_state.scores[player] += 1
        if st.session_state.mode == 'ai':
            st.session_state.status = '🎉 You won! Amazing!' if player == 'X' else '🤖 AI wins! Better luck next time.'
        else:
            st.session_state.status = f'🎉 Player {player} wins!'
    elif all(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.winner = None
        st.session_state.scores['D'] += 1
        st.session_state.status = "🤝 It's a draw!"
    else:
        st.session_state.current = 'O' if player == 'X' else 'X'
        nxt = st.session_state.current
        if st.session_state.mode == 'ai':
            st.session_state.status = 'Your turn — play X' if nxt == 'X' else 'AI is thinking... 🤖'
        else:
            st.session_state.status = f"Player {nxt}'s turn"

def reset_game():
    st.session_state.board = [''] * 9
    st.session_state.current = 'X'
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.win_line = []
    st.session_state.status = 'Your turn — play X' if st.session_state.mode == 'ai' else "Player X's turn"

def reset_all():
    st.session_state.scores = {'X': 0, 'O': 0, 'D': 0}
    reset_game()

# ── Render ─────────────────────────────────────────────────────────────────────
st.markdown('<h1>TIC·TAC·TOE</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Minimax AI — Try to Win</div>', unsafe_allow_html=True)

# Mode toggle
col_a, col_b, col_c = st.columns([1, 1, 1])
with col_b:
    mode_options = ['🤖 vs AI', '👥 2 Players']
    chosen = st.radio("Mode", mode_options, index=0 if st.session_state.mode == 'ai' else 1,
                      horizontal=True, label_visibility="collapsed")
    new_mode = 'ai' if '🤖' in chosen else 'pvp'
    if new_mode != st.session_state.mode:
        st.session_state.mode = new_mode
        reset_game()
        st.rerun()

# Scoreboard
s = st.session_state.scores
win_x = 'win-x' if st.session_state.winner == 'X' else ''
win_o = 'win-o' if st.session_state.winner == 'O' else ''
o_label = 'AI (O)<span class="ai-badge">Minimax</span>' if st.session_state.mode == 'ai' else 'Player (O)'
st.markdown(f"""
<div class="scoreboard">
  <div class="score-card {win_x}">
    <div class="score-label">You (X)</div>
    <div class="score-val-x">{s['X']}</div>
  </div>
  <div class="score-card">
    <div class="score-label">Draws</div>
    <div class="score-val-d">{s['D']}</div>
  </div>
  <div class="score-card {win_o}">
    <div class="score-label">{o_label}</div>
    <div class="score-val-o">{s['O']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Status
st.markdown(f'<div class="status-bar">{st.session_state.status}</div>', unsafe_allow_html=True)

# Board
board = st.session_state.board
win_line = st.session_state.win_line

SYMBOLS = {'X': '✕', 'O': '○', '': ''}
COLORS  = {'X': '#ff6b6b', 'O': '#4ecdc4', '': '#a7a9be'}

rows = [st.columns(3) for _ in range(3)]
for idx in range(9):
    r, c = divmod(idx, 3)
    with rows[r][c]:
        val = board[idx]
        is_win = idx in win_line
        label = SYMBOLS.get(val, val) or ' '

        border = '2px solid #ffe66d' if is_win else ('2px solid rgba(255,107,107,0.35)' if val == 'X' else ('2px solid rgba(78,205,196,0.35)' if val == 'O' else '2px solid #2d2b3d'))
        bg = 'rgba(255,230,109,0.08)' if is_win else '#1a1826'
        color = COLORS.get(val, '#a7a9be')

        st.markdown(f"""
        <div style="
            width:100%; height:90px;
            background:{bg};
            border:{border};
            border-radius:16px;
            display:flex; align-items:center; justify-content:center;
            font-family:'Bebas Neue',sans-serif;
            font-size:2.8rem;
            color:{color};
            margin-bottom:8px;
            cursor:{'default' if val or st.session_state.game_over else 'pointer'};
        ">{label if val else ''}</div>
        """, unsafe_allow_html=True)

        if not val and not st.session_state.game_over:
            if st.button('', key=f'cell_{idx}', use_container_width=True):
                if st.session_state.mode == 'ai' and st.session_state.current == 'O':
                    pass
                else:
                    do_move(idx, st.session_state.current)
                    if (st.session_state.mode == 'ai' and
                            not st.session_state.game_over and
                            st.session_state.current == 'O'):
                        time.sleep(0.35)
                        ai_move()
                    st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# Controls
c1, c2, c3 = st.columns([1, 1, 1])
with c1:
    st.markdown("")
with c2:
    if st.button("🔄  New Game", use_container_width=True):
        reset_game()
        st.rerun()
with c3:
    if st.button("🗑  Reset Score", use_container_width=True):
        reset_all()
        st.rerun()
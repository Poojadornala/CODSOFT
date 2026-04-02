import streamlit as st
import random
import re
from datetime import datetime

st.set_page_config(page_title="ARIA — Rule-Based Chatbot", page_icon="👾", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@300;400;500&family=Syne:wght@400;600;800&display=swap');

html, body, [class*="css"] { font-family: 'DM Mono', monospace; }
.stApp { background: #0a0a0f; color: #e2e8f0; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 1rem; max-width: 720px; }

.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(124,58,237,0.04) 1px, transparent 1px),
        linear-gradient(90deg, rgba(124,58,237,0.04) 1px, transparent 1px);
    background-size: 40px 40px;
    pointer-events: none;
    z-index: 0;
}

.aria-header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 4px 16px;
    border-bottom: 1px solid #1e1e2e;
    margin-bottom: 1rem;
}
.logo-orb {
    width: 36px; height: 36px;
    border-radius: 50%;
    background: conic-gradient(from 0deg, #7c3aed, #06b6d4, #7c3aed);
    animation: spin 6s linear infinite;
    flex-shrink: 0;
    box-shadow: 0 0 18px rgba(124,58,237,0.3);
}
@keyframes spin { to { transform: rotate(360deg); } }
.header-title { font-family: 'Syne', sans-serif; font-size: 1.2rem; font-weight: 800; letter-spacing: 0.08em; color: #e2e8f0; }
.header-sub { font-size: 0.58rem; color: #64748b; letter-spacing: 0.15em; text-transform: uppercase; }
.status-pill {
    margin-left: auto;
    background: rgba(6,182,212,0.1);
    border: 1px solid rgba(6,182,212,0.3);
    color: #06b6d4;
    font-size: 0.58rem;
    padding: 4px 10px;
    border-radius: 20px;
    letter-spacing: 0.1em;
    display: flex; align-items: center; gap: 5px;
    white-space: nowrap;
}
.status-dot {
    width: 5px; height: 5px; border-radius: 50%;
    background: #06b6d4;
    animation: blink 1.5s ease infinite;
    display: inline-block;
    flex-shrink: 0;
}
@keyframes blink { 0%,100% { opacity:1; } 50% { opacity:0.2; } }

.msg-row { display: flex; gap: 10px; align-items: flex-end; margin-bottom: 12px; }
.msg-row.user { flex-direction: row-reverse; }
.avatar {
    width: 28px; height: 28px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.6rem; font-weight: 600; font-family: 'DM Mono', monospace;
}
.avatar.bot { background: linear-gradient(135deg, #7c3aed, #06b6d4); color: #fff; }
.avatar.user { background: linear-gradient(135deg, #1e1b4b, #312e81); color: #a5b4fc; border: 1px solid #4338ca; }
.bubble {
    max-width: 74%;
    padding: 10px 14px;
    border-radius: 16px;
    font-size: 0.8rem;
    line-height: 1.65;
    font-family: 'DM Mono', monospace;
}
.bubble.bot {
    background: #0f172a;
    border: 1px solid #1e1e2e;
    border-bottom-left-radius: 4px;
    color: #e2e8f0;
}
.bubble.user {
    background: #1e1b4b;
    border: 1px solid rgba(124,58,237,0.3);
    border-bottom-right-radius: 4px;
    color: #c7d2fe;
    text-align: right;
}
.bubble-time { font-size: 0.5rem; color: #64748b; margin-top: 3px; font-family: 'DM Mono', monospace; }

.divider { border: none; border-top: 1px solid #1e1e2e; margin: 0.75rem 0; }

.stTextInput input {
    background: #111118 !important;
    border: 1px solid #1e1e2e !important;
    border-radius: 12px !important;
    color: #e2e8f0 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    caret-color: #7c3aed !important;
}
.stTextInput input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.15) !important;
}
.stTextInput input::placeholder { color: #374151 !important; }

.stButton > button {
    background: linear-gradient(135deg, #7c3aed, #4f46e5) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.04em !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
    box-shadow: 0 0 16px rgba(124,58,237,0.4) !important;
}

div[data-testid="column"] .stButton > button {
    background: transparent !important;
    border: 1px solid #1e1e2e !important;
    color: #64748b !important;
    font-size: 0.6rem !important;
    padding: 4px 8px !important;
    border-radius: 20px !important;
    width: 100%;
}
div[data-testid="column"] .stButton > button:hover {
    border-color: #7c3aed !important;
    color: #a78bfa !important;
    background: rgba(124,58,237,0.08) !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)


# ── Rule engine ────────────────────────────────────────────────────────────────
RULES = [
    (r'^(hi|hello|hey|howdy|sup|greetings)', [
        "Hey there! I'm ARIA 👾 How can I assist?",
        "Hello, human! Ready to chat?",
        "Hi! Great to see you. What's on your mind?"
    ]),
    (r'how are you|how do you do|you doing', [
        "Running at 100% — no bugs today! 🚀",
        "Feeling electric! Thanks for asking.",
        "Optimal. My circuits are humming nicely."
    ]),
    (r"what.?s? your name|who are you", [
        "I'm ARIA — Adaptive Rule Intelligence Agent. Built to chat!",
        "Call me ARIA. I live here and respond to your queries."
    ]),
    (r'what can you do|capabilities|features|help', [
        "I can:\n• Answer greetings\n• Tell jokes 😄\n• Share the time & date\n• Chat about weather\n• Do basic math\n\nAsk me anything!"
    ]),
    (r'joke|funny|laugh|humor', [
        "Why do programmers prefer dark mode? Because light attracts bugs! 🐛",
        "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads. 🍫",
        "Why did the AI go to therapy? Too many unresolved issues. 🤖"
    ]),
    (r'time|clock|what time', ['__TIME__']),
    (r'date|today|what day', ['__DATE__']),
    (r'weather|temperature|forecast|rain|sunny', [
        "I can't fetch live weather, but I hope it's sunny wherever you are! ☀️",
        "No weather API here, but statistically it's probably fine outside! 🌤"
    ]),
    (r'meaning of life|42', ["42. Obviously. Douglas Adams had it right. 📖"]),
    (r'(\d+)\s*([\+\-\*\/])\s*(\d+)', ['__MATH__']),
    (r'bye|goodbye|see ya|cya|later|farewell', [
        "Goodbye! Come back anytime 👋",
        "Later! Stay curious 🚀",
        "Farewell, human. My circuits will miss you."
    ]),
    (r'thank|thanks|thx', [
        "You're very welcome! 😊",
        "Anytime! That's what I'm here for.",
        "Happy to help! ✨"
    ]),
    (r'who (made|created|built) you|your creator', [
        "I was built as a rule-based chatbot demo — pattern matching in action!"
    ]),
]

FALLBACKS = [
    "Interesting! I'm not sure I have a rule for that yet. 🤔",
    "My pattern engine didn't catch that. Try rephrasing?",
    "Hmm, that's outside my rulebook. Ask me something else!",
    "Error 404: Response not found. Try: jokes, time, or greetings!",
]

def get_reply(text):
    for pattern, replies in RULES:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            reply = random.choice(replies)
            if reply == '__TIME__':
                return f"The current time is ⏰ {datetime.now().strftime('%I:%M %p')}"
            if reply == '__DATE__':
                return f"Today is 📅 {datetime.now().strftime('%A, %B %d, %Y')}"
            if reply == '__MATH__':
                try:
                    a, op, b = int(m.group(1)), m.group(2), int(m.group(3))
                    result = {'+': a+b, '-': a-b, '*': a*b, '/': round(a/b, 2) if b != 0 else '∞'}[op]
                    return f"That equals: {result} 🧮"
                except:
                    return "Hmm, I couldn't compute that safely."
            return reply
    return random.choice(FALLBACKS)

def ts():
    return datetime.now().strftime('%I:%M %p')


# ── Session state ──────────────────────────────────────────────────────────────
if 'messages' not in st.session_state:
    st.session_state.messages = [{
        'role': 'bot',
        'text': "Hello! I'm ARIA 👾 — a rule-based AI assistant. Try asking me about the time, a joke, or just say hello!",
        'time': ts()
    }]
if 'sug_input' not in st.session_state:
    st.session_state.sug_input = ''


# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="aria-header">
  <div class="logo-orb"></div>
  <div>
    <div class="header-title">ARIA</div>
    <div class="header-sub">Adaptive Rule Intelligence Agent</div>
  </div>
  <div class="status-pill"><div class="status-dot"></div>ONLINE</div>
</div>
""", unsafe_allow_html=True)


# ── Messages ───────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    role = msg['role']
    initials = 'AI' if role == 'bot' else 'ME'
    t_align = 'left' if role == 'bot' else 'right'
    st.markdown(f"""
    <div class="msg-row {role}">
      <div class="avatar {role}">{initials}</div>
      <div>
        <div class="bubble {role}">{msg['text'].replace(chr(10), '<br>')}</div>
        <div class="bubble-time" style="text-align:{t_align}">{msg['time']}</div>
      </div>
    </div>""", unsafe_allow_html=True)

st.markdown('<hr class="divider">', unsafe_allow_html=True)


# ── Suggestion chips ───────────────────────────────────────────────────────────
SUGGESTIONS = ["👋 Hello", "❓ What can you do?", "🕐 Time?", "😂 Joke", "🌤 Weather", "👋 Bye"]
sug_cols = st.columns(len(SUGGESTIONS))
for i, sug in enumerate(SUGGESTIONS):
    with sug_cols[i]:
        if st.button(sug, key=f's{i}'):
            clean = re.sub(r'^[^\w]+', '', sug).strip()
            st.session_state.sug_input = clean
            st.rerun()


# ── Input row ──────────────────────────────────────────────────────────────────
in_col, btn_col = st.columns([5, 1])
with in_col:
    user_text = st.text_input(
        "msg",
        value=st.session_state.sug_input,
        placeholder="Type a message...",
        label_visibility="collapsed",
        key="user_input"
    )
with btn_col:
    send_clicked = st.button("Send ➤", use_container_width=True, key="send_main")


# ── Process ────────────────────────────────────────────────────────────────────
msg_to_send = user_text.strip() if send_clicked else st.session_state.sug_input.strip()

if msg_to_send and (send_clicked or st.session_state.sug_input):
    st.session_state.messages.append({'role': 'user', 'text': msg_to_send, 'time': ts()})
    st.session_state.messages.append({'role': 'bot', 'text': get_reply(msg_to_send), 'time': ts()})
    st.session_state.sug_input = ''
    st.rerun()
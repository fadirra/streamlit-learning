import streamlit as st
from google import genai

st.set_page_config(page_title="Simple Gemini Chatbot", page_icon="💬")
st.title("💬 Simple Chatbot — google-genai")

# --- Sidebar ---
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")
system_prompt = st.sidebar.text_area(
    "🧠 System prompt",
    "You are a helpful chatbot. Jawab ringkas dan sopan dalam bahasa Indonesia.",
    height=100,
)
temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3, 0.1)
reset = st.sidebar.button("♻️ Reset chat")

if not api_key:
    st.warning("Masukkan Gemini API key di sidebar terlebih dahulu.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- State ---
if reset or "messages" not in st.session_state:
    st.session_state.messages = []

# --- Tampilkan riwayat ---
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# --- Input user ---
user_input = st.chat_input("Tulis pesan kamu di sini...")
if user_input:
    # simpan & tampilkan pesan user
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # build contents: list of Content {role, parts:[Part]}
    contents = [
        {"role": m["role"], "parts": [{"text": m["content"]}]}
        for m in st.session_state.messages
    ]

    try:
        resp = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=contents,
            config={
                "temperature": float(temperature),
                "system_instruction": system_prompt,
            },
        )
        answer = resp.output_text
    except Exception as e:
        answer = f"⚠️ Terjadi error: {e}"

    st.chat_message("assistant").markdown(answer)
    # role balasan AI = "model"
    st.session_state.messages.append({"role": "model", "content": answer})

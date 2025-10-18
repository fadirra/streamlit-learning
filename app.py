import streamlit as st
from google import genai

# --- Page setup ---
st.set_page_config(page_title="Simple Gemini Chatbot", page_icon="💬")
st.title("💬 Simple Chatbot — Gemini API (google-genai)")

# --- Sidebar setup ---
api_key = st.sidebar.text_input("🔑 Gemini API Key", type="password")

if not api_key:
    st.warning("Masukkan Gemini API key di sidebar terlebih dahulu.")
    st.stop()

client = genai.Client(api_key=api_key)

system_prompt = st.sidebar.text_area(
    "🧠 System prompt",
    "You are a helpful chatbot. Jawab ringkas dan sopan dalam bahasa Indonesia.",
    height=100,
)

# --- Chat history ---
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display chat history ---
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# --- User input ---
user_input = st.chat_input("Tulis pesan kamu di sini...")

if user_input:
    # tampilkan pesan user
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    try:
        # buat context dari chat sebelumnya
        context = [
            {"role": "system", "content": system_prompt},
        ] + [
            {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
        ]

        # kirim ke Gemini
        response = client.models.generate_content(
            model="gemini-1.5-flash",
            contents=context,
        )
        answer = response.output_text
    except Exception as e:
        answer = f"⚠️ Terjadi error: {e}"

    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "assistant", "content": answer})

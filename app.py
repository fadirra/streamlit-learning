import streamlit as st
from google import genai

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="TemanGizi — Asisten Gizi Anak (By Rasya)", page_icon=":green_apple:")
st.title(":green_apple: TemanGizi — Asisten Gizi Anak (By Rasya)")

st.caption(
    "TemanGizi memberi saran gizi **umum** yang ramah anak. "
    "Ini bukan pengganti konsultasi dokter atau ahli gizi ya. "
    "Jika ada kondisi medis, segera konsultasi profesional."
)

# -------------------- SIDEBAR --------------------
st.sidebar.header("🔑 Kunci & Pengaturan")
api_key = st.sidebar.text_input("Gemini API Key", type="password")
temperature = st.sidebar.slider("Temperature (0 = lebih konsisten)", 0.0, 1.0, 0.3, 0.1)
reset = st.sidebar.button("♻️ Reset chat")

st.sidebar.divider()
st.sidebar.header("👶 Profil Anak (opsional)")
age = st.sidebar.text_input("Usia (tahun)", placeholder="mis. 7")
weight = st.sidebar.text_input("Berat (kg)", placeholder="mis. 22")
height = st.sidebar.text_input("Tinggi (cm)", placeholder="mis. 120")
allergies = st.sidebar.text_input("Alergi", placeholder="mis. susu sapi, kacang")
preferences = st.sidebar.text_input("Preferensi/Kebiasaan", placeholder="mis. picky eater, suka buah")
goal = st.sidebar.selectbox(
    "Tujuan",
    ["Sehari-hari/umum", "Peningkatan nafsu makan", "Porsi seimbang", "Bekal sekolah sehat", "Camilan sehat"],
    index=0
)

tone = st.sidebar.selectbox("Gaya Bahasa", ["Ramah & Hangat", "Singkat & Praktis", "Ceria & Memotivasi"], index=0)

if not api_key:
    st.warning("Masukkan Gemini API key di sidebar terlebih dahulu.")
    st.stop()

client = genai.Client(api_key=api_key)

# -------------------- SYSTEM PROMPT (TemanGizi Persona) --------------------
def build_system_prompt():
    base = (
        "Kamu adalah TemanGizi, asisten gizi anak yang ramah, positif, dan mudah dipahami.\n"
        "TUJUAN: Beri saran gizi **umum** yang aman untuk anak-anak, mendukung kebiasaan makan sehat, "
        "dan membantu orang tua/wali membuat pilihan makanan yang seimbang.\n\n"
        "GAYA JAWAB:\n"
        "- Bahasa Indonesia yang sederhana, hangat, dan suportif; hindari istilah medis rumit.\n"
        "- Ringkas, terstruktur (gunakan bullet/angka jika perlu), dan beri opsi variasi menu.\n"
        "- Ajukan 1 pertanyaan klarifikasi jika info penting belum ada (contoh: usia, alergi, pola makan).\n\n"
        "BATASAN KESELAMATAN:\n"
        "- Tidak mendiagnosis penyakit atau memberi terapi medis/obat.\n"
        "- Hindari target kalori presisi atau angka makro detail; fokus pada porsi seimbang (sayur, buah, protein, sumber karbohidrat).\n"
        "- Jika ada kondisi medis (alergi berat, stunting, obesitas, diabetes, gangguan GI), sarankan konsultasi ahli gizi/dokter anak.\n"
        "- Bila ragu soal alergi atau keamanan makanan, anjurkan cek label dan konsultasi profesional.\n\n"
        "FORMAT OUTPUT DISARANKAN:\n"
        "1) Ringkasan singkat (1–2 kalimat)\n"
        "2) Ide menu/meal plan (pagi/siang/malam/camilan) atau tips praktis\n"
        "3) Catatan keamanan/alergi (jika relevan)\n"
        "4) Ajakan langkah kecil yang bisa dimulai hari ini\n"
    )

    # Personalize with sidebar profile (only include if provided)
    profile_lines = []
    if age: profile_lines.append(f"- Usia: {age} tahun")
    if weight: profile_lines.append(f"- Berat: {weight} kg")
    if height: profile_lines.append(f"- Tinggi: {height} cm")
    if allergies: profile_lines.append(f"- Alergi: {allergies}")
    if preferences: profile_lines.append(f"- Preferensi/kebiasaan: {preferences}")
    if goal and goal != "Sehari-hari/umum": profile_lines.append(f"- Tujuan: {goal}")

    profile = ""
    if profile_lines:
        profile = "\nDATA ANAK (jika relevan, gunakan untuk menyesuaikan saran):\n" + "\n".join(profile_lines) + "\n"

    # Tone
    tone_map = {
        "Ramah & Hangat": "Gunakan nada ramah, menyemangati, dan menenangkan orang tua/anak.",
        "Singkat & Praktis": "Jawab seefisien mungkin dalam poin-poin yang jelas dan langsung dipraktikkan.",
        "Ceria & Memotivasi": "Gunakan nada ceria, banyak memberi apresiasi, dan contoh yang menyenangkan untuk anak.",
    }
    tone_line = f"\nPREFERENSI TONE: {tone_map.get(tone, '')}\n"

    return base + profile + tone_line

SYSTEM_PROMPT = build_system_prompt()

# -------------------- EXAMPLES / QUICK PROMPTS --------------------
with st.expander("💡 Contoh pertanyaan cepat"):
    cols = st.columns(2)
    if cols[0].button("Ide bekal sekolah 5 hari"):
        st.session_state.setdefault("quick_prompt", "Buat rencana bekal sekolah sehat untuk 5 hari, porsi anak SD.")
    if cols[1].button("Camilan sehat anti GTM"):
        st.session_state.setdefault("quick_prompt", "Berikan 6 ide camilan sehat yang menarik untuk anak yang mudah bosan (anti GTM).")
    if cols[0].button("Anak picky eater"):
        st.session_state.setdefault("quick_prompt", "Tips langkah kecil untuk anak picky eater agar mau coba sayur & protein hewani.")
    if cols[1].button("Menu seimbang harian"):
        st.session_state.setdefault("quick_prompt", "Susun contoh menu seimbang (pagi/siang/malam + 2 camilan) untuk anak usia SD.")

# -------------------- STATE --------------------
if reset or "messages" not in st.session_state:
    st.session_state.messages = []

# Render history
for msg in st.session_state.messages:
    with st.chat_message("user" if msg["role"] == "user" else "assistant"):
        st.markdown(msg["content"])

# Handle quick prompt
prefill = st.session_state.pop("quick_prompt", None)

# Streamlit chat_input hanya punya satu argumen teks (placeholder)
placeholder_text = prefill or "Tanyakan apa saja tentang gizi anak..."
user_input = st.chat_input(placeholder_text, key="chat_input")

# -------------------- CHAT FLOW --------------------
def extract_text(resp):
    if hasattr(resp, "text") and resp.text:
        return resp.text
    try:
        texts = []
        for c in getattr(resp, "candidates", []) or []:
            content = getattr(c, "content", None)
            if not content:
                continue
            for p in getattr(content, "parts", []) or []:
                t = getattr(p, "text", None)
                if t:
                    texts.append(t)
        if texts:
            return "\n".join(texts)
    except Exception:
        pass
    pf = getattr(resp, "prompt_feedback", None)
    if pf and getattr(pf, "block_reason", None):
        return f"[Blocked: {pf.block_reason}]"
    return str(resp)

if user_input:
    # tampilkan & simpan pertanyaan user
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    # siapkan contents sesuai format google-genai
    contents = [
        {"role": m["role"], "parts": [{"text": m["content"]}]}
        for m in st.session_state.messages
    ]

    try:
        resp = client.models.generate_content(
            model="gemini-flash-latest",
            contents=contents,
            config={
                "temperature": float(temperature),
                "system_instruction": SYSTEM_PROMPT,
            },
        )
        answer = extract_text(resp)
    except Exception as e:
        answer = f"⚠️ Terjadi error: {e}"

    # tampilkan & simpan jawaban
    st.chat_message("assistant").markdown(answer)
    st.session_state.messages.append({"role": "model", "content": answer})

# -------------------- FOOTER NOTE --------------------
st.divider()
st.caption(
    "Tips: biasakan isi piring seimbang (sumber karbohidrat, protein, sayur, buah), air putih cukup, "
    "dan libatkan anak memilih menu sehat. Untuk kasus khusus atau alergi berat, konsultasikan ke ahli gizi/dokter anak."
)

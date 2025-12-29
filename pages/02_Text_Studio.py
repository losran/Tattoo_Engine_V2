import streamlit as st
import sys, os, random, time

# ===========================
# 基础环境
# ===========================
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
if parent_dir not in sys.path:
    sys.path.append(parent_dir)

from engine_manager import init_data, render_sidebar, fetch_image_refs_auto
from style_manager import apply_pro_style

st.set_page_config(layout="wide", page_title="Text Studio")
apply_pro_style()
render_sidebar()
init_data()

# ===========================
# Session State
# ===========================
if "selected_assets" not in st.session_state:
    st.session_state.selected_assets = set()

if "text_solutions" not in st.session_state:
    st.session_state.text_solutions = []

# ===========================
# CSS：真正可用的响应式 Grid
# ===========================
st.markdown("""
<style>
.textstudio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
    gap: 14px;
}
.textstudio-card {
    background: #0a0a0a;
    border: 1px solid #222;
}
.textstudio-card:hover {
    border-color: #555;
}
.textstudio-card img {
    width: 100%;
    display: block;
}
.card-actions {
    display: flex;
    border-top: 1px solid #222;
}
.card-actions button {
    flex: 1;
    height: 36px;
    border-radius: 0 !important;
    border: none !important;
}
button[kind="primary"] {
    background-color: #1b3a1b !important;
    color: #4CAF50 !important;
    font-weight: 700;
}
button[kind="secondary"] {
    background-color: #111 !important;
    color: #888 !important;
}
button[kind="secondary"]:hover {
    background-color: #222 !important;
    color: #ddd !important;
}
button[title="View fullscreen"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

# ===========================
# Header
# ===========================
st.markdown("## ✏️ Text Studio")
st.caption("垫图 + 改字，用于纹身贴 / 字体图 / 文案图")

# ===========================
# Visual Library（纯选图）
# ===========================
raw_map = fetch_image_refs_auto()
files = [v for v in raw_map.values() if v and os.path.exists(os.path.join("images", v))]
files.sort(key=lambda f: os.path.getmtime(os.path.join("images", f)), reverse=True)

if not files:
    st.info("Visual Library is empty.")
else:
    st.markdown('<div class="textstudio-grid">', unsafe_allow_html=True)
    for f in files:
        path = os.path.join("images", f)
        active = f in st.session_state.selected_assets

        st.markdown('<div class="textstudio-card">', unsafe_allow_html=True)
        st.image(path, use_container_width=True)

        c1, c2 = st.columns([3,1], gap="small")
        with c1:
            if active:
                if st.button("✅ Active", key=f"s_{f}", type="primary"):
                    st.session_state.selected_assets.remove(f)
                    st.rerun()
            else:
                if st.button("Select", key=f"s_{f}", type="secondary"):
                    st.session_state.selected_assets.add(f)
                    st.rerun()
        with c2:
            if st.button("🗑", key=f"d_{f}", type="secondary"):
                os.remove(path)
                st.session_state.selected_assets.discard(f)
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ===========================
# Generate Controls
# ===========================
st.divider()

db = st.session_state.get("db_all", {})
font_list = db.get("Font_Style", []) or ["Handwritten", "Gothic"]
lang_keys = [k for k in db.keys() if k.startswith("Text_")] or ["Text_English"]

c1, c2, c3 = st.columns([1,1,1])
with c1:
    lang = st.selectbox("Language", lang_keys)
with c2:
    font = st.selectbox("Font", ["Random"] + font_list)
with c3:
    qty = st.number_input("Qty", 1, 10, 4)

manual_text = st.text_input("Custom Text (Optional)", placeholder="留空则随机")

# ===========================
# Generate Logic
# ===========================
if st.button("🚀 GENERATE", type="primary", use_container_width=True):
    with st.spinner("Generating..."):
        results = []
        text_pool = db.get(lang, []) or ["LOVE", "HOPE"]
        imgs = list(st.session_state.selected_assets)

        for _ in range(qty):
            word = manual_text.strip() if manual_text.strip() else random.choice(text_pool)
            img = random.choice(imgs) if imgs else ""
            fnt = font if font != "Random" else random.choice(font_list)

            prompt = f"{img} Tattoo design of the word '{word}', {fnt} typography, clean white background, high contrast --iw 2"
            results.append({"image": img, "prompt": prompt})

        st.session_state.text_solutions = results
        time.sleep(0.2)
        st.rerun()

# ===========================
# Results
# ===========================
if st.session_state.text_solutions:
    st.divider()
    st.subheader("Results")

    for r in st.session_state.text_solutions:
        with st.container(border=True):
            cimg, ctxt = st.columns([1,4])
            with cimg:
                if r["image"]:
                    st.image(os.path.join("images", r["image"]), use_container_width=True)
            with ctxt:
                st.markdown(f"**Prompt:** {r['prompt']}")

    if st.button("Import to Automation", type="primary", use_container_width=True):
        st.session_state.setdefault("global_queue", [])
        st.session_state.global_queue += [r["prompt"] for r in st.session_state.text_solutions]
        st.switch_page("pages/03_Automation.py")

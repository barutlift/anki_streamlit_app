# st_words_cleaned.py
# Streamlit uygulaması, CSV’deki English_Word ve Examples sütununa göre çalışacak
# - Ön yüzde sadece kelime gözükür
# - Üzerine tıklandığında Examples madde olarak gösterilir

import streamlit as st
import pandas as pd
import random
import os

st.set_page_config(page_title="Kelime Oyunu", layout="centered")

CSV_FILE = 'english_words_seen.csv'
if not os.path.exists(CSV_FILE):
    st.error(f"CSV bulunamadı: {CSV_FILE}")
    st.stop()

try:
    df = pd.read_csv(CSV_FILE)
    df = df.dropna(subset=['English_Word'])
    df['English_Word'] = df['English_Word'].astype(str).str.strip()
    df['Examples'] = df['Examples'].astype(str).str.strip()
except Exception as e:
    st.error(f"CSV hatası: {e}")
    st.stop()

words_data = df.to_dict('records')
words_list = [w['English_Word'] for w in words_data]

if len(words_list) < 5:
    st.error("En az 5 kelime olmalı!")
    st.stop()

# Session state
if 'selected_words' not in st.session_state:
    st.session_state.selected_words = random.sample(words_list, 5)
if 'show_examples' not in st.session_state:
    st.session_state.show_examples = {}

# CSS
st.markdown("""
<style>
.title { font-size: 38px; font-weight: bold; text-align: center; margin: 30px 0; color: #1E3A8A; }
.subtitle { text-align: center; font-size: 20px; margin-bottom: 30px; color: #eee; }
.word-container { display: flex; justify-content: center; gap: 15px; flex-wrap: wrap; margin: 30px 0; }
.word-button { background-color: #FFD60A; color: black; padding: 14px 24px; font-size: 20px; font-weight: bold; border-radius: 50px; border: 3px solid #333; min-width: 160px; text-align: center; box-shadow: 0 4px 8px rgba(0,0,0,0.3); cursor: pointer; }
.word-button:hover { background-color: #FFC300; transform: translateY(-2px); }
.example-box { background-color: #333; color: #fff; padding: 10px 16px; border-radius: 10px; margin-top: 5px; white-space: pre-line; }
</style>
""", unsafe_allow_html=True)

# Başlık
st.markdown("<div class='title'>Kelime Kısıtlamalı Tartışma</div>", unsafe_allow_html=True)

# Random 5 kelime butonu
if st.button("Random 5 Kelime", use_container_width=True):
    st.session_state.selected_words = random.sample(words_list, 5)
    st.session_state.show_examples = {}
    st.rerun()

# Kelimeleri göster
st.markdown("<div class='subtitle'>Bu kelimeleri kullanarak tartış!</div>", unsafe_allow_html=True)
st.markdown("<div class='word-container'>", unsafe_allow_html=True)
for word_record in words_data:
    word = word_record['English_Word']
    if word in st.session_state.selected_words:
        clicked = st.button(word, key=word)
        if clicked:
            st.session_state.show_examples[word] = not st.session_state.show_examples.get(word, False)
st.markdown("</div>", unsafe_allow_html=True)

# Tıklanan kelimelerin örnekleri
for word_record in words_data:
    word = word_record['English_Word']
    if st.session_state.show_examples.get(word, False):
        examples_text = word_record['Examples']
        st.markdown(f"<div class='example-box'>{examples_text}</div>", unsafe_allow_html=True)

# İstatistik
st.caption(f"Toplam kelime: {len(words_list):,} | Kullanılan: 5")

# ----------------------------
# 1️⃣ Anki Export Script
# ----------------------------
# anki_export_clean.py
# - Sadece English_Word ve Examples_EN_HTML
# - HTML temizlenip madde listesi olarak kaydedilecek

import requests
import csv
import json
import re

ANKI_CONNECT_URL = "http://127.0.0.1:8765"
API_VERSION = 6
SEARCH_QUERY = 'prop:reps>0'

# HTML temizleyip madde listesi

def clean_html_to_bullets(raw_html: str) -> str:
    if not raw_html:
        return ""
    matches = re.findall(r'<div>(.*?)</div>', raw_html, re.DOTALL)
    lines = [m.strip() for m in matches if m.strip()]
    return '\n- '.join(['- ' + line for line in lines]) if lines else ''

# Anki Connect request helper

def anki_request(action: str, params=None):
    payload = {"action": action, "version": API_VERSION}
    if params:
        payload["params"] = params
    resp = requests.post(ANKI_CONNECT_URL, json=payload)
    resp.raise_for_status()
    data = resp.json()
    if data.get("error"):
        raise RuntimeError(f"AnkiConnect error: {data['error']}")
    return data.get("result")

# Kartları bul

def find_card_ids(query: str):
    return anki_request("findCards", {"query": query}) or []

def get_cards_info(card_ids):
    if not card_ids:
        return []
    return anki_request("cardsInfo", {"cards": card_ids}) or []

def get_notes_info(note_ids):
    if not note_ids:
        return []
    return anki_request("notesInfo", {"notes": note_ids}) or []

# Alanları çek

def extract_words_and_examples(notes_info):
    data = []
    seen_words = set()
    for note in notes_info:
        fields = note.get("fields", {})
        word = fields.get("English_Word", {}).get("value", "").strip()
        examples_html = fields.get("Examples_EN_HTML", {}).get("value", "")
        examples_bullets = clean_html_to_bullets(examples_html)
        if word and word not in seen_words:
            seen_words.add(word)
            data.append({"English_Word": word, "Examples": examples_bullets})
    return data

# Kaydet

def save_csv(data, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["English_Word", "Examples"])
        for item in data:
            writer.writerow([item['English_Word'], item['Examples']])

# MAIN

if __name__ == "__main__":
    card_ids = find_card_ids(SEARCH_QUERY)
    cards_info = get_cards_info(card_ids)

    seen_note_ids = [c.get('note') or c.get('noteId') for c in cards_info if c.get('reps',0) > 0]
    seen_note_ids = list(dict.fromkeys(seen_note_ids))

    notes_info = get_notes_info(seen_note_ids)
    data = extract_words_and_examples(notes_info)

    save_csv(data, 'english_words_seen.csv')
    print(f"CSV kaydedildi: {len(data)} kelime")


# ----------------------------
# 2️⃣ Streamlit Uygulaması
# ----------------------------
# st_words.py
# - CSV’deki kelimeyi gösterir
# - Üzerine tıklandığında Examples madde olarak gösterir

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

# Session state
if 'selected_words' not in st.session_state:
    st.session_state.selected_words = random.sample(words_list, 5)
if 'show_examples' not in st.session_state:
    st.session_state.show_examples = {}

# Random butonu
if st.button("Random 5 Kelime", use_container_width=True):
    st.session_state.selected_words = random.sample(words_list, 5)
    st.session_state.show_examples = {}
    st.rerun()

# Kelimeleri göster
st.markdown("<h2 style='text-align:center;color:#1E3A8A;'>Bu kelimeleri kullanarak tartış!</h2>", unsafe_allow_html=True)
col1, col2, col3, col4, col5 = st.columns(5)
columns = [col1, col2, col3, col4, col5]

for i, word in enumerate(st.session_state.selected_words):
    if columns[i].button(word, key=word):
        st.session_state.show_examples[word] = not st.session_state.show_examples.get(word, False)

# Tıklanan kelimelerin örnekleri
for word_record in words_data:
    word = word_record['English_Word']
    if st.session_state.show_examples.get(word, False):
        st.markdown(f"<div style='background:#333;color:#fff;padding:10px;border-radius:10px;white-space:pre-line;margin-top:5px;'>{word_record['Examples']}</div>", unsafe_allow_html=True)

st.caption(f"Toplam kelime: {len(words_list):,} | Kullanılan: 5")

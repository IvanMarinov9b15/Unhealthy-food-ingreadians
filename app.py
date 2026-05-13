import streamlit as st
import easyocr
from PIL import Image
import numpy as np

HARMFUL_DB = {
    "E102": {"name": "Тартразин / Tartrazine / Tartrazin", "risk": "Висок"},
    "E104": {"name": "Хинолиново жълто / Quinoline Yellow / Chinolingelb", "risk": "Висок"},
    "E110": {"name": "Сънсет жълто / Sunset Yellow / Gelborange S", "risk": "Висок"},
    "E122": {"name": "Азорубин / Azorubine / Azorubin", "risk": "Висок"},
    "E124": {"name": "Понсо 4R / Ponceau 4R / Cochenillerot A", "risk": "Висок"},
    "E127": {"name": "Еритрозин / Erythrosine / Erythrosin", "risk": "Висок"},
    "E129": {"name": "Алура червено / Allura Red / Allurarot AC", "risk": "Висок"},
    "E210": {"name": "Бензоена киселина / Benzoic Acid / Benzoesäure", "risk": "Среден"},
    "E211": {"name": "Натриев бензоат / Sodium Benzoate / Natriumbenzoat", "risk": "Среден"},
    "E249": {"name": "Калиев нитрит / Potassium Nitrite / Kaliumnitrit", "risk": "Висок"},
    "E250": {"name": "Натриев нитрит / Sodium Nitrite / Natriumnitrit", "risk": "Висок"},
    "E251": {"name": "Натриев нитрат / Sodium Nitrate / Natriumnitrat", "risk": "Среден"},
    "E621": {"name": "Мононатриев глутамат / Monosodium Glutamate / Glutamat", "risk": "Среден"},
    "E622": {"name": "Монокалиев глутамат / Monopotassium Glutamate", "risk": "Среден"},
    "E951": {"name": "Аспартам / Aspartame / Aspartam", "risk": "Висок"},
    "E952": {"name": "Цикламова киселина / Cyclamic Acid / Cyclamat", "risk": "Висок"},
    "palm oil": {"name": "Палмово масло / Palm oil / Palmöl", "risk": "Среден"},
    "trans fats": {"name": "Трансмазнини / Trans fats / Transfette", "risk": "Висок"}
}

st.title("AI Detector")

langs = st.multiselect("Избор на езици:", ['bg', 'en', 'de', 'ru', 'fr', 'tr', 'el'], default=['bg', 'en'])

uploaded_file = st.file_uploader("Качване на етикет", type=["jpg", "png", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image)
    
    if st.button("Анализ"):
        reader = easyocr.Reader(langs)
        results = reader.readtext(np.array(image), detail=0)
        full_text = " ".join(results).lower()
        
        for key, data in HARMFUL_DB.items():
            if key.lower() in full_text or any(name.strip().lower() in full_text for name in data['name'].split("/")):
                st.write(f"Намерено: {data['name']} - Риск: {data['risk']}")

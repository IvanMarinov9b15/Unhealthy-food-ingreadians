import streamlit as st
import easyocr
from PIL import Image
import numpy as np

# 1. Настройка на заглавието и интерфейса
st.set_page_config(page_title="Скенер за вредни съставки", layout="centered")
st.title("🔍 Анализатор на етикети")
st.write("Качете снимка или използвайте камерата, за да проверите за вредни съставки.")

# 2. Дефиниране на база данни с вредни съставки
# Можете да разширите този списък според вашите нужди
HARMFUL_INGREDIENTS = {
    "палмово масло": "Палмово масло (Palm Oil) - високо съдържание на наситени мазнини.",
    "palm oil": "Palm Oil - high saturated fat content.",
    "e621": "E621 (Мононатриев глутамат) - подобрител на вкуса, може да предизвика реакции.",
    "msg": "MSG (Monosodium Glutamate) - flavor enhancer.",
    "аспартам": "Аспартам (E951) - изкуствен подсладител.",
    "aspartame": "Aspartame (E951) - artificial sweetener.",
    "хидрогенирани": "Хидрогенирани мазнини - източник на вредни транс-мазнини.",
    "hydrogenated": "Hydrogenated fats - source of trans fats.",
    "захар": "Високо съдържание на захар.",
    "sugar": "High sugar content."
}

# 3. Инициализиране на EasyOCR (зарежда се веднъж)
@st.cache_resource
def load_ocr():
    # Зареждаме български и английски език
    return easyocr.Reader(['bg', 'en'])

reader = load_ocr()

# 4. Избор на метод за качване
option = st.radio("Изберете метод:", ("Качване на снимка", "Използване на камера"))

if option == "Качване на снимка":
    uploaded_file = st.file_uploader("Изберете изображение...", type=["jpg", "jpeg", "png"])
else:
    uploaded_file = st.camera_input("Снимайте етикета")

if uploaded_file is not None:
    # Отваряне на изображението с Pillow
    image = Image.open(uploaded_file)
    st.image(image, caption='Обработвана снимка', use_column_width=True)
    
    with st.spinner('Анализиране на текста... моля изчакайте.'):
        # Превръщане на изображението в NumPy масив за EasyOCR
        img_array = np.array(image)
        
        # Извличане на текст
        results = reader.readtext(img_array, detail=0)
        full_text = " ".join(results).lower()
        
        st.subheader("Резултати от анализа:")
        
        found_harmful = []
        
        # Проверка за вредни съставки
        for ingredient, description in HARMFUL_INGREDIENTS.items():
            if ingredient in full_text:
                found_harmful.append(description)
        
        # Показване на резултатите
        if found_harmful:
            st.error("⚠️ Внимание! Намерени са потенциално вредни съставки:")
            for item in found_harmful:
                st.write(f"- {item}")
        else:
            st.success("✅ Не са открити съставки от списъка с вредни вещества.")
            
        # Възможност за преглед на целия разпознат текст (за проверка)
        with st.expander("Виж разпознатия текст"):
            st.write(full_text)

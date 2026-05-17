import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['bg', 'en'])

reader = load_ocr_reader()

OREO_INGREDIENTS_DB = [
    {
        "keywords": ["палмово", "palm"],
        "name": "Палмово масло / Растителна мазнина (Palm oil)",
        "type": "Вредна",
        "risk": "Висока",
        "problems": "Изключително богато на наситени мастни киселини. Честата му консумация повишава нивата на лошия холестерол (LDL), запушва артериите и увеличава риска от инфаркт и захарен диабет тип 2.",
        "category": "Вредни мазнини"
    },
    {
        "keywords": ["захар", "sugar"],
        "name": "Рафинирана бяла захар (Sugar)",
        "type": "Вредна",
        "risk": "Висока",
        "problems": "Води до бързи пикове в кръвната захар, претоварва панкреаса, причинява зъбен кариес, затлъстяване и води до силна поведенческа зависимост към сладко.",
        "category": "Въглехидрати / Захари"
    },
    {
        "keywords": ["глюкозо", "фруктозен", "glucose", "fructose"],
        "name": "Глюкозо-фруктозен сироп (Glucose-fructose syrup)",
        "type": "Вредна",
        "risk": "Висока",
        "problems": "По-евтин и по-вреден заместител на захарта. Натоварва директно черния дроб, превръща се бързо в мазнини и е основен причинител на метаболитен синдром.",
        "category": "Въглехидрати / Захари"
    },
    {
        "keywords": ["e503", "амониев", "ammonium"],
        "name": "E503(ii) - Амониеви карбонати (Ammonium carbonates)",
        "type": "Спорна",
        "risk": "Средна",
        "problems": "Използва се като набухвател. Въпреки че се разпада при печене, остатъчни микроколичества могат да раздразнят стомашната лигавица при хора с чувствителен стомах.",
        "category": "Набухватели"
    },
    {
        "keywords": ["e501", "калиев", "potassium"],
        "name": "E501(ii) - Калиеви карбонати (Potassium carbonates)",
        "type": "Спорна",
        "risk": "Средна",
        "problems": "Използва се за регулиране на киселинността и като набухвател. Прекомерната консумация може да предизвика лек стомашен дискомфорт.",
        "category": "Набухватели"
    },
    {
        "keywords": ["e500", "натриев", "sodium", "bicarbonate"],
        "name": "E500(ii) - Натриеви карбонати / Сода бикарбонат (Sodium carbonates)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Стандартен и напълно безопасен набухвател, използван и в домашната кулинария.",
        "category": "Набухватели"
    },
    {
        "keywords": ["пшенично", "брашно", "wheat", "flour"],
        "name": "Пшенично брашно (Wheat flour)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Основна структурна съставка. Естествен източник на въглехидрати. Изисква внимание единствено при хора с глутенова непоносимост.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["нишесте", "starch"],
        "name": "Пшенично нишесте (Wheat starch)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Използва се за подобряване на текстурата на бисквитката. Въглехидрат, безопасен за здравето.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["какао", "cocoa"],
        "name": "Нискомаслено какао на прах (Fat-reduced cocoa powder)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Дава характерния тъмен цвят и вкус. Какаото съдържа естествени антиоксиданти (флавоноиди), които са полезни за сърцето.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["соев", "soya", "lecithin"],
        "name": "Соев лецитин (Soya lecithin)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Естествен емулгатор. Полезен е за организма – подпомага паметта и функцията на черния дроб.",
        "category": "Емулгатори"
    },
    {
        "keywords": ["слънчогледов", "sunflower"],
        "name": "Слънчогледов лецитин (Sunflower lecithin)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Натурална алтернатива на соевия лецитин. Напълно безопасен и хипоалергенен емулгатор.",
        "category": "Емулгатори"
    },
    {
        "keywords": ["ванилин", "flavouring", "vanillin"],
        "name": "Ароматизант / Ванилин (Flavouring / Vanillin)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Ароматизант за подобряване на миризмата. В използваните индустриални количества е напълно безопасен.",
        "category": "Ароматизанти"
    },
    {
        "keywords": ["сол", "salt"],
        "name": "Сол (Salt)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Използва се за балансиране на вкуса. Трябва да се внимава с общото количество приета сол за деня заради кръвното налягане.",
        "category": "Базови съставки"
    }
]

st.sidebar.title("Проект: Сканиране на Oreo")
choice = st.sidebar.radio("Премени към:", [
    "Сканиране на етикет", 
    "Ръчна проверка на съставки", 
    "Здравословни алтернативи"
])

if choice == "Сканиране на етикет":
    st.title("Интелигентен Скенер за Сладкарски Етикети")
    st.write("Качете или заснемете задния етикет на бисквити Oreo, за да анализирате съставките му.")
    
    upload_type = st.radio("Изберете метод:", ["Качване на файл", "Използване на камера"])
    
    uploaded_file = None
    if upload_type == "Качване на файл":
        uploaded_file = st.file_uploader("Качете снимка на етикет (PNG, JPG):", type=["jpg", "jpeg", "png"])
    else:
        uploaded_file = st.camera_input("Снимайте етикета тук")
        
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Зареден етикет за анализ", use_container_width=True)
        
        with st.spinner("Изкуственият интелект чете етикета..."):
            img_np = np.array(image)
            ocr_text_list = reader.readtext(img_np, detail=0)
            full_text = " ".join(ocr_text_list).lower()
            
        st.subheader("Разпознат текст от опаковката:")
        with st.expander("Виж прочетения текст"):
            st.write(full_text)
            
        st.subheader("Анализ на съставките в продукта:")
        
        found_any = False
        
        for info in OREO_INGREDIENTS_DB:
            is_matched = False
            for key in info["keywords"]:
                pattern = key.replace("e", "[eе]\\s*") if key.startswith("e") else key
                if re.search(pattern, full_text):
                    is_matched = True
                    break
            
            if is_matched:
                found_any = True
                if info["type"] == "Вредна":
                    st.error(f"Внимание! Намерена съставка: {info['name']}")
                    st.markdown(f"* **Категория:** {info['category']} | **Степен на риск:** {info['risk']}")
                    st.markdown(f"* **Здравословни проблеми:** {info['problems']}")
                elif info["type"] == "Спорна":
                    st.warning(f"Спорна съставка: {info['name']}")
                    st.markdown(f"* **Категория:** {info['category']} | **Степен на риск:** {info['risk']}")
                    st.markdown(f"* **Бележка:** {info['problems']}")
                else:
                    st.success(f"Безопасна съставка: {info['name']}")
                    st.markdown(f"* **Категория:** {info['category']} | **Ефект/Полза:** {info['problems']}")
                st.markdown("---")
                
        if not found_any:
            st.info("Не са открити познати съставки от базата данни на Oreo. Опитайте с по-ясно изображение.")

elif choice == "Ръчна проверка на съставки":
    st.title("Ръчно търсене в сладкарската база данни")
    st.write("Въведете съставка или Е-номер ръчно (напр. палмово масло, захар, E322, E503), за да разберете значението й.")
    
    query = st.text_input("Въведете име или номер на добавка:").strip().lower()
    query = query.replace("е", "e")
    
    if query:
        matched = False
        for info in OREO_INGREDIENTS_DB:
            is_query_match = False
            if query in info["name"].lower():
                is_query_match = True
            else:
                for key in info["keywords"]:
                    if query in key:
                        is_query_match = True
                        break
            
            if is_query_match:
                matched = True
                if info["type"] == "Вредна":
                    st.error(f"{info['name']}")
                    st.markdown(f"* **Категория:** {info['category']} | **Ниво на риск:** {info['risk']}")
                    st.markdown(f"* **Здравословни проблеми:** {info['problems']}")
                elif info["type"] == "Спорна":
                    st.warning(f"{info['name']}")
                    st.markdown(f"* **Категория:** {info['category']} | **Ниво на риск:** {info['risk']}")
                    st.markdown(f"* **Бележка:** {info['problems']}")
                else:
                    st.success(f"{info['name']}")
                    st.markdown(f"* **Категория:** {info['category']} | **Въздействие:** {info['problems']}")
                st.markdown("---")
        if not matched:
            st.warning("Съставката не е намерена. Моля, проверете изписването.")

elif choice == "Здравословни алтернативи":
    st.title("По-добрият избор: Здравословни алтернативи")
    st.write("Индустриалните сладкиши като Oreo са направени да издържат с месеци по складовете благодарение на палмовата мазнина. Ето как да задоволим глада за сладко по здравословен начин:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Избягвай или намали:")
        st.error("Купени бисквити със заливки (Пълни с палмово масло, което вреди на сърцето)")
        st.error("Рафинирана бяла захар (Води до рязък спад на енергията, умора и кариеси)")
        st.error("Продукти с дълъг срок на годност (Наситени с химически консерванти)")
        
    with col2:
        st.markdown("### Замени със здравословни:")
        st.success("Домашни бананово-овесени бисквити (Направени само с овесени ядки, намачкан банан, истинско какао и малко мед)")
        st.success("Черен шоколад (Над 70% какао – богат на антиоксиданти и без палмова мазнина)")
        st.success("Фурми или сушени плодове (Естествен източник на захари, фибри и енергия)")
        
    st.markdown("---")
    st.info("💡 Златно правило: Когато ви се хапва Oreo, опитайте се да го комбинирате с плод или просто си направете бързи домашни какаови бисквити. Вашето тяло ще ви благодари!")

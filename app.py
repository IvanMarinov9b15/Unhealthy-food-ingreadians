import streamlit as st
import easyocr
from PIL import Image
import numpy as np
import re

@st.cache_resource
def load_ocr_reader():
    return easyocr.Reader(['bg', 'en'])

reader = load_ocr_reader()

# Обновена и разширена база данни, съобразена напълно с американския етикет
OREO_INGREDIENTS_DB = [
    {
        "keywords": ["unbleached", "enriched flour", "wheat flour", "пшенично", "брашно"],
        "name": "Неизбелено обогатено пшенично брашно (Unbleached Enriched Flour)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Основна структурна съставка. Естествен източник на въглехидрати. Изисква внимание единствено при хора с глутенова непоносимост.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["niacin", "reduced iron", "thiamine", "mononitrate", "riboflavin", "folic acid"],
        "name": "Обогатители за брашно (Витамини B1, B2, B3, Фолиева киселина и Желязо)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Добавени задължителни микроелементи в САЩ за възстановяване на хранителната стойност на рафинираното брашно. Напълно безопасни.",
        "category": "Витамини и Минерали"
    },
    {
        "keywords": ["sugar", "захар"],
        "name": "Рафинирана бяла захар (Sugar)",
        "type": "Вредна",
        "risk": "Висока",
        "problems": "Води до бързи пикове в кръвната захар, претоварва панкреаса, причинява зъбен кариес, затлъстяване и води до силна поведенческа зависимост към сладко.",
        "category": "Въглехидрати / Захари"
    },
    {
        "keywords": ["palm", "canola oil", "палмово"],
        "name": "Палмово масло и/или Канолово масло (Palm and/or Canola Oil)",
        "type": "Вредна",
        "risk": "Висока",
        "problems": "Палмовото масло е изключително богато на наситени мастни киселини, които повишават лошия холестерол (LDL) и увреждат артериите. Каноловото масло е силно преработено рафинирано олио.",
        "category": "Вредни мазнини"
    },
    {
        "keywords": ["cocoa", "alkali", "какао"],
        "name": "Какао, обработено с алкали (Cocoa - Processed with Alkali)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Преминало през алкализация ('холандски процес') за намаляване на горчивината и потъмняване на цвета. Напълно безопасно, запазва част от естествените какаови антиоксиданти.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["high fructose", "corn syrup", "глюкозо", "фруктозен"],
        "name": "Глюкозо-фруктозен сироп от царевица (High Fructose Corn Syrup)",
        "type": "Вредна",
        "risk": "Висока",
        "problems": "Евтин и силно вреден индустриален подсладител. Натоварва директно черния дроб, превръща се бързо в мазнини около органите и е основен причинител на Диабет тип 2.",
        "category": "Въглехидрати / Захари"
    },
    {
        "keywords": ["baking soda", "e500", "sodium hydrogen"],
        "name": "Сода бикарбонат (Baking Soda / Натриев хидрогенкарбонат)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Стандартен и напълно безопасен набухвател, чиято роля е да помогне на бисквитката да бухне при печене.",
        "category": "Набухватели"
    },
    {
        "keywords": ["calcium phosphate", "калциев фосфат"],
        "name": "Калциев фосфат (Calcium Phosphate)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Минерална сол, която се използва като набухвател и регулатор на киселинността. Напълно безопасна в хранителните продукти.",
        "category": "Набухватели"
    },
    {
        "keywords": ["cornstarch", "нишесте"],
        "name": "Царевично нишесте (Cornstarch)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Растителен въглехидрат, използван за сгъстяване и подобряване на кремообразната текстура на пълнежа.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["salt", "сол"],
        "name": "Сол (Salt)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Използва се в минимални количества за балансиране на сладостта и подчертаване на какаовия вкус.",
        "category": "Базови съставки"
    },
    {
        "keywords": ["soy lecithin", "soya", "соев лецитин", "e322"],
        "name": "Соев лецитин (Soy Lecithin)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Натурален емулгатор, който не позволява на мазнините и водата в продукта да се отделят. Полезен за нервната система и черния дроб.",
        "category": "Емулгатори"
    },
    {
        "keywords": ["vanillin", "artificial flavor", "ароматизант"],
        "name": "Изкуствен ароматизант - Ванилин (Vanillin - An Artificial Flavor)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Синтетичен заместител на естествената ванилия. Използва се за придаване на приятен аромат. В кулинарните дози е безвреден.",
        "category": "Ароматизанти"
    },
    {
        "keywords": ["chocolate", "шоколад"],
        "name": "Шоколад (Chocolate)",
        "type": "Невредна",
        "risk": "Безопасна",
        "problems": "Добавена какаова маса за подсилване на шоколадовия вкус на хрупкавата бисквита.",
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
            full_text = " ".join(ocr_text_list)
            
        st.subheader("Разпознат текст от опаковката:")
        with st.expander("Виж прочетения текст"):
            st.write(full_text)
            
        st.subheader("Анализ на съставките в продукта:")
        
        found_any = False
        
        for info in OREO_INGREDIENTS_DB:
            is_matched = False
            for key in info["keywords"]:
                # Специална проверка за Е-номера
                if key.lower().startswith("e") and len(key) == 4 and key[1:].isdigit():
                    num = key[1:]
                    pattern = rf"[EЕeе]\s*{num}"
                else:
                    pattern = re.escape(key)
                
                if re.search(pattern, full_text, re.IGNORECASE):
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
    st.write("Въведете съставка или Е-номер ръчно (напр. палмово масло, захар, нишесте), за да разберете значението й.")
    
    query = st.text_input("Въведете име или номер на добавка:").strip().lower()
    
    if query:
        matched = False
        for info in OREO_INGREDIENTS_DB:
            is_query_match = False
            if query in info["name"].lower():
                is_query_match = True
            else:
                for key in info["keywords"]:
                    if query in key.lower():
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
    st.write("Индустриалните сладкиши като Oreo са направени да издържат с месеци по складовете благодарение на палма и сиропи. Ето как да задоволим глада за сладко по здравословен начин:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Избягвай или намали:")
        st.error("Купени бисквити със заливки (Пълни с палмово масло, което вреди на сърцето)")
        st.error("Рафинирана бяла захар (Води до рязък спад на енергията, умора и кариеси)")
        st.error("Продукти с дълъг срок на годност (Наситени с високо-фруктозен царевичен сироп)")
        
    with col2:
        st.markdown("### Замени со здравословни:")
        st.success("Домашни бананово-овесени бисквити (Направени само с овесени ядки, намачкан банан, истинско какао и малко мед)")
        st.success("Черен шоколад (Над 70% какао – богат на антиоксиданти и без палмова мазнина)")
        st.success("Фурми или сушени плодове (Естествен източник на захари, фибри и енергия)")
        
    st.markdown("---")
    st.info("💡 Златно правило: Когато ви се хапва Oreo, опитайте се да го комбинирате с плод или просто си направете бързи домашни какаови бисквити. Вашето тяло ще ви благодари!")

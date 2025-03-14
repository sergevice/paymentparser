import streamlit as st
import re

def extract_fields(text):
    # Регулярний вираз для IBAN (29 символів, починається з UA, далі цифри)
    iban_pattern = re.compile(r'UA\d{2}(?:\s?\d{4}){6}')
    
    # Регулярний вираз для ІПН (10 цифр)
    ipn_pattern = re.compile(r'\b\d{10}\b')
    
    # Регулярний вираз для Отримувача (три слова з буквами, апострофом, дефісом)
    receiver_pattern = re.compile(r'([А-ЯҐЄІЇа-яґєії\'’-]+\s+[А-ЯҐЄІЇа-яґєії\'’-]+\s+[А-ЯҐЄІЇа-яґєії\'’-]+)')
    
    # Регулярний вираз для Призначення платежу (останній блок тексту після "Призначення платежу")
    payment_purpose_pattern = re.compile(r'Призначення платежу\s*(.*)', re.DOTALL)
    
    iban = iban_pattern.search(text)
    ipn = ipn_pattern.search(text)
    receiver = receiver_pattern.search(text)
    payment_purpose = payment_purpose_pattern.search(text)
    
    return {
        "IBAN": iban.group(0) if iban else "Не знайдено",
        "ІПН": ipn.group(0) if ipn else "Не знайдено",
        "Отримувач": receiver.group(0) if receiver else "Не знайдено",
        "Призначення платежу": payment_purpose.group(1).strip() if payment_purpose else "Не знайдено"
    }

st.title("Парсер платіжної інформації")

text_input = st.text_area("Вставте текст для розбору:")

if st.button("Розпарсити"):
    if text_input.strip():
        parsed_data = extract_fields(text_input)
        
        st.write("**IBAN:**", parsed_data["IBAN"])
        st.write("**ІПН:**", parsed_data["ІПН"])
        st.write("**Отримувач:**", parsed_data["Отримувач"])
        st.write("**Призначення платежу:**", parsed_data["Призначення платежу"])
    else:
        st.warning("Будь ласка, введіть текст для розбору.")

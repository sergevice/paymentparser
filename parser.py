import streamlit as st
import re
import gspread
import logging
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials

# Налаштування логування
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def get_google_credentials():
    """Load Google Sheets credentials from Streamlit secrets."""
    try:
        encoded_creds = st.secrets["GOOGLE_CREDENTIALS"]
        creds_json = base64.b64decode(encoded_creds).decode("utf-8")
        credentials_dict = json.loads(creds_json)
        return ServiceAccountCredentials.from_json_keyfile_dict(credentials_dict)
    except Exception as e:
        logging.error(f"Помилка завантаження Google Credentials: {e}")
        st.error("Помилка при завантаженні Google Credentials. Перевірте секрети Streamlit.")
        return None

def extract_fields(text):
    logging.info("Розпочато обробку тексту")
    # Регулярний вираз для IBAN (29 символів, починається з UA, далі цифри)
    iban_pattern = re.compile(r'UA\d{27}|\bUA\d{2}(?:\s?\d{4}){6}\s?\d{1}\b')
    
    # Регулярний вираз для ІПН (10 цифр)
    ipn_pattern = re.compile(r'\b\d{10}\b')
    
    # Регулярний вираз для Отримувача (три слова з буквами, апострофом, дефісом)
    receiver_pattern = re.compile(r'(?<=Отримувач\s)\b([А-ЯҐЄІЇа-яґєії\'’-]+\s+[А-ЯҐЄІЇа-яґєії\'’-]+\s+[А-ЯҐЄІЇа-яґєії\'’-]+)\b', re.IGNORECASE)
    
    # Регулярний вираз для Призначення платежу (останній блок тексту після "Призначення платежу")
    payment_purpose_pattern = re.compile(r'Призначення платежу\s*(.*)', re.DOTALL)
    
    iban = iban_pattern.search(text)
    ipn = ipn_pattern.search(text)
    receiver = receiver_pattern.search(text)
    payment_purpose = payment_purpose_pattern.search(text)
    
    parsed_data = {
        "IBAN": iban.group(0) if iban else "Не знайдено",
        "ІПН": ipn.group(0) if ipn else "Не знайдено",
        "Отримувач": receiver.group(0) if receiver else "Не знайдено",
        "Призначення платежу": payment_purpose.group(1).strip() if payment_purpose else "Не знайдено"
    }
    
    validity = "Вірно" if all(value != "Не знайдено" for value in parsed_data.values()) else "Невірно"
    logging.info(f"Розібрані дані: {parsed_data}, Оцінка: {validity}")
    return parsed_data, validity


def send_to_google_sheets(text, parsed_data, validity):
    logging.info(f"Початок запису в Google Sheets з оцінкою: {validity}")

    try:
        credentials = get_google_credentials()
        if not credentials:
            return
        
        client = gspread.authorize(credentials)
        sheet = client.open("parsing_payments_doc").sheet1
        
        row = [
            text,
            parsed_data["Отримувач"],
            parsed_data["IBAN"],
            parsed_data["ІПН"],
            parsed_data["Призначення платежу"],
            validity
        ]
        
        logging.debug(f"Спроба запису: {row}")
        sheet.append_row(row)
        logging.info(f"Успішно записано в Google Sheets: {row}")
        st.success(f"Дані успішно збережені як '{validity}'")
    except Exception as e:
        logging.error(f"Помилка запису в Google Sheets: {e}")
        st.error(f"Помилка при записі в Google Sheets: {e}")

st.title("Парсер платіжної інформації")

text_input = st.text_area("Вставте текст для розбору:")

if st.button("Розпарсити"):
    if text_input.strip():
        parsed_data, validity = extract_fields(text_input)
        
        st.write("**IBAN:**", parsed_data["IBAN"])
        st.write("**ІПН:**", parsed_data["ІПН"])
        st.write("**Отримувач:**", parsed_data["Отримувач"])
        st.write("**Призначення платежу:**", parsed_data["Призначення платежу"])
        
        send_to_google_sheets(text_input, parsed_data, validity)

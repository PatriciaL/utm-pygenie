# UTM Genie: Generador de URL's con UTM

#Importamos las librerias
import streamlit as st
import re
from urllib.parse import urlencode

#Nos permite mostrar un titulo en la parte superior de la APP

#La libreria de streamlit nos permite construir interfaces sencillas
#url encode nos permite convertir un diccionario en una cadena de parámetros url

st.title("🔧 UTM Genie: Generador de URL's con UTM", layout="centered")

#Funcion para validar UTM: solo letras, numeros , guiones y guiones bajos

def is_valid_utm(value):
    return bool(re.match()r"^[a-zA-Z0-9_-]+$",value))

#Input personalizado con color

def validated_input(label,key):
    value = st.text_input(label, key=key)
    is_Valid = is_valid_utm(value) if value else True #vacio se considera valido
    color = "#d4edda" if is_valid else "#f8d7da"  # verde o rojo
    st.markdown(
        f"""
        <style>
        div[data-testid="stTextInput"] input#{key} {{
            background-color: {color};
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    return value.strip()




#Crea un campo de texto donde el usuario puede introducir parametros
base_url = st.text_input("Url base","https://tusitio.com")

utm_source = validated_input("utm_source", "utm_source")
utm_medium = validated_input("utm_medium", "utm_medium")
utm_campaign = validated_input("utm_campaign", "utm_campaign")
utm_term = validated_input("utm_term", "utm_term")
utm_content = validated_input("utm_content", "utm_content")

#Crea un dicionario params con los valores introducidos por el usuario, si un campo esta vacio añade una cadena vacia
params = {
    "utm_source": utm_source,
    "utm_medium": utm_medium,
    "utm_campaign": utm_campaign,
    "utm_term": utm_term,
    "utm_content": utm_content
}

#Fultra el diccionario para eliminar algun campo que este vacio asi evitamos que aparezcan parametros que no estan solicitados

params = {k: v for k, v in params.items() if v}


#Muestra un boton para que el usuario pueda generar una url 

utm_source = validated_input("utm_source", "utm_source")
utm_medium = validated_input("utm_medium", "utm_medium")
utm_campaign = validated_input("utm_campaign", "utm_campaign")
utm_term = validated_input("utm_term", "utm_term")
utm_content = validated_input("utm_content", "utm_content")
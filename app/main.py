# UTM Genie: Generador de URL's con UTM

#Importamos las librerias
"""La libreria de streamlit nos permite construir interfaces sencillas"""
"""url encode nos permite convertir un diccionario en una cadena de parámetros url"""


import streamlit as st
from urllib.parse import urlencode

#Nos permite mostrar un titulo en la parte superior de la APP
st.title("🔧 UTM Genie: Generador de URL's con UTM")

#Crea un campo de texto donde el usuario puede introducir parametros
base_url = st.text_input("Url base","https://tusitio.com")

utm_source = st.text_input("utm_source")
utm_medium = st.text_input("utm_medium")
utm_campaign = st.text_input("utm_campaign")
utm_term = st.text_input("utm_term")
utm_content = st.text_input("utm_content")

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

if st.button("Generar URL"):
    #Creal a url concatenando la base con los parametros modificados
    final_url = f"{base_url}?{urlencode(params)}"
    
    #muestra un mensaje de exito, la url generada con formato de código y un enlace clicable para probarla
    
    st.success("URL generada:")
    est.text_input("URL generada", value=final_url, key="final_url", label_visibility="collapsed")
    st.markdown(f"[Ir al enlace({final_url})]")
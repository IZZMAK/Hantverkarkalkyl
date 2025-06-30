
import streamlit as st
from datetime import datetime
import os

st.set_page_config(page_title="Kalkyl för Hantverkare", page_icon="💼")

# Logotyp och sidhuvud
st.image("https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/000000/external-construction-project-management-flaticons-lineal-color-flat-icons.png", width=60)
st.title("Avancerat Kalkylverktyg för Hantverkare")
st.markdown("*Skapa professionella offerter med hänsyn till tid, material, risk och ROT-avdrag.*")

with st.form("input_form"):
    st.header(":bust_in_silhouette: Kunduppgifter")
    kund_namn = st.text_input("Kundens namn")
    kund_adress = st.text_input("Adress")
    arbetsbeskrivning = st.text_area("Beskrivning av arbetet")

    st.header(":calendar: Arbetstid och Svårighetsgrad")
    arbetstid = st.number_input("Hur många timmar tar arbetet?", min_value=0.0, value=10.0)
    timpris = st.number_input("Timpris (kr)", min_value=0.0, value=450.0)
    svarighetsgrad = st.selectbox("Svårighetsgrad", ["Låg", "Medel", "Hög"])

    st.header(":toolbox: Material och Verktyg")
    materialkostnad = st.number_input("Materialkostnader (kr)", min_value=0.0, value=2000.0)
    hyra_utrustning = st.number_input("Hyra av verktyg/maskiner (kr)", min_value=0.0, value=0.0)

    st.header(":warning: Risknivå")
    riskniva = st.selectbox("Risknivå i arbetet", ["Låg", "Medel", "Hög"])

    st.header(":money_with_wings: ROT-avdrag")
    anvand_rot = st.checkbox("Tillämpa ROT-avdrag (30% på arbetskostnad upp till 50 000 kr)")

    moms_procent = st.slider("Moms (%)", 0, 50, 25)

    st.header(":page_facing_up: Export & Utskrift")
    exportera_pdf = st.checkbox("Förbered offert för utskrift")
    spara_offert = st.checkbox("Spara offerten som textfil")

    submitted = st.form_submit_button("Beräkna offert")

if submitted:
    # Justeringsfaktorer
    svarighets_faktor = {"Låg": 1.0, "Medel": 1.15, "Hög": 1.3}[svarighetsgrad]
    risk_faktor = {"Låg": 1.0, "Medel": 1.1, "Hög": 1.25}[riskniva]

    justerat_timpris = timpris * svarighets_faktor * risk_faktor
    arbetskostnad = arbetstid * justerat_timpris

    # ROT-avdrag
    rot_avdrag = 0
    if anvand_rot:
        rot_avdrag = min(arbetskostnad * 0.30, 50000)

    totalsumma_exkl_moms = arbetskostnad + materialkostnad + hyra_utrustning - rot_avdrag
    totalsumma_inkl_moms = totalsumma_exkl_moms * (1 + moms_procent / 100)

    st.subheader(":receipt: Offert")
    offert_text = f"Offert - {datetime.today().strftime('%Y-%m-%d')}\n"
    if kund_namn:
        st.write(f"**Kund:** {kund_namn}")
        offert_text += f"Kund: {kund_namn}\n"
    if kund_adress:
        st.write(f"**Adress:** {kund_adress}")
        offert_text += f"Adress: {kund_adress}\n"
    if arbetsbeskrivning:
        st.write(f"**Arbetsbeskrivning:** {arbetsbeskrivning}")
        offert_text += f"Arbetsbeskrivning: {arbetsbeskrivning}\n"

    st.write(f"**Justerat timpris (inkl. svårighet och risk):** {justerat_timpris:.2f} kr")
    st.write(f"**Arbetskostnad:** {arbetskostnad:.2f} kr")
    if anvand_rot:
        st.write(f"**ROT-avdrag:** -{rot_avdrag:.2f} kr")
        offert_text += f"ROT-avdrag: -{rot_avdrag:.2f} kr\n"
    st.write(f"**Material + verktyg:** {materialkostnad + hyra_utrustning:.2f} kr")
    st.write(f"**Totalt (exkl. moms):** {totalsumma_exkl_moms:.2f} kr")
    st.write(f"**Totalt (inkl. moms):** {totalsumma_inkl_moms:.2f} kr")

    offert_text += f"Justerat timpris: {justerat_timpris:.2f} kr\n"
    offert_text += f"Arbetskostnad: {arbetskostnad:.2f} kr\n"
    offert_text += f"Material + verktyg: {materialkostnad + hyra_utrustning:.2f} kr\n"
    offert_text += f"Totalt exkl. moms: {totalsumma_exkl_moms:.2f} kr\n"
    offert_text += f"Totalt inkl. moms: {totalsumma_inkl_moms:.2f} kr\n"

    if exportera_pdf:
        st.info("Tips: Använd webbläsarens utskriftsfunktion (Ctrl+P eller Cmd+P) för att spara offerten som PDF.")

    if spara_offert:
        filnamn = f"offert_{kund_namn.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.txt"
        with open(filnamn, "w", encoding="utf-8") as f:
            f.write(offert_text)
        with open(filnamn, "rb") as f:
            st.download_button("Ladda ner offert som textfil", f, file_name=filnamn)
        os.remove(filnamn)


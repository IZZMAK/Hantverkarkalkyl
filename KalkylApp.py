import streamlit as st
from datetime import datetime
import os
from fpdf import FPDF

st.set_page_config(page_title="Kalkyl för Hantverkare", page_icon="💼")

st.image("https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/000000/external-construction-project-management-flaticons-lineal-color-flat-icons.png", width=60)
st.title("Avancerat Kalkylverktyg för Hantverkare")
st.markdown("*Skapa professionella offerter med tid, material, svårighet, risk och ROT-avdrag.*")

with st.form("input_form"):
    st.header(":bust_in_silhouette: Kunduppgifter")
    kund_namn = st.text_input("Kundens namn")
    kund_adress = st.text_input("Adress")
    arbetsbeskrivning = st.text_area("Beskrivning av arbetet")

    st.header(":hammer: Automatiserad Tidsuppskattning")
    jobb_typ = st.selectbox("Typ av arbete", [
        "Välj...", "Måla vägg/tak", "Byta fönster", "Lägga golv", "Renovera badrum",
        "Takläggning", "Montera köksskåp", "Installera dörrar", "Bygga innervägg", "Anpassat snickeri"
    ])

    uppskattad_tid = 0
    if jobb_typ == "Måla vägg/tak":
        langd = st.number_input("Väggens längd (m)", min_value=0.0, value=5.0)
        hojd = st.number_input("Väggens höjd (m)", min_value=0.0, value=2.5)
        antal_vaggar = st.number_input("Antal väggar", min_value=1, value=4)
        fonster = st.number_input("Antal fönster", min_value=0, value=2)
        dorar = st.number_input("Antal dörrar", min_value=0, value=1)
        yta = langd * hojd * antal_vaggar - fonster * 1.5 - dorar * 2
        uppskattad_tid = max(0, yta * 0.25)

    elif jobb_typ == "Byta fönster":
        antal = st.number_input("Antal fönster", min_value=1, value=2)
        uppskattad_tid = antal * 3

    elif jobb_typ == "Lägga golv":
        golvyta = st.number_input("Yta (m²)", min_value=1.0, value=20.0)
        uppskattad_tid = golvyta * 0.4

    elif jobb_typ == "Renovera badrum":
        yta = st.number_input("Badrummets yta (m²)", min_value=1.0, value=6.0)
        uppskattad_tid = yta * 3

    elif jobb_typ == "Takläggning":
        takyta = st.number_input("Takyta (m²)", min_value=1.0, value=30.0)
        uppskattad_tid = takyta * 0.7

    elif jobb_typ == "Montera köksskåp":
        antal = st.number_input("Antal skåp", min_value=1, value=6)
        uppskattad_tid = antal * 0.75

    elif jobb_typ == "Installera dörrar":
        antal = st.number_input("Antal dörrar", min_value=1, value=2)
        uppskattad_tid = antal * 1.5

    elif jobb_typ == "Bygga innervägg":
        längd = st.number_input("Längd på innervägg (m)", min_value=1.0, value=4.0)
        uppskattad_tid = längd * 1.2

    elif jobb_typ == "Anpassat snickeri":
        yta = st.number_input("Yta (m²)", min_value=1.0, value=10.0)
        detalj = st.selectbox("Detaljnivå", ["Standard", "Avancerat"])
        uppskattad_tid = yta * (1 if detalj == "Standard" else 2)

    if uppskattad_tid > 0:
        st.success(f"Föreslagen arbetstid: {uppskattad_tid:.1f} timmar")

    st.header(":calendar: Arbetstid och Svårighetsgrad")
    arbetstid = st.number_input("Hur många timmar tar arbetet?", min_value=0.0, value=uppskattad_tid or 10.0)
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
    exportera_pdf = st.checkbox("Förbered offert för utskrift (PDF)")
    spara_offert = st.checkbox("Spara offerten som textfil")

    submitted = st.form_submit_button("Beräkna offert")

if submitted:
    svarighets_faktor = {"Låg": 1.0, "Medel": 1.15, "Hög": 1.3}[svarighetsgrad]
    risk_faktor = {"Låg": 1.0, "Medel": 1.1, "Hög": 1.25}[riskniva]

    justerat_timpris = timpris * svarighets_faktor * risk_faktor
    arbetskostnad = arbetstid * justerat_timpris

    rot_avdrag = min(arbetskostnad * 0.5, 50000) if anvand_rot else 0
    totalsumma_före_rot = arbetskostnad + materialkostnad + hyra_utrustning
    totalsumma_efter_rot = totalsumma_före_rot - rot_avdrag
    totalsumma_inkl_moms = totalsumma_efter_rot * (1 + moms_procent / 100)

    st.subheader(":receipt: Offert")
    offert_text = f"""Offert - {datetime.today().strftime('%Y-%m-%d')}
Kund: {kund_namn}
Adress: {kund_adress}
Arbetsbeskrivning: {arbetsbeskrivning}
Justerat timpris: {justerat_timpris:.2f} kr
Arbetskostnad: {arbetskostnad:.2f} kr
Material + verktyg: {materialkostnad + hyra_utrustning:.2f} kr
Totalt före ROT (exkl. moms): {totalsumma_före_rot:.2f} kr
ROT-avdrag: -{rot_avdrag:.2f} kr
Totalt efter ROT (exkl. moms): {totalsumma_efter_rot:.2f} kr
Totalt inkl. moms: {totalsumma_inkl_moms:.2f} kr"""

    st.text(offert_text)

    if exportera_pdf:
        class PDF(FPDF):
            def header(self):
                self.set_font("Arial", "B", 14)
                self.cell(0, 10, "Offert - Hantverkartjänster", 0, 1, "C")
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font("Arial", "I", 8)
                self.cell(0, 10, f"Sida {self.page_no()}", 0, 0, "C")

        pdf = PDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        for line in offert_text.split("\n"):
            pdf.multi_cell(0, 10, line)

        pdf_file = f"offert_{kund_namn.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.pdf"
        pdf.output(pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("📅 Ladda ner offert som PDF", f, file_name=pdf_file, mime="application/pdf")
        os.remove(pdf_file)

    if spara_offert:
        filnamn = f"offert_{kund_namn.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.txt"
        with open(filnamn, "w", encoding="utf-8") as f:
            f.write(offert_text)
        with open(filnamn, "rb") as f:
            st.download_button("💾 Ladda ner offert som textfil", f, file_name=filnamn)
        os.remove(filnamn)

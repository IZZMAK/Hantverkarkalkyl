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

    st.header(":calendar: Arbetstid")
    arbetstid = st.number_input("Hur många timmar tar arbetet?", min_value=0.0, value=10.0)
    timpris = st.number_input("Timpris (kr/tim)", min_value=0.0, value=500.0)

    st.header(":toolbox: Material och Övriga Kostnader")
    materialkostnad = st.number_input("Materialkostnader (kr)", min_value=0.0, value=3000.0)
    hyra_stallning = st.number_input("Hyra av ställning (kr)", min_value=0.0, value=0.0)
    reseersattning = st.number_input("Resekostnader (kr)", min_value=0.0, value=0.0)
    bortforsling = st.number_input("Bortforsling/Transport (kr)", min_value=0.0, value=0.0)

    anvand_rot = st.checkbox("Tillämpa ROT-avdrag (30% av arbetskostnad inkl. moms, max 50 000 kr)")
    moms_procent = st.slider("Moms (%)", 0, 50, 25)

    submitted = st.form_submit_button("Beräkna offert")

if submitted:
    arbetskostnad_exkl_moms = arbetstid * timpris
    ovrig_kostnad = hyra_stallning + reseersattning + bortforsling
    total_exkl_moms = arbetskostnad_exkl_moms + materialkostnad + ovrig_kostnad
    moms_belopp = total_exkl_moms * moms_procent / 100
    total_inkl_moms = total_exkl_moms + moms_belopp

    rot_avdrag = 0
    if anvand_rot:
        rot_avdrag = min(arbetskostnad_exkl_moms * (1 + moms_procent / 100) * 0.3, 50000)

    att_betala = total_inkl_moms - rot_avdrag

    st.subheader(":receipt: Offert")
    offert_text = f"""
Offert - {datetime.today().strftime('%Y-%m-%d')}
Kund: {kund_namn}
Adress: {kund_adress}
Arbetsbeskrivning: {arbetsbeskrivning}

---
Arbetskostnad: {arbetstid:.1f} tim x {timpris:.2f} kr = {arbetskostnad_exkl_moms:.2f} kr
Materialkostnader: {materialkostnad:.2f} kr
Hyra av ställning: {hyra_stallning:.2f} kr
Resekostnader: {reseersattning:.2f} kr
Bortforsling/Transport: {bortforsling:.2f} kr

Totalt exkl. moms: {total_exkl_moms:.2f} kr
Moms ({moms_procent}%): {moms_belopp:.2f} kr
Totalt inkl. moms: {total_inkl_moms:.2f} kr

ROT-avdrag: -{rot_avdrag:.2f} kr

Att betala: {att_betala:.2f} kr
"""
    st.text(offert_text)

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
        st.download_button("📄 Ladda ner offert som PDF", f, file_name=pdf_file, mime="application/pdf")
    os.remove(pdf_file)

import streamlit as st
from datetime import datetime
import os
from fpdf import FPDF

# Sida och titel
st.set_page_config(page_title="Kalkyl för Hantverkare", page_icon="💼")
st.image("https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/000000/external-construction-project-management-flaticons-lineal-color-flat-icons.png", width=60)
st.title("Avancerat Kalkylverktyg för Hantverkare")
st.markdown("*Offert med ROT-avdrag och lönekalkyl enligt Bokios metod för enskild firma (<200 000 kr)*")

# Indata
with st.form("input_form"):
    st.header("Kunduppgifter")
    kund_namn = st.text_input("Kundens namn")
    kund_adress = st.text_input("Adress")
    arbetsbeskrivning = st.text_area("Arbetsbeskrivning")

    st.header("Prisuppgifter")
    arbetstid = st.number_input("Arbetstid (timmar)", min_value=0.0, value=10.0)
    timpris = st.number_input("Timpris (kr/tim)", min_value=0.0, value=500.0)

    st.subheader("Material & Övriga kostnader")
    materialkostnad = st.number_input("Materialkostnader (kr)", min_value=0.0, value=2000.0)
    hyra_stallning = st.number_input("Hyra ställning (kr)", min_value=0.0, value=0.0)
    reseersattning = st.number_input("Resekostnader (kr)", min_value=0.0, value=0.0)
    bortforsling = st.number_input("Transportkostnader (kr)", min_value=0.0, value=0.0)

    anvand_rot = st.checkbox("Tillämpa ROT-avdrag (30% av arbetskostnad inkl. moms, max 50 000 kr)")

    submitted = st.form_submit_button("Beräkna offert")

if submitted:
    # Grundberäkningar
    arbetskostnad = arbetstid * timpris
    direkta_kostnader = materialkostnad + hyra_stallning + reseersattning + bortforsling
    moms_sats = 0.25
    total_exkl_moms = arbetskostnad + direkta_kostnader
    moms_belopp = total_exkl_moms * moms_sats
    total_inkl_moms = total_exkl_moms + moms_belopp

    # ROT-avdrag (på arbetskostnad inkl. moms)
    rot_avdrag = 0
    if anvand_rot:
        rot_avdrag = min(arbetskostnad * (1 + moms_sats) * 0.30, 50000)
    att_betala = total_inkl_moms - rot_avdrag

    # Bokios lönekalkyl-metod:
    # 1) Vinst före schablonavdrag = total_exkl_moms - direkta kostnader
    vinst = total_exkl_moms - direkta_kostnader
    # 2) Schablonavdrag 25% av vinsten
    schablon = vinst * 0.25
    skattemässig_vinst = vinst - schablon
    # 3) Sociala avgifter 28.97% på skattemässig vinst
    social_avgift = skattemässig_vinst * 0.2897
    # 4) Nettovinst efter egenavgifter
    netto_efter_egenavg = skattemässig_vinst - social_avgift
    # 5) Kommunalskatt 32% på nettovinst (under 200 000 kr -> ingen statlig)
    kommunalskatt = netto_efter_egenavg * 0.32
    # 6) Lön kvar (fika) efter skatt
    fikan = netto_efter_egenavg - kommunalskatt

    # Visa resultat
    st.subheader("Offert")
    st.text(f"Totalt exkl. moms: {total_exkl_moms:.2f} kr")
    st.text(f"Moms (25%): {moms_belopp:.2f} kr")
    st.text(f"Totalt inkl. moms: {total_inkl_moms:.2f} kr")
    if anvand_rot:
        st.text(f"ROT-avdrag: -{rot_avdrag:.2f} kr")
    st.text(f"Att betala: {att_betala:.2f} kr")
    st.markdown("---")
    st.subheader("Lönekalkyl enligt Bokio")
    st.text(f"Vinst före schablonavdrag: {vinst:.2f} kr")
    st.text(f"Schablonavdrag (25%): -{schablon:.2f} kr")
    st.text(f"Skattemässig vinst: {skattemässig_vinst:.2f} kr")
    st.text(f"Sociala avgifter (28.97%): {social_avgift:.2f} kr")
    st.text(f"Nettovinst efter egenavgifter: {netto_efter_egenavg:.2f} kr")
    st.text(f"Kommunalskatt (32%): {kommunalskatt:.2f} kr")
    st.subheader(f"Att behålla (fika) efter skatt: {fikan:.2f} kr")

    # PDF-export
    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Offert - Hantverkartjänster", 0, 1, "C")
            self.ln(5)
        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 8)
            self.cell(0, 10, f"Sida {self.page_no()}", 0, 0, "C")
    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    radlista = [
        f"Offert - {datetime.today().strftime('%Y-%m-%d')}",
        f"Kund: {kund_namn}",
        f"Adress: {kund_adress}",
        f"Beskrivning: {arbetsbeskrivning}",
        "", f"Totalt exkl. moms: {total_exkl_moms:.2f} kr",
        f"Moms (25%): {moms_belopp:.2f} kr", f"Totalt inkl. moms: {total_inkl_moms:.2f} kr",
    ]
    if anvand_rot:
        radlista.append(f"ROT-avdrag: -{rot_avdrag:.2f} kr")
    radlista += [
        f"Att betala: {att_betala:.2f} kr",
        "", "Lönekalkyl enligt Bokio:", f"Vinst före schablonavdrag: {vinst:.2f} kr",
        f"Schablonavdrag: -{schablon:.2f} kr", f"Sociala avgifter: {social_avgift:.2f} kr",
        f"Nettovinst: {netto_efter_egenavg:.2f} kr", f"Kommunalskatt: {kommunalskatt:.2f} kr",
        "", f"Att behålla (fika): {fikan:.2f} kr",
    ]
    for line in radlista:
        pdf.multi_cell(0, 8, line)
    pdf_file = f"offert_{kund_namn.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.pdf"
    pdf.output(pdf_file)
    with open(pdf_file, 'rb') as f:
        st.download_button("📄 Ladda ner offert som PDF", f, file_name=pdf_file, mime="application/pdf")
    os.remove(pdf_file)

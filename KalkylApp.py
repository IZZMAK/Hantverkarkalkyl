import streamlit as st
from datetime import datetime
import os
from fpdf import FPDF

# Titel och ikon
st.set_page_config(page_title="Kalkyl för Hantverkare", page_icon="💼")
st.image(
    "https://img.icons8.com/external-flaticons-lineal-color-flat-icons/64/000000/external-construction-project-management-flaticons-lineal-color-flat-icons.png",
    width=60
)
st.title("Avancerat Kalkylverktyg för Hantverkare")

st.markdown(
    "*Offert med detaljerad lönekalkyl enligt Bokio för enskild firma*  \n"
    "**ROT‑avdrag 50 %** \n"
    "---"
)

# 📋 Indataformulär
with st.form("input_form"):
    st.header("Kunduppgifter")
    kund_namn = st.text_input("Kundens namn")
    kund_adress = st.text_input("Adress")
    arbetsbeskrivning = st.text_area("Arbetsbeskrivning")

    st.header("Prisuppgifter")
    arbetstid = st.number_input(
        "Arbetstid (timmar)",
        min_value=0.0,
        value=10.0,
        help="Antal debiterbara timmar du räknar med att lägga på projektet."
    )
    timpris = st.number_input(
        "Timpris (kr/tim)",
        min_value=0.0,
        value=500.0,
        help="Priset du fakturerar kunden per timme (exkl. moms)."
    )

    st.subheader("Material & Övriga kostnader")
    materialkostnad = st.number_input(
        "Materialkostnader (kr)",
        min_value=0.0,
        value=2000.0,
        help="Inköpspris för material **exkl. moms**. Lägg på ev. påslag som intäkt i vinsten."
    )
    hyra_stallning = st.number_input("Hyra ställning (kr)", min_value=0.0, value=0.0)
    reseersattning = st.number_input("Resekostnader (kr)", min_value=0.0, value=0.0)
    bortforsling = st.number_input("Transportkostnader (kr)", min_value=0.0, value=0.0)

    # 📑 Bokio‑indata
    st.subheader("Lönekalkyl (Bokio‐metod)")
    ar = st.selectbox("Skatteår", [2025, 2026, 2027])
    fodelsear = st.number_input("Födelseår", min_value=1900, max_value=datetime.today().year, value=1979)
    kommunalskatt = st.number_input("Kommunalskatt (%)", min_value=0.0, max_value=100.0, value=31.0)

    vinst_per_ar = st.number_input(
        "Beräknad vinst per år (kr)",
        min_value=0.0,
        value=300000.0,
        help="**Intäkter exkl. moms** (arbete + påslag material) minus **alla avdragsgilla kostnader exkl. moms** – t.ex. materialinköp, resor, hyra, försäkring."
    )

    ovrig_inkomst = st.number_input(
        "Övrig inkomst per år (kr)",
        min_value=0.0,
        value=420000.0,
        help="Bruttoinkomst (före skatt) från anställning eller andra företag. Ange 0 kr om du inte har annan inkomst."
    )

    # ROT‑avdrag
    anvand_rot = st.checkbox(
        "Tillämpa ROT‑avdrag (50 % av arbetskostnad inkl. moms, max 50 000 kr)"
    )

    submitted = st.form_submit_button("Beräkna offert & lön")

# --- BERÄKNINGAR ---
if submitted:
    # Offertberäkning
    arbetskostnad = arbetstid * timpris
    direkta_kostnader = materialkostnad + hyra_stallning + reseersattning + bortforsling
    moms_sats = 0.25
    total_exkl_moms = arbetskostnad + direkta_kostnader
    moms_belopp = total_exkl_moms * moms_sats
    total_inkl_moms = total_exkl_moms + moms_belopp

    rot_avdrag = min(arbetskostnad * (1 + moms_sats) * 0.50, 50000) if anvand_rot else 0
    att_betala = total_inkl_moms - rot_avdrag

    # Vinst för uppdraget (intäkter - kostnader)
    job_vinst = arbetskostnad - direkta_kostnader

    # Lönekalkyl enligt Bokio (årsvärden)
    vinst_schablon = vinst_per_ar * 0.75
    grundavdrag = min(25000, vinst_schablon * 0.02)
    beskattningsbar = vinst_schablon - grundavdrag
    socialavg = beskattningsbar * 0.2897
    skatt_fore = (beskattningsbar - socialavg) * (kommunalskatt / 100)
    jobbskattavdrag = skatt_fore * 0.05
    skatt_efter = skatt_fore - jobbskattavdrag
    netto_efter_skatt = (beskattningsbar - socialavg) - skatt_efter
    nettolon = netto_efter_skatt + ovrig_inkomst  # nettolön efter skatt + övrig inkomst netto_efter_skatt + ovrig_inkomst

    effekt_ratio = netto_efter_skatt / beskattningsbar if beskattningsbar else 0
    fikan_uppdrag = job_vinst * effekt_ratio

    # --- RESULTATVISNING ---
        # --- RESULTATVISNING ---
    st.subheader("Offert")
    st.text(f"Totalt exkl. moms: {total_exkl_moms:,.2f} kr")
    st.text(f"Moms 25 %: {moms_belopp:,.2f} kr")
    st.text(f"Totalt inkl. moms: {total_inkl_moms:,.2f} kr")
    if anvand_rot:
        st.text(f"ROT-avdrag (50 %): -{rot_avdrag:,.2f} kr")
    st.text(f"Att betala: {att_betala:,.2f} kr")

    st.markdown("---")
    st.subheader("Lönekalkyl enligt Bokio (årsvärden)")
    st.text(f"Nettobelopp efter skatt (helår): {nettolon:,.2f} kr")

    st.markdown("---")
    st.subheader("Fika för detta uppdrag")
    st.text(f"Uppdragets vinst: {job_vinst:,.2f} kr")
    st.text(f"Andel kvar efter skatt (årsvärde): {effekt_ratio:.2%}")
    st.text(f"Fika för uppdrag (estimerat): {fikan_uppdrag:,.2f} kr")

    # --- PDF-EXPORT ---
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
    ascii_lines = [
        f"Offert - {datetime.today().strftime('%Y-%m-%d')}",
        f"Kund: {kund_namn}",
        f"Adress: {kund_adress}",
        f"Beskrivning: {arbetsbeskrivning}",
        "",
        f"Totalt exkl. moms: {total_exkl_moms:,.2f} kr",
        f"Moms 25 %: {moms_belopp:,.2f} kr",
        f"Totalt inkl. moms: {total_inkl_moms:,.2f} kr",
    ]
    if anvand_rot:
        ascii_lines.append(f"ROT-avdrag: -{rot_avdrag:,.2f} kr")
    ascii_lines += [
        f"Att betala: {att_betala:,.2f} kr",
        "",
        "Lönekalkyl enligt Bokio:",
        f"Nettobelopp efter skatt (helår): {nettolon:,.2f} kr",
        "",
        "Fika för detta uppdrag:",
        f"Uppdragets vinst: {job_vinst:,.2f} kr",
        f"Fika (efter skatt): {fikan_uppdrag:,.2f} kr",
    ]
    for line in ascii_lines:
        pdf.multi_cell(0, 8, line.encode('latin-1', 'replace').decode('latin-1'))

    pdf_file = f"offert_{kund_namn.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.pdf"
    pdf.output(pdf_file)
    with open(pdf_file, "rb") as f:
        st.download_button("📄 Ladda ner offert som PDF", f, file_name=pdf_file, mime="application/pdf")
    os.remove(pdf_file)

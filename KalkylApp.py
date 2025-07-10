import streamlit as st
from datetime import datetime
import os
from fpdf import FPDF

# ---------- SIDKONFIG ----------
st.set_page_config(page_title="Hantverkarkalkyl", page_icon="🛠️", layout="wide")

# Stabil ikon (ingen bruten länk)
st.image("https://img.icons8.com/fluency/64/toolbox.png", width=64)
st.title("Hantverkarkalkyl – Offert & Lönekalkyl (Bokio)")

st.markdown("**ROT‑avdrag 50 %**  •  Alla priser anges *exklusive* moms i inmatningen")

# ---------- INDATAFORMULÄR ----------
with st.form("calc_form"):
    # Kundblock i två kolumner för mindre scroll
    st.subheader("Kunduppgifter")
    kund1, kund2 = st.columns(2)
    with kund1:
        kund_namn = st.text_input("Kundens namn")
    with kund2:
        kund_adress = st.text_input("Adress")
    arbetsbeskrivning = st.text_area("Arbetsbeskrivning")

    # Prisblock – delas i två kolumner
    st.subheader("Prisuppgifter")
    p1, p2 = st.columns(2)
    with p1:
        arbetstid = st.number_input("Arbetstid (timmar)", min_value=0.0, value=10.0)
        timpris = st.number_input("Timpris (kr/tim)", min_value=0.0, value=500.0)
    with p2:
        materialkostnad = st.number_input("Materialkostnader (kr)", min_value=0.0, value=2000.0,
            help="Inköpspris för material – exkl. moms. Påslag redovisas som intäkt i vinstfältet nedan.")
        hyra_stallning = st.number_input("Hyra ställning (kr)", min_value=0.0, value=0.0)
        reseersattning = st.number_input("Resekostnader (kr)", min_value=0.0, value=0.0)
        bortforsling = st.number_input("Transportkostnader (kr)", min_value=0.0, value=0.0)

    anvand_rot = st.checkbox("Tillämpa ROT‑avdrag (50 % på arbetskostnad inkl. moms, max 50 000 kr)")

    # Bokio‑del i expander för att spara plats
    with st.expander("Lönekalkyl (Bokio‑metod) – klicka för detaljer"):
        l1, l2 = st.columns(2)
        with l1:
            ar = st.selectbox("Skatteår", [2025, 2026, 2027])
            kommunalskatt = st.number_input("Kommunalskatt (%)", min_value=0.0, max_value=100.0, value=31.0)
        with l2:
            fodelsear = st.number_input("Födelseår", min_value=1900, max_value=datetime.today().year, value=1979)

        vinst_per_ar = st.number_input(
            "Beräknad vinst per år (kr)",
            min_value=0.0,
            value=300000.0,
            help="INTÄKTER exkl. moms – KOSTNADER exkl. moms (arbete + påslag material − materialinköp och övriga kostnader)."
        )
        ovrig_inkomst = st.number_input(
            "Övrig inkomst per år (kr)",
            min_value=0.0,
            value=420000.0,
            help="Bruttoinkomst före skatt från anställning/andra företag."
        )

    submitted = st.form_submit_button("Beräkna offert & lön")

# ---------- BERÄKNING ----------
if submitted:
    # Offertdel
    arbetskostnad = arbetstid * timpris
    direkta_kostnader = materialkostnad + hyra_stallning + reseersattning + bortforsling
    moms_sats = 0.25
    total_exkl_moms = arbetskostnad + direkta_kostnader
    moms_belopp = total_exkl_moms * moms_sats
    total_inkl_moms = total_exkl_moms + moms_belopp

    rot_avdrag = min(arbetskostnad * (1 + moms_sats) * 0.50, 50000) if anvand_rot else 0
    att_betala = total_inkl_moms - rot_avdrag

    # Uppdragsvinst (intäkt exkl. moms – direkta kostnader)
    job_vinst = arbetskostnad - direkta_kostnader

    # Bokio‑årskalkyl (förenklad)
    vinst_schablon = vinst_per_ar * 0.75
    grundavdrag = min(25000, vinst_schablon * 0.02)
    beskattningsbar = vinst_schablon - grundavdrag
    socialavg = beskattningsbar * 0.2897
    skatt_fore = (beskattningsbar - socialavg) * (kommunalskatt / 100)
    jobbskattavdrag = skatt_fore * 0.05
    skatt_efter = skatt_fore - jobbskattavdrag
    netto_efter_skatt = (beskattningsbar - socialavg) - skatt_efter
    nettolon = netto_efter_skatt + ovrig_inkomst

    effekt_ratio = netto_efter_skatt / beskattningsbar if beskattningsbar else 0
    fikan_uppdrag = job_vinst * effekt_ratio

    # ---------- RESULTAT ----------
    colA, colB = st.columns(2)
    with colA:
        st.subheader("Offert – sammanfattning")
        st.metric("Totalt inkl. moms", f"{total_inkl_moms:,.0f} kr")
        if anvand_rot:
            st.text(f"ROT-avdrag 50 %: -{rot_avdrag:,.0f} kr")
        st.metric("Att betala", f"{att_betala:,.0f} kr")
    with colB:
        st.subheader("Fika för uppdraget")
        st.metric("Vinst (exkl. moms)", f"{job_vinst:,.0f} kr")
        st.metric("Andel kvar", f"{effekt_ratio:.0%}")
        st.metric("Fika (netto)", f"{fikan_uppdrag:,.0f} kr")

    st.markdown("---")
    st.subheader("Lönekalkyl (helår, Bokio‑modell)")
    st.text(f"Nettobelopp efter skatt: {nettolon:,.0f} kr")

    # ---------- PDF ----------
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
    lines = [
        f"Offert - {datetime.today().strftime('%Y-%m-%d')}",
        f"Kund: {kund_namn}",
        f"Adress: {kund_adress}",
        f"Beskrivning: {arbetsbeskrivning}",
        "",
        f"Totalt exkl. moms: {total_exkl_moms:,.0f} kr",
        f"Moms 25%: {moms_belopp:,.0f} kr",
        f"Totalt inkl. moms: {total_inkl_moms:,.0f} kr",
    ]
    if anvand_rot:
        lines.append(f"ROT-avdrag: -{rot_avdrag:,.0f} kr")
    lines += [
        f"Att betala: {att_betala:,.0f} kr",
        "",
        f"Uppdragets vinst (exkl. moms): {job_vinst:,.0f} kr",
        f"Fika efter skatt: {fikan_uppdrag:,.0f} kr",
    ]
    for l in lines:
        pdf.multi_cell(0, 8, l.encode("latin-1", "replace").decode("latin-1"))
    file_name = f"offert_{kund_namn.replace(' ', '_')}_{datetime.today().strftime('%Y%m%d')}.pdf"
    pdf.output(file_name)
    with open(file_name, "rb") as f:
        st.download_button("📄 Ladda ner offert som PDF", f, file_name=file_name)
    os.remove(file_name)

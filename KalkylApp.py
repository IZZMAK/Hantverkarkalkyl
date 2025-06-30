import streamlit as st

st.set_page_config(page_title="Kalkyl för Hantverkare", page_icon="🛠️")

st.title("🧰 Kalkylverktyg för Hantverkare (Enmansföretag)")

with st.form("input_form"):
    timmar_per_manad = st.number_input("Debiterbara timmar per månad", min_value=1, value=120)
    onskad_nettolon = st.number_input("Önskad nettolön efter skatt (kr)", min_value=0, value=25000)
    skatt_procent = st.slider("Skatt (%)", 0, 60, 30)
    foretagskostnader = st.number_input("Företagskostnader per månad (kr)", min_value=0, value=10000)
    fasta_kostnader = st.number_input("Övriga fasta kostnader per månad (kr)", min_value=0, value=3000)
    moms_procent = st.slider("Moms (%)", 0, 50, 25)
    vinst_procent = st.slider("Buffert/vinstmarginal (%)", 0, 100, 10)

    submitted = st.form_submit_button("Beräkna")

if submitted:
    bruttolon = onskad_nettolon / (1 - skatt_procent / 100)
    total_utgifter = bruttolon + foretagskostnader + fasta_kostnader
    vinst = total_utgifter * (vinst_procent / 100)
    oms_exkl_moms = total_utgifter + vinst
    oms_inkl_moms = oms_exkl_moms * (1 + moms_procent / 100)
    timpris_exkl_moms = oms_exkl_moms / timmar_per_manad
    timpris_inkl_moms = oms_inkl_moms / timmar_per_manad

    st.subheader("📊 Resultat")
    st.write(f"**Bruttolön före skatt:** {bruttolon:.2f} kr")
    st.write(f"**Total månadskostnad (inkl. lön):** {total_utgifter:.2f} kr")
    st.write(f"**Vinstpåslag:** {vinst:.2f} kr")
    st.write(f"**Omsättning exkl. moms:** {oms_exkl_moms:.2f} kr")
    st.write(f"**Omsättning inkl. moms:** {oms_inkl_moms:.2f} kr")
    st.write(f"**Timpris exkl. moms:** {timpris_exkl_moms:.2f} kr")
    st.write(f"**Timpris inkl. moms:** {timpris_inkl_moms:.2f} kr")

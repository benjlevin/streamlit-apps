import datetime
import streamlit as st

def parse_date(date_str):
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError("Enter date as MMDDYYYY (e.g., 05252025)")
    return datetime.datetime.strptime(date_str, "%m%d%Y").date()

def copy_button(label, text, key):
    """Render a button that copies given text to clipboard using JS."""
    escaped_text = text.replace("'", "\\'")
    copy_code = f"""
    <script>
    function copyToClipboard_{key}() {{
        navigator.clipboard.writeText('{escaped_text}').then(function() {{
            const status = document.getElementById('copy-status-{key}');
            status.innerText = '📋 Copied!';
        }});
    }}
    </script>
    <button onclick="copyToClipboard_{key}()">📋 {label}</button>
    <span id="copy-status-{key}" style="margin-left:10px;color:green"></span>
    """
    st.components.v1.html(copy_code, height=35)

st.title("🍼 Pregnancy EDD Calculator")

# --- LMP to EDD ---
st.markdown("### 📅 Calculate EDD from LMP")
lmp_str = st.text_input("LMP (MMDDYYYY)", "")
ref_str = st.text_input("Reference Date (MMDDYYYY)", datetime.datetime.today().strftime("%m%d%Y"))
if st.button("Calculate EDD from LMP"):
    try:
        lmp = parse_date(lmp_str)
        ref_date = parse_date(ref_str)
        edd = lmp + datetime.timedelta(days=280)
        ga_days = (ref_date - lmp).days
        weeks, days = divmod(ga_days, 7)
        output = f"LMP: {lmp.strftime('%m/%d/%Y')} | EDD: {edd.strftime('%m/%d/%Y')} | GA on {ref_date.strftime('%m/%d/%Y')}: {weeks}w{days}d"
        st.info(output)
        copy_button("Copy LMP Result", output, "lmp")
    except Exception as e:
        st.error(str(e))

# --- GA to Date ---
st.markdown("---")
st.markdown("### ⏳ Calculate Date from Gestational Age")
edd_str = st.text_input("EDD (MMDDYYYY)", "")
weeks = st.number_input("GA Weeks", min_value=0, max_value=42, value=0, step=1)
days = st.number_input("GA Days", min_value=0, max_value=6, value=0, step=1)
if st.button("Calculate Date for Given GA"):
    try:
        edd = parse_date(edd_str)
        target_date = edd - datetime.timedelta(weeks=40 - weeks, days=-days)
        output = f"Date when patient will be {weeks}w{days}d: {target_date.strftime('%m/%d/%Y')}"
        st.info(output)
        copy_button("Copy GA Date", output, "ga")
    except Exception as e:
        st.error(str(e))

# --- US to EDD ---
st.markdown("---")
st.markdown("### 🩻 Calculate EDD from Ultrasound")
us_date_str = st.text_input("Ultrasound Date (MMDDYYYY)", "")
us_weeks = st.number_input("US GA Weeks", min_value=0, max_value=42, value=0, step=1)
us_days = st.number_input("US GA Days", min_value=0, max_value=6, value=0, step=1)
if st.button("Calculate EDD from Ultrasound"):
    try:
        us_date = parse_date(us_date_str)
        edd = us_date + datetime.timedelta(days=(280 - (us_weeks * 7 + us_days)))
        output = f"US date: {us_date.strftime('%m/%d/%Y')} | US GA: {us_weeks}w{us_days}d | EDD from ultrasound: {edd.strftime('%m/%d/%Y')}"
        st.info(output)
        copy_button("Copy US EDD", output, "us")
    except Exception as e:
        st.error(str(e))

# --- Reconciliation ---
st.markdown("---")
st.markdown("### ⚖️ Reconcile EDDs (LMP vs US)")
if st.button("Reconcile LMP and US EDDs"):
    try:
        lmp = parse_date(lmp_str)
        lmp_edd = lmp + datetime.timedelta(days=280)

        us_date = parse_date(us_date_str)
        ga_by_lmp_on_us = (us_date - lmp).days
        ga_by_us = us_weeks * 7 + us_days
        diff = abs(ga_by_lmp_on_us - ga_by_us)

        if ga_by_lmp_on_us <= 62:
            threshold = 6
        elif 63 <= ga_by_lmp_on_us <= 111:
            threshold = 8
        elif 112 <= ga_by_lmp_on_us <= 153:
            threshold = 11
        elif 154 <= ga_by_lmp_on_us <= 195:
            threshold = 16
        else:
            threshold = 22

        us_edd = us_date + datetime.timedelta(days=(280 - ga_by_us))
        ga_weeks, ga_days = divmod(ga_by_lmp_on_us, 7)

        recommendation = (
            f"Use US EDD: {us_edd.strftime('%m/%d/%Y')}"
            if diff >= threshold else
            f"Keep LMP EDD: {lmp_edd.strftime('%m/%d/%Y')}"
        )

        output = (
            f"EDD from LMP: {lmp_edd.strftime('%m/%d/%Y')}\n"
            f"EDD from US: {us_edd.strftime('%m/%d/%Y')}\n"
            f"GA by LMP on US date: {ga_weeks}w{ga_days}d\n"
            f"Difference: {diff} days\n"
            f"ACOG threshold: {threshold} days\n"
            f"Recommendation: {recommendation}"
        )
        st.info(output.replace("\n", "<br>"), unsafe_allow_html=True)
        copy_button("Copy Reconciliation", output, "recon")
    except Exception as e:
        st.error(str(e))

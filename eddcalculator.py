import datetime
import streamlit as st

try:
    import pyperclip
except ImportError:
    import subprocess, sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyperclip"])
    import pyperclip

def parse_date(date_str):
    if len(date_str) != 8 or not date_str.isdigit():
        raise ValueError("Enter date as MMDDYYYY (e.g., 05252025)")
    return datetime.datetime.strptime(date_str, "%m%d%Y").date()

def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        st.success("Result copied to clipboard!")
    except Exception as e:
        st.error(f"Failed to copy to clipboard: {e}")

st.title("Pregnancy EDD Calculator")

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
        copy_to_clipboard(output)
    except Exception as e:
        st.error(str(e))

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
        copy_to_clipboard(output)
    except Exception as e:
        st.error(str(e))

st.markdown("---")
st.markdown("### 📊 Calculate EDD from Ultrasound")
us_date_str = st.text_input("Ultrasound Date (MMDDYYYY)", "")
us_weeks = st.number_input("US GA Weeks", min_value=0, max_value=42, value=0, step=1)
us_days = st.number_input("US GA Days", min_value=0, max_value=6, value=0, step=1)
if st.button("Calculate EDD from Ultrasound"):
    try:
        us_date = parse_date(us_date_str)
        edd = us_date + datetime.timedelta(days=(280 - (us_weeks * 7 + us_days)))
        output = f"US date: {us_date.strftime('%m/%d/%Y')} | US GA: {us_weeks}w{us_days}d | EDD from ultrasound: {edd.strftime('%m/%d/%Y')}"
        st.info(output)
        copy_to_clipboard(output)
    except Exception as e:
        st.error(str(e))

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

        lmp_edd_str = lmp_edd.strftime("%m/%d/%Y")
        us_edd_str = us_edd.strftime("%m/%d/%Y")

        output = (
            f"- EDD based on LMP: {lmp_edd_str}\n"
            f"- EDD based on US: {us_edd_str}\n"
            f"- GA based on LMP on US date: {ga_weeks}w{ga_days}d\n"
            f"- Difference: {diff} days\n"
            f"- ACOG threshold: {threshold} days\n"
        )

        if diff >= threshold:
            output += f"- Use US EDD: {us_edd_str}"
        else:
            output += f"- Keep LMP EDD: {lmp_edd_str}"

        st.info(output)
        copy_to_clipboard(output)
    except Exception as e:
        st.error(str(e))

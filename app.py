import streamlit as st
import pandas as pd
import math

# Page Configuration
st.set_page_config(
    page_title="مركز بحوث الطاقة - بابل",
    page_icon="☀️",
    layout="centered"
)

# Custom CSS for Arabic RTL and Styling
st.markdown("""
<style>
    .main {
        direction: rtl;
        font-family: 'Tajawal', sans-serif;
    }
    h1, h2, h3 {
        text-align: center;
        color: #f39c12;
    }
    .stButton>button {
        width: 100%;
        background-color: #f39c12;
        color: white;
        font-weight: bold;
    }
    .stDataFrame {
        direction: rtl;
    }
    div[class*="stTextInput"] label, div[class*="stNumberInput"] label {
        text-align: right;
        direction: rtl;
        width: 100%;
    }
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .result-box {
        padding: 20px;
        background-color: #f0f2f6;
        border-radius: 10px;
        margin-top: 20px;
        border: 2px solid #f39c12;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.title("حاسبة منظومات الطاقة الشمسية")
st.markdown("### مركز بحوث الطاقة - بابل")
st.markdown("---")

# Inputs
col1, col2, col3 = st.columns(3)

with col3:
    ampere = st.number_input("الأمبير المطلوب (Ampere)", min_value=1.0, value=5.0, step=0.5)

with col2:
    night_hours = st.number_input("ساعات التشغيل الليلي", min_value=0.0, max_value=24.0, value=6.0, step=0.5)

with col1:
    day_hours = st.number_input("ساعات التشغيل النهاري", min_value=0.0, max_value=24.0, value=6.0, step=0.5)

# Calculate Button
if st.button("احسب متطلبات المنظومة"):
    # Constants
    VOLTAGE = 220
    BATTERY_VOLTAGE = 48
    BATTERY_DOD = 0.5
    BATTERY_CAPACITY_AH_UNIT = 200  # Assuming 200Ah 12V batteries
    PANEL_WATT_PEAK = 550  # Assuming 550W panels
    PEAK_SUN_HOURS = 5
    SYSTEM_EFFICIENCY = 0.8
    INVERTER_SAFETY_FACTOR = 1.25

    # 1. Load Calculations
    load_watts = ampere * VOLTAGE
    
    # 2. Inverter Calculation (kVA)
    inverter_kva = (load_watts * INVERTER_SAFETY_FACTOR) / 1000
    # Round up to nearest standard size (simplified logic, just showing calculated minimum)
    inverter_kva_display = math.ceil(inverter_kva * 10) / 10  # Round to 1 decimal

    # 3. Energy Calculations
    energy_night_wh = load_watts * night_hours
    energy_day_wh = load_watts * day_hours
    total_daily_energy_wh = energy_night_wh + energy_day_wh

    # 4. Battery Calculations
    # Energy required from batteries = Night Energy
    # Considering DoD
    required_battery_capacity_wh = energy_night_wh / BATTERY_DOD
    
    # Bank Capacity in Ah at 48V
    required_bank_ah = required_battery_capacity_wh / BATTERY_VOLTAGE
    
    # Number of parallel strings needed (using 200Ah batteries)
    parallel_strings = math.ceil(required_bank_ah / BATTERY_CAPACITY_AH_UNIT)
    
    # Total batteries (4 in series for 48V * parallel strings)
    total_batteries = parallel_strings * 4

    # 5. Solar Panel Calculations
    # Total energy needed from panels needs to cover total daily consumption + efficiency losses
    required_pv_energy_wh = total_daily_energy_wh / SYSTEM_EFFICIENCY
    
    # Total Array Watt Peak required
    required_array_watts = required_pv_energy_wh / PEAK_SUN_HOURS
    
    # Number of Panels
    total_panels = math.ceil(required_array_watts / PANEL_WATT_PEAK)

    # Display Results
    st.markdown("### النتائج والتوصيات")
    
    results = {
        "العنصر": [
            "حجم الإنفرتر (kVA)",
            "عدد البطاريات (200Ah/12V)",
            "عدد الألواح الشمسية (550W)",
            "نظام البطاريات (Voltage)",
            "الحمل الكلي (Watt)"
        ],
        "القيمة المحسوبة": [
            f"{inverter_kva_display} kVA",
            f"{total_batteries} بطارية",
            f"{total_panels} لوح",
            "48 Volt",
            f"{load_watts} Watt"
        ],
        "ملاحظات": [
            "يوصى باختيار أقرب حجم قياسي أكبر",
            f"{parallel_strings} مصفوفة (String) على التوازي",
            f"إجمالي قدرة الألواح: {total_panels * PANEL_WATT_PEAK} Watt",
            "4 بطاريات على التوالي لكل مصفوفة",
            "عند جهد 220 فولت"
        ]
    }

    df = pd.DataFrame(results)
    
    # Styling the dataframe
    st.table(df)

    # Detailed Summary
    st.info(f"""
    **تفاصيل سريعة:**
    - استهلاك الطاقة اليومي المتوقع: {total_daily_energy_wh/1000:.2f} كيلو واط ساعة.
    - سعة البطاريات المطلوبة (للييل): {required_battery_capacity_wh/1000:.2f} كيلو واط ساعة.
    """)

else:
    st.markdown("""
    <div class="result-box">
        قم بإدخال البيانات أعلاه ثم اضغط على زر "احسب" لعرض النتائج
    </div>
    """, unsafe_allow_html=True)

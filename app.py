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

st.markdown("---")
st.markdown("### خصائص البطارية")
b_col1, b_col2 = st.columns(2)

with b_col2:
    battery_type = st.selectbox(
        "نوع البطارية", 
        ["Lead Acid / Gel / AGM (12V - DoD 50%)", "Lithium Ion (Integrated 48V - DoD 80%)"],
        index=0
    )

with b_col1:
    if "48V" in battery_type:
        battery_kwh = st.number_input("سعة البطارية الواحدة (kWh)", min_value=1.0, value=5.0, step=0.1, help="مثلاً 5kWh أو 10kWh")
    else:
        battery_kwh = st.number_input("سعة البطارية الواحدة (kWh)", min_value=0.5, value=2.4, step=0.1, help="بطارية 200Ah-12V تعادل 2.4kWh")

# Calculate Button
if st.button("احسب متطلبات المنظومة"):
    # Constants
    VOLTAGE = 220
    BATTERY_SYSTEM_VOLTAGE = 48
    
    # Determine DoD and voltage per unit based on selection
    is_lithium_48v = "48V" in battery_type
    
    if is_lithium_48v:
        BATTERY_DOD = 0.8
        BATTERY_UNIT_VOLTAGE = 48
    else:
        BATTERY_DOD = 0.5
        BATTERY_UNIT_VOLTAGE = 12
        
    PANEL_WATT_PEAK = panel_power  # Use User Input
    PEAK_SUN_HOURS = 5
    SYSTEM_EFFICIENCY = 0.8
    INVERTER_SAFETY_FACTOR = 1.25

    # 1. Load Calculations
    load_watts = ampere * VOLTAGE
    
    # 2. Energy Calculations (Moved up for Inverter Sizing)
    energy_night_wh = load_watts * night_hours
    energy_day_wh = load_watts * day_hours
    total_daily_energy_wh = energy_night_wh + energy_day_wh

    # 3. Inverter Calculation (Global Standard - C-Rate Method)
    # A. Size based on instantaneous load (Surge & Continous)
    inverter_load_kva = (load_watts * INVERTER_SAFETY_FACTOR) / 1000
    
    # B. Size based on Battery C-Rate (Charging/Discharging Capability)
    # Global Standards:
    # - Lead Acid: Recommended charge rate ~0.1C to 0.2C (Mean 0.15C) to prevent overheating/damage.
    # - Lithium: Recommended charge rate ~0.5C (can go up to 1C but 0.5C is standard for longevity).
    
    # Calculate Total Battery Capacity in kWh first (needed for C-Rate)
    required_battery_capacity_wh = energy_night_wh / BATTERY_DOD
    total_kwh_storage_needed = required_battery_capacity_wh / 1000
    
    # Determine actual selected bank size (roughly) based on unit count rounding
    # This ensures we size for the ACTUAL bank, not just the required minimum
    if is_lithium_48v:
        c_rate_factor = 0.5  # 0.5C for Lithium
        total_batteries_calc = math.ceil(total_kwh_storage_needed / battery_kwh)
        actual_bank_kwh = total_batteries_calc * battery_kwh
        inverter_battery_kva = actual_bank_kwh * c_rate_factor
        reason_c_rate = "توافقية الليثيوم (0.5C Charging)"
    else:
        c_rate_factor = 0.2  # 0.2C for Lead Acid (Max recommended)
        raw_total_batteries = math.ceil(total_kwh_storage_needed / battery_kwh)
        # Adjust for 48V series strings
        remainder = raw_total_batteries % 4
        if remainder != 0:
            total_batteries_calc = raw_total_batteries + (4 - remainder)
        else:
            total_batteries_calc = raw_total_batteries
        actual_bank_kwh = total_batteries_calc * battery_kwh
        inverter_battery_kva = actual_bank_kwh * c_rate_factor
        reason_c_rate = "توافقية البطاريات السائلة/الجل (0.2C Charging)"

    # Select the larger size
    if inverter_battery_kva > inverter_load_kva:
        inverter_kva = inverter_battery_kva
        inverter_reason = f"تم التكبير ليتوافق مع سعة البطاريات ({reason_c_rate})"
    else:
        inverter_kva = inverter_load_kva
        inverter_reason = "الحجم بناءً على إجمالي الحمل التشغيلي (Load)"

    # Round up to nearest standard size
    inverter_kva_display = math.ceil(inverter_kva * 10) / 10

    # 4. Battery Calculations
    # (Calculations for totals done upstream for Inverter Sizing, re-using values)
    
    if is_lithium_48v:
        # Lithium (Integrated 48V)
        total_batteries = total_batteries_calc
        
        notes_batteries = f"توصيل {total_batteries} وحدات على التوازي"
        batt_desc = f"عدد وحدات الليثيوم ({battery_kwh}kWh/48V)"
        batt_val_desc = f"{total_batteries} وحدة"
        batt_voltage_desc = "48 Volt (Integrated)"
        
    else:
        # Lead Acid (12V blocks)
        total_batteries = total_batteries_calc
        parallel_strings = int(total_batteries / 4)
        
        notes_batteries = f"{parallel_strings} مصفوفة (String) على التوازي، كل مصفوفة 4 بطاريات توالي"
        batt_desc = f"عدد البطاريات ({battery_kwh}kWh/12V)"
        batt_val_desc = f"{int(total_batteries)} بطارية"
        batt_voltage_desc = "48 Volt (4x12V Series)"


    # 5. Solar Panel Calculations
    required_pv_energy_wh = total_daily_energy_wh / SYSTEM_EFFICIENCY
    required_array_watts = required_pv_energy_wh / PEAK_SUN_HOURS
    total_panels = math.ceil(required_array_watts / PANEL_WATT_PEAK)
    
    # Calculate total PV capacity
    total_pv_capacity = total_panels * PANEL_WATT_PEAK
    
    # Calculate Total Area
    total_area_m2 = total_panels * panel_area

    # Display Results
    st.markdown("### النتائج والتوصيات")
    
    results = {
        "العنصر": [
            "حجم الإنفرتر (kVA)",
            batt_desc,
            f"عدد الألواح الشمسية ({PANEL_WATT_PEAK}W)",
            "المساحة المطلوبة للألواح (م²)",
            "نظام البطاريات (Voltage)",
            "الحمل الكلي (Watt)"
        ],
        "القيمة المحسوبة": [
            f"{inverter_kva_display} kVA",
            batt_val_desc,
            f"{total_panels} لوح",
            f"{total_area_m2:.2f} م²",
            batt_voltage_desc,
            f"{load_watts} Watt"
        ],
        "ملاحظات": [
            f"يوصى باختيار أقرب حجم قياسي أكبر ({inverter_reason})",
            notes_batteries,
            f"إجمالي قدرة الألواح: {total_pv_capacity} Watt",
            f"مساحة اللوح الواحد: {panel_area:.2f} م²",
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

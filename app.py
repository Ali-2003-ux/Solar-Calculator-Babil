import streamlit as st
import pandas as pd
import math

# Page Configuration
st.set_page_config(
    page_title="مركز بحوث الطاقة - بابل",
    page_icon="☀️",
    layout="centered"
)

# Custom CSS
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

# Helper function to load image
import os
def load_image(image_path):
    if os.path.exists(image_path):
        return image_path
    return None

# Logos & Header Layout (Centered Title with Logos on sides)
header_col1, header_col2, header_col3 = st.columns([1, 2, 1])

with header_col1:
    uni_logo = load_image("assets/logo_university.png")
    if uni_logo:
        st.image(uni_logo, use_container_width=True)
    else:
        st.info("University Logo")

with header_col2:
    st.markdown("<h1 style='text-align: center; color: #f39c12; margin-bottom: 0;'>حاسبة منظومات الطاقة الشمسية</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #555; margin-top: 0;'>مركز بحوث الطاقة - بابل</h3>", unsafe_allow_html=True)

with header_col3:
    center_logo = load_image("assets/logo_center.png")
    if center_logo:
        st.image(center_logo, use_container_width=True)
    else:
        st.info("Center Logo")

st.markdown("---")

# Inputs: Load & Hours
col1, col2 = st.columns(2)
with col2:
    ampere = st.number_input("الأمبير المطلوب (Ampere)", min_value=1.0, value=5.0, step=0.5)
with col1:
    night_hours = st.number_input("ساعات التشغيل (Hours)", min_value=0.0, max_value=24.0, value=6.0, step=0.5, help="عدد ساعات تشغيل الحمل (يتم الاعتماد عليها كلياً لحساب المنظومة)")

# Phase Selection
phase_type = st.radio(
    "نوع المنظومة (System Phase)",
    ["Single Phase (1 Phase)", "Three Phase (3 Phase)"],
    horizontal=True,
    help="اختر 3 Phase إذا كانت الأحمال موزعة على 3 خطوط (سيتم ضرب القدرة في 3)"
)

# Inputs: Battery
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

# Inputs: Solar Panel Specs (NEW)
st.markdown("---")
st.markdown("### مواصفات الألواح الشمسية (تحليل الكفاءة)")
p_col1, p_col2, p_col3 = st.columns(3)

with p_col3:
    panel_power = st.number_input("قدرة اللوح (Watt)", min_value=100, value=550, step=10)
with p_col2:
    panel_length = st.number_input("طول اللوح (متر)", min_value=1.0, value=2.27, step=0.01)
with p_col1:
    panel_width = st.number_input("عرض اللوح (متر)", min_value=0.5, value=1.13, step=0.01)

# Real-time Efficiency Calculation
panel_area = panel_length * panel_width
if panel_area > 0:
    panel_efficiency = (panel_power / (panel_area * 1000)) * 100
else:
    panel_efficiency = 0

st.caption(f"📊 **كفاءة اللوح المحسوبة:** {panel_efficiency:.2f}%")

# Quality Check
if panel_efficiency > 21:
    st.success("✨ كفاءة ممتازة (Technology: Monocrystalline PERC/N-Type)")
elif panel_efficiency > 19:
    st.info("✅ كفاءة جيدة جداً (Technology: Monocrystalline)")
elif panel_efficiency > 15:
    st.warning("⚠️ كفاءة متوسطة (Technology: Polycrystalline)")
else:
    st.error("❌ كفاءة منخفضة (قد تكون تقنية قديمة)")

# Advanced Settings (Editable Equation Parameters)
with st.sidebar:
    st.header("⚙️ إعدادات المعادلة (متقدم)")
    st.info("يمكنك تعديل ثوابت المعادلة من هنا لتناسب موقعك الجغرافي ونوعية الأسلاك.")
    
    PEAK_SUN_HOURS = st.number_input(
        "ساعات ذروة الشمس (Sun Hours)", 
        min_value=2.0, max_value=12.0, value=5.0, step=0.1,
        help="المعدل اليومي لساعات السطوع الشمسي القوي (في العراق عادة 5 ساعات)"
    )
    
    SYSTEM_EFFICIENCY_PCT = st.number_input(
        "كفاءة النظام (System Efficiency %)", 
        min_value=50, max_value=100, value=80, step=5,
        help="نسبة الطاقة الفعلية المستفادة بعد طرح الفواقد (حرارة، أسلاك، غبار)"
    )
    SYSTEM_EFFICIENCY = SYSTEM_EFFICIENCY_PCT / 100.0
    
    INVERTER_SAFETY_FACTOR = st.number_input(
        "معامل أمان الإنفرتر", 
        min_value=1.0, max_value=2.0, value=1.25, step=0.05,
        help="زيادة حجم الإنفرتر لتحمل التيارات اللحظية (Surge)"
    )
    
    st.markdown("---")
    st.markdown("Developed by: Energy Research Center")

# Calculate Button
if st.button("احسب متطلبات المنظومة"):
    # Constants
    VOLTAGE = 220
    BATTERY_SYSTEM_VOLTAGE = 48
    
    # Determine DoD and voltage based on battery selection
    is_lithium_48v = "48V" in battery_type
    if is_lithium_48v:
        BATTERY_DOD = 0.8
    else:
        BATTERY_DOD = 0.5
        
    PANEL_WATT_PEAK = panel_power
    # PEAK_SUN_HOURS & SYSTEM_EFFICIENCY came from Sidebar now

    # 1. Load Calculations
    if "Three Phase" in phase_type:
        # For 3-Phase, Total Power = 3 * V_phase * I_phase (assuming user inputs Amp per phase)
        load_watts = ampere * VOLTAGE * 3
        system_type_str = "Three Phase (3PH)"
    else:
        # For 1-Phase
        load_watts = ampere * VOLTAGE
        system_type_str = "Single Phase (1PH)"
    
    # 2. Energy Calculations
    # Based on user request: Ignore daytime direct consumption overlap.
    # Calculate Total Energy based on the input hours (Night/Total Operation hours)
    energy_total_wh = load_watts * night_hours
    total_daily_energy_wh = energy_total_wh

    # 3. Inverter Calculation (C-Rate Method)
    inverter_load_kva = (load_watts * INVERTER_SAFETY_FACTOR) / 1000
    
    # Battery Capacity for C-Rate
    required_battery_capacity_wh = energy_total_wh / BATTERY_DOD
    total_kwh_storage_needed = required_battery_capacity_wh / 1000
    
    if is_lithium_48v:
        c_rate_factor = 0.5
        total_batteries_calc = math.ceil(total_kwh_storage_needed / battery_kwh)
        actual_bank_kwh = total_batteries_calc * battery_kwh
        inverter_battery_kva = actual_bank_kwh * c_rate_factor
        reason_c_rate = "توافقية الليثيوم (0.5C Charging)"
        
        # Battery Display Logic
        total_batteries = total_batteries_calc
        notes_batteries = f"توصيل {total_batteries} وحدات على التوازي"
        batt_desc = f"عدد وحدات الليثيوم ({battery_kwh}kWh/48V)"
        batt_val_desc = f"{total_batteries} وحدة"
        batt_voltage_desc = "48 Volt (Integrated)"
        
    else:
        c_rate_factor = 0.2
        raw_total_batteries = math.ceil(total_kwh_storage_needed / battery_kwh)
        remainder = raw_total_batteries % 4
        if remainder != 0:
            total_batteries_calc = raw_total_batteries + (4 - remainder)
        else:
            total_batteries_calc = raw_total_batteries
            
        actual_bank_kwh = total_batteries_calc * battery_kwh
        inverter_battery_kva = actual_bank_kwh * c_rate_factor
        reason_c_rate = "توافقية البطاريات السائلة/الجل (0.2C Charging)"
        
        # Battery Display Logic
        total_batteries = total_batteries_calc
        parallel_strings = int(total_batteries / 4)
        notes_batteries = f"{parallel_strings} مصفوفة (String) على التوازي، كل مصفوفة 4 بطاريات توالي"
        batt_desc = f"عدد البطاريات ({battery_kwh}kWh/12V)"
        batt_val_desc = f"{int(total_batteries)} بطارية"
        batt_voltage_desc = "48 Volt (4x12V Series)"

    # Select Inverter Size
    if inverter_battery_kva > inverter_load_kva:
        inverter_kva = inverter_battery_kva
        inverter_reason = f"تم التكبير ليتوافق مع سعة البطاريات ({reason_c_rate})"
    else:
        inverter_kva = inverter_load_kva
        inverter_reason = "الحجم بناءً على إجمالي الحمل التشغيلي (Load)"

    inverter_kva_display = math.ceil(inverter_kva * 10) / 10

    # 4. Solar Panel Calculations
    required_pv_energy_wh = total_daily_energy_wh / SYSTEM_EFFICIENCY
    required_array_watts = required_pv_energy_wh / PEAK_SUN_HOURS
    total_panels = math.ceil(required_array_watts / PANEL_WATT_PEAK)
    total_pv_capacity = total_panels * PANEL_WATT_PEAK
    total_area_m2 = total_panels * panel_area

    # Display Results
    st.markdown("### النتائج والتوصيات")
    results = {
        "العنصر": [
            f"حجم الإنفرتر ({system_type_str})",
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
            "عند جهد 220 فولت (فيز واحد) أو 380 فولت (3 فيز)"
        ]
    }
    
    df = pd.DataFrame(results)
    st.table(df)
    
    st.info(f"""
    **تفاصيل سريعة:**
    - استهلاك الطاقة اليومي (المعتمد): {total_daily_energy_wh/1000:.2f} كيلو واط ساعة.
    - سعة البطاريات المطلوبة: {required_battery_capacity_wh/1000:.2f} كيلو واط ساعة.
    """)
    
    # Mathematical Formulas Section
    with st.expander("📚 كيف تم الحساب؟ (المعادلات الرياضية)"):
        st.markdown("""
        ### 1. حساب كفاءة الألواح (Panel Efficiency)
        $$
        \\eta = \\left( \\frac{P_{max}}{Area \\times 1000} \\right) \\times 100
        $$
        حيث:
        - $P_{max}$: قدرة اللوح (وات).
        - $Area$: مساحة اللوح (متر مربع).
        - $1000$: شدة الإشعاع القياسية ($W/m^2$).

        ### 2. حجم منظومة البطاريات (Battery Bank)
        $$
        Capacity_{kWh} = \\frac{Energy_{night}}{DoD}
        $$
        حيث:
        - $DoD$: عمق التفريغ (80% لليثيوم، 50% للرصاص).

        ### 3. حجم الإنفرتر (Inverter Sizing)
        يتم اختيار الحجم الأكبر بين القيمتين:
        $$
        Size_{Load} = \\frac{Total\\_Watt \\times Safety\\_Factor}{1000}
        $$
        $$
        Size_{Charging} = Battery\\_kWh \\times C\\_Rate
        $$
        حيث:
        - $C\\_Rate$: 0.5 لليثيوم، 0.2 للرصاص.

        ### 4. عدد الألواح الشمسية (PV Array)
        $$
        N_{Panels} = \\frac{Daily\\_Energy}{(Sun\\_Hours \\times Panel\\_Watt \\times System\\_Eff)}
        $$
        **تطبيق بالأرقام الحالية:**
        - الاستهلاك اليومي = {total_daily_energy_wh:.0f} وات/ساعة
        - إنتاج اللوح الواحد = {PANEL_WATT_PEAK} × {PEAK_SUN_HOURS} × {SYSTEM_EFFICIENCY} = {PANEL_WATT_PEAK * PEAK_SUN_HOURS * SYSTEM_EFFICIENCY:.0f} وات/ساعة
        - عدد الألواح = {total_daily_energy_wh:.0f} ÷ {PANEL_WATT_PEAK * PEAK_SUN_HOURS * SYSTEM_EFFICIENCY:.0f} = **{total_daily_energy_wh / (PANEL_WATT_PEAK * PEAK_SUN_HOURS * SYSTEM_EFFICIENCY):.2f}**
        (يتم جبر الرقم للأعلى ليصبح **{total_panels}** لوح)
        حيث أن القيم المستخدمة حالياً هي:
        - **Sun_Hours**: {PEAK_SUN_HOURS} ساعات
        - **System_Eff**: {SYSTEM_EFFICIENCY:.2f} ({SYSTEM_EFFICIENCY*100}%)
        
        ويمكنك تعديل هذه القيم من القائمة الجانبية (⚙️) للحصول على "قراءة صحيحة" تناسب ظروفك الخاصة.
        """)

else:
    st.markdown("""
    <div class="result-box">
        قم بإدخال البيانات أعلاه ثم اضغط على زر "احسب" لعرض النتائج
    </div>
    """, unsafe_allow_html=True)

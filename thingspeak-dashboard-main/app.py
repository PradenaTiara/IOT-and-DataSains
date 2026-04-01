import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import pytz
import streamlit as st

# === CUSTOM STYLE ===
# Tambahkan font Poppins via Google Fonts + CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Poppins', sans-serif;
    }
    </style>
    """, unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Buat seluruh page tanpa margin/padding */
    body, .block-container {
        margin: 0;
        padding: 0;
        max-width: 100%;
    }

    .main { background-color: #f4f9f4; }
    .block-container { padding-top: 1rem; padding-bottom: 3rem; padding-left: 10rem;padding-right: 10rem;}
    .metric-box {
        border-radius: 12px;
        padding: 20px;
        background-color: #e6f4ea;
        border: 1px solid #cce3d6;
        text-align: center;
        margin-bottom: 15px;
    }
    .metric-title {
        font-weight: bold;
        font-size: 16px;
    }
    .metric-value {
        font-size: 26px;
    }
    .element-container:has(.stColumns) > div {
        gap: 2rem !important;
    }
    </style>
""", unsafe_allow_html=True)

# === KONFIGURASI CHANNEL ===
CHANNEL_ID = "2993969"
READ_API_KEY = "AYQ9SIZ6BKQV310B"
CHANNEL_LAT = -7.328
CHANNEL_LON = 110.508

FIELD_NAMES = {
    'field1': "Kelembaban Tanah 1",
    'field2': "Kelembaban Tanah 2",
    'field3': "Status Pompa 1",
    'field4': "Status Pompa 2",
    'field5': "Water Level 1",
    'field6': "Water Level 2",
    'field7': "Suhu (°C)",
    'field8': "Kualitas Udara"
}

@st.cache_data(ttl=60)
def get_thingspeak_data(channel_id, api_key, results=100):
    url = f"https://api.thingspeak.com/channels/{channel_id}/feeds.json?api_key={api_key}&results={results}"
    response = requests.get(url)
    if response.status_code == 200:
        feeds = response.json().get('feeds', [])
        if not feeds:
            return pd.DataFrame()
        df = pd.DataFrame(feeds)
        df['created_at'] = pd.to_datetime(df['created_at'], utc=True)
        for field in FIELD_NAMES:
            df[field] = pd.to_numeric(df[field], errors='coerce')
        return df
    return pd.DataFrame()

# === AMBIL DATA ===
data = get_thingspeak_data(CHANNEL_ID, READ_API_KEY)

if data.empty:
    st.warning("⚠️ Gagal mengambil data dari ThingSpeak. Pastikan ESP32 mengirim data.")
else:
    latest = data.iloc[-1]
    wib = pytz.timezone("Asia/Jakarta")
    last_time = latest['created_at'].tz_convert(wib)
    st.markdown("<h1 class='center-title' style='text-align:center'>Smart Farming Dashboard</h1>", unsafe_allow_html=True)
    st.markdown(
        """
        <p style='text-align:center; font-size:18px; margin-top:-10px;'>
        <br>Sistem pemantauan dan visualisasi data sensor pertanian berbasis IoT secara real-time untuk meningkatkan efisiensi irigasi, pemeliharaan tanaman, dan kualitas lingkungan tanam. 
        Dashboard ini menyediakan informasi menyeluruh mengenai kelembaban tanah, suhu, kualitas udara, serta status pompa dan level air guna membantu petani dalam pengambilan keputusan berbasis data.
        <br><br><br><br></p>
        """,
        unsafe_allow_html=True
    )

    # === KELEMBABAN TANAH ===
    st.markdown("## 🌱 Kelembaban Tanah")
    col_k1, col_k2 = st.columns([1, 1])
    with col_k1:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest['field1'],
            gauge={'axis': {'range': [0, 4095]}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=data['created_at'], y=data['field1'], mode='lines+markers'))
        fig_line.update_layout(title="Kelembaban Tanah 1", xaxis_title="Waktu", yaxis_title="Kelembaban", template="plotly_white", height=300)
        fig_line.update_yaxes(range=[0, 4095])
        st.plotly_chart(fig_line, use_container_width=True)
    with col_k2:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest['field2'],
            gauge={'axis': {'range': [0, 4095]}},
            domain={'x': [0, 1], 'y': [0, 1]}
        ))
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=data['created_at'], y=data['field2'], mode='lines+markers'))
        fig_line.update_layout(title="Kelembaban Tanah 2", xaxis_title="Waktu", yaxis_title="Kelembaban", template="plotly_white", height=300)
        fig_line.update_yaxes(range=[0, 4095])
        st.plotly_chart(fig_line, use_container_width=True)


    # === STATUS POMPA DENGAN LAMPU ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🚿 Status Pompa")
    st.divider()
    col3, col4 = st.columns(2)
    with col3:
        status1 = "🟢 Aktif" if latest['field3'] == 1 else "🔴 Nonaktif"
        st.markdown(f"""<div class="metric-value"><div class="metric-title">Pompa 1</div>
        <div class="metric-value">{status1}</div></div>""", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['created_at'], y=data['field3'], mode='lines+markers'))
        fig.update_layout(title="Status Pompa 1", xaxis_title="Waktu", yaxis_title="Status", template='plotly_white', height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col4:
        status2 = "🟢 Aktif" if latest['field4'] == 1 else "🔴 Nonaktif"
        st.markdown(f"""<div class="metric-value"><div class="metric-title">Pompa 2</div>
        <div class="metric-value">{status2}</div></div>""", unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['created_at'], y=data['field4'], mode='lines+markers'))
        fig.update_layout(title="Status Pompa 2", xaxis_title="Waktu", yaxis_title="Status", template='plotly_white', height=300)
        st.plotly_chart(fig, use_container_width=True)

    # === WATER LEVEL MONITORING ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 💧 Water Level Monitoring")
    st.divider()
    col5, col6 = st.columns(2)
    with col5:
        status_w1 = "🟢 Aman" if latest['field5'] < 80 else "🔴 Tinggi"
        st.markdown(f"""<div class="metric-value"><div class="metric-title">Water Level 1</div>
            <div class="metric-value">{status_w1} ({latest['field5']})</div></div>""", unsafe_allow_html=True)
    with col6:
        status_w2 = "🟢 Aman" if latest['field6'] < 80 else "🔴 Tinggi"
        st.markdown(f"""<div class="metric-value"><div class="metric-title">Water Level 2</div>
            <div class="metric-value">{status_w2} ({latest['field6']})</div></div>""", unsafe_allow_html=True)

    # === HISTORI GRAFIK WATER LEVEL ===
    col7, col8 = st.columns(2)
    with col7:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['created_at'], y=data['field5'], mode='lines+markers'))
        fig.update_layout(title="Grafik Water Level 1", xaxis_title="Waktu", yaxis_title="Level", template='plotly_white', height=300)
        st.plotly_chart(fig, use_container_width=True)
    with col8:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['created_at'], y=data['field6'], mode='lines+markers'))
        fig.update_layout(title="Grafik Water Level 2", xaxis_title="Waktu", yaxis_title="Level", template='plotly_white', height=300)
        st.plotly_chart(fig, use_container_width=True)

    # === SUHU DHT22 ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🌡️ Suhu (DHT22)")
    st.divider()
    st.markdown(f"""<div class='metric-card'><div class='metric-title'>Suhu Saat Ini</div><div class='metric-value'>{latest['field7']} °C</div></div>""", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['created_at'], y=data['field7'], mode='lines+markers', name='Suhu'))
    fig.update_layout(title="Suhu (°C)", xaxis_title="Waktu", yaxis_title="Suhu", template="plotly_white", height=300)
    st.plotly_chart(fig, use_container_width=True)

    # === GAS MQ135 ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 💨 Kualitas Udara")
    st.divider()
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""<div class='metric-card'><div class='metric-title'>Gas MQ135</div><div class='metric-value'>{latest['field8']}</div></div>""", unsafe_allow_html=True)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data['created_at'], y=data['field8'], mode='lines+markers'))
    fig.update_layout(title="Kualitas Udara", xaxis_title="Waktu", yaxis_title="MQ135", template='plotly_white', height=300)
    st.plotly_chart(fig, use_container_width=True)

    # === TABEL DATA TERBARU ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 📋 Data Terbaru")
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(data.tail(10).rename(columns=FIELD_NAMES), use_container_width=True)

    # === LOKASI CHANNEL & WAKTU ===
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("## 🧭 Informasi Lokasi Channel")
    st.markdown("<br>", unsafe_allow_html=True)
    #st.divider()
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown(f"""
        **📍 Koordinat Lokasi:**
        - Latitude: `{CHANNEL_LAT}`
        - Longitude: `{CHANNEL_LON}`
        """)
        st.success(f"📅 Update Terakhir: **{last_time.strftime('%d %B %Y %H:%M:%S WIB')}**")
    with col2:
        st.markdown("<iframe width='100%' height='400' frameborder='0' scrolling='no' marginheight='0' marginwidth='0' src='https://maps.google.com/maps?q=-7.328,110.508&hl=id&z=15&output=embed'></iframe>", unsafe_allow_html=True)


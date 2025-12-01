import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# 1. PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Kalkulator Kelayakan Produksi",
    page_icon="🌶️",
    layout="wide"
)

st.title("🌶️ Dashboard Kelayakan Produksi Sambal")
st.markdown("### Hitung biaya produksi, HPP, BEP, margin, dan kelayakan usaha secara otomatis.")

# ============================================================
# 2. INPUT – PRODUKSI
# ============================================================
st.sidebar.header("⚙️ Parameter Produksi")

output_botol = st.sidebar.number_input("Jumlah Botol Jadi per Batch", 5, 300, 20)
harga_jual = st.sidebar.number_input("Harga Jual per Botol (Rp)", 1000, 200000, 20000)

st.sidebar.markdown("---")
st.sidebar.header("🥣 Input Bahan Baku")

st.sidebar.caption("Tambahkan daftar bahan baku yang diperlukan.")
num_items = st.sidebar.number_input("Jumlah Jenis Bahan", 1, 20, 5)

bahan_list = []
harga_list = []
qty_list = []

for i in range(num_items):
    col1, col2, col3 = st.sidebar.columns([2, 1, 1])
    bahan = col1.text_input(f"Nama Bahan #{i+1}", f"Bahan {i+1}")
    harga = col2.number_input(f"Harga/kg atau unit", 0, 10_000_000, 10000, key=f"harga{i}")
    qty = col3.number_input(f"Jumlah", 0.0, 1000.0, 1.0, key=f"qty{i}")
    bahan_list.append(bahan)
    harga_list.append(harga)
    qty_list.append(qty)

# Bahan Table
df_bahan = pd.DataFrame({
    "Bahan": bahan_list,
    "Harga per Unit (Rp)": harga_list,
    "Jumlah": qty_list,
    "Total Biaya": np.array(harga_list) * np.array(qty_list)
})

# ============================================================
# 3. INPUT – BIAYA OPERASIONAL
# ============================================================
st.sidebar.markdown("---")
st.sidebar.header("👷‍♀️ Biaya Operasional")

tenaga_kerja = st.sidebar.number_input("Upah Tenaga Kerja (Rp)", 0, 5000000, 30000)
overhead = st.sidebar.number_input("Overhead (gas, listrik, penyusutan) (Rp)", 0, 5000000, 10000)
kemasan = st.sidebar.number_input("Biaya Kemasan per Botol (Rp)", 0, 50000, 2000)

total_operasional = tenaga_kerja + overhead + (kemasan * output_botol)

# ============================================================
# 4. PERHITUNGAN DASAR
# ============================================================
total_bahan = df_bahan["Total Biaya"].sum()
total_biaya = total_bahan + total_operasional
hpp_per_unit = total_biaya / output_botol
total_omzet = output_botol * harga_jual
keuntungan_bersih = total_omzet - total_biaya
margin_percent = (keuntungan_bersih / total_omzet) * 100 if total_omzet > 0 else 0
rc_ratio = total_omzet / total_biaya if total_biaya > 0 else 0
bep_unit = total_biaya / harga_jual if harga_jual > 0 else 0
bep_rupiah = bep_unit * harga_jual

# MARKUP IDEAL
markup_30 = hpp_per_unit * 1.30
markup_40 = hpp_per_unit * 1.40
markup_50 = hpp_per_unit * 1.50

# ============================================================
# 5. OUTPUT HASIL – CARDS
# ============================================================
st.subheader("📊 Ringkasan Hasil Produksi")

colA, colB, colC, colD = st.columns(4)

colA.metric("Total Biaya Produksi", f"Rp {total_biaya:,.0f}")
colB.metric("HPP per Botol", f"Rp {hpp_per_unit:,.0f}")
colC.metric("Keuntungan per Batch", f"Rp {keuntungan_bersih:,.0f}")
colD.metric("Margin (%)", f"{margin_percent:.1f}%")

colE, colF = st.columns(2)
colE.metric("R/C Ratio", f"{rc_ratio:.2f}")
colF.metric("BEP (Unit)", f"{bep_unit:.1f} botol")

# ============================================================
# 6. TABEL BAHAN
# ============================================================
st.subheader("📋 Detail Bahan Baku & Biaya")
st.dataframe(df_bahan, use_container_width=True)

# ============================================================
# 7. CHART – KOMPOSISI BIAYA
# ============================================================
st.subheader("📊 Komposisi Biaya Produksi")

pie_df = pd.DataFrame({
    "Kategori": ["Total Bahan", "Tenaga Kerja", "Overhead", "Kemasan"],
    "Biaya": [total_bahan, tenaga_kerja, overhead, kemasan * output_botol]
})

fig = px.pie(pie_df, values="Biaya", names="Kategori", title="Persentase Komponen Biaya")
st.plotly_chart(fig, use_container_width=True)

# ============================================================
# 8. ANALISIS MARKUP IDEAL
# ============================================================
st.subheader("💰 Harga Jual yang Disarankan Berdasarkan Markup")

st.markdown(f"""
- **Markup 30%** → Rp **{markup_30:,.0f}**
- **Markup 40%** → Rp **{markup_40:,.0f}**
- **Markup 50%** → Rp **{markup_50:,.0f}**

Harga jualmu saat ini: **Rp {harga_jual:,.0f}**
""")

# ============================================================
# 9. SENSITIVITAS HARGA JUAL
# ============================================================
st.subheader("📈 Simulasi Sensitivitas Harga Jual terhadap Keuntungan")

prices = np.linspace(hpp_per_unit, hpp_per_unit * 2.5, 20)
profits = (prices * output_botol) - total_biaya

df_sim = pd.DataFrame({
    "Harga Jual": prices,
    "Keuntungan": profits
})

fig2 = px.line(df_sim, x="Harga Jual", y="Keuntungan", title="Kurva Sensitivitas Profit")
st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# 10. KESIMPULAN KELAYAKAN
# ============================================================
st.subheader("📌 Kesimpulan Kelayakan")

if rc_ratio > 1:
    st.success("**LAYAK** — R/C > 1 ✔️ Produksi dapat dilanjutkan.")
else:
    st.error("**TIDAK LAYAK** — R/C < 1 ❌ Perlu revisi biaya atau harga jual.")


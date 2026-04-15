import pandas as pd
import matplotlib.pyplot as plt

# ---- 1. Veriyi oku ----
df = pd.read_csv("metal_tracks_with_audio.csv")

# mode sütununu emin olmak için sayısala çevir (0 / 1)
df["mode"] = pd.to_numeric(df["mode"], errors="coerce")

# Sadece 0 ve 1 olan satırları kullan
df_mode = df[df["mode"].isin([0, 1])].copy()

# ---- 2. Major / Minor sayıları ve oranları ----
# Toplam şarkı sayısı
total_counts = df_mode.groupby("main_genre")["mode"].count()

# Major (1) şarkı sayısı
major_counts = df_mode[df_mode["mode"] == 1].groupby("main_genre")["mode"].count()

# Minor (0) şarkı sayısı
minor_counts = df_mode[df_mode["mode"] == 0].groupby("main_genre")["mode"].count()

# Tüm genre'lar için indexleri hizala (eksik olanlar için 0 doldur)
major_counts = major_counts.reindex(total_counts.index, fill_value=0)
minor_counts = minor_counts.reindex(total_counts.index, fill_value=0)

# Oranlar
major_ratio = major_counts / (major_counts + minor_counts)
minor_ratio = 1 - major_ratio

# Hepsini tek bir tabloya koymak istersen:
mode_table = pd.DataFrame({
    "total_tracks": total_counts,
    "major_count": major_counts,
    "minor_count": minor_counts,
    "major_ratio": major_ratio,
    "minor_ratio": minor_ratio
}).sort_values("major_ratio", ascending=False)

print("Mode (Major/Minor) statistics per main genre:")
print(mode_table)

# ---- 3. Grafik 1: Major / Minor Count (Grouped Bar Chart) ----
plt.figure(figsize=(12, 6))

x = range(len(mode_table))
width = 0.4

plt.bar([i - width/2 for i in x], mode_table["major_count"], width=width, label="Major (mode = 1)")
plt.bar([i + width/2 for i in x], mode_table["minor_count"], width=width, label="Minor (mode = 0)")

plt.xticks(x, mode_table.index, rotation=90)
plt.ylabel("Number of Tracks")
plt.title("Major vs Minor Track Counts by Main Genre")
plt.legend()
plt.tight_layout()
plt.show()

# ---- 4. Grafik 2: Major / Minor Ratio (Stacked Bar Chart) ----
plt.figure(figsize=(12, 6))

plt.bar(mode_table.index, mode_table["minor_ratio"], label="Minor (mode = 0)")
plt.bar(mode_table.index, mode_table["major_ratio"],
        bottom=mode_table["minor_ratio"], label="Major (mode = 1)")

plt.xticks(rotation=90)
plt.ylabel("Proportion of Tracks")
plt.title("Proportion of Major vs Minor Tracks by Main Genre")
plt.ylim(0, 1)
plt.legend()
plt.tight_layout()
plt.show()

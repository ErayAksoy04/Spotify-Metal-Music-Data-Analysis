import pandas as pd
import matplotlib.pyplot as plt

# --- 1. Veri setini oku ---
df = pd.read_csv("metal_tracks_with_audio.csv")

# --- 2. Valence sütununu numerik hale getir ---
# (Her ihtimale karşı string yapıp, virgül vs. varsa noktaya çeviriyoruz)
df["valence"] = (
    df["valence"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)
df["valence"] = pd.to_numeric(df["valence"], errors="coerce")

# İstersen kontrol için:
# print(df["valence"].dtype)  # float64 olmalı

# --- 3. Her main_genre için istatistikleri hesapla ---
genre_valence = (
    df.groupby("main_genre")["valence"]
      .agg(["count", "mean", "median", "std"])
      .sort_values("mean", ascending=False)
)

print("Valence Statistics Per Main Genre:")
print(genre_valence)

# --- 4. Grafik 1: Mean Valence Bar Plot ---
plt.figure(figsize=(12, 6))
plt.bar(genre_valence.index, genre_valence["mean"])
plt.xticks(rotation=90)
plt.ylabel("Mean Valence")
plt.title("Mean Valence by Main Genre")
plt.tight_layout()
plt.show()

# --- 5. Grafik 2: Valence Boxplot Per Genre ---
plt.figure(figsize=(14, 7))
df.boxplot(column="valence", by="main_genre", rot=90)
plt.title("Valence Distribution by Genre")
plt.suptitle("")  # ekstra üst başlığı kaldır
plt.ylabel("Valence")
plt.tight_layout()
plt.show()

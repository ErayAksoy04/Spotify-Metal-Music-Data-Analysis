import pandas as pd
import matplotlib.pyplot as plt

# Dosyayı oku
df = pd.read_csv("metal_tracks_with_audio.csv")

# Sadece popularity analizini yapmak için:
genre_popularity = df.groupby("main_genre")["valence"].agg(
    ["count", "mean", "median", "std"]
).sort_values("mean", ascending=False)

print("Popularity Statistics Per Main Genre:")
print(genre_popularity)

# ---- Grafik 1: Mean Popularity Bar Plot ----
plt.figure(figsize=(12, 6))
plt.bar(genre_popularity.index, genre_popularity["mean"])
plt.xticks(rotation=90)
plt.ylabel("Mean Popularity")
plt.title("Mean Popularity by Main Genre")
plt.tight_layout()
plt.show()

# ---- Grafik 2: Popularity Boxplot Per Genre ----
plt.figure(figsize=(14, 7))
df.boxplot(column="popularity", by="main_genre", rot=90)
plt.title("Popularity Distribution by Genre")
plt.suptitle("")  # Mendix'teki ekstra başlığı kaldırır
plt.ylabel("Popularity")
plt.tight_layout()
plt.show()

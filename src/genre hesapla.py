import pandas as pd

# Veri setini oku
df = pd.read_csv("metal_tracks_with_audio.csv")

# Her main genre ve subgenre kombinasyonunun kaç şarkısı olduğunu hesapla
genre_table = (
    df.groupby(["main_genre", "sub_genre"])
      .size()
      .reset_index(name="track_count")
      .sort_values(["main_genre", "sub_genre"])
)

print(genre_table)
# Ek olarak istersen CSV çıktısı da verebilirsin:
# genre_table.to_csv("genre_subgenre_table.csv", index=False)

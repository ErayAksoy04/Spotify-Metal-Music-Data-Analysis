import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import math
import time

# ==============================
#  Spotify API Kimlik Bilgilerin
# ==============================
CLIENT_ID = "1059db9faca445a5ba06fd78b78cee13"
CLIENT_SECRET = "d2ed39a90706443e920e0b42f4f03597"

# API bağlantısı
sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET
    )
)

# ==============================
#  Tür Listesi
# ==============================
genres = []
with open("metal_genres.txt", "r", encoding="utf-8") as f:
    genres = [line.strip() for line in f.readlines() if line.strip()]

# ==============================
#  Parametreler
# ==============================
N_MIN = 300
N_MAX = 1500
TOTAL_TARGET = 60000

# ==============================
#  Veri Çekme Fonksiyonları
# ==============================
def get_artist_count(genre):
    """Türdeki sanatçı sayısını döndürür (max 1000)."""
    count = 0
    for offset in range(0, 1000, 50):
        results = sp.search(q=f'genre:"{genre}"', type='artist', limit=50, offset=offset)
        items = results['artists']['items']
        if not items:
            break
        count += len(items)
        time.sleep(0.2)
    return count

def get_track_stats(genre):
    """Türdeki toplam şarkı sayısını ve ortalama popülerliği döndürür."""
    total_tracks, total_popularity = 0, 0
    for offset in range(0, 1000, 50):
        results = sp.search(q=f'genre:"{genre}"', type='track', limit=50, offset=offset)
        tracks = results['tracks']['items']
        if not tracks:
            break
        total_tracks += len(tracks)
        total_popularity += sum(t['popularity'] for t in tracks)
        time.sleep(0.2)

    avg_pop = (total_popularity / total_tracks) if total_tracks > 0 else 0
    return total_tracks, avg_pop

# ==============================
#  Ana Döngü
# ==============================
data = []
for g in genres:
    print(f" {g} türü analiz ediliyor...")
    try:
        A = get_artist_count(g)
        T, P = get_track_stats(g)
        data.append({"genre": g, "artists": A, "tracks": T, "popularity": P})
    except Exception as e:
        print(f"Hata ({g}):", e)
        data.append({"genre": g, "artists": 0, "tracks": 0, "popularity": 0})

df = pd.DataFrame(data)

# ==============================
#  Logaritmik Skor Hesabı
# ==============================
df["S_g"] = (
    math.log1p(1) +  # dummy base to avoid zero
    df["tracks"].apply(lambda x: math.log1p(x)) +
    0.5 * df["artists"].apply(lambda x: math.log1p(x)) +
    0.1 * df["popularity"]
)

# Normalize ve örnek sayısını hesapla
sum_S = df["S_g"].sum()
df["N_g_raw"] = TOTAL_TARGET * (df["S_g"] / sum_S)
df["N_g"] = df["N_g_raw"].apply(lambda x: min(max(round(x), N_MIN), N_MAX))

# ==============================
#  Sonuçları Kaydet
# ==============================
df.to_csv("genre_sampling_plan_v2.csv", index=False, encoding="utf-8")
print(" İşlem tamamlandı. 'genre_sampling_plan_v2.csv' dosyası oluşturuldu.")
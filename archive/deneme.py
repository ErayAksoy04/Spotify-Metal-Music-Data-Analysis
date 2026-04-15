import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from time import sleep

#  Spotify OAuth kimlik bilgileri
CLIENT_ID = "1059db9faca445a5ba06fd78b78cee13"
CLIENT_SECRET = "d2ed39a90706443e920e0b42f4f03597"
REDIRECT_URI = "https://127.0.0.1:8888/callback"

#  Yetki alanı (scope) - yalnızca genel verilere erişim
scope = "user-read-private user-read-email"

# Spotify OAuth kimlik doğrulama
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET,
    redirect_uri=REDIRECT_URI,
    scope=scope,
    open_browser=True
))

#  Veriyi oku (.txt veya .csv)
df = pd.read_csv("your_file.csv", sep=",", header=0)

#  Sonuçları ve hataları kaydetmek için listeler
results = []
failed_artists = []

for idx, row in df.iterrows():
    main_genre = row['main_genre']
    sub_genre = row['sub_genre']
    artist_name = row['artist_name']

    try:
        #  Sanatçıyı bul
        search = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        if not search['artists']['items']:
            print(f" Sanatçı bulunamadı: {artist_name}")
            failed_artists.append(artist_name)
            continue

        artist_id = search['artists']['items'][0]['id']

        #  En popüler 20 şarkı
        top_tracks = sp.artist_top_tracks(artist_id, country='US')['tracks'][:20]

        for track in top_tracks:
            track_id = track['id']
            track_name = track['name']
            popularity = track['popularity']

            # 🎚 Audio özellikleri
            try:
                features = sp.audio_features([track_id])[0]
                if features:
                    results.append({
                        "main_genre": main_genre,
                        "sub_genre": sub_genre,
                        "artist_name": artist_name,
                        "track_name": track_name,
                        "track_id": track_id,
                        "popularity": popularity,
                        "tempo": features['tempo'],
                        "energy": features['energy'],
                        "danceability": features['danceability'],
                        "valence": features['valence'],
                        "loudness": features['loudness'],
                        "acousticness": features['acousticness'],
                        "instrumentalness": features['instrumentalness'],
                        "speechiness": features['speechiness']
                    })
            except Exception as fe:
                print(f" Audio Feature hatası ({artist_name} - {track_name}): {fe}")
                continue

        print(f" {artist_name} işlendi ({len(top_tracks)} şarkı).")
        sleep(1)  # API yükünü azaltmak için

    except Exception as e:
        print(f" Genel hata ({artist_name}): {e}")
        failed_artists.append(artist_name)
        sleep(2)

#  Sonuçları kaydet
output_df = pd.DataFrame(results)
output_df.to_csv("spotify_metal_audio_features.csv", index=False, encoding="utf-8-sig")

#  Başarısız sanatçı listesi
with open("failed_artists.txt", "w", encoding="utf-8") as f:
    for artist in failed_artists:
        f.write(f"{artist}\n")

print(" Veri çekimi tamamlandı. Başarısız sanatçılar failed_artists.txt dosyasına kaydedildi.")

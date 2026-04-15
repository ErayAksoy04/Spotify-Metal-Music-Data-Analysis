import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd
import time

#  Spotify API Kimlik Bilgileri
CLIENT_ID = "1059db9faca445a5ba06fd78b78cee13"
CLIENT_SECRET = "d2ed39a90706443e920e0b42f4f03597"

# Spotify bağlantısı
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

#  Dosyayı oku (örneğin 'metal_artists.txt' veya 'metal_artists.csv')
input_file = "your_file.csv"  # veya .csv
df = pd.read_csv(input_file)

# Çıktı verileri
results = []

#  Her satır için: sanatçı ID’sini bul, sonra top 20 şarkısını çek
for index, row in df.iterrows():
    main_genre = row['main_genre']
    sub_genre = row['sub_genre']
    artist_name = row['artist_name']

    try:
        #  Sanatçıyı ara
        search_results = sp.search(q=f"artist:{artist_name}", type="artist", limit=1)
        if search_results['artists']['items']:
            artist_id = search_results['artists']['items'][0]['id']

            #  En popüler 20 şarkıyı al
            top_tracks = sp.artist_top_tracks(artist_id, country='US')
            for track in top_tracks['tracks'][:20]:
                results.append({
                    "main_genre": main_genre,
                    "sub_genre": sub_genre,
                    "artist_name": artist_name,
                    "track_name": track['name'],
                    "album_name": track['album']['name'],
                    "spotify_track_id": track['id'],
                    "popularity": track['popularity']
                })

            print(f"{artist_name}  {len(top_tracks['tracks'][:20])} track collected.")

        else:
            print(f"{artist_name}  not found on Spotify.")

    except Exception as e:
        print(f"Hata: {artist_name} → {e}")
        time.sleep(1)

#  Sonuçları CSV’ye kaydet
output_file = "artist_top_tracks.csv"
pd.DataFrame(results).to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\nToplam {len(results)} şarkı kaydedildi → {output_file}")

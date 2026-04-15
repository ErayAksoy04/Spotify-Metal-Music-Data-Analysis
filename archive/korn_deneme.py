import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import pandas as pd

# 🔑 Spotify API kimlik bilgilerini gir
CLIENT_ID = "1059db9faca445a5ba06fd78b78cee13"
CLIENT_SECRET = "d2ed39a90706443e920e0b42f4f03597"

# Spotify bağlantısı
sp = spotipy.Spotify(auth_manager=SpotifyClientCredentials(
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
))

# 🎸 Sanatçı bilgilerini buraya gir
main_genre = "Alternative Metal"
sub_genre = "Nu Metal"
artist_name = "Korn"
artist_id = "3RNrq3jvMZxD9ZyoOZbQOD"  # Korn'un Spotify Artist ID'si

# 🔝 En popüler 10 şarkıyı al
top_tracks = sp.artist_top_tracks(artist_id, country='US')

# 🎶 Verileri listeye kaydet
results = []
for track in top_tracks['tracks']:
    results.append({
        "main_genre": main_genre,
        "sub_genre": sub_genre,
        "artist_name": artist_name,
        "track_name": track['name'],
        "album_name": track['album']['name'],
        "spotify_track_id": track['id'],
        "popularity": track['popularity']
    })

# 💾 CSV olarak kaydet
output_file = f"{artist_name.replace(' ', '_')}_top_tracks.csv"
pd.DataFrame(results).to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"✅ {artist_name} için {len(results)} şarkı kaydedildi → {output_file}")

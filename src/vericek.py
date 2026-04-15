import spotipy
from spotipy.oauth2 import  SpotifyClientCredentials

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id="1059db9faca445a5ba06fd78b78cee13",
        client_secret="d2ed39a90706443e920e0b42f4f03597"
    )
)

# Örnek test: Black metal şarkıları çek
results = sp.search(q='genre:"black metal"', type='track', limit=10)
for track in results['tracks']['items']:
    print(track['name'], "-", track['artists'][0]['name'])
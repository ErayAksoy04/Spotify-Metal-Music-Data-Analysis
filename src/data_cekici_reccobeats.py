import pandas as pd
import http.client
import json
import time

#  1. Girdi dosyan (örneğin: "metal_tracks.csv")
input_file = "artist_top_tracks.csv"
output_file = "metal_tracks_with_audio.csv"

# ReccoBeats API bağlantısı
BASE_URL = "api.reccobeats.com"

# 2. Dosyayı oku
df = pd.read_csv(input_file)

# Sonuçlar için liste
audio_features_list = []

# Spotify ID'leri 40'lık gruplara böl
batch_size = 40
track_ids = df['spotify_track_id'].dropna().unique().tolist()

for i in range(0, len(track_ids), batch_size):
    batch = track_ids[i:i + batch_size]
    ids_param = ",".join(batch)

    conn = http.client.HTTPSConnection(BASE_URL)
    headers = {'Accept': 'application/json'}

    try:
        conn.request("GET", f"/v1/audio-features?ids={ids_param}", "", headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")

        response_json = json.loads(data)

        if "content" in response_json:
            for item in response_json["content"]:
                audio_features_list.append(item)

        print(f"Batch {i//batch_size + 1} processed ({len(batch)} tracks).")

    except Exception as e:
        print(f"Hata batch {i//batch_size + 1}: {e}")

    conn.close()
    time.sleep(1)  # API'yı yormamak için küçük gecikme

# 3. Audio feature verilerini DataFrame'e çevir
features_df = pd.DataFrame(audio_features_list)

# href içinden sadece Spotify ID'yi çıkar
features_df['spotify_track_id'] = features_df['href'].str.extract(r'track/([A-Za-z0-9]+)')

# 4. Orijinal dataframe ile birleştir
merged_df = pd.merge(df, features_df, on='spotify_track_id', how='left')

# 5. Yeni CSV olarak kaydet
merged_df.to_csv(output_file, index=False, encoding='utf-8-sig')

print(f"\n Tüm veriler başarıyla işlendi ve kaydedildi: {output_file}")

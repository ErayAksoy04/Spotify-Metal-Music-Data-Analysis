import http.client

conn = http.client.HTTPSConnection("api.reccobeats.com")
payload = ''
headers = {
  'Accept': 'application/json'
}
conn.request("GET", "/v1/audio-features?ids=5LyRtsQLhcXmy50VXhQXXS,3LpHzQU2CZzZJGdUWV79SI,6FUwPb4mGlUDbx42uspXaZ", payload, headers)
res = conn.getresponse()
data = res.read()
print(data.decode("utf-8"))
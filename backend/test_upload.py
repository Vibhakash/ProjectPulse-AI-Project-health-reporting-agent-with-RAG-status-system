import urllib.request
boundary = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
body = f'--{boundary}\r\nContent-Disposition: form-data; name="files"; filename="Test_Suite.zip"\r\nContent-Type: application/zip\r\n\r\n'.encode() + open('Test_Suite.zip', 'rb').read() + f'\r\n--{boundary}--\r\n'.encode()
req = urllib.request.Request('http://localhost:8001/api/analyze', data=body, headers={'Content-Type': f'multipart/form-data; boundary={boundary}'})
r = urllib.request.urlopen(req)
print(r.status, r.read().decode())

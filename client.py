import hashlib
import json
import urllib.request

class HMAC:
    def __init__(self, type, counter, signature, consumer_id):
        self.type = type
        self.counter = counter
        self.signature = signature
        self.consumer_id = consumer_id

class Client:
    def __init__(self, host, key, secret):
        self.host = host
        self.key = key
        self.secret = secret

    def sha256_hash(self, value):
        return hashlib.sha256(value.encode('utf-8')).hexdigest()

    def generate_hmac(self, body):
        consumer_id = self.key
        secret = self.secret
        counter = 1
        content = body if body else "{}"
        prehash = f"{secret}{counter}{content}"
        signature = self.sha256_hash(prehash)
        return HMAC("sha256", counter, signature, consumer_id)

    def _send_request(self, method, route, body=None):
        hmac = self.generate_hmac(body if body else "")
        url = f"{self.host}/integration{route}"
        request = urllib.request.Request(url, method=method)
        request.add_header("Content-Type", "application/json")
        request.add_header("Consumer-ID", hmac.consumer_id)
        request.add_header("Counter", str(hmac.counter))
        request.add_header("Signature-Type", hmac.type)
        request.add_header("Signature", hmac.signature)

        if method == "POST" and body:
            request.data = body.encode('utf-8')

        with urllib.request.urlopen(request) as response:
            return response.read().decode('utf-8')

    def get(self, route):
        return self._send_request("GET", route)

    def post(self, route, body):
        return self._send_request("POST", route, body)

    def devices(self):
        return self.get("/v1/devices")
    
    def enter(self, device_id, name, device_description):
        url = f"/v1/devices/{device_id}/enter"
        body = json.dumps({"name": name, "device_description": device_description})
        return self.post(url, body)

if __name__ == "__main__":
    client = Client("https://DOMAIN", "YOUR_KEY", "YOUR_SECRET")
    print(client.devices())
    print(client.enter("DEVICE_ID", "NAME_TO_SHOW_TO_PATIENT", "META_DATA"))

import json
import base64

def decode(payload: str) -> dict:
	padded = payload + ('=' * divmod(len(payload), 4)[1])
	decoded = base64.urlsafe_b64decode(padded)

	return json.loads(decoded)
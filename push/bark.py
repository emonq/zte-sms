import base64
import logging
import time
import httpx
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
import os


class TokenCache:
    def __init__(self):
        self.gen_token()

    @property
    def token(self):
        if (
            self._cached_token
            and self._cached_time
            and (time.time() - self._cached_time < 20 * 60)
        ):
            return self._cached_token
        return self.gen_token()

    def sign_token(self, header_claims, key_file):
        with open(key_file, "rb") as f:
            private_key = f.read()

        # 加载私钥
        pkey = load_pem_private_key(private_key, password=None)

        # 使用私钥签名
        signature = pkey.sign(header_claims.encode(), ec.ECDSA(hashes.SHA256()))

        # 解码签名
        r, s = decode_dss_signature(signature)
        encoded_signature = (
            base64.urlsafe_b64encode(
                r.to_bytes(32, byteorder="big") + s.to_bytes(32, byteorder="big")
            )
            .decode()
            .rstrip("=")
        )

        return encoded_signature

    def gen_token(self):
        TEAM_ID = "5U8LBRXG3A"
        AUTH_KEY_ID = "LH4T9V5U4R"

        JWT_ISSUE_TIME = int(time.time())
        JWT_HEADER = (
            base64.urlsafe_b64encode(
                f'{{ "alg": "ES256", "kid": "{AUTH_KEY_ID}" }}'.encode()
            )
            .decode()
            .rstrip("=")
        )
        JWT_CLAIMS = (
            base64.urlsafe_b64encode(
                f'{{ "iss": "{TEAM_ID}", "iat": {JWT_ISSUE_TIME} }}'.encode()
            )
            .decode()
            .rstrip("=")
        )
        JWT_HEADER_CLAIMS = f"{JWT_HEADER}.{JWT_CLAIMS}"
        JWT_SIGNED_HEADER_CLAIMS = self.sign_token(
            JWT_HEADER_CLAIMS, os.getenv("TOKEN_KEY_FILE_NAME")
        )
        self._cached_token = f"{JWT_HEADER}.{JWT_CLAIMS}.{JWT_SIGNED_HEADER_CLAIMS}"
        self._cached_time = time.time()


cached_token = TokenCache()


def push(sms, group="短信"):
    from_number = sms["number"]
    content = sms["content"]
    datetime = "20{0}-{1}-{2} {3}:{4}:{5}".format(*sms["date"].split(","))
    APNS_HOST_NAME = "api.push.apple.com"
    TOPIC = "me.fin.bark"

    headers = {
        "apns-topic": TOPIC,
        "apns-push-type": "alert",
        "authorization": f"bearer {cached_token.token}",
    }

    data = {
        "aps": {
            "mutable-content": 1,
            "alert": {
                "title": from_number,
                "subtitle": datetime,
                "body": content,
            },
            "sound": "default",
        },
        "isarchive": "1",
        "group": group,
    }

    # 发送请求
    with httpx.Client(http2=True) as client:
        DEVICE_TOKEN = os.getenv("DEVICE_TOKEN")
        response = client.post(
            f"https://{APNS_HOST_NAME}/3/device/{DEVICE_TOKEN}",
            headers=headers,
            json=data,
        )
        return response.status_code == 200

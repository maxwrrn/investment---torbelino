# market_sim/consensus/crypto.py
# Simple HMAC-based "signatures" for the demo

import os, hmac, hashlib, dataclasses

@dataclasses.dataclass(frozen=True)
class Keypair:
    secret: bytes
    @property
    def public(self) -> bytes:
        return hashlib.sha256(self.secret).digest()

def gen_keypair() -> Keypair:
    return Keypair(secret=os.urandom(32))

def sign(secret: bytes, message: bytes) -> bytes:
    return hmac.new(secret, message, hashlib.sha256).digest()

def verify(public: bytes, secret: bytes, message: bytes, signature: bytes) -> bool:
    ok_sig = hmac.compare_digest(hmac.new(secret, message, hashlib.sha256).digest(), signature)
    ok_pub = hashlib.sha256(secret).digest() == public
    return ok_sig and ok_pub


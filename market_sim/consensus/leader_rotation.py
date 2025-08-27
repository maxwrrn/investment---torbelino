# market_sim/consensus/leader_rotation.py
# Deterministic leader choice per epoch

import hashlib

class DeterministicLeaderRotation:
    def __init__(self, n: int, seed: str = "consensus-seed"):
        self.n, self.seed = n, seed

    def leader_for(self, epoch: int) -> int:
        h = hashlib.sha256((self.seed + ":" + str(epoch)).encode()).digest()
        return int.from_bytes(h, "big") % self.n


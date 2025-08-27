# market_sim/consensus/blockchain_log.py
# Minimal block/chain with notarization + 3-chain finality

import dataclasses, json, hashlib
from typing import List, Tuple

def hash_bytes(b: bytes) -> bytes:
    return hashlib.sha256(b).digest()

@dataclasses.dataclass(frozen=True)
class Block:
    parent_hash: bytes
    epoch: int
    payload: str
    proposer_pub: bytes
    votes: Tuple[bytes, ...] = dataclasses.field(default_factory=tuple)
    notarized: bool = False

    def with_votes(self, new_votes: Tuple[bytes, ...], notarized: bool) -> "Block":
        return dataclasses.replace(self, votes=new_votes, notarized=notarized)

    def serialized_without_hash(self) -> bytes:
        obj = {
            "parent_hash": self.parent_hash.hex(),
            "epoch": self.epoch,
            "payload": self.payload,
            "proposer_pub": self.proposer_pub.hex(),
            "votes": [v.hex() for v in self.votes],
            "notarized": self.notarized,
        }
        return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode()

    def id(self) -> str:
        return hashlib.sha256(self.serialized_without_hash()).hexdigest()

class Chain:
    def __init__(self):
        genesis = Block(parent_hash=b"", epoch=0, payload="GENESIS", proposer_pub=b"", votes=tuple(), notarized=True)
        self.blocks: List[Block] = [genesis]
        self.finalized_height: int = 0

    def tip(self) -> Block:
        return self.blocks[-1]

    def height(self) -> int:
        return len(self.blocks) - 1

    def _prefix_hash(self, prefix: List[Block]) -> bytes:
        state = b""
        for blk in prefix:
            state = hash_bytes(state + blk.serialized_without_hash())
        return state

    def notarized_longest_prefix_hash(self) -> bytes:
        return self._prefix_hash(self.blocks)

    def append(self, blk: Block) -> None:
        expected = self.notarized_longest_prefix_hash()
        assert blk.parent_hash == expected
        self.blocks.append(blk)

    def try_finalize(self) -> None:
        for i in range(1, len(self.blocks) - 2):
            b1, b2, b3 = self.blocks[i], self.blocks[i+1], self.blocks[i+2]
            if b1.notarized and b2.notarized and b3.notarized:
                if b2.epoch == b1.epoch + 1 and b3.epoch == b2.epoch + 1:
                    self.finalized_height = max(self.finalized_height, i+1)

    def finalized(self) -> List[Block]:
        return self.blocks[: self.finalized_height + 1]


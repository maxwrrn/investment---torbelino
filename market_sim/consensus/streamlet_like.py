# market_sim/consensus/streamlet_like.py
# Streamlet-inspired demo: leader proposes, nodes vote, blocks notarize/finalize

import dataclasses, random
from typing import List, Dict, Set, Tuple
from .crypto import gen_keypair, sign, verify, Keypair
from .blockchain_log import Block, Chain
from .leader_rotation import DeterministicLeaderRotation

@dataclasses.dataclass
class Node:
    idx: int
    keypair: Keypair
    n_nodes: int
    f_byzantine: int
    chain: Chain
    is_byzantine: bool = False

    def public(self) -> bytes:
        return self.keypair.public

    def choose_payload(self, epoch: int) -> str:
        return f"tx:epoch={epoch}:node={self.idx}"

    def propose_block(self, epoch: int) -> Block:
        parent_h = self.chain.notarized_longest_prefix_hash()
        return Block(parent_hash=parent_h, epoch=epoch, payload=self.choose_payload(epoch), proposer_pub=self.public())

    def validate_proposal(self, blk: Block, parent_hash: bytes) -> bool:
        return blk.parent_hash == parent_hash

class Network:
    def __init__(self, nodes: List[Node], rotation: DeterministicLeaderRotation, quorum: int):
        self.nodes, self.rotation, self.quorum = nodes, rotation, quorum

    def run_epoch(self, epoch: int, drop: Set[int] | None = None) -> Dict[int, Block]:
        drop = drop or set()
        leader_idx = self.rotation.leader_for(epoch)
        leader = self.nodes[leader_idx]
        proposal = leader.propose_block(epoch)

        votes: Dict[int, Tuple[bytes, bytes]] = {}
        for node in self.nodes:
            if node.idx in drop or node.is_byzantine:
                continue
            if node.validate_proposal(proposal, node.chain.notarized_longest_prefix_hash()):
                sig = sign(node.keypair.secret, proposal.serialized_without_hash())
                votes[node.idx] = (node.public(), sig)

        notarized = len(votes) >= self.quorum
        blk = proposal.with_votes(tuple(sorted([pub for pub, _ in votes.values()])), notarized)

        for node in self.nodes:
            if node.idx in drop: continue
            if notarized and node.validate_proposal(blk, node.chain.notarized_longest_prefix_hash()):
                node.chain.append(blk)
                node.chain.try_finalize()

        return {leader_idx: blk}

def math_quorum_2n_over_3(n: int) -> int:
    return (2 * n + 2) // 3

def make_demo_network(n: int = 7, f_byz: int = 2, seed: int = 0):
    random.seed(seed)
    nodes = [Node(idx=i, keypair=gen_keypair(), n_nodes=n, f_byzantine=f_byz, chain=Chain(), is_byzantine=(i < f_byz)) for i in range(n)]
    return nodes, Network(nodes, DeterministicLeaderRotation(n, seed="demo-seed"), quorum=math_quorum_2n_over_3(n))


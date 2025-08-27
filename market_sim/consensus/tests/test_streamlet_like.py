from market_sim.consensus.streamlet_like import make_demo_network, math_quorum_2n_over_3

def test_quorum():
    assert math_quorum_2n_over_3(7) == 5
    assert math_quorum_2n_over_3(3) == 2

def test_finalization_progress():
    nodes, net = make_demo_network(n=7, f_byz=2, seed=42)
    for e in range(1, 20):
        net.run_epoch(e)
    assert max(node.chain.finalized_height for node in nodes) >= 2


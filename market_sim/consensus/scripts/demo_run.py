import argparse, csv
from pathlib import Path
from market_sim.consensus.streamlet_like import make_demo_network

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=7)
    ap.add_argument("--f", type=int, default=2)
    ap.add_argument("--epochs", type=int, default=15)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", type=str, default="market_sim/consensus/consensus_log.csv")
    args = ap.parse_args()

    nodes, net = make_demo_network(n=args.n, f_byz=args.f, seed=args.seed)
    rows = []
    for e in range(1, args.epochs + 1):
        delivered = net.run_epoch(e)
        leader_idx, blk = next(iter(delivered.items()))
        for node in nodes:
            rows.append({
                "epoch": e,
                "leader": leader_idx,
                "node": node.idx,
                "chain_height": node.chain.height(),
                "finalized_height": node.chain.finalized_height,
            })

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)

if __name__ == "__main__":
    main()


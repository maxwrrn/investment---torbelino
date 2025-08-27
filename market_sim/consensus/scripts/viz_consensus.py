import argparse, csv, matplotlib.pyplot as plt

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--log", type=str, default="market_sim/consensus/consensus_log.csv")
    args = ap.parse_args()

    heights, finalized = {}, {}
    with open(args.log, newline="") as f:
        for row in csv.DictReader(f):
            e, n = int(row["epoch"]), int(row["node"])
            heights.setdefault(n, []).append(int(row["chain_height"]))
            finalized.setdefault(n, []).append(int(row["finalized_height"]))

    for n in sorted(heights.keys()):
        plt.figure()
        plt.plot(range(1, len(heights[n]) + 1), heights[n], label=f"node {n} chain")
        plt.plot(range(1, len(finalized[n]) + 1), finalized[n], "--", label=f"node {n} finalized")
        plt.xlabel("epoch"); plt.ylabel("height"); plt.title(f"Node {n}")
        plt.legend(); plt.show()

if __name__ == "__main__":
    main()


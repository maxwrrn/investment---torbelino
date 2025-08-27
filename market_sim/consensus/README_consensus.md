# Consensus Demo

This adds a small Streamlet-inspired consensus example:

- Leader rotation per epoch
- Propose → vote → notarize with quorum
- Finalization after 3 consecutive notarized blocks
- Minimal chain data structure
- Demo + visualization scripts
- Pytest tests

## Run

```bash
pytest -q market_sim/consensus/tests/test_streamlet_like.py
python -m market_sim.consensus.scripts.demo_run --epochs 20
python -m market_sim.consensus.scripts.viz_consensus --log market_sim/consensus/consensus_log.csv
```

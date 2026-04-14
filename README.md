# MPIP Framework: Modular-Polynomial Identity Proof

This repository contains the Python simulation code used to validate the cryptographic bounds, rejection sampling rates, and Zero-Knowledge entropy of the MPIP framework, as detailed in our manuscript.

## Repository Structure
* `mpip_core.py`: Contains the core lattice arithmetic, Key Generation, Proof Generation (featuring the Modular Guard), and Verification logic.
* `kat_eval.py`: The evaluation script that runs 10,000 simulated deterministic vectors to calculate empirical performance metrics.

## Installation
Ensure you have Python 3.8+ installed. Install the required dependencies using:
```bash
pip install -r requirements.txt
## Reproducing Empirical Results
To reproduce the data found in **Table 4** of our manuscript, run the evaluation script:
```bash
python kat_eval.py

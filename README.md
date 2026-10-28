# YottaFlex Inventory Management and Data Validation

## Project Overview

This project develops a synthetic inventory management and data-quality validation system. It generates inventory master data, balances, movements, orders, reservations, shipments, replenishment rules, and anomaly test cases.

The goal is to demonstrate inventory traceability, stock reconciliation, available-to-promise (ATP) calculations, data integrity, and reproducible dataset generation.

## Technology Stack

- Python
- FastAPI
- PostgreSQL
- SQLAlchemy
- CSV and JSON
- Pytest

## Key Features

- Synthetic product, SKU, and location data generation
- Inventory balance and movement history generation
- ATP calculation using on-hand stock, reservations, blocked stock, and safety stock
- Order and order-line generation
- Reservation, shipment, and replenishment-rule datasets
- Automated primary-key, foreign-key, quantity, and reconciliation checks
- Separate ground-truth labels and anomaly test fixtures
- Reproducible data generation using a configurable random seed

## Project Structure

```text
yottaflex-inventory/
├── app/
│   ├── main.py
│   ├── models.py
│   ├── seed_sample.py
│   └── services/
├── generator/
│   ├── generate_challenge_data.py
│   ├── validate_challenge_dataset.py
│   ├── generate_consistent_data.py
│   ├── validate_consistent_data.py
│   ├── generate_movements.py
│   └── validate_movements.py
├── tests/
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

Create and activate a Python virtual environment if one does not already exist.

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Configure the PostgreSQL connection using a local `.env` file. Never commit credentials or secrets to GitHub.

## Generate a Small Dataset

Run the following command from the project root:

```bash
python generator/generate_challenge_data.py \
  --skus 10 \
  --locations 3 \
  --orders 20 \
  --movements 100 \
  --seed 20261022 \
  --output generator/test_output_v3
```

The generator creates CSV files for products, SKUs, locations, balances, movements, orders, order lines, reservations, shipments, replenishment rules, anomaly cases, and ground-truth labels. It also writes supporting JSON metadata.

## Validate the Dataset

```bash
python generator/validate_challenge_dataset.py generator/test_output_v3
```

The validator checks data relationships, unique identifiers, quantity constraints, ATP arithmetic, movement reconciliation, and ground-truth scenario coverage.

## Run Tests

```bash
python -m pytest -q
```

## Anomaly Scenarios

The current anomaly test fixtures cover four categories:

1. Inventory balance differs from movement history
2. Reservation quantity exceeds available-to-promise stock
3. An order attempts to allocate blocked stock
4. A transfer receipt is recorded prematurely

These are currently separate test fixtures. Full integration with transaction histories and automated business-rule detection remains part of the validation work.

## Reproducibility

The default random seed is `20261022`. Use the same seed and parameters to regenerate the same dataset. Compare SHA-256 checksums to verify that generated CSV files are identical.

## Data Safety

All generated records are synthetic. Do not include real customer data, passwords, database credentials, or other sensitive information in the repository.

## Current Status

The small and medium sample datasets have passed the current automated validator. The existing backend test suite has six passing tests.

Full-scale generation, complete business-rule validation, final documentation review, and repository submission remain to be completed.

## Future Improvements

- Complete transfer and in-transit inventory handling
- Integrate reservations with stock availability and lifecycle validation
- Strengthen anomaly detection and ground-truth traceability
- Generate and validate the target dataset at full scale
- Add a Streamlit dashboard for inventory monitoring and validation results

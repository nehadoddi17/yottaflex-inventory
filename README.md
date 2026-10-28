# YottaFlex Inventory Management

A synthetic inventory management, reconciliation, and data-quality validation project built with FastAPI, SQLAlchemy, PostgreSQL, and Python.

## Overview

This project demonstrates unified inventory tracking across locations, inventory movements, available-to-promise (ATP) calculations, reservations, stock transfers, and reconciliation. It also includes a reproducible synthetic data generator and a validation pipeline for large inventory datasets.

A lightweight web dashboard provides stock lookup and inventory reconciliation through the FastAPI backend.

## Technology Stack

- Python
- FastAPI and Uvicorn
- SQLAlchemy
- PostgreSQL
- Pydantic
- HTML, CSS, and JavaScript
- Pytest
- CSV and JSON

## Features

- Synthetic product, SKU, location, balance, movement, order, reservation, shipment, and replenishment data.
- Configurable dataset generation with a fixed random seed.
- ATP calculation using on-hand, reserved, blocked, safety-stock, and approved-inbound quantities.
- Inventory movement recording.
- Reservation creation and expiry processing.
- Inventory reconciliation against movement history.
- Stock-transfer dispatch and receipt services.
- Primary-key, foreign-key, quantity, arithmetic, movement-history, and ground-truth validation.
- Four labelled anomaly scenarios.
- Browser dashboard for inventory lookup and reconciliation.

## Project Structure

```text
app/
  main.py
  database.py
  init_db.py
  models.py
  seed_sample.py
  services/
  static/
    index.html
generator/
  generate_challenge_data.py
  validate_challenge_dataset.py
tests/
docs/
requirements.txt
README.md
.gitignore
```

## Prerequisites

- Python 3.10 or compatible version
- PostgreSQL configured for the application
- Git, if cloning the repository

## Setup

Clone the repository and enter the project directory:

```bash
git clone https://github.com/nehadoddi17/yottaflex-inventory.git
cd yottaflex-inventory
```

Create and activate a virtual environment.

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Configure your local PostgreSQL connection using the environment settings expected by `app/database.py`. Keep credentials in a local `.env` file and never commit secrets.

Initialize the database using the project's database initialization script:

```bash
python -m app.init_db
```

If the project requires an existing PostgreSQL database, create it before running the initialization command.

## Run the API and Dashboard

Start the application from the repository root:

```bash
python -m uvicorn app.main:app --reload
```

Open the dashboard:

- http://127.0.0.1:8000/

Open the interactive API documentation:

- http://127.0.0.1:8000/docs

Useful endpoints include:

- `GET /health`
- `GET /db-check`
- `GET /inventory/atp`
- `POST /inventory/movements`
- `POST /reservations`
- `POST /reservations/expire`
- `GET /inventory/reconcile`

## Generate a Small Dataset

Run the generator from the repository root:

```powershell
python generator/generate_challenge_data.py --skus 20 --locations 5 --orders 10 --movements 120 --seed 20261022 --output generator/gt_test
```

The output directory contains generated CSV files and supporting metadata.

## Generate the Full-Scale Dataset

The following command generates the challenge-scale dataset:

```powershell
python generator/generate_challenge_data.py --skus 5000 --locations 100 --orders 50000 --movements 1000000 --seed 20261022 --output generator/challenge_output_v2
```

Large dataset generation can take time and requires sufficient disk space. Generated datasets are intentionally excluded from Git; reproduce them locally when needed.

## Validate a Dataset

```powershell
python generator/validate_challenge_dataset.py generator/gt_test
```

To validate the full-scale output:

```powershell
python generator/validate_challenge_dataset.py generator/challenge_output_v2
```

The current full-scale validation run completed with zero reported errors. Its reported counts included 5,000 products, 5,000 SKUs, 100 locations, 500,000 balances, 1,000,000 movements, 50,000 orders and order lines, 1,000 reservations, 1,000 shipments, 5,000 replenishment rules, and four ground-truth cases.

## Run Tests

```powershell
python -m pytest -q
```

The backend test suite most recently reported 12 passing tests.

## ATP Calculation

The implemented ATP calculation is:

```text
ATP = on_hand - reserved - blocked - safety_stock + approved_inbound
```

For example, with 120 on-hand, 15 reserved, 5 blocked, 10 safety stock, and zero approved inbound:

```text
ATP = 120 - 15 - 5 - 10 + 0 = 90
```

Approved inbound must follow the application's eligibility rules; it should not include unapproved or otherwise ineligible stock.

## Anomaly Scenarios

The generated ground-truth fixtures represent four anomaly categories:

1. Recorded inventory differs from expected inventory.
2. A requested reservation exceeds ATP.
3. An allocation attempts to use blocked stock.
4. A transfer receipt timestamp precedes its dispatch timestamp.

These fixtures provide labelled scenarios for validation. They should not be interpreted as proof that every anomaly is automatically detected end-to-end. The blocked-stock scenario is currently a fixture referencing a balance with blocked inventory, rather than a persisted allocation event.

## Reproducibility

The generator accepts a configurable seed. Using seed `20261022` with the same parameters produced matching SHA-256 hashes for all 12 CSV files in a repeated small-scale generation test.

For reproducibility checks, compare the SHA-256 hashes of each corresponding CSV file.

## Data Safety

All generated challenge records are synthetic. Never commit real customer data, credentials, API keys, passwords, or database secrets.

## Known Limitations

- The anomaly fixtures are not all persisted operational events.
- The dashboard currently supports SKU/location stock lookup and reconciliation; the summary cards reflect the selected SKU and location, not network-wide aggregate totals.
- End-to-end testing of every reservation and transfer lifecycle is still needed.
- Database schema initialization uses the existing project setup; a production migration strategy would be a future improvement.

## Current Status

- Full-scale synthetic dataset generated and validated with zero reported errors.
- Small-scale dataset reproducibility verified for all 12 CSV files.
- Backend test suite: 12 tests passing.
- Health and database connectivity endpoints returned successful responses.
- ATP lookup and inventory reconciliation tested through the browser dashboard.
- The project and AI usage documentation have been pushed to the public GitHub repository. Final review of the challenge requirements and remaining limitations is still recommended.

# YottaFlex Inventory Management

A Python-based inventory management and reconciliation prototype built with FastAPI, PostgreSQL, SQLAlchemy, and a reproducible synthetic dataset.

## Understanding the Problem

Businesses often store products across multiple stores, warehouses, and online channels. Keeping inventory accurate across all these locations can be challenging. For example, some products may already be reserved for customer orders, blocked because they are damaged, or still in transit.

This project addresses the challenge of tracking inventory, calculating how much stock is available to promise to customers, and identifying differences between recorded stock and inventory movement history.

It demonstrates these concepts using Python, FastAPI, PostgreSQL, automated tests, and a lightweight web dashboard.

## Real-World Application

Retailers need accurate inventory information to fulfil customer orders, identify stock discrepancies, and make better replenishment decisions.

An inventory reconciliation system can help compare recorded stock with expected stock, identify inconsistencies, and provide clearer visibility into available inventory.

This project uses synthetic data to demonstrate these workflows. It is a prototype and is not connected to a real retailer's inventory system.

## Important Terms

- **Inventory balance:** The quantity of a product recorded at a particular location.
- **Inventory movement:** A transaction that changes stock, such as receiving, selling, or transferring goods.
- **Available-to-Promise (ATP):** The quantity available to promise to customers after accounting for relevant stock deductions and eligible incoming inventory.
- **Reserved stock:** Inventory allocated to existing orders.
- **Blocked stock:** Inventory that must not be treated as available for normal fulfilment.
- **Safety stock:** Extra inventory kept as a buffer against uncertainty in demand or supply.
- **Inventory reconciliation:** Comparing recorded inventory with expected inventory to identify discrepancies.
- **Ground-truth anomaly:** A known example of an inventory issue used to test validation logic.

## What I Built

- A FastAPI backend for inventory lookup and reconciliation.
- PostgreSQL database integration for inventory records.
- Available-to-Promise (ATP) calculations.
- Inventory movement, reservation, and stock-transfer services.
- A configurable synthetic data generator and dataset validation pipeline.
- Four labelled anomaly scenarios.
- A lightweight HTML, CSS, and JavaScript dashboard.
- Automated tests using pytest.

## Technology Stack

- Python 3.10
- FastAPI and Uvicorn
- SQLAlchemy
- PostgreSQL
- Pydantic
- HTML, CSS, and JavaScript
- Pytest
- CSV and JSON

## Features

- Synthetic product, SKU, location, inventory balance, movement, order, reservation, shipment, and replenishment data.
- Configurable dataset generation using a fixed random seed.
- ATP calculation using on-hand, reserved, blocked, safety-stock, and approved-inbound quantities.
- Inventory movement recording.
- Reservation creation and expiry processing.
- Inventory reconciliation against movement history.
- Stock-transfer dispatch and receipt services.
- Data validation covering keys, quantities, arithmetic, movement history, and labelled anomaly scenarios.
- Browser dashboard for inventory lookup and reconciliation.

## Project Structure

```text
yottaflex-inventory/
├── app/
│   ├── services/
│   ├── static/
│   │   └── index.html
│   ├── main.py
│   ├── database.py
│   ├── init_db.py
│   ├── models.py
│   └── seed_sample.py
├── docs/
│   ├── DATA_DICTIONARY.md
│   └── SCHEMA.md
├── generator/
│   ├── generate_challenge_data.py
│   └── dataset validation scripts
├── screenshots/
│   ├── API Documentation.png
│   ├── Dataset Validation.png
│   ├── Inventory Dashboard.png
│   └── Result.png
├── tests/
│   ├── test_inventory.py
│   ├── test_reconciliation.py
│   ├── test_reservations.py
│   └── test_transfers.py
├── AI_USAGE.md
├── README.md
├── requirements.txt
└── .gitignore
```

- **`app/`** — FastAPI application, database configuration, models, and business services.
- **`docs/`** — Data dictionary and database schema documentation.
- **`generator/`** — Synthetic dataset generation and validation scripts.
- **`screenshots/`** — Screenshots showing the dashboard, API documentation, test results, and dataset validation.
- **`tests/`** — Automated tests for inventory, reconciliation, reservations, and transfers.
- **`AI_USAGE.md`** — Documentation of AI-assisted development and validation.

## Prerequisites

Install the following before running the project:

- Python 3.10 or a compatible version.
- PostgreSQL.
- Git, if cloning the repository.
- A PostgreSQL username and password with permission to use the project database.

## Setup

### 1. Clone the repository

Open PowerShell or the VS Code terminal and run:

```powershell
git clone https://github.com/nehadoddi17/yottaflex-inventory.git
cd yottaflex-inventory
```

### 2. Create and activate a virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure PostgreSQL

Make sure PostgreSQL is installed and running.

Create a database named `yottaflex_inventory` if it does not already exist. You can create it using a PostgreSQL administration tool or the PostgreSQL command line.

For example, if your PostgreSQL user has permission to create databases:

```powershell
createdb -U postgres yottaflex_inventory
```

Replace `postgres` with your PostgreSQL username if needed. If the database already exists, skip this command.

Create a `.env` file in the project root directory, in the same folder as `README.md`.

Add your local PostgreSQL connection settings:

```env
DB_USER=your_postgres_username
DB_PASSWORD=your_postgres_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=yottaflex_inventory
```

Replace the example username and password with your actual PostgreSQL credentials. The host and port shown above are the defaults used by the application.

**Important:** Keep `.env` private. Never commit database passwords, API keys, or other secrets to GitHub.

### 5. Initialize the database

With the virtual environment activated and the PostgreSQL database configured, run:

```powershell
python -m app.init_db
```

This runs the project's database initialization script.

## Run the API and Dashboard

From the project root, start the FastAPI application:

```powershell
python -m uvicorn app.main:app --reload
```

Keep the terminal open while using the application.

Open the following URLs in your browser:

| Resource | URL |
|---|---|
| Inventory dashboard | http://127.0.0.1:8000/ |
| Interactive API documentation | http://127.0.0.1:8000/docs |
| Health check | http://127.0.0.1:8000/health |
| Database connection check | http://127.0.0.1:8000/db-check |

Useful API endpoints include:

- `GET /health`
- `GET /db-check`
- `GET /inventory/atp`
- `POST /inventory/movements`
- `POST /reservations`
- `POST /reservations/expire`
- `GET /inventory/reconcile`

The dashboard and API use the inventory records available in the configured PostgreSQL database.

To stop the development server, press `Ctrl + C` in the terminal running Uvicorn.

## Generate a Small Dataset

A small dataset is useful for quickly checking the data generator and validator without generating the full challenge dataset.

Run:

```powershell
python generator/generate_challenge_data.py --skus 20 --locations 5 --orders 10 --movements 120 --seed 20261022 --output generator/gt_test
```

The generator creates CSV files and supporting metadata in the specified output directory.

## Generate the Full-Scale Dataset

To reproduce the challenge-scale dataset, run:

```powershell
python generator/generate_challenge_data.py --skus 5000 --locations 100 --orders 50000 --movements 1000000 --seed 20261022 --output generator/challenge_output_v2
```

This operation can take time and requires sufficient disk space.

Generated datasets are excluded from Git, so they can be reproduced locally using the generator and its parameters.

## Validate a Dataset

Validate the small dataset:

```powershell
python generator/validate_challenge_dataset.py generator/gt_test
```

Validate the full-scale dataset:

```powershell
python generator/validate_challenge_dataset.py generator/challenge_output_v2
```

The full-scale validation run completed with zero reported errors.

The reported dataset counts included:

- 5,000 products.
- 5,000 SKUs.
- 100 locations.
- 500,000 inventory balances.
- 1,000,000 inventory movements.
- 50,000 orders and order lines.
- 1,000 reservations.
- 1,000 shipments.
- 5,000 replenishment rules.
- Four ground-truth anomaly cases.

## Run Automated Tests

From the project root, run:

```powershell
python -m pytest -v
```

Or use the shorter output format:

```powershell
python -m pytest -q
```

The verified test suite currently contains **12 passing tests** covering selected ATP calculations, stock validation, reconciliation, reservation expiry, and transfer operations.

## ATP Calculation

The implemented Available-to-Promise calculation is:

```text
ATP = on_hand - reserved - blocked - safety_stock + approved_inbound
```

For example, if inventory has:

- On-hand stock: 120
- Reserved stock: 15
- Blocked stock: 5
- Safety stock: 10
- Approved inbound stock: 0

The calculation is:

```text
ATP = 120 - 15 - 5 - 10 + 0
ATP = 90
```

Therefore, 90 units are available to promise under these assumptions. Incoming stock should be included only when it meets the application's eligibility rules.

## Anomaly Scenarios

The generated ground-truth fixtures represent four anomaly categories:

1. Recorded inventory differs from expected inventory.
2. A requested reservation exceeds ATP.
3. An allocation attempts to use blocked stock.
4. A transfer receipt timestamp precedes its dispatch timestamp.

These fixtures provide labelled examples for validation and review. They do not prove that every anomaly is automatically detected through a complete application workflow. In particular, the blocked-stock scenario references a balance containing blocked inventory rather than a persisted allocation event.

## Reproducibility

The generator accepts a configurable random seed.

Using seed `20261022` with the same parameters produced matching SHA-256 hashes for all 12 CSV files in a repeated small-scale generation test.

To verify reproducibility, generate the same dataset twice using identical parameters and compare the corresponding CSV file hashes.

## Data Safety

All generated challenge records are synthetic.

- Keep database credentials and secrets in your local `.env` file.
- Do not commit real customer information, passwords, API keys, or database secrets.
- Generated challenge datasets are excluded from Git and can be recreated locally.

## Known Limitations

- **Anomaly scenarios:** Four labelled anomaly examples are included, but not all are connected to complete application workflows or automatically detected end to end.
- **Dashboard scope:** The dashboard displays inventory for a selected SKU and location rather than network-wide totals.
- **Testing coverage:** The 12 automated tests cover selected backend behaviours. Additional end-to-end tests are needed to verify every reservation and transfer scenario.
- **Database setup:** The project uses basic database initialization. A formal migration process would help manage future schema changes.

## Current Status

- Full-scale synthetic dataset generated and validated with zero reported errors.
- Small-scale dataset reproducibility verified for all 12 CSV files.
- Backend test suite: 12 tests passing.
- Health and database connectivity endpoints verified.
- ATP lookup and inventory reconciliation tested through the browser dashboard.
- Project and AI usage documentation pushed to the public GitHub repository.

## AI Usage and Development Notes

See [AI_USAGE.md](AI_USAGE.md) for information about AI-assisted development, implementation decisions, testing, and acknowledged limitations.

## Project in Action

Explore the project visuals in the [`project-showcase/`](project-showcase/) folder.

- **Inventory Dashboard** — View the inventory interface.
- **API Documentation** — Explore the available API endpoints.
- **Dataset Validation** — Review dataset validation results.
- **Reconciliation Results** — See the generated output and verification results.

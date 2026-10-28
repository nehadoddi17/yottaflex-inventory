# AI Usage and Prompt History

**Tool:** ChatGPT  
**Purpose:** Understanding requirements, learning technical concepts, implementation guidance, debugging, testing, documentation, and GitHub workflow.

## 1. Understanding the Problem and Selecting Technologies

As a fresher, I used ChatGPT to understand unfamiliar technical terms in the challenge and break the requirements into manageable tasks.

**Representative prompts:**
- "Explain the inventory challenge requirements in simple English and tell me what I need to build."
- "Explain available-to-promise (ATP), reserved stock, blocked stock, and safety stock with examples."
- "Can I use FastAPI, PostgreSQL, Pandas, and pytest for this project?"

AI helped me understand inventory reconciliation, ATP, reservations, and data validation. I used its explanations to evaluate a practical technology stack: Python, FastAPI, PostgreSQL, SQLAlchemy, Pandas, pytest, HTML, CSS, and JavaScript.

## 2. Implementation and Development

I used ChatGPT for step-by-step guidance while implementing inventory APIs, ATP calculation, reconciliation, dataset generation, validation, and the frontend dashboard.

**Representative prompts:**
- "Explain how to calculate ATP using on-hand stock, reservations, blocked stock, safety stock, and approved inbound inventory."
- "Help me connect the HTML dashboard to my FastAPI endpoints."
- "How can I generate a large inventory dataset with configurable SKU, location, order, and movement counts?"
- "Explain how to run the FastAPI application using Uvicorn."

AI helped me understand implementation approaches and connect the different components. Some implementation suggestions and code changes were AI-assisted, and I used local execution and testing to check their behavior.

## 3. Debugging and Problem Solving

I used ChatGPT to understand development errors and investigate their causes instead of blindly applying suggested fixes.

**Examples of prompts and issues:**
- Asked for help resolving PowerShell quoting errors when running Python commands.
- Shared a PostgreSQL foreign-key error after attempting to insert an inventory balance for a nonexistent SKU.
- Asked how to find valid SKU and location IDs in the database.
- Shared the frontend error: "No inventory balance found for this SKU and location."

These experiences helped me understand database relationships, foreign-key constraints, and why generated CSV data is separate from data stored in PostgreSQL. I ran the suggested commands locally and used the actual output to guide troubleshooting.

## 4. Testing and Personal Validation

I used ChatGPT to understand testing approaches and verify whether the application behaved as expected.

**Representative prompts:**
- "How do I run my pytest test suite and interpret the results?"
- "How can I verify that running the generator with the same seed produces reproducible output?"
- Asked how to test the frontend with valid and invalid SKU/location IDs.

**Validation performed:**
- Ran the automated test suite: **12 tests passed**.
- Ran the full-scale dataset validator: **zero validation errors**.
- Compared SHA-256 hashes across 12 corresponding CSV files from repeated small-data generation runs.
- Tested ATP and reconciliation using SKU ID 1 and Location ID 1.
- Verified that the frontend displayed a clear error for an invalid SKU.

These results support the scenarios tested but do not prove that every possible inventory workflow is correct.

## 5. AI Contribution, Limitations, and Learning

ChatGPT accelerated my learning by explaining unfamiliar concepts, helping me evaluate technologies, troubleshooting errors, and organizing documentation. I relied heavily on AI for step-by-step guidance and some implementation suggestions.

I personally ran commands, examined outputs, tested the APIs and frontend, validated generated data, and reviewed the Git workflow before pushing the project to GitHub.

The local database currently contains only one inventory balance record, limiting testing across multiple inventory combinations. The generated CSV dataset is separate from the application database, and the consistency of the ground-truth anomaly cases requires further review.

My main takeaway is that AI can accelerate development, but its suggestions must be checked through testing and technical judgment. I remain responsible for understanding the submitted implementation, explaining my decisions, and communicating its limitations honestly.


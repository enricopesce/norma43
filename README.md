# Norma 43 Parser (Python)

[![PyPI version](https://badge.fury.io/py/norma43.svg)](https://badge.fury.io/py/norma43)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python Version](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/downloads/)
[![Code Style](https://img.shields.io/badge/code%20style-typed-black)](https://github.com/python/typing)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](http://makeapullrequest.com)

**The definitive, zero-dependency Python library for parsing Spanish banking statements in the Norma 43 (Cuaderno 43 / AEB 43) format.**

Designed for fintech developers, accountants, and financial data analysts who need a reliable, high-performance tool to automate bank reconciliation and process financial movements from Spanish banks (CaixaBank, BBVA, Santander, Sabadell, etc.).

---

## 🚀 Key Features

*   **🔒 Complete Compliance:** rigorous implementation of the **AEB (Asociación Española de Banca)** specifications for **Norma 43**.
*   **⚡ High Performance:** Optimized for processing large files quickly using only Python's standard library. **No external dependencies.**
*   **🛠️ Developer Ready:** Fully **type-hinted** (PEP 484) for excellent IDE support and error checking.
*   **✅ Robust Parsing:** Handles common edge cases, including complex sign management (debit/credit) and multi-line concepts (Record 23).
*   **📦 Multi-Format Export:** Built-in CLI to convert `.n43` files to **JSON** or **CSV** for easy integration with Excel, Pandas, or DataFrames.

## 📖 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [CLI Usage](#cli-usage)
- [Data Structure](#data-structure)
- [Supported Records](#supported-records)
- [License](#license)

## 📥 Installation

Requires Python 3.7+.

Install the latest version from PyPI:

```bash
pip install norma43
```

Or clone the repository and install directly:

```bash
git clone https://github.com/enricopesce/norma43.git
cd norma43
pip install .
```

## 💻 Quick Start

Easily integrate Norma 43 parsing into your Python financial applications:

```python
from norma43.parser import Norma43Parser

# 1. Initialize the parser
parser = Norma43Parser("path/to/statement.n43")

# 2. Parse the file
accounts = parser.parse()

# 3. Process the data
for account in accounts:
    print(f"🏦 Account: {account.bank}-{account.branch}-{account.account_number}")
    print(f"👤 Owner: {account.owner}")
    print(f"💰 Balance: {account.final_balance} {account.currency}")
    
    for tx in account.transactions:
        # Use tx.full_description for all lines joined, or check if tx.description exists
        desc = tx.description[0] if tx.description else "No description"
        print(f"   📅 {tx.date} | {tx.amount:>10} | {desc}")
```

## 🖥️ CLI Usage

This library includes a powerful command-line interface (CLI) for quick file inspection and conversion.

### 1. View Summary (Text)
Ideal for quick verification of file contents.
```bash
python -m norma43 statement.n43
```

### 2. Convert to JSON
Export data for use in web apps or NoSQL databases.
```bash
python -m norma43 statement.n43 --format json --output data.json
```

### 3. Convert to CSV
Generate spreadsheets for Excel or import into Pandas.
```bash
python -m norma43 statement.n43 --format csv --output report.csv
```

## 📊 Data Structure

The parser returns a `List[Account]` where `Account` and its `Transaction` objects are **dataclasses**:

### Account Object (dataclass)
| Field | Type | Description |
|-------|------|-------------|
| `bank` | `str` | 4-digit Bank Code |
| `branch` | `str` | 4-digit Branch Code |
| `account_number` | `str` | 10-digit Account Number |
| `initial_balance` | `Decimal` | Balance at start period |
| `final_balance` | `Decimal` | Balance at end period |
| `currency` | `str` | ISO 4217 Currency Code (e.g., 978 for EUR) |
| `transactions` | `List[Transaction]` | List of transaction objects |

### Transaction Object (dataclass)
| Field | Type | Description |
|-------|------|-------------|
| `date` | `date` | Transaction date |
| `value_date` | `date` | Value date (Fecha valor) |
| `amount` | `Decimal` | Signed transaction amount |
| `description` | `List[str]` | Full description lines |
| `full_description` | `property (str)` | All description lines joined by space |
| `reference1` | `str` | Primary reference / Document ID |

## 📋 Supported Records

| Record | Type | Status | Description |
|:------:|:-----|:------:|:------------|
| **11** | Header | ✅ | Account identification and initial balance |
| **22** | Transaction | ✅ | Main movement details (Date, Amount, IDs) |
| **23** | Complementary | ✅ | Extended concepts and descriptions |
| **33** | Footer | ✅ | Account final balance and totals verification |
| **88** | End of File | ✅ | File integrity check |

## ⚖️ License

Distributed under the **Apache License 2.0**. See [LICENSE](LICENSE) for more information.

---

**Keywords:** *Norma 43, Cuaderno 43, CSB 43, AEB 43, Conciliación Bancaria, Bank Reconciliation, Spanish Banking Standard, Python Parser, Finance, Fintech, Open Banking.*

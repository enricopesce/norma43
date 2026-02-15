# Norma 43 Parser (Python)

A robust, dependency-free Python library for parsing **Norma 43** (Cuaderno 43) banking files, the standard format for exchanging bank account statements in Spain.

This parser strictly follows the official specifications defined by the Spanish banking association (AEB), ensuring accuracy for records 11 (Header), 22 (Transactions), 23 (Complementary Info), 33 (Footer), and 88 (End of File).

## Features

*   **Complete Standard Support:** Parses all standard record types (11, 22, 23, 33, 88).
*   **Zero Dependencies:** Built using only Python's standard library.
*   **Type Hinted:** Fully typed for better IDE support and code quality.
*   **Robust Date & Amount Parsing:** Correctly handles sign digits and various field formats.
*   **Multiple Output Formats:** Includes a CLI tool to export data to JSON or CSV.
*   **Comprehensive Tests:** Unit tested against synthetic data and verified against real-world examples.

## Installation

This library requires Python 3.7 or higher.

You can install it directly from source (until it's published to PyPI):

```bash
git clone https://github.com/enricopesce/norma43.git
cd norma43
pip install .
```

## Usage

### As a Library

```python
from norma43.parser import Norma43Parser

# Initialize the parser with your file path
parser = Norma43Parser("path/to/file.n43")

# Parse the file
accounts = parser.parse()

# Access the data
for account in accounts:
    print(f"Account: {account['account_number']}")
    print(f"Owner: {account['owner']}")
    print(f"Final Balance: {account['final_balance']} {account['currency']}")
    
    for tx in account['transactions']:
        print(f"  Date: {tx['date']} | Amount: {tx['amount']} | Desc: {tx['description']}")
```

### CLI Tool

You can use the parser from the command line to inspect files or convert them.

**1. Text Summary**
```bash
python -m norma43.parser path/to/file.n43
```

**2. Export to JSON**
```bash
python -m norma43.parser path/to/file.n43 --format json --output export.json
```

**3. Export to CSV**
```bash
python -m norma43.parser path/to/file.n43 --format csv --output export.csv
```

## Data Structure

The `parse()` method returns a list of dictionaries, where each dictionary represents a bank account found in the file.

**Account Object:**
*   `bank`, `branch`, `account_number`: Strings identifying the account.
*   `start_date`, `end_date`: `datetime.date` objects.
*   `initial_balance`, `final_balance`: `decimal.Decimal` objects.
*   `owner`: Account holder name.
*   `currency`: Currency code (e.g., '978' for EUR).
*   `transactions`: List of transaction objects.

**Transaction Object:**
*   `date`, `value_date`: `datetime.date` objects.
*   `amount`: `decimal.Decimal`.
*   `description`: List of strings (concatenated from Type 23 records).
*   `document`, `reference1`, `reference2`: Tracking numbers.
*   `common_code`, `own_code`: Transaction type codes.

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please ensure that any changes include updated unit tests in the `tests/` directory.

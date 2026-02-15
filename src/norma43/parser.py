import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional, Any, Union
from dataclasses import dataclass, field

@dataclass
class Transaction:
    """Represents a single bank movement (Record 22 + 23)."""
    date: Optional[datetime.date]
    value_date: Optional[datetime.date]
    amount: Decimal
    common_code: str
    own_code: str
    document: str
    reference1: str
    reference2: str
    origin_branch: str
    description: List[str] = field(default_factory=list)
    description_details: Dict[str, List[str]] = field(default_factory=dict)

    @property
    def full_description(self) -> str:
        return " ".join(self.description)

@dataclass
class Account:
    """Represents a bank account and its movements (Record 11 + 33)."""
    bank: str
    branch: str
    account_number: str
    start_date: Optional[datetime.date]
    end_date: Optional[datetime.date]
    initial_balance: Decimal
    currency: str
    mode: str
    owner: str
    transactions: List[Transaction] = field(default_factory=list)
    
    # Footer data (Record 33)
    final_balance: Optional[Decimal] = None
    num_debits: int = 0
    total_debit: Decimal = Decimal('0.00')
    num_credits: int = 0
    total_credit: Decimal = Decimal('0.00')
    footer_currency: Optional[str] = None

class Norma43Parser:
    """
    A strongly-typed parser for the Norma 43 banking file format.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.accounts: List[Account] = []
        self.total_records_count: int = 0
        self.actual_records_count: int = 0

    def parse(self) -> List[Account]:
        """
        Parses the Norma 43 file and returns a list of Account objects.
        """
        current_account: Optional[Account] = None
        current_transaction: Optional[Transaction] = None
        self.actual_records_count = 0
        self.accounts = []

        try:
            with open(self.file_path, 'r', encoding='latin-1') as f:
                for line in f:
                    self.actual_records_count += 1
                    line = line.rstrip('\r\n')
                    if not line:
                        continue
                    
                    record_type = line[:2]
                    
                    if record_type == '11':
                        current_account = self._parse_header(line)
                        self.accounts.append(current_account)
                        current_transaction = None 
                    
                    elif record_type == '22':
                        if current_account is not None:
                            current_transaction = self._parse_transaction(line)
                            current_account.transactions.append(current_transaction)
                    
                    elif record_type == '23':
                        if current_transaction is not None:
                            self._parse_complementary(line, current_transaction)
                    
                    elif record_type == '33':
                        if current_account is not None:
                            self._parse_footer(line, current_account)

                    elif record_type == '88':
                        self._parse_eof(line)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Error parsing file {self.file_path}: {e}")

        return self.accounts

    def _parse_header(self, line: str) -> Account:
        return Account(
            bank=line[2:6],
            branch=line[6:10],
            account_number=line[10:20],
            start_date=self._parse_date(line[20:26]),
            end_date=self._parse_date(line[26:32]),
            initial_balance=self._parse_signed_amount(line[32:47]), 
            currency=line[47:50],
            mode=line[50:51],
            owner=line[51:77].strip()
        )

    def _parse_transaction(self, line: str) -> Transaction:
        return Transaction(
            origin_branch=line[6:10],
            date=self._parse_date(line[10:16]),
            value_date=self._parse_date(line[16:22]),
            common_code=line[22:24],
            own_code=line[24:27],
            amount=self._parse_signed_amount(line[27:42]),
            document=line[42:52].strip(),
            reference1=line[52:64].strip(),
            reference2=line[64:80].strip()
        )

    def _parse_complementary(self, line: str, transaction: Transaction) -> None:
        subcode = line[2:4]
        concept1 = line[4:42].strip()
        concept2 = line[42:80].strip()
        
        if concept1:
            transaction.description.append(concept1)
        if concept2:
            transaction.description.append(concept2)
            
        if subcode not in transaction.description_details:
            transaction.description_details[subcode] = []
        if concept1:
            transaction.description_details[subcode].append(concept1)
        if concept2:
            transaction.description_details[subcode].append(concept2)

    def _parse_footer(self, line: str, account: Account) -> None:
        account.num_debits = int(line[20:25])
        account.total_debit = self._parse_unsigned_amount(line[25:39])
        account.num_credits = int(line[39:44])
        account.total_credit = self._parse_unsigned_amount(line[44:58])
        account.final_balance = self._parse_signed_amount(line[58:73]) 
        account.footer_currency = line[73:76]

    def _parse_eof(self, line: str) -> None:
        try:
            self.total_records_count = int(line[20:26])
        except (ValueError, IndexError):
            self.total_records_count = 0

    @staticmethod
    def _parse_date(date_str: str) -> Optional[datetime.date]:
        try:
            return datetime.datetime.strptime(date_str, '%y%m%d').date()
        except ValueError:
            return None

    @staticmethod
    def _parse_signed_amount(amount_field: str) -> Decimal:
        if len(amount_field) < 2:
            return Decimal('0.00')
        sign_digit = amount_field[0]
        actual_amount_str = ''.join(filter(str.isdigit, amount_field[1:]))
        if not actual_amount_str:
            return Decimal('0.00')
        try:
            val = Decimal(actual_amount_str) / 100
            return -val if sign_digit == '1' else val
        except InvalidOperation:
            return Decimal('0.00')

    @staticmethod
    def _parse_unsigned_amount(amount_str: str) -> Decimal:
        amount_str = ''.join(filter(str.isdigit, amount_str))
        if not amount_str:
            return Decimal('0.00')
        try:
            return Decimal(amount_str) / 100
        except InvalidOperation:
            return Decimal('0.00')

if __name__ == '__main__':
    import sys
    import json
    import csv
    import argparse
    from dataclasses import asdict

    parser = argparse.ArgumentParser(description='Parse Norma 43 banking files.')
    parser.add_argument('file', help='Path to the Norma 43 file')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file path (optional)')

    args = parser.parse_args()

    n43_parser = Norma43Parser(args.file)
    data = n43_parser.parse()
    
    def json_serial(obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if isinstance(obj, Decimal):
            return float(obj)
        raise TypeError (f"Type {type(obj)} not serializable")

    if args.format == 'json':
        # Convert dataclasses to dict for JSON serialization
        json_data = [asdict(acc) for acc in data]
        output_str = json.dumps(json_data, default=json_serial, indent=2)
        if args.output:
            with open(args.output, 'w') as f: f.write(output_str)
        else:
            print(output_str)

    elif args.format == 'csv':
        flat_data = []
        for acc in data:
            for tx in acc.transactions:
                flat_data.append({
                    'bank': acc.bank,
                    'branch': acc.branch,
                    'account': acc.account_number,
                    'owner': acc.owner,
                    'date': tx.date,
                    'amount': tx.amount,
                    'document': tx.document,
                    'ref1': tx.reference1,
                    'ref2': tx.reference2,
                    'description': tx.full_description
                })
        
        if flat_data:
            keys = flat_data[0].keys()
            if args.output:
                with open(args.output, 'w', newline='') as f:
                    csv.DictWriter(f, fieldnames=keys).writeheader()
                    csv.DictWriter(f, fieldnames=keys).writerows(flat_data)
            else:
                writer = csv.DictWriter(sys.stdout, fieldnames=keys)
                writer.writeheader()
                writer.writerows(flat_data)

    else:
        for acc in data:
            print(f"Account: {acc.bank}-{acc.branch}-{acc.account_number}")
            print(f"Owner: {acc.owner}")
            print(f"Initial Balance: {acc.initial_balance:12.2f}")
            print(f"Final Balance:   {acc.final_balance:12.2f}" if acc.final_balance else "Final Balance: N/A")
            print(f"Transactions: {len(acc.transactions)}")
            print(f"{'Date':10} | {'Amount':10} | {'Description'}")
            print("-" * 60)
            for tx in acc.transactions[:15]: 
                desc = tx.full_description
                if len(desc) > 40: desc = desc[:37] + "..."
                print(f"{str(tx.date):10} | {tx.amount:10.2f} | {desc}")
            if len(acc.transactions) > 15:
                print(f"  ... and {len(acc.transactions) - 15} more transactions.")
            print("-" * 60)
        print(f"Total Records in File: {n43_parser.actual_records_count}")

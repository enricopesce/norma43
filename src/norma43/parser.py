import datetime
from decimal import Decimal, InvalidOperation
from typing import List, Dict, Optional, Any, Union

class Norma43Parser:
    """
    A parser for the Norma 43 banking file format (Spanish standard).
    Follows the official specifications for records 11, 22, 23, 33, and 88.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.accounts: List[Dict[str, Any]] = []
        self.total_records_count: int = 0
        self.actual_records_count: int = 0

    def parse(self) -> List[Dict[str, Any]]:
        """
        Parses the Norma 43 file and returns a list of account dictionaries.
        Each account contains header info, a list of transactions, and footer info.
        """
        current_account: Optional[Dict[str, Any]] = None
        current_transaction: Optional[Dict[str, Any]] = None
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
                        # Header Record
                        current_account = self._parse_header(line)
                        self.accounts.append(current_account)
                        current_transaction = None 
                    
                    elif record_type == '22':
                        # Transaction Record
                        if current_account is not None:
                            current_transaction = self._parse_transaction(line)
                            current_account['transactions'].append(current_transaction)
                    
                    elif record_type == '23':
                        # Complementary Concept Record
                        if current_transaction is not None:
                            self._parse_complementary(line, current_transaction)
                    
                    elif record_type == '33':
                        # Account Footer Record
                        if current_account is not None:
                            self._parse_footer(line, current_account)

                    elif record_type == '88':
                        # End of File Record
                        self._parse_eof(line)

        except FileNotFoundError:
            raise FileNotFoundError(f"File not found: {self.file_path}")
        except Exception as e:
            raise ValueError(f"Error parsing file {self.file_path}: {e}")

        return self.accounts

    def _parse_header(self, line: str) -> Dict[str, Any]:
        return {
            'bank': line[2:6],
            'branch': line[6:10],
            'account_number': line[10:20],
            'start_date': self._parse_date(line[20:26]),
            'end_date': self._parse_date(line[26:32]),
            # Position 33 is sign (1/2), 34-47 is amount
            'initial_balance': self._parse_signed_amount(line[32:47]), 
            'currency': line[47:50],
            'mode': line[50:51],
            'owner': line[51:77].strip(),
            'transactions': []
        }

    def _parse_transaction(self, line: str) -> Dict[str, Any]:
        return {
            'origin_branch': line[6:10],
            'date': self._parse_date(line[10:16]),
            'value_date': self._parse_date(line[16:22]),
            'common_code': line[22:24],
            'own_code': line[24:27],
            # Position 28 is sign (1/2), 29-42 is amount
            'amount': self._parse_signed_amount(line[27:42]),
            'document': line[42:52].strip(),
            'reference1': line[52:64].strip(),
            'reference2': line[64:80].strip(),
            'description': [],
            'description_details': {}
        }

    def _parse_complementary(self, line: str, transaction: Dict[str, Any]) -> None:
        subcode = line[2:4]
        # Two 38-char fields for concept
        concept1 = line[4:42].strip()
        concept2 = line[42:80].strip()
        
        if concept1:
            transaction['description'].append(concept1)
        if concept2:
            transaction['description'].append(concept2)
            
        if subcode not in transaction['description_details']:
            transaction['description_details'][subcode] = []
        if concept1:
            transaction['description_details'][subcode].append(concept1)
        if concept2:
            transaction['description_details'][subcode].append(concept2)

    def _parse_footer(self, line: str, account: Dict[str, Any]) -> None:
        account['num_debits'] = int(line[20:25])
        account['total_debit'] = self._parse_unsigned_amount(line[25:39])
        account['num_credits'] = int(line[39:44])
        account['total_credit'] = self._parse_unsigned_amount(line[44:58])
        # Position 59 is sign (1/2), 60-73 is amount
        account['final_balance'] = self._parse_signed_amount(line[58:73]) 
        account['footer_currency'] = line[73:76]

    def _parse_eof(self, line: str) -> None:
        try:
            # End of file record count (positions 21-26)
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
        """
        Parses amount where first digit is sign:
        1 = Debit (Negative)
        2 = Credit (Positive)
        Format: SNNNNNNNNNNNNNN (15 chars)
        """
        if len(amount_field) < 2:
            return Decimal('0.00')
        
        sign_digit = amount_field[0]
        actual_amount_str = amount_field[1:]
        
        # Remove non-digits if any exist (though strict N43 should be digits)
        actual_amount_str = ''.join(filter(str.isdigit, actual_amount_str))
        
        if not actual_amount_str:
            return Decimal('0.00')
            
        try:
            val = Decimal(actual_amount_str) / 100
            if sign_digit == '1':
                return -val
            return val
        except InvalidOperation:
            return Decimal('0.00')

    @staticmethod
    def _parse_unsigned_amount(amount_str: str) -> Decimal:
        """Parses positive amount without a sign digit."""
        amount_str = ''.join(filter(str.isdigit, amount_str))
        if not amount_str:
            return Decimal('0.00')
        try:
            return Decimal(amount_str) / 100
        except InvalidOperation:
            return Decimal('0.00')

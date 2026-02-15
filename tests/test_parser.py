import unittest
import os
import datetime
from decimal import Decimal
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from norma43.parser import Norma43Parser

class TestNorma43Parser(unittest.TestCase):
    def setUp(self):
        self.test_file = 'test_n43.txt'
        with open(self.test_file, 'w', encoding='latin-1') as f:
            # Header (11)
            header = (
                "11" + 
                "1234" + 
                "5678" + 
                "0123456789" + 
                "220101" + 
                "220131" + 
                "2" + "00000000010000" + # Credit 100.00
                "978" + 
                "3" + 
                "{:<26}".format("TEST USER") + 
                "   \n"
            )
            f.write(header)
            
            # Transaction (22) - Debit 50.00
            tx1 = (
                "22" + 
                "    " + 
                "5678" + 
                "220105" + 
                "220105" + 
                "01" + 
                "001" + 
                "1" + "00000000005000" + # Debit 50.00
                "0001234567" + 
                "000123456789" + 
                "{:<16}".format("REF2EXTENDED") + 
                "\n"
            )
            f.write(tx1)
            
            # Complementary (23)
            comp1 = (
                "23" + 
                "01" + 
                "{:<38}".format("Concept Line 1") + 
                "{:<38}".format("Concept Line 2") + 
                "\n"
            )
            f.write(comp1)
            
            # Transaction (22) - Credit 200.00
            tx2 = (
                "22" + 
                "    " + 
                "5678" + 
                "220110" + 
                "220110" + 
                "01" + 
                "002" + 
                "2" + "00000000020000" + # Credit 200.00
                "0007654321" + 
                "000987654321" + 
                "{:<16}".format("REF2MORE") + 
                "\n"
            )
            f.write(tx2)
            
            # Footer (33)
            footer = (
                "33" + 
                "1234" + 
                "5678" + 
                "0123456789" + 
                "00001" + 
                "00000000005000" + # 50.00
                "00001" + 
                "00000000020000" + # 200.00
                "2" + "00000000025000" + # 250.00
                "978" + 
                "    \n"
            )
            f.write(footer)
            
            # EOF (88)
            eof = (
                "88" + 
                "9" * 18 + 
                "000005" + 
                " " * 54 + 
                "\n"
            )
            f.write(eof)

    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)

    def test_parse_header(self):
        parser = Norma43Parser(self.test_file)
        accounts = parser.parse()
        self.assertEqual(len(accounts), 1)
        acc = accounts[0]
        self.assertEqual(acc.bank, '1234')
        self.assertEqual(acc.branch, '5678')
        self.assertEqual(acc.owner, 'TEST USER')
        self.assertEqual(acc.initial_balance, Decimal('100.00'))
        self.assertEqual(acc.currency, '978')

    def test_parse_transactions(self):
        parser = Norma43Parser(self.test_file)
        accounts = parser.parse()
        txs = accounts[0].transactions
        self.assertEqual(len(txs), 2)
        
        # Tx 1: Debit 50.00
        self.assertEqual(txs[0].amount, Decimal('-50.00'))
        self.assertEqual(txs[0].date, datetime.date(2022, 1, 5))
        self.assertEqual(len(txs[0].description), 2)
        self.assertEqual(txs[0].description[0], 'Concept Line 1')
        self.assertEqual(txs[0].description[1], 'Concept Line 2')
        
        # Tx 2: Credit 200.00
        self.assertEqual(txs[1].amount, Decimal('200.00'))

    def test_parse_footer(self):
        parser = Norma43Parser(self.test_file)
        accounts = parser.parse()
        acc = accounts[0]
        self.assertEqual(acc.num_debits, 1)
        self.assertEqual(acc.total_debit, Decimal('50.00'))
        self.assertEqual(acc.num_credits, 1)
        self.assertEqual(acc.total_credit, Decimal('200.00'))
        self.assertEqual(acc.final_balance, Decimal('250.00'))

    def test_record_count(self):
        parser = Norma43Parser(self.test_file)
        parser.parse()
        self.assertEqual(parser.total_records_count, 5)
        self.assertEqual(parser.actual_records_count, 6)

if __name__ == '__main__':
    unittest.main()

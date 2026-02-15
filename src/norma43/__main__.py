import datetime
from decimal import Decimal
import sys
import json
import csv
import argparse
from dataclasses import asdict
from .parser import Norma43Parser

def json_serial(obj):
    if isinstance(obj, (datetime.date, datetime.datetime)):
        return obj.isoformat()
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError(f"Type {type(obj)} not serializable")

def main():
    parser = argparse.ArgumentParser(description='Parse Norma 43 banking files.')
    parser.add_argument('file', help='Path to the Norma 43 file')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='Output format')
    parser.add_argument('--output', help='Output file path (optional)')

    args = parser.parse_args()

    n43_parser = Norma43Parser(args.file)
    try:
        data = n43_parser.parse()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

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

if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Custom parsers example for Invoice OCR Parser.

This example demonstrates how to create custom parsers by extending
the base parser class for specific document types.
"""

import sys
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

# Add the src directory to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ocrinvoice.parsers.base_parser import BaseParser
from ocrinvoice.core import OCREngine


class ReceiptParser(BaseParser):
    """
    Custom parser for receipt documents.

    This parser is designed to extract information from receipt documents
    including store name, date, items, and total amount.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config or {})
        self.receipt_patterns = {
            "store_name": [
                r"^([A-Z\s&]+)\s*$",  # Store name at top
                r"([A-Z\s&]+)\s*RECEIPT",  # Store name with RECEIPT
                r"([A-Z\s&]+)\s*STORE",  # Store name with STORE
            ],
            "date": [
                r"(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})",  # MM/DD/YYYY or DD/MM/YYYY
                r"(\d{4}-\d{2}-\d{2})",  # YYYY-MM-DD
                r"(\w+\s+\d{1,2},\s+\d{4})",  # Month DD, YYYY
            ],
            "total": [
                r"TOTAL[:\s]*\$?(\d+\.\d{2})",
                r"AMOUNT[:\s]*\$?(\d+\.\d{2})",
                r"DUE[:\s]*\$?(\d+\.\d{2})",
                r"\$(\d+\.\d{2})\s*$",  # Amount at end of line
            ],
            "items": [
                r"(\d+)\s+([A-Z\s]+)\s+\$?(\d+\.\d{2})",  # Quantity Item Price
                r"([A-Z\s]+)\s+\$?(\d+\.\d{2})",  # Item Price
            ],
        }

    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """Parse receipt document and return structured data."""
        try:
            # Extract text from PDF
            text = self.ocr_engine.extract_text_from_pdf(pdf_path)

            # Parse the extracted text
            result = {
                "document_type": "receipt",
                "filename": Path(pdf_path).name,
                "store_name": self.extract_store_name(text),
                "date": self.extract_date(text),
                "total": self.extract_total(text),
                "items": self.extract_items(text),
                "raw_text": text[:500] + "..." if len(text) > 500 else text,
                "confidence": 0.8,  # Placeholder confidence score
            }

            return result

        except Exception as e:
            raise ValueError(f"Error parsing receipt: {e}")

    def extract_store_name(self, text: str) -> Optional[str]:
        """Extract store name from receipt text."""
        lines = text.split("\n")

        # Try to find store name in first few lines
        for line in lines[:5]:
            line = line.strip()
            for pattern in self.receipt_patterns["store_name"]:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    return match.group(1).strip()

        return None

    def extract_date(self, text: str) -> Optional[str]:
        """Extract date from receipt text."""
        for pattern in self.receipt_patterns["date"]:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    def extract_total(self, text: str) -> Optional[str]:
        """Extract total amount from receipt text."""
        for pattern in self.receipt_patterns["total"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        return None

    def extract_items(self, text: str) -> List[Dict[str, Any]]:
        """Extract individual items from receipt text."""
        items = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            # Try to match item patterns
            for pattern in self.receipt_patterns["items"]:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    if len(match.groups()) == 3:
                        # Quantity, Item, Price
                        items.append(
                            {
                                "quantity": int(match.group(1)),
                                "description": match.group(2).strip(),
                                "price": f"${match.group(3)}",
                            }
                        )
                    elif len(match.groups()) == 2:
                        # Item, Price
                        items.append(
                            {
                                "quantity": 1,
                                "description": match.group(1).strip(),
                                "price": f"${match.group(2)}",
                            }
                        )
                    break

        return items


class BankStatementParser(BaseParser):
    """
    Custom parser for bank statement documents.

    This parser extracts account information, statement period,
    and transaction details from bank statements.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config or {})
        self.statement_patterns = {
            "account_number": [
                r"ACCOUNT[:\s]*(\d{4}[-*]\d{4}[-*]\d{4}[-*]\d{4})",
                r"ACCT[:\s]*(\d{4}[-*]\d{4}[-*]\d{4}[-*]\d{4})",
                r"(\d{4}[-*]\d{4}[-*]\d{4}[-*]\d{4})",
            ],
            "statement_period": [
                r"STATEMENT\s+PERIOD[:\s]*(\w+\s+\d{1,2},\s+\d{4})\s*-\s*(\w+\s+\d{1,2},\s+\d{4})",
                r"(\w+\s+\d{1,2},\s+\d{4})\s*-\s*(\w+\s+\d{1,2},\s+\d{4})",
            ],
            "balance": [
                r"BALANCE[:\s]*\$?([\d,]+\.\d{2})",
                r"CURRENT\s+BALANCE[:\s]*\$?([\d,]+\.\d{2})",
                r"ENDING\s+BALANCE[:\s]*\$?([\d,]+\.\d{2})",
            ],
            "transactions": [
                r"(\d{1,2}/\d{1,2})\s+([A-Z\s]+)\s+([+-]?\$?[\d,]+\.\d{2})",
                r"(\w+\s+\d{1,2})\s+([A-Z\s]+)\s+([+-]?\$?[\d,]+\.\d{2})",
            ],
        }

    def parse(self, pdf_path: str) -> Dict[str, Any]:
        """Parse bank statement document and return structured data."""
        try:
            # Extract text from PDF
            text = self.ocr_engine.extract_text_from_pdf(pdf_path)

            # Parse the extracted text
            result = {
                "document_type": "bank_statement",
                "filename": Path(pdf_path).name,
                "account_number": self.extract_account_number(text),
                "statement_period": self.extract_statement_period(text),
                "balance": self.extract_balance(text),
                "transactions": self.extract_transactions(text),
                "raw_text": text[:500] + "..." if len(text) > 500 else text,
                "confidence": 0.85,  # Placeholder confidence score
            }

            return result

        except Exception as e:
            raise ValueError(f"Error parsing bank statement: {e}")

    def extract_account_number(self, text: str) -> Optional[str]:
        """Extract account number from statement text."""
        for pattern in self.statement_patterns["account_number"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def extract_statement_period(self, text: str) -> Optional[Dict[str, str]]:
        """Extract statement period from text."""
        for pattern in self.statement_patterns["statement_period"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {"start_date": match.group(1), "end_date": match.group(2)}
        return None

    def extract_balance(self, text: str) -> Optional[str]:
        """Extract current balance from statement text."""
        for pattern in self.statement_patterns["balance"]:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        return None

    def extract_transactions(self, text: str) -> List[Dict[str, Any]]:
        """Extract transactions from statement text."""
        transactions = []
        lines = text.split("\n")

        for line in lines:
            line = line.strip()

            for pattern in self.statement_patterns["transactions"]:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    amount = match.group(3)
                    # Determine if it's a credit or debit
                    is_credit = amount.startswith("+") or amount.startswith("-")

                    transactions.append(
                        {
                            "date": match.group(1),
                            "description": match.group(2).strip(),
                            "amount": amount,
                            "type": "credit" if is_credit else "debit",
                        }
                    )
                    break

        return transactions


def demonstrate_custom_parsers():
    """Demonstrate the custom parsers."""
    print("=== Custom Parsers Demonstration ===")

    # Create custom parsers
    receipt_parser = ReceiptParser()
    statement_parser = BankStatementParser()

    # Example usage (replace with actual PDF files)
    receipt_pdf = "path/to/receipt.pdf"
    statement_pdf = "path/to/statement.pdf"

    # Test receipt parser
    if Path(receipt_pdf).exists():
        print(f"\nParsing receipt: {receipt_pdf}")
        try:
            receipt_result = receipt_parser.parse(receipt_pdf)
            print("Receipt parsing result:")
            print(f"  Store: {receipt_result.get('store_name', 'Not found')}")
            print(f"  Date: {receipt_result.get('date', 'Not found')}")
            print(f"  Total: {receipt_result.get('total', 'Not found')}")
            print(f"  Items: {len(receipt_result.get('items', []))}")
        except Exception as e:
            print(f"Error parsing receipt: {e}")
    else:
        print(f"\nReceipt PDF not found: {receipt_pdf}")

    # Test statement parser
    if Path(statement_pdf).exists():
        print(f"\nParsing bank statement: {statement_pdf}")
        try:
            statement_result = statement_parser.parse(statement_pdf)
            print("Statement parsing result:")
            print(f"  Account: {statement_result.get('account_number', 'Not found')}")
            print(f"  Balance: {statement_result.get('balance', 'Not found')}")
            print(f"  Transactions: {len(statement_result.get('transactions', []))}")
        except Exception as e:
            print(f"Error parsing statement: {e}")
    else:
        print(f"\nStatement PDF not found: {statement_pdf}")


def create_parser_registry():
    """Demonstrate how to create a parser registry."""
    print("\n=== Parser Registry Example ===")

    # Create a registry of parsers
    parser_registry = {
        "receipt": ReceiptParser(),
        "bank_statement": BankStatementParser(),
        "invoice": None,  # Would be InvoiceParser()
        "credit_card": None,  # Would be CreditCardBillParser()
    }

    print("Available parsers:")
    for doc_type, parser in parser_registry.items():
        status = "✓ Available" if parser else "✗ Not implemented"
        print(f"  {doc_type}: {status}")

    return parser_registry


def main():
    """Main function to run custom parser examples."""
    print("Invoice OCR Parser - Custom Parsers Examples")
    print("=" * 60)

    # Demonstrate custom parsers
    demonstrate_custom_parsers()

    # Create parser registry
    parser_registry = create_parser_registry()

    print("\n" + "=" * 60)
    print("Custom parser examples completed!")
    print("=" * 60)
    print("Key points:")
    print("1. Custom parsers extend BaseParser")
    print("2. Implement parse() method for main logic")
    print("3. Use regex patterns for text extraction")
    print("4. Handle errors gracefully")
    print("5. Return structured data consistently")


if __name__ == "__main__":
    main()

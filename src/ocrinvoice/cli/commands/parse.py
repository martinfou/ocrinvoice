"""
Parse command implementation.

This module contains the parse command implementation for
parsing single PDF invoices.
"""

import click
import logging
import json
import csv
from pathlib import Path
from typing import Dict, Any, Optional

from ocrinvoice.parsers.invoice_parser import InvoiceParser
from ocrinvoice.parsers.credit_card_parser import CreditCardBillParser
from ocrinvoice.config import get_config
from ocrinvoice.utils.file_manager import FileManager

logger = logging.getLogger(__name__)


def parse_command(
    pdf_path: str,
    output: Optional[str] = None,
    format: str = "json",
    parser_type: str = "invoice",
) -> Dict[str, Any]:
    """
    Parse a single PDF invoice.

    Args:
        pdf_path: Path to PDF file
        output: Output file path (optional)
        format: Output format (json, csv, xml)
        parser_type: Type of parser to use (invoice, credit_card)

    Returns:
        Parsing result dictionary
    """
    logger.info(f"Parsing PDF: {pdf_path} with {parser_type} parser")

    # Validate input file
    pdf_file = Path(pdf_path)
    if not pdf_file.exists():
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    if not pdf_file.suffix.lower() == ".pdf":
        raise ValueError(f"File must be a PDF: {pdf_path}")

    try:
        # Initialize parser based on type
        if parser_type.lower() == "invoice":
            parser = InvoiceParser()
        elif parser_type.lower() == "credit_card":
            parser = CreditCardBillParser()
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")

        # Parse the PDF
        logger.info(f"Starting parsing with {parser.__class__.__name__}")
        result = parser.parse(str(pdf_file))

        # Handle file renaming if enabled
        config = get_config()
        file_manager = FileManager(config)
        new_path = file_manager.process_file(pdf_file, result)
        
        # Update the result with the new file path if it was renamed
        if new_path != pdf_file:
            result['original_filename'] = pdf_file.name
            result['new_filename'] = new_path.name
            result['file_renamed'] = True
        else:
            result['file_renamed'] = False

        # Format the result
        formatted_result = format_parsing_result(result, pdf_path, parser_type)

        # Save output if specified
        if output:
            save_result(formatted_result, output, format)

        return formatted_result

    except Exception as e:
        logger.error(f"Error parsing PDF {pdf_path}: {e}")
        return {
            "status": "error",
            "filename": pdf_path,
            "parser": parser_type,
            "error": str(e),
            "data": {},
        }


def format_parsing_result(
    parser_result: Dict[str, Any], pdf_path: str, parser_type: str
) -> Dict[str, Any]:
    """
    Format the parser result for CLI output.

    Args:
        parser_result: Raw result from parser
        pdf_path: Path to the PDF file
        parser_type: Type of parser used

    Returns:
        Formatted result dictionary
    """
    # Extract key data from parser result
    data = {}

    if parser_type.lower() == "invoice":
        data = {
            "company": parser_result.get("company", "N/A"),
            "total": parser_result.get("total", "N/A"),
            "date": parser_result.get("date", "N/A"),
            "invoice_number": parser_result.get("invoice_number", "N/A"),
            "confidence": parser_result.get("confidence", 0.0),
            "currency": parser_result.get("currency", "USD"),
            "tax_amount": parser_result.get("tax_amount", "N/A"),
            "subtotal": parser_result.get("subtotal", "N/A"),
        }
    elif parser_type.lower() == "credit_card":
        data = {
            "card_issuer": parser_result.get("card_issuer", "N/A"),
            "account_number": parser_result.get("account_number", "N/A"),
            "statement_date": parser_result.get("statement_date", "N/A"),
            "due_date": parser_result.get("due_date", "N/A"),
            "total_amount": parser_result.get("total_amount", "N/A"),
            "minimum_payment": parser_result.get("minimum_payment", "N/A"),
            "confidence": parser_result.get("confidence", 0.0),
        }

    return {
        "status": "success",
        "filename": Path(pdf_path).name,
        "filepath": pdf_path,
        "parser": parser_type,
        "data": data,
        "raw_result": parser_result,
        "timestamp": parser_result.get("timestamp", ""),
    }


def save_result(result: Dict[str, Any], output_path: str, format: str) -> None:
    """
    Save parsing result to file.

    Args:
        result: Parsing result
        output_path: Output file path
        format: Output format
    """
    logger.info(f"Saving result to: {output_path} (format: {format})")

    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Save based on format
        if format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        elif format.lower() == "csv":
            with open(output_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)

                # Write header
                data = result.get("data", {})
                if data:
                    writer.writerow(["Field", "Value"])
                    for key, value in data.items():
                        writer.writerow([key, value])
                else:
                    writer.writerow(["Status", "Error"])
                    writer.writerow(
                        [
                            result.get("status", "unknown"),
                            result.get("error", "Unknown error"),
                        ]
                    )

        elif format.lower() == "xml":
            save_as_xml(result, output_path)

        else:
            logger.warning(f"Unsupported format: {format}, saving as JSON")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Result saved to: {output_path}")

    except Exception as e:
        logger.error(f"Error saving result to {output_path}: {e}")
        raise


def save_as_xml(result: Dict[str, Any], output_path: str) -> None:
    """
    Save result as XML format.

    Args:
        result: Parsing result
        output_path: Output file path
    """
    try:
        import xml.etree.ElementTree as ET
        from xml.dom import minidom

        # Create root element
        root = ET.Element("invoice_parse_result")

        # Add metadata
        meta = ET.SubElement(root, "metadata")
        ET.SubElement(meta, "filename").text = result.get("filename", "")
        ET.SubElement(meta, "parser").text = result.get("parser", "")
        ET.SubElement(meta, "status").text = result.get("status", "")
        ET.SubElement(meta, "timestamp").text = result.get("timestamp", "")

        # Add data
        data_elem = ET.SubElement(root, "data")
        data = result.get("data", {})
        for key, value in data.items():
            elem = ET.SubElement(data_elem, key.replace(" ", "_").lower())
            elem.text = str(value)

        # Add error if present
        if result.get("error"):
            ET.SubElement(root, "error").text = result.get("error", "")

        # Pretty print XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="  ")

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(xml_str)

    except ImportError:
        logger.warning("XML support not available, saving as JSON instead")
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving XML: {e}")
        raise

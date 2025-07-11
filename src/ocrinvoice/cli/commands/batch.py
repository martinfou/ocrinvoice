"""
Batch command implementation.

This module contains the batch command implementation for
processing multiple PDF invoices.
"""

import logging
import json
import csv
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from ocrinvoice.parsers.invoice_parser import InvoiceParser
from ocrinvoice.parsers.credit_card_parser import CreditCardBillParser
from ocrinvoice.config import get_config
from ocrinvoice.utils.file_manager import FileManager

logger = logging.getLogger(__name__)


def batch_command(
    folder_path: str,
    output: Optional[str] = None,
    format: str = "csv",
    parser_type: str = "invoice",
    recursive: bool = False,
    document_type: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Process multiple PDF invoices in batch.

    Args:
        folder_path: Path to folder containing PDFs
        output: Output file path (optional)
        format: Output format (json, csv)
        parser_type: Type of parser to use (invoice, credit_card)
        recursive: Process subdirectories recursively

    Returns:
        Batch processing result dictionary
    """
    logger.info(f"Processing batch from folder: {folder_path}")

    # Validate input folder
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Folder not found: {folder_path}")

    # Find PDF files
    if recursive:
        pdf_files = list(folder.rglob("*.pdf"))
    else:
        pdf_files = list(folder.glob("*.pdf"))

    logger.info(f"Found {len(pdf_files)} PDF files")

    if not pdf_files:
        return {
            "status": "warning",
            "processed": 0,
            "successful": 0,
            "errors": 0,
            "message": "No PDF files found in the specified folder",
            "results": [],
            "error_details": [],
        }

    # Initialize parser and file manager
    try:
        if parser_type.lower() == "invoice":
            parser = InvoiceParser()
        elif parser_type.lower() == "credit_card":
            parser = CreditCardBillParser()
        else:
            raise ValueError(f"Unknown parser type: {parser_type}")

        # Initialize file manager for renaming
        config = get_config()

        # Add document type to config if specified
        if document_type:
            config["file_management"] = config.get("file_management", {})
            config["file_management"]["document_type"] = document_type.lower()

        file_manager = FileManager(config)

    except Exception as e:
        logger.error(f"Error initializing parser: {e}")
        return {
            "status": "error",
            "error": f"Failed to initialize parser: {e}",
            "processed": 0,
            "successful": 0,
            "errors": len(pdf_files),
            "results": [],
            "error_details": [],
        }

    results = []
    errors = []
    start_time = datetime.now()

    # Process each PDF
    for i, pdf_file in enumerate(pdf_files, 1):
        try:
            logger.info(f"Processing {i}/{len(pdf_files)}: {pdf_file.name}")

            # Parse the PDF
            result = parser.parse(str(pdf_file))

            # Handle file renaming if enabled
            new_path = file_manager.process_file(pdf_file, result)

            # Update the result with the new file path if it was renamed or dry-run
            if new_path != pdf_file:
                result["original_filename"] = pdf_file.name
                result["new_filename"] = new_path.name
                result["file_renamed"] = True
            else:
                result["file_renamed"] = False

            # Format the result
            formatted_result = format_batch_result(result, pdf_file, parser_type)
            results.append(formatted_result)

            logger.info(f"✓ Processed: {pdf_file.name}")

        except Exception as e:
            error_info = {
                "filename": pdf_file.name,
                "filepath": str(pdf_file),
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
            errors.append(error_info)
            logger.error(f"✗ Error processing {pdf_file.name}: {e}")

    # Calculate processing time
    end_time = datetime.now()
    processing_time = (end_time - start_time).total_seconds()

    # Create batch result
    batch_result = {
        "status": (
            "success" if errors == [] else "partial_success" if results else "error"
        ),
        "processed": len(pdf_files),
        "successful": len(results),
        "errors": len(errors),
        "processing_time_seconds": processing_time,
        "parser_type": parser_type,
        "folder_path": folder_path,
        "recursive": recursive,
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "error_details": errors,
    }

    # Save output if specified
    if output:
        try:
            save_batch_result(batch_result, output, format)
        except Exception as e:
            logger.error(f"Error saving batch result: {e}")
            batch_result["save_error"] = str(e)

    return batch_result


def format_batch_result(
    parser_result: Dict[str, Any], pdf_file: Path, parser_type: str
) -> Dict[str, Any]:
    """
    Format a single parsing result for batch output.

    Args:
        parser_result: Raw result from parser
        pdf_file: Path to the PDF file
        parser_type: Type of parser used

    Returns:
        Formatted result dictionary
    """
    # Extract key data from parser result
    data = {}

    if parser_type.lower() == "invoice":
        data = {
            "filename": pdf_file.name,
            "filepath": str(pdf_file),
            "company": parser_result.get("company", "N/A"),
            "total": parser_result.get("total", "N/A"),
            "date": parser_result.get("date", "N/A"),
            "invoice_number": parser_result.get("invoice_number", "N/A"),
            "confidence": parser_result.get("confidence", 0.0),
            "currency": parser_result.get("currency", "USD"),
            "tax_amount": parser_result.get("tax_amount", "N/A"),
            "subtotal": parser_result.get("subtotal", "N/A"),
            "status": "success",
        }
    elif parser_type.lower() == "credit_card":
        data = {
            "filename": pdf_file.name,
            "filepath": str(pdf_file),
            "card_issuer": parser_result.get("card_issuer", "N/A"),
            "account_number": parser_result.get("account_number", "N/A"),
            "statement_date": parser_result.get("statement_date", "N/A"),
            "due_date": parser_result.get("due_date", "N/A"),
            "total_amount": parser_result.get("total_amount", "N/A"),
            "minimum_payment": parser_result.get("minimum_payment", "N/A"),
            "confidence": parser_result.get("confidence", 0.0),
            "status": "success",
        }

    return {
        **data,
        "timestamp": parser_result.get("timestamp", datetime.now().isoformat()),
        "raw_result": parser_result,
        "original_filename": parser_result.get("original_filename"),
        "new_filename": parser_result.get("new_filename"),
        "file_renamed": parser_result.get("file_renamed", False),
    }


def save_batch_result(result: Dict[str, Any], output_path: str, format: str) -> None:
    """
    Save batch processing result to file.

    Args:
        result: Batch processing result
        output_path: Output file path
        format: Output format
    """
    logger.info(f"Saving batch result to: {output_path} (format: {format})")

    # Create output directory if needed
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Save based on format
        if format.lower() == "json":
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        elif format.lower() == "csv":
            save_batch_as_csv(result, output_path)

        else:
            logger.warning(f"Unsupported format: {format}, saving as JSON")
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(result, f, indent=2, ensure_ascii=False)

        logger.info(f"Batch result saved to: {output_path}")

    except Exception as e:
        logger.error(f"Error saving batch result to {output_path}: {e}")
        raise


def save_batch_as_csv(result: Dict[str, Any], output_path: str) -> None:
    """
    Save batch result as CSV format.

    Args:
        result: Batch processing result
        output_path: Output file path
    """
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write summary header
        writer.writerow(["BATCH PROCESSING SUMMARY"])
        writer.writerow([])
        writer.writerow(["Total Files Processed", result.get("processed", 0)])
        writer.writerow(["Successful", result.get("successful", 0)])
        writer.writerow(["Errors", result.get("errors", 0)])
        writer.writerow(
            ["Processing Time (seconds)", result.get("processing_time_seconds", 0)]
        )
        writer.writerow(["Parser Type", result.get("parser_type", "unknown")])
        writer.writerow(["Folder Path", result.get("folder_path", "")])
        writer.writerow(["Recursive", result.get("recursive", False)])
        writer.writerow(["Timestamp", result.get("timestamp", "")])
        writer.writerow([])

        # Write results header
        results = result.get("results", [])
        if results:
            # Determine headers from first result
            first_result = results[0]
            headers = [
                key
                for key in first_result.keys()
                if key not in ["raw_result", "timestamp"]
            ]

            writer.writerow(headers)

            # Write results
            for item in results:
                row = []
                for header in headers:
                    value = item.get(header, "")
                    # Convert complex objects to string
                    if isinstance(value, (dict, list)):
                        value = str(value)
                    row.append(value)
                writer.writerow(row)

        # Write errors if any
        errors = result.get("error_details", [])
        if errors:
            writer.writerow([])
            writer.writerow(["ERRORS"])
            writer.writerow(["Filename", "Filepath", "Error", "Timestamp"])
            for error in errors:
                writer.writerow(
                    [
                        error.get("filename", ""),
                        error.get("filepath", ""),
                        error.get("error", ""),
                        error.get("timestamp", ""),
                    ]
                )

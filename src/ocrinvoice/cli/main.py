"""
Main CLI entry point for Invoice OCR Parser.

This module provides the main CLI interface for the Invoice OCR Parser
using the Click framework.
"""

import click
import logging
import sys
from pathlib import Path
from typing import Optional

from ocrinvoice.config import get_config
from ocrinvoice.cli.commands.parse import parse_command
from ocrinvoice.cli.commands.batch import batch_command
from ocrinvoice.cli.commands.test import test_command

# Import BusinessMappingManager for managing business mappings
try:
    from ocrinvoice.business.business_mapping_manager import BusinessMappingManager
except ImportError:
    # Fallback if the module doesn't exist in the new structure
    BusinessMappingManager = None

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def setup_logging(verbose: bool = False, debug: bool = False) -> None:
    """Setup logging configuration based on verbosity level."""
    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        logging.getLogger().setLevel(logging.INFO)
    else:
        logging.getLogger().setLevel(logging.WARNING)


@click.group()
@click.version_option(version="1.0.0")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--debug", is_flag=True, help="Enable debug output")
@click.option("--config", "-c", help="Path to configuration file")
def cli(verbose: bool, debug: bool, config: Optional[str]):
    """
    Invoice OCR Parser - Extract structured data from PDF invoices using OCR.

    This tool can parse individual PDF invoices or process multiple files in batch.
    It supports various output formats including JSON, CSV, and XML.
    """
    # Setup logging
    setup_logging(verbose, debug)

    # Load configuration
    if config:
        config_path = Path(config)
        if not config_path.exists():
            click.echo(f"Error: Configuration file not found: {config}", err=True)
            sys.exit(1)

    logger.debug("CLI initialized with verbose=%s, debug=%s", verbose, debug)


@cli.command()
@click.argument("pdf_path", type=click.Path(exists=True, path_type=Path))
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file path"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv", "xml"], case_sensitive=False),
    default="json",
    help="Output format (default: json)",
)
@click.option(
    "--parser",
    "-p",
    type=click.Choice(["invoice", "credit_card"], case_sensitive=False),
    default="invoice",
    help="Parser type to use (default: invoice)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--show-text", "-t", is_flag=True, help="Show extracted raw text")
@click.option("--rename", is_flag=True, help="Rename file based on extracted data")
@click.option(
    "--rename-dry-run", is_flag=True, help="Preview rename operation without executing"
)
@click.option(
    "--document-type",
    "-d",
    type=click.Choice(["facture", "relevé"], case_sensitive=False),
    help="Document type to prefix filename (facture or relevé)",
)
def parse(
    pdf_path: Path,
    output: Optional[Path],
    format: str,
    parser: str,
    verbose: bool,
    show_text: bool,
    rename: bool,
    rename_dry_run: bool,
    document_type: Optional[str],
):
    """
    Parse a single PDF invoice.

    PDF_PATH: Path to the PDF file to parse
    """
    try:
        if verbose:
            setup_logging(verbose=True)

        click.echo(f"Parsing PDF: {pdf_path}")
        click.echo(f"Parser: {parser}")
        click.echo(f"Output format: {format}")

        if output:
            click.echo(f"Output file: {output}")

        # Update config for rename options if specified
        config = get_config()
        if rename or rename_dry_run:
            config["file_management"] = config.get("file_management", {})
            config["file_management"]["rename_files"] = True
            if rename_dry_run:
                config["file_management"]["rename_dry_run"] = True

        # Add document type to config if specified
        if document_type:
            config["file_management"] = config.get("file_management", {})
            config["file_management"]["document_type"] = document_type.lower()

        # Call the actual parse command
        result = parse_command(
            str(pdf_path),
            str(output) if output else None,
            format,
            parser,
            document_type,
        )

        # Show raw text if requested
        if show_text and result.get("status") == "success":
            raw_result = result.get("raw_result", {})
            # Try different possible field names for extracted text
            extracted_text = (
                raw_result.get("extracted_text", "")
                or raw_result.get("raw_text", "")
                or raw_result.get("text", "")
            )
            if extracted_text:
                click.echo("\n📄 Extracted Raw Text:")
                click.echo("=" * 50)
                click.echo(extracted_text)
                click.echo("=" * 50)
            else:
                click.echo("\n⚠️  No raw text available in result")

        if result.get("status") == "success":
            click.echo("✓ PDF parsed successfully")

            # Display filename information if file was renamed or dry-run
            if result.get("file_renamed") or rename_dry_run:
                original_filename = result.get("original_filename", pdf_path.name)
                new_filename = result.get("new_filename", "unknown")
                if rename_dry_run:
                    click.echo("\n📁 File would be renamed:")
                else:
                    click.echo("\n📁 File renamed:")
                click.echo(f"  From: {original_filename}")
                click.echo(f"  To:   {new_filename}")

            # Display summary
            data = result.get("data", {})
            if data:
                click.echo("\nExtracted Data:")
                click.echo(f"  Company: {data.get('company', 'N/A')}")
                click.echo(f"  Total: {data.get('total', 'N/A')}")
                click.echo(f"  Date: {data.get('date', 'N/A')}")
                click.echo(f"  Invoice #: {data.get('invoice_number', 'N/A')}")
                click.echo(f"  Confidence: {data.get('confidence', 'N/A')}")
        else:
            click.echo(
                "\u2717 Parsing failed: {}".format(
                    result.get("error", "Unknown error")
                ),
                err=True,
            )
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error parsing PDF: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.argument(
    "folder_path", type=click.Path(exists=True, file_okay=False, path_type=Path)
)
@click.option(
    "--output", "-o", type=click.Path(path_type=Path), help="Output file path"
)
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "csv"], case_sensitive=False),
    default="csv",
    help="Output format (default: csv)",
)
@click.option(
    "--parser",
    "-p",
    type=click.Choice(["invoice", "credit_card"], case_sensitive=False),
    default="invoice",
    help="Parser type to use (default: invoice)",
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option(
    "--recursive", "-r", is_flag=True, help="Process subdirectories recursively"
)
@click.option("--rename", is_flag=True, help="Rename files based on extracted data")
@click.option(
    "--rename-dry-run", is_flag=True, help="Preview rename operations without executing"
)
@click.option(
    "--document-type",
    "-d",
    type=click.Choice(["facture", "relevé"], case_sensitive=False),
    help="Document type to prefix filename (facture or relevé)",
)
def batch(
    folder_path: Path,
    output: Optional[Path],
    format: str,
    parser: str,
    verbose: bool,
    recursive: bool,
    rename: bool,
    rename_dry_run: bool,
    document_type: Optional[str],
):
    """
    Process multiple PDF invoices in batch.

    FOLDER_PATH: Path to folder containing PDF files
    """
    try:
        if verbose:
            setup_logging(verbose=True)

        click.echo(f"Processing folder: {folder_path}")
        click.echo(f"Parser: {parser}")
        click.echo(f"Output format: {format}")
        click.echo(f"Recursive: {recursive}")

        if output:
            click.echo(f"Output file: {output}")

        # Update config for rename options if specified
        config = get_config()
        if rename or rename_dry_run:
            config["file_management"] = config.get("file_management", {})
            config["file_management"]["rename_files"] = True
            if rename_dry_run:
                config["file_management"]["rename_dry_run"] = True

        # Add document type to config if specified
        if document_type:
            config["file_management"] = config.get("file_management", {})
            config["file_management"]["document_type"] = document_type.lower()

        # Call the actual batch command
        result = batch_command(
            str(folder_path),
            str(output) if output else None,
            format,
            parser,
            recursive,
            document_type,
        )

        if result.get("status") == "success":
            click.echo("✓ Batch processing completed")

            # Display summary
            click.echo("\nProcessing Summary:")
            click.echo(f"  Total files: {result.get('processed', 0)}")
            click.echo(f"  Successful: {result.get('successful', 0)}")
            click.echo(f"  Errors: {result.get('errors', 0)}")

            # Display renamed files information
            renamed_files = []
            for file_result in result.get("results", []):
                if file_result.get("file_renamed") or rename_dry_run:
                    renamed_files.append(
                        {
                            "original": file_result.get("original_filename", "unknown"),
                            "new": file_result.get("new_filename", "unknown"),
                        }
                    )

            if renamed_files:
                if rename_dry_run:
                    click.echo("\n📁 Files that would be renamed:")
                else:
                    click.echo("\n📁 Renamed Files:")
                for file_info in renamed_files:
                    click.echo(f"  {file_info['original']} → {file_info['new']}")

            if result.get("errors", 0) > 0:
                click.echo("\nFiles with errors:")
                for error in result.get("error_details", []):
                    click.echo(
                        "  \u2717 {}: {}".format(
                            error.get("filename", "Unknown"),
                            error.get("error", "Unknown error"),
                        )
                    )
        else:
            click.echo(
                "\u2717 Batch processing failed: {}".format(
                    result.get("error", "Unknown error")
                ),
                err=True,
            )
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error in batch processing: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--test-data", type=click.Path(exists=True, path_type=Path), help="Test data file"
)
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose output")
@click.option("--coverage", is_flag=True, help="Generate coverage report")
@click.option(
    "--output",
    "-o",
    type=click.Path(path_type=Path),
    help="Output file for test results",
)
def test(
    test_data: Optional[Path], verbose: bool, coverage: bool, output: Optional[Path]
):
    """
    Run the test suite to verify functionality.
    """
    try:
        if verbose:
            setup_logging(verbose=True)

        click.echo("Running test suite...")

        if test_data:
            click.echo(f"Using test data: {test_data}")

        if coverage:
            click.echo("Coverage reporting enabled")

        if output:
            click.echo(f"Test results will be saved to: {output}")

        # Call the actual test command
        result = test_command(
            str(test_data) if test_data else None,
            verbose,
            coverage,
            str(output) if output else None,
        )

        if result.get("status") == "success":
            click.echo("✓ All tests passed")
        else:
            click.echo("\u2717 Some tests failed", err=True)
            sys.exit(1)

    except Exception as e:
        logger.error(f"Error running tests: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config", "-c", type=click.Path(path_type=Path), help="Configuration file path"
)
def config(config: Optional[Path]):
    """
    Show current configuration and available options.
    """
    try:
        current_config = get_config()

        click.echo("Current Configuration:")
        click.echo("=" * 50)

        for key, value in current_config.items():
            if isinstance(value, dict):
                click.echo(f"{key}:")
                for subkey, subvalue in value.items():
                    click.echo(f"  {subkey}: {subvalue}")
            else:
                click.echo(f"{key}: {value}")

        click.echo("\nConfiguration can be set via:")
        click.echo("- Environment variables (OCRINVOICE_* prefix)")
        click.echo("- Configuration file (YAML format)")
        click.echo("- Command line options")

    except Exception as e:
        logger.error(f"Error showing configuration: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def gui():
    """Launch the GUI for managing business mappings"""
    try:
        from ocrinvoice.gui.main_window import main

        main()
    except ImportError as e:
        click.echo(f"Error: GUI not available - {e}", err=True)
        click.echo("Make sure PyQt6 is installed: pip install PyQt6", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error launching GUI: {e}", err=True)
        sys.exit(1)


@cli.group()
def mappings():
    """Manage business name mappings (business_mappings.json)"""
    if BusinessMappingManager is None:
        click.echo(
            "Error: BusinessMappingManager not available. Make sure business_mapping_manager.py is in your project.",  # noqa: E501
            err=True,
        )
        sys.exit(1)


@mappings.command("list")
def list_mappings():
    """List all official business names and mappings"""
    try:
        manager = BusinessMappingManager()

        click.echo("📋 Business Mappings Configuration")
        click.echo("=" * 50)

        # Official business names
        click.echo("\n🏢 Official Business Names:")
        official_names = manager.get_official_names()
        if official_names:
            for name in official_names:
                click.echo(f"  • {name}")
        else:
            click.echo("  (none defined)")

        # Exact matches
        click.echo("\n🎯 Exact Matches:")
        exact_matches = manager.config.get("exact_matches", {})
        if exact_matches:
            for mapping, name in exact_matches.items():
                click.echo("Mapping: {}".format(mapping))
                click.echo("Name: {}".format(name))
        else:
            click.echo("  (none defined)")

        # Partial matches
        click.echo("\n🔍 Partial Matches:")
        partial_matches = manager.config.get("partial_matches", {})
        if partial_matches:
            for mapping, name in partial_matches.items():
                click.echo(f"Mapping: {mapping}")
                click.echo(f"Name: {name}")
        else:
            click.echo("  (none defined)")

        # Fuzzy candidates
        click.echo("\n🔎 Fuzzy Match Candidates:")
        fuzzy_candidates = manager.config.get("fuzzy_candidates", [])
        if fuzzy_candidates:
            for name in fuzzy_candidates:
                click.echo(f"  • {name}")
        else:
            click.echo("  (none defined)")

        # Statistics
        stats = manager.get_stats()
        click.echo("\n📊 Statistics:")
        click.echo(f"  Total canonical names: {stats['official_names']}")
        click.echo(f"  Total exact matches: {stats['exact_matches']}")
        click.echo(f"  Total partial matches: {stats['partial_matches']}")
        click.echo(f"  Total fuzzy candidates: {stats['fuzzy_candidates']}")
        click.echo(f"  Total unique businesses: {stats['total_businesses']}")

    except Exception as e:
        logger.error(f"Error listing mappings: {e}")
        click.echo(f"\u2717 Error: {e}", err=True)
        sys.exit(1)


@mappings.command("add")
@click.argument("mapping")
@click.argument("official_name")
@click.option(
    "--type",
    "match_type",
    default="exact_matches",
    type=click.Choice(["exact_matches", "partial_matches"]),
    help="Type of match (default: exact_matches)",
)
def add_mapping(mapping: str, official_name: str, match_type: str):
    """Add a new mapping for a business"""
    try:
        manager = BusinessMappingManager()

        # Check if canonical name exists
        if not manager.is_official_name(official_name):
            click.echo(
                f"❌ Error: '{official_name}' is not a canonical business name.",
                err=True,
            )
            click.echo("Use 'ocrinvoice mappings add-official' to add it first.")
            return

        # Check if mapping already exists
        if mapping in manager.config.get(match_type, {}):
            click.echo(f"⚠️  Warning: Mapping '{mapping}' already exists in {match_type}")
            if not click.confirm("Do you want to overwrite it?"):
                return

        # Add the mapping
        manager.add_mapping(mapping, official_name, match_type)
        click.echo(f"✅ Added mapping '{mapping}' → '{official_name}' ({match_type})")

    except Exception as e:
        logger.error(f"Error adding mapping: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@mappings.command("add-official")
@click.argument("name")
def add_official(name: str):
    """Add a new canonical business name"""
    try:
        manager = BusinessMappingManager()

        # Check if name already exists
        if manager.is_official_name(name):
            click.echo(f"ℹ️  '{name}' is already a canonical business name.")
            return

        # Add the canonical name
        manager.official_names.add(name)
        manager.config["official_names"] = sorted(manager.official_names)
        manager._save_config()
        click.echo(f"✅ Added canonical business name: '{name}'")

    except Exception as e:
        logger.error(f"Error adding canonical name: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@mappings.command("remove")
@click.argument("mapping")
@click.option(
    "--type",
    "match_type",
    default="exact_matches",
    type=click.Choice(["exact_matches", "partial_matches"]),
    help="Type of match (default: exact_matches)",
)
def remove_mapping(mapping: str, match_type: str):
    """Remove a mapping"""
    try:
        manager = BusinessMappingManager()

        # Check if mapping exists
        if mapping not in manager.config.get(match_type, {}):
            click.echo(f"❌ Error: Mapping '{mapping}' not found in {match_type}")
            return

        # Confirm removal
        official_name = manager.config[match_type][mapping]
        if not click.confirm(
            f"Remove mapping '{mapping}' → '{official_name}' from {match_type}?"
        ):
            return

        # Remove the mapping
        del manager.config[match_type][mapping]
        manager._save_config()
        click.echo(f"✅ Removed mapping '{mapping}' from {match_type}")

    except Exception as e:
        logger.error(f"Error removing mapping: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@mappings.command("remove-official")
@click.argument("name")
def remove_official(name: str):
    """Remove a canonical business name"""
    try:
        manager = BusinessMappingManager()

        # Check if name exists
        if not manager.is_official_name(name):
            click.echo(f"❌ Error: '{name}' is not a canonical business name.")
            return

        # Check for dependencies
        dependencies = []
        for match_type in ["exact_matches", "partial_matches"]:
            for mapping, official_name in manager.config.get(match_type, {}).items():
                if official_name == name:
                    dependencies.append(f"{mapping} ({match_type})")

        if dependencies:
            click.echo(f"⚠️  Warning: '{name}' is referenced by the following mappings:")
            for dep in dependencies:
                click.echo(f"  • {dep}")
            if not click.confirm(
                "Remove anyway? This will also remove all dependent mappings."
            ):
                return

            # Remove dependent mappings
            for match_type in ["exact_matches", "partial_matches"]:
                mappings_to_remove = [
                    mapping
                    for mapping, official_name in manager.config.get(
                        match_type, {}
                    ).items()
                    if official_name == name
                ]
                for mapping in mappings_to_remove:
                    del manager.config[match_type][mapping]

        # Remove the canonical name
        manager.official_names.remove(name)
        manager.config["official_names"] = sorted(manager.official_names)
        manager._save_config()
        click.echo(f"✅ Removed canonical business name: '{name}'")

    except Exception as e:
        logger.error(f"Error removing canonical name: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


@mappings.command("test")
@click.argument("text")
def test_mapping(text: str):
    """Test how a text would be matched against business mappings"""
    try:
        manager = BusinessMappingManager()
        result = manager.find_business_match(text)

        if result:
            business_name, match_type, confidence = result
            click.echo(f"✅ Match found!")
            click.echo(f"  Text: '{text}'")
            click.echo(f"  Business: '{business_name}'")
            click.echo(f"  Match type: {match_type}")
            click.echo(f"  Confidence: {confidence:.2f}")
        else:
            click.echo(f"❌ No match found for text: '{text}'")
            click.echo("\n💡 Suggestions:")
            click.echo("  • Add a new mapping with 'ocrinvoice mappings add'")
            click.echo(
                "  • Add a new canonical name with 'ocrinvoice mappings add-official'"
            )

    except Exception as e:
        logger.error(f"Error testing mapping: {e}")
        click.echo(f"✗ Error: {e}", err=True)
        sys.exit(1)


if __name__ == "__main__":
    cli()

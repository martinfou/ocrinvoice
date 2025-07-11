"""
File management utilities for OCR invoice parser.
Handles file renaming based on extracted invoice data.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional


class FileManager:
    """Manages file operations for invoice PDFs."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize FileManager with configuration."""
        self.config = config
        self.file_config = config.get('file_management', {})
        self.rename_enabled = self.file_config.get('rename_files', False)
        self.rename_format = self.file_config.get('rename_format', '{date}_{company}_{total}.pdf')
        self.dry_run = self.file_config.get('rename_dry_run', False)
        self.backup_original = self.file_config.get('backup_original', False)
        self.document_type = self.file_config.get('document_type')
    
    def safe_filename(self, text: str) -> str:
        """Convert text to a safe filename by removing/replacing invalid characters."""
        if not text:
            return 'unknown'
            
        # Replace invalid filename characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            text = text.replace(char, '_')
        
        # Replace spaces with underscores
        text = text.replace(' ', '_')
        
        # Remove multiple consecutive underscores
        while '__' in text:
            text = text.replace('__', '_')
        
        # Remove leading/trailing underscores
        text = text.strip('_')
        
        return text or 'unknown'
    
    def format_filename(self, extracted_data: Dict[str, Any]) -> str:
        """Format filename based on extracted data and configured format."""
        # Extract data with fallbacks
        company = extracted_data.get('company', 'unknown')
        total = extracted_data.get('total')
        date_str = extracted_data.get('date', 'unknown')
        
        # Handle missing or invalid data
        if not company or company == 'unknown':
            company = 'unknown'
        
        if not total:
            total = 'unknown'
        else:
            # Format total as currency
            try:
                total = f"${float(total):.2f}"
            except (ValueError, TypeError):
                total = 'unknown'
        
        if not date_str or date_str == 'unknown':
            date_str = 'unknown'
        else:
            # Convert ISO date to YYYY-MM-DD format
            try:
                date_obj = datetime.fromisoformat(date_str)
                date_str = date_obj.strftime('%Y-%m-%d')
            except (ValueError, TypeError):
                date_str = 'unknown'
        
        # Format the filename
        filename = self.rename_format.format(
            date=date_str,
            company=company,
            total=total
        )
        
        # Add document type prefix if specified
        if self.document_type:
            filename = f"{self.document_type}_{filename}"
        
        # Make it safe
        return self.safe_filename(filename)
    
    def rename_invoice_file(self, pdf_path: Path, extracted_data: Dict[str, Any]) -> Optional[Path]:
        """
        Rename invoice PDF file based on extracted data.
        
        Args:
            pdf_path: Path to the PDF file
            extracted_data: Dictionary containing extracted invoice data
            
        Returns:
            New path if renamed, None if not renamed or error
        """
        if not self.rename_enabled:
            return None
        
        if not pdf_path.exists():
            return None
        
        if not pdf_path.suffix.lower() == '.pdf':
            return None
        
        try:
            # Generate new filename
            new_filename = self.format_filename(extracted_data)
            new_path = pdf_path.parent / new_filename
            
            # Check if target file already exists
            if new_path.exists() and not self.dry_run:
                # Add timestamp to make it unique
                timestamp = datetime.now().strftime('%H%M%S')
                name_without_ext = new_filename[:-4]  # Remove .pdf
                new_filename = f"{name_without_ext}_{timestamp}.pdf"
                new_path = pdf_path.parent / new_filename
            
            if self.dry_run:
                print(f"🔍 DRY RUN - Would rename:")
                print(f"   From: {pdf_path.name}")
                print(f"   To:   {new_filename}")
                doc_type_info = f"Document Type: {self.document_type}, " if self.document_type else ""
                print(f"   Data: {doc_type_info}Date={extracted_data.get('date', 'unknown')}, "
                      f"Company={extracted_data.get('company', 'unknown')}, "
                      f"Total={extracted_data.get('total', 'unknown')}")
                return None
            else:
                # Create backup if enabled
                if self.backup_original:
                    backup_path = pdf_path.parent / f"backup_{pdf_path.name}"
                    shutil.copy2(pdf_path, backup_path)
                
                # Rename the file
                pdf_path.rename(new_path)
                print(f"✅ Renamed: {pdf_path.name} → {new_filename}")
                doc_type_info = f"Document Type: {self.document_type}, " if self.document_type else ""
                print(f"   Data: {doc_type_info}Date={extracted_data.get('date', 'unknown')}, "
                      f"Company={extracted_data.get('company', 'unknown')}, "
                      f"Total={extracted_data.get('total', 'unknown')}")
                return new_path
                
        except Exception as e:
            print(f"❌ Error renaming {pdf_path.name}: {e}")
            return None
    
    def process_file(self, pdf_path: Path, extracted_data: Dict[str, Any]) -> Optional[Path]:
        """
        Process a single file with all file management operations.
        
        Args:
            pdf_path: Path to the PDF file
            extracted_data: Dictionary containing extracted invoice data
            
        Returns:
            New path if file was renamed, original path otherwise
        """
        if self.rename_enabled:
            return self.rename_invoice_file(pdf_path, extracted_data) or pdf_path
        return pdf_path 
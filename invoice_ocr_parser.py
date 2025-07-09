#!/usr/bin/env python3
"""
Invoice OCR Parser Core Module
Extracts company names and invoice totals from scanned PDF invoices
"""

import os
import re
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime

# Conditional imports for optional dependencies
try:
    import cv2
    import numpy as np
    import pandas as pd
    from PIL import Image
    import pytesseract
    from pdf2image import convert_from_path
    import pdfplumber
    from PyPDF2 import PdfReader
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    DEPENDENCIES_AVAILABLE = False
    logging.warning(f"Some dependencies are missing: {e}. OCR functionality will be limited.")

# Import business alias manager
try:
    from business_alias_manager import BusinessAliasManager
except ImportError:
    # If the module doesn't exist, create a simple fallback
    class BusinessAliasManager:
        def __init__(self, alias_file="business_aliases.json"):
            self.alias_file = alias_file
            
        def find_business_match(self, text):
            return None

class FuzzyMatcher:
    """Fuzzy string matching using Soundex and Levenshtein distance"""
    
    @staticmethod
    def soundex(word: str) -> str:
        """Generate Soundex code for a word"""
        if not word:
            return ""
        
        # Soundex mapping
        soundex_map = {
            'B': '1', 'F': '1', 'P': '1', 'V': '1',
            'C': '2', 'G': '2', 'J': '2', 'K': '2', 'Q': '2', 'S': '2', 'X': '2', 'Z': '2',
            'D': '3', 'T': '3',
            'L': '4',
            'M': '5', 'N': '5',
            'R': '6'
        }
        
        # Convert to uppercase and get first letter
        word = word.upper()
        first_letter = word[0]
        
        # Generate code
        code = first_letter
        prev_code = soundex_map.get(first_letter, '')
        
        for char in word[1:]:
            if char in soundex_map:
                current_code = soundex_map[char]
                if current_code != prev_code:
                    code += current_code
                    prev_code = current_code
        
        # Pad with zeros and return first 4 characters
        code = code + '0000'
        return code[:4]
    
    @staticmethod
    def levenshtein_distance(s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings"""
        if len(s1) < len(s2):
            return FuzzyMatcher.levenshtein_distance(s2, s1)
        
        if len(s2) == 0:
            return len(s1)
        
        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row
        
        return previous_row[-1]
    
    @staticmethod
    def normalized_levenshtein_distance(s1: str, s2: str) -> float:
        """Calculate normalized Levenshtein distance (0-1, where 0 is identical)"""
        if not s1 and not s2:
            return 0.0
        if not s1 or not s2:
            return 1.0
        
        distance = FuzzyMatcher.levenshtein_distance(s1, s2)
        max_len = max(len(s1), len(s2))
        return distance / max_len
    
    @staticmethod
    def fuzzy_match(target: str, candidates: List[str], threshold: float = 0.3) -> Optional[str]:
        """Find the best fuzzy match for target among candidates"""
        if not target or not candidates:
            return None
        
        best_match = None
        best_score = float('inf')
        
        target_soundex = FuzzyMatcher.soundex(target)
        
        for candidate in candidates:
            # Calculate normalized Levenshtein distance
            distance = FuzzyMatcher.normalized_levenshtein_distance(target, candidate)
            
            # Calculate Soundex similarity
            candidate_soundex = FuzzyMatcher.soundex(candidate)
            soundex_match = target_soundex == candidate_soundex
            
            # Combined score (lower is better)
            score = distance
            if soundex_match:
                score *= 0.5  # Bonus for Soundex match
            
            if score < best_score and score <= threshold:
                best_score = score
                best_match = candidate
        
        return best_match

class InvoiceDatabase:
    """Simple database to store known business names for fallback matching"""
    
    def __init__(self, db_file: str = "invoice_database.json"):
        self.db_file = db_file
        self.database = self._load_database()
    
    def _load_database(self) -> Dict[str, Any]:
        """Load the invoice database from file"""
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logging.warning(f"Could not load invoice database: {e}")
        return {"companies": {}, "company_names": []}
    
    def _save_database(self):
        """Save the invoice database to file"""
        try:
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.database, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logging.error(f"Could not save invoice database: {e}")
    
    def add_company(self, company_name: str, confidence: str = "medium"):
        """Add a new company to the database"""
        if not company_name:
            return
        
        # Normalize company name
        normalized_company = self._normalize_company_name(company_name)
        
        # Store company frequency
        if normalized_company not in self.database["companies"]:
            self.database["companies"][normalized_company] = 0
        self.database["companies"][normalized_company] += 1
        
        # Store unique company names
        if normalized_company not in self.database["company_names"]:
            self.database["company_names"].append(normalized_company)
        
        self._save_database()
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for consistent matching"""
        if not name:
            return ""
        
        # Convert to lowercase and remove extra whitespace
        normalized = name.lower().strip()
        
        # Remove common suffixes
        suffixes = [' inc', ' llc', ' ltd', ' corp', ' corporation', ' company', ' co.']
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)]
        
        return normalized.strip()
    
    def find_company_match(self, text: str) -> Optional[Tuple[str, float, str]]:
        """Find a company match in the database"""
        if not text or not self.database["company_names"]:
            return None
        
        # Try exact match first
        for company in self.database["company_names"]:
            if company.lower() in text.lower():
                return (company, 1.0, "exact_match")
        
        # Try fuzzy match
        best_match = FuzzyMatcher.fuzzy_match(text, self.database["company_names"], threshold=0.3)
        if best_match:
            return (best_match, 0.8, "fuzzy_match")
        
        return None
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics"""
        return {
            "total_companies": len(self.database["company_names"]),
            "company_frequencies": self.database["companies"]
        }

class InvoiceOCRParser:
    """Main class for parsing invoices using OCR"""
    
    def __init__(self, tesseract_path: Optional[str] = None, debug: bool = False, use_database: bool = False):
        """
        Initialize the Invoice OCR Parser
        
        Args:
            tesseract_path: Path to Tesseract executable (optional)
            debug: Enable debug logging
            use_database: Enable invoice database for fallback matching (default: False)
        """
        if not DEPENDENCIES_AVAILABLE:
            raise ImportError("Required dependencies are not available. Please install: opencv-python, numpy, pandas, pillow, pytesseract, pdf2image, pdfplumber, PyPDF2")
        
        self.debug = debug
        self.tesseract_path = tesseract_path
        
        # Initialize invoice database (optional)
        self.use_database = use_database
        if self.use_database:
            self.invoice_db = InvoiceDatabase()
            logging.info("Invoice database initialized")
        else:
            self.invoice_db = None
            logging.info("Invoice database disabled")
        
        # Initialize business alias manager
        self.alias_manager = BusinessAliasManager()
        logging.info("Business alias manager initialized")
        
        # Configure Tesseract path
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
        
        # Configure logging
        logging.basicConfig(
            level=logging.DEBUG if debug else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Test Tesseract installation
        try:
            pytesseract.get_tesseract_version()
            logging.info("Tesseract is properly installed")
        except Exception as e:
            logging.error(f"Tesseract not found: {e}")
            logging.error("Please install Tesseract and ensure it's in your PATH")

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from PDF using multiple methods"""
        try:
            # Try pdfplumber first (better for text-based PDFs)
            with pdfplumber.open(pdf_path) as pdf:
                text = ""
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logging.info(f"Successfully extracted text using pdfplumber from {pdf_path}")
                    return text
            
            # Try PyPDF2 as fallback
            with open(pdf_path, 'rb') as file:
                reader = PdfReader(file)
                text = ""
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
                
                if text.strip():
                    logging.info(f"Successfully extracted text using PyPDF2 from {pdf_path}")
                    return text
            
            # If no text found, return empty string (will trigger OCR)
            logging.warning(f"No text found in PDF, will use OCR: {pdf_path}")
            return ""
            
        except Exception as e:
            logging.error(f"Error extracting text from PDF {pdf_path}: {e}")
            return ""

    def convert_pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to PIL Images"""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)
            logging.info(f"Converted PDF to {len(images)} images: {pdf_path}")
            return images
        except Exception as e:
            logging.error(f"Error converting PDF to images {pdf_path}: {e}")
            return []

    def extract_text_with_ocr(self, images: List[Image.Image]) -> str:
        """Extract text from images using OCR"""
        if not images:
            return ""
        
        all_text = []
        
        for i, image in enumerate(images):
            try:
                text = pytesseract.image_to_string(
                    image, 
                    config='--oem 3 --psm 6',
                    lang='eng+fra'  # English + French
                )
                
                if text.strip():
                    all_text.append(text)
                    
            except Exception as e:
                logging.error(f"Error in OCR for image {i}: {e}")
                continue
        
        # Combine all text
        combined_text = "\n".join(all_text)
        return combined_text

    def extract_company_name(self, text: str, expected_company: str = None) -> str:
        """Extract company name from text using multiple strategies"""
        if not text:
            return "Unknown"
        
        # Split text into lines for analysis
        lines = text.split('\n')
        
        # Keywords that indicate we should skip a line
        exclude_indicators = [
            'TOTAL', 'AMOUNT', 'DUE', 'BALANCE', 'GRAND TOTAL', 'FINAL TOTAL',
            'INVOICE', 'BILL', 'RECEIPT', 'DATE', 'TIME', 'PHONE', 'FAX',
            'EMAIL', 'WEB', 'WWW', 'HTTP', 'HTTPS', 'COM', 'ORG', 'NET',
            'ADDRESS', 'STREET', 'AVENUE', 'BOULEVARD', 'ROAD', 'DRIVE',
            'CITY', 'STATE', 'PROVINCE', 'POSTAL', 'ZIP', 'CODE',
            'ACCOUNT', 'REFERENCE', 'REF', 'INVOICE #', 'BILL #',
            'QUANTITY', 'QTY', 'DESCRIPTION', 'DESC', 'UNIT', 'PRICE',
            'SUBTOTAL', 'TAX', 'SHIPPING', 'HANDLING', 'DISCOUNT',
            'PAYMENT', 'TERMS', 'DUE DATE', 'BALANCE DUE'
        ]
        
        # Known company names for exact matching
        known_companies = [
            'BMR', 'TD', 'RBC', 'SCOTIA', 'DESJARDINS', 'HYDRO-QUÉBEC',
            'HYDRO QUEBEC', 'HYDRO QUEBEC', 'HYDRO-QUÉBEC', 'HYDRO-QUÉBEC',
            'LA FORFAITERIE', 'LA FORFAITERIE', 'LA FORFAITERIE',
            'COMPTE DE TAXES SCOLAIRE', 'COMPTE DE TAXES SCOLAIRE',
            'CENTRE DE SERVICES SCOLAIRES', 'CENTRE DE SERVICES SCOLAIRES',
            'GARY CHARTRAND', 'GARY CHARTRAND', 'GARY CHARTRAND'
        ]
        
        # Search in the first 20 lines (usually where company names appear)
        search_lines = lines[:20]
        candidates = []
        
        # First pass: Look for exact matches with known companies
        if not candidates:
            for company in known_companies:
                if company.lower() in text.lower():
                    candidates.append((company, f"Found in text: {company}", 15))  # Highest priority
                    break
        
        # Special pass: Look for "compte de taxes scolaire" variations with STRICT fuzzy matching
        if not candidates:
            if 'compte de taxes scolaire' in text.lower() or 'centre de services scolaire' in text.lower():
                candidates.append(('compte de taxes scolaire', 'Found tax school account', 15))
        
        # Special pass: Look for business alias variations with VERY strict fuzzy matching
        if not candidates:
            # Use BusinessAliasManager for configurable business matching
            for line in search_lines:
                line_clean = line.strip()
                if len(line_clean) > 5:
                    # Try to find a business match using the alias manager
                    business_match = self.alias_manager.find_business_match(line_clean)
                    if business_match:
                        business_name, match_type, confidence = business_match
                        priority = 15 if match_type == "exact_match" else 12 if match_type == "partial_match" else 10
                        candidates.append((business_name, f'Business alias {match_type}: {line_clean}', priority))
                        logging.info(f"Business alias found: '{line_clean}' -> '{business_name}' (type: {match_type}, confidence: {confidence})")
                        break
        
        # Second pass: Look for lines that look like company names
        if not candidates:
            for i, line in enumerate(search_lines):
                line = line.strip()
                
                # Skip if too short or too long
                if len(line) < 5 or len(line) > 60:
                    continue
                
                # Skip if contains exclusion indicators
                if any(indicator in line.upper() for indicator in exclude_indicators):
                    continue
                
                # Look for lines that are mostly letters and spaces
                if re.match(r'^[A-Z][A-Za-z\s&\.\-]+$', line):
                    # Skip if too many numbers
                    if len(re.findall(r'\d', line)) < len(line) * 0.1:
                        candidates.append((line, line, 5))  # Medium priority
        
        # Third pass: Look for lines with company-like keywords
        if not candidates:
            company_keywords = ['SERVICES', 'CENTRE', 'CLINIQUE', 'RESTAURANT', 'STORE', 'MAGASIN', 'CONSTRUCTION']
            for line in search_lines:
                line = line.strip()
                if any(keyword in line.upper() for keyword in company_keywords):
                    if len(line) > 5 and len(line) < 50:
                        candidates.append((line, line, 3))  # Low priority
        
        # Return the best candidate or Unknown if none found
        if candidates:
            # Sort by priority, then by length (prefer longer names)
            candidates.sort(key=lambda x: (x[2], -len(x[0])), reverse=True)
            best_company, source_line, priority = candidates[0]
            
            logging.info(f"Found company name: '{best_company}' from line: {source_line}")
            return best_company
        
        logging.info("No company name found, returning 'Unknown'")
        return "Unknown"

    def extract_invoice_total(self, text: str, expected_total: float = None) -> Optional[str]:
        """Extract invoice total from text"""
        if not text:
            return None
        
        lines = text.split('\n')
        
        # Enhanced OCR correction for digits and common OCR errors
        def ocr_correct_amount(s):
            return (
                s.replace('I', '1')
                 .replace('O', '0')
                 .replace('S', '5')
                 .replace('G', '6')
                 .replace('B', '8')
                 .replace('l', '1')
                 .replace('o', '0')
                 .replace('s', '5')
                 .replace('g', '6')
                 .replace('b', '8')
                 .replace('Z', '2')
                 .replace('z', '2')
                 .replace('A', '4')
                 .replace('a', '4')
                 .replace('E', '3')
                 .replace('e', '3')
                 .replace('T', '7')
                 .replace('t', '7')
            )
        
        # Normalize amount string
        def normalize_amount(amount_str):
            amount_str = ocr_correct_amount(amount_str)
            # Remove spaces
            amount_str = amount_str.replace(' ', '')
            # Handle decimal separators
            if amount_str.count(',') == 1 and amount_str.count('.') == 0:
                # Single comma as decimal separator
                amount_str = amount_str.replace(',', '.')
            elif amount_str.count('.') == 1 and amount_str.count(',') == 0:
                # Single dot as decimal separator
                pass
            elif amount_str.count(',') > 1 and amount_str.count('.') == 0:
                # Multiple commas, treat last as decimal
                parts = amount_str.split(',')
                amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
            elif amount_str.count('.') > 1 and amount_str.count(',') == 0:
                # Multiple dots, treat last as decimal
                parts = amount_str.split('.')
                amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
            else:
                # Mixed separators, try to guess
                if amount_str.count(',') >= amount_str.count('.'):
                    # More commas, treat last comma as decimal
                    parts = amount_str.split(',')
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
                else:
                    # More dots, treat last dot as decimal
                    parts = amount_str.split('.')
                    amount_str = ''.join(parts[:-1]) + '.' + parts[-1]
            return amount_str
        
        # High-priority patterns for invoice totals
        high_priority_patterns = [
            r'(?:TOTAL À PAYER|TOTAL A PAYER)\s*:?\s*\$?([\d.,SIOSBGZAE]+)',
            r'(?:Solde à recevoir|Solde a recevoir)\s*:?\s*\$?([\d.,SIOSBGZAE]+)',
            r'(?:MONTANTDU VERSEMENT|MONTANT DU VERSEMENT)\s*\$?([\d.,SIOSBGZAE]+)',
            r'(?:ECHEANCE)\s*\$?([\d.,SIOSBGZAE]+)',
            r'(?:TOTAL|MONTANT|SOMME|DÛ|À PAYER|FACTURÉ|SOLDE)\s*:?\s*\$?([\d.,SIOSBGZAE]+)',
            r'(?:Total)\s*:\s*\$?([\d.,SIOSBGZAE]+)',
            r'([\d.,SIOSBGZAE]+)\s*(?:TOTAL|MONTANT|SOMME|DÛ|À PAYER|SOLDE)',
        ]
        
        # Currency patterns
        currency_patterns = [
            r'\$\s*([\d.,SIOSBGZAE]+)',
            r'(?:CAD|USD|EUR|C\$)\s*([\d.,SIOSBGZAE]+)',
            r'([\d.,SIOSBGZAE]+)\s*(?:CAD|USD|EUR|C\$)',
        ]
        
        candidates = []
        
        # First try high-priority patterns
        for line_num, line in enumerate(lines):
            line_lower = line.lower()
            line_original = line
            
            # Check for high-priority patterns
            for pattern in high_priority_patterns:
                matches = re.findall(pattern, line_original, re.IGNORECASE)
                for match in matches:
                    try:
                        # Apply OCR corrections and normalize
                        corrected_amount = normalize_amount(match)
                        
                        # Try to convert to float
                        amount_float = float(corrected_amount)
                        
                        # Format as string with two decimal places
                        formatted_amount = f"{amount_float:.2f}"
                        
                        candidates.append((formatted_amount, f"High-priority pattern: {line_original}", 15))
                        
                    except ValueError:
                        continue
        
        # If no high-priority matches, try currency patterns
        if not candidates:
            for line_num, line in enumerate(lines):
                line_original = line
                
                for pattern in currency_patterns:
                    matches = re.findall(pattern, line_original, re.IGNORECASE)
                    for match in matches:
                        try:
                            corrected_amount = normalize_amount(match)
                            amount_float = float(corrected_amount)
                            formatted_amount = f"{amount_float:.2f}"
                            candidates.append((formatted_amount, f"Currency pattern: {line_original}", 10))
                        except ValueError:
                            continue
        
        # If still no matches, try general number patterns
        if not candidates:
            for line_num, line in enumerate(lines):
                line_original = line
                
                # Look for numbers that might be totals
                number_patterns = [
                    r'(\d+[.,]\d{2})',  # Numbers with exactly 2 decimal places
                    r'(\d+[.,]\d{1,2})',  # Numbers with 1-2 decimal places
                ]
                
                for pattern in number_patterns:
                    matches = re.findall(pattern, line_original)
                    for match in matches:
                        try:
                            corrected_amount = normalize_amount(match)
                            amount_float = float(corrected_amount)
                            
                            # Only consider reasonable amounts (between 0.01 and 100000)
                            if 0.01 <= amount_float <= 100000:
                                formatted_amount = f"{amount_float:.2f}"
                                candidates.append((formatted_amount, f"General pattern: {line_original}", 5))
                        except ValueError:
                            continue
        
        # Return the best candidate
        if candidates:
            # Sort by priority (highest first)
            candidates.sort(key=lambda x: x[2], reverse=True)
            best_amount, source_line, priority = candidates[0]
            
            logging.info(f"Found invoice total: '{best_amount}' from line: {source_line}")
            return best_amount
        
        logging.info("No invoice total found")
        return None

    def calculate_confidence(self, company: str, total: Optional[float], text: str) -> str:
        """Calculate confidence level for the extraction"""
        confidence_score = 0
        
        # Company name confidence
        if company and company != "Unknown":
            confidence_score += 1
            if len(company) > 3:
                confidence_score += 1
        
        # Total amount confidence
        if total is not None:
            confidence_score += 1
            try:
                total_float = float(total)
                if 0.01 <= total_float <= 100000:
                    confidence_score += 1
            except ValueError:
                pass
        
        # Text quality confidence
        if text and len(text) > 50:
            confidence_score += 1
        
        # Determine confidence level
        if confidence_score >= 4:
            return "high"
        elif confidence_score >= 2:
            return "medium"
        else:
            return "low"

    def parse_invoice(self, pdf_path: str, expected_total: float = None, expected_company: str = None) -> Dict[str, Any]:
        """Parse a single invoice PDF"""
        start_time = datetime.now()
        
        try:
            # Check if file exists
            if not os.path.exists(pdf_path):
                return {
                    'file_path': pdf_path,
                    'company_name': None,
                    'invoice_total': None,
                    'extraction_method': 'error',
                    'confidence': 'low',
                    'processing_time': 0,
                    'error': f'File not found: {pdf_path}'
                }
            
            # Extract text from PDF
            text = self.extract_text_from_pdf(pdf_path)
            
            # If no text found, use OCR
            if not text.strip():
                logging.info(f"No text found in PDF, using OCR: {pdf_path}")
                images = self.convert_pdf_to_images(pdf_path)
                if images:
                    text = self.extract_text_with_ocr(images)
                    extraction_method = 'ocr'
                else:
                    return {
                        'file_path': pdf_path,
                        'company_name': None,
                        'invoice_total': None,
                        'extraction_method': 'error',
                        'confidence': 'low',
                        'processing_time': 0,
                        'error': 'Could not convert PDF to images for OCR'
                    }
            else:
                extraction_method = 'text_extraction'
            
            # Extract company name
            company_name = self.extract_company_name(text, expected_company)
            
            # Extract invoice total
            invoice_total = self.extract_invoice_total(text, expected_total)
            
            # Calculate confidence
            confidence = self.calculate_confidence(company_name, invoice_total, text)
            
            # Calculate processing time
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Add to database if enabled
            if self.use_database and company_name and company_name != "Unknown":
                self.invoice_db.add_company(company_name)
            
            return {
                'file_path': pdf_path,
                'company_name': company_name,
                'invoice_total': invoice_total,
                'extraction_method': extraction_method,
                'confidence': confidence,
                'processing_time': processing_time,
                'error': None
            }
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            logging.error(f"Error parsing invoice {pdf_path}: {e}")
            
            return {
                'file_path': pdf_path,
                'company_name': None,
                'invoice_total': None,
                'extraction_method': 'error',
                'confidence': 'low',
                'processing_time': processing_time,
                'error': str(e)
            }

    def parse_invoices_batch(self, folder_path: str, output_file: str = None) -> pd.DataFrame:
        """Parse multiple invoices in a folder"""
        if not os.path.exists(folder_path):
            logging.error(f"Folder not found: {folder_path}")
            return pd.DataFrame()
        
        # Find all PDF files
        pdf_files = []
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_files.append(os.path.join(root, file))
        
        if not pdf_files:
            logging.warning(f"No PDF files found in {folder_path}")
            return pd.DataFrame()
        
        logging.info(f"Found {len(pdf_files)} PDF files to process")
        
        # Parse each invoice
        results = []
        for pdf_file in pdf_files:
            result = self.parse_invoice(pdf_file)
            results.append(result)
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Save to CSV if output file specified
        if output_file:
            df.to_csv(output_file, index=False)
            logging.info(f"Results saved to {output_file}")
        
        return df

    def rename_pdf(self, pdf_path: str, company_name: str, invoice_total: str) -> str:
        """Rename PDF file based on extracted information"""
        try:
            # Get directory and filename
            directory = os.path.dirname(pdf_path)
            filename = os.path.basename(pdf_path)
            name, ext = os.path.splitext(filename)
            
            # Create new filename
            if company_name and company_name != "Unknown":
                new_name = f"{company_name}"
                if invoice_total:
                    new_name += f"_{invoice_total}"
                new_name += ext
            else:
                new_name = f"unknown_{invoice_total}{ext}" if invoice_total else f"unknown{ext}"
            
            # Create new path
            new_path = os.path.join(directory, new_name)
            
            # Rename file
            os.rename(pdf_path, new_path)
            logging.info(f"Renamed {pdf_path} to {new_path}")
            
            return new_path
            
        except Exception as e:
            logging.error(f"Error renaming file {pdf_path}: {e}")
            return pdf_path 
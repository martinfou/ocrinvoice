"""Fuzzy string matching utilities for OCR text processing."""

from typing import List, Dict, Any, Optional, Tuple, Union
import re
from difflib import SequenceMatcher
from fuzzywuzzy import fuzz, process


class FuzzyMatcher:
    """Fuzzy string matching utility for OCR text processing.

    This class provides various methods for fuzzy string matching,
    which is useful for handling OCR errors and variations in text.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the fuzzy matcher.

        Args:
            config: Configuration dictionary with matching settings
        """
        config = config or {}

        # Extract configuration values
        self.threshold: float = config.get("threshold", 0.8)
        self.case_sensitive: bool = config.get("case_sensitive", False)
        self.normalize_whitespace: bool = config.get("normalize_whitespace", True)
        self.remove_punctuation: bool = config.get("remove_punctuation", True)
        self.cache_size: int = config.get("cache_size", 1000)

        # Validate threshold
        if not 0.0 <= self.threshold <= 1.0:
            raise ValueError("Threshold must be between 0 and 1")

        # Initialize cache
        self.cache: Dict[Tuple[str, str], float] = {}

    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for matching.

        Args:
            text: Text to preprocess

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        processed = text

        # Case sensitivity
        if not self.case_sensitive:
            processed = processed.lower()

        # Punctuation removal
        if self.remove_punctuation:
            # Remove punctuation but preserve spaces
            processed = re.sub(r"[^\w\s]", "", processed)

        # Whitespace normalization (after punctuation removal)
        if self.normalize_whitespace:
            processed = " ".join(processed.split())

        return processed.strip()

    def _calculate_similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings.

        Args:
            str1: First string to compare
            str2: Second string to compare

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Preprocess strings
        processed1 = self._preprocess_text(str1)
        processed2 = self._preprocess_text(str2)

        # Check for exact match first
        if processed1 == processed2:
            return 1.0

        # Calculate similarity using multiple methods
        ratios = [
            SequenceMatcher(None, processed1, processed2).ratio(),
            fuzz.ratio(processed1, processed2) / 100.0,
            fuzz.partial_ratio(processed1, processed2) / 100.0,
            fuzz.token_sort_ratio(processed1, processed2) / 100.0,
        ]

        # Use the highest ratio
        similarity = max(ratios)

        return similarity

    def similarity(self, str1: str, str2: str) -> float:
        """Calculate similarity between two strings.

        Args:
            str1: First string to compare
            str2: Second string to compare

        Returns:
            Similarity score between 0.0 and 1.0
        """
        # Handle invalid inputs
        if not isinstance(str1, str) or not isinstance(str2, str):
            str1 = str(str1) if str1 is not None else ""
            str2 = str(str2) if str2 is not None else ""

        return self._calculate_similarity(str1, str2)

    def find_best_match(
        self, query: str, candidates: List[str]
    ) -> Tuple[Optional[str], float]:
        """Find the best match for a query string among candidates.

        Args:
            query: String to find a match for
            candidates: List of candidate strings to match against

        Returns:
            Tuple of (best_match, similarity_score) where best_match can be None
        """
        # Validate inputs
        if query is None:
            raise ValueError("Query cannot be None")
        if candidates is None:
            raise ValueError("Candidates cannot be None")
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
        if not isinstance(candidates, list):
            raise TypeError("Candidates must be a list")

        if not query or not candidates:
            return None, 0.0

        # Check for None values in candidates
        if any(c is None for c in candidates):
            raise ValueError("Candidates list cannot contain None values")

        # Filter out None values from candidates
        valid_candidates = [c for c in candidates if c is not None]
        if not valid_candidates:
            return None, 0.0

        # Create cache key for this specific query-candidates combination
        cache_key = (query, tuple(sorted(valid_candidates)))

        # Check cache first
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if cached_result is None:
                return None, 0.0
            return cached_result

        best_match = None
        best_score = 0.0

        # First pass: look for exact matches
        for candidate in valid_candidates:
            if not isinstance(candidate, str):
                raise TypeError("All candidates must be strings")
            if candidate == query:
                result = (candidate, 1.0)
                # Cache the result
                if len(self.cache) < self.cache_size:
                    self.cache[cache_key] = result
                return result

        # Second pass: look for fuzzy matches
        for candidate in valid_candidates:
            if not isinstance(candidate, str):
                raise TypeError("All candidates must be strings")
            score = self._calculate_similarity(query, candidate)
            if score > best_score and score >= self.threshold:
                best_score = score
                best_match = candidate

        result = (best_match, best_score)

        # Cache the result (with size limit)
        if len(self.cache) < self.cache_size:
            self.cache[cache_key] = result

        return result

    @property
    def _cache(self) -> Dict[Tuple[str, str], float]:
        """Property to access cache for backward compatibility with tests."""
        return self.cache

    def find_all_matches(
        self, query: str, candidates: List[str], min_similarity: Optional[float] = None
    ) -> List[Tuple[str, float]]:
        """Find all matches above a threshold.

        Args:
            query: String to find matches for
            candidates: List of candidate strings to match against
            min_similarity: Minimum threshold for matches (uses self.threshold if None)

        Returns:
            List of tuples (match, similarity_score) sorted by score descending
        """
        if not query or not candidates:
            return []

        threshold = min_similarity or self.threshold
        matches = []

        # Filter out None values from candidates
        valid_candidates = [c for c in candidates if c is not None]

        for candidate in valid_candidates:
            score = self.similarity(query, candidate)
            if score >= threshold:
                matches.append((candidate, score))

        # Sort by score descending
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def correct_ocr_errors(self, text: str, corrections: Dict[str, str]) -> str:
        """Correct common OCR errors in text.

        Args:
            text: Text that may contain OCR errors
            corrections: Dictionary mapping incorrect text to correct text

        Returns:
            Text with OCR errors corrected
        """
        corrected_text = text

        for incorrect, correct in corrections.items():
            if incorrect in corrected_text:
                corrected_text = corrected_text.replace(incorrect, correct)

        return corrected_text

    def normalize_text(self, text: str) -> str:
        """Normalize text for better matching.

        Args:
            text: Text to normalize

        Returns:
            Normalized text
        """
        # Convert to lowercase
        normalized = text.lower()

        # Remove extra whitespace
        normalized = " ".join(normalized.split())

        # Remove common punctuation that might be OCR errors
        normalized = re.sub(r"[^\w\s]", "", normalized)

        return normalized.strip()

    def extract_numbers(self, text: str) -> List[str]:
        """Extract numbers from text.

        Args:
            text: Text to extract numbers from

        Returns:
            List of extracted number strings
        """
        # Find all number patterns
        number_patterns = [
            r"\d+\.?\d*",  # Decimal numbers
            r"\$\d+\.?\d*",  # Dollar amounts
            r"\d+%",  # Percentages
        ]

        numbers = []
        for pattern in number_patterns:
            matches = re.findall(pattern, text)
            numbers.extend(matches)

        return numbers

    def extract_dates(self, text: str) -> List[str]:
        """Extract date patterns from text.

        Args:
            text: Text to extract dates from

        Returns:
            List of extracted date strings
        """
        date_patterns = [
            r"\d{1,2}[/-]\d{1,2}[/-]\d{2,4}",  # MM/DD/YYYY or MM-DD-YYYY
            r"\d{4}[/-]\d{1,2}[/-]\d{1,2}",  # YYYY/MM/DD or YYYY-MM-DD
            r"\w+\s+\d{1,2},?\s+\d{4}",  # Month DD, YYYY
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            dates.extend(matches)

        return dates

    def extract_amounts(self, text: str) -> List[str]:
        """Extract monetary amounts from text.

        Args:
            text: Text to extract amounts from

        Returns:
            List of extracted amount strings
        """
        amount_patterns = [
            r"[\$]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?",  # $1,234.56 or 1234.56
            r"[\$]?\d+\.\d{2}",  # $123.45 or 123.45
            r"[\$]?\d+",  # $123 or 123
        ]

        amounts = []
        for pattern in amount_patterns:
            matches = re.findall(pattern, text)
            amounts.extend(matches)

        return amounts

    def is_likely_company_name(self, text: str) -> bool:
        """Check if text is likely a company name.

        Args:
            text: Text to check

        Returns:
            True if text is likely a company name
        """
        # Company name indicators
        company_indicators = [
            r"\b(?:inc|corp|llc|ltd|co|company|corporation|limited)\b",
            r"\b(?:&|and)\b",
            r"[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*",  # Title case words
        ]

        text_lower = text.lower()
        for pattern in company_indicators:
            if re.search(pattern, text_lower):
                return True

        return False

    def is_likely_amount(self, text: str) -> bool:
        """Check if text is likely a monetary amount.

        Args:
            text: Text to check

        Returns:
            True if text is likely a monetary amount
        """
        # Amount patterns
        amount_patterns = [
            r"^[\$]?\d{1,3}(?:,\d{3})*(?:\.\d{2})?$",
            r"^[\$]?\d+\.\d{2}$",
            r"^[\$]?\d+$",
        ]

        for pattern in amount_patterns:
            if re.match(pattern, text):
                return True

        return False

    def is_likely_date(self, text: str) -> bool:
        """Check if text is likely a date.

        Args:
            text: Text to check

        Returns:
            True if text is likely a date
        """
        # Date patterns
        date_patterns = [
            r"^\d{1,2}[/-]\d{1,2}[/-]\d{2,4}$",
            r"^\d{4}[/-]\d{1,2}[/-]\d{1,2}$",
            r"^\w+\s+\d{1,2},?\s+\d{4}$",
        ]

        for pattern in date_patterns:
            if re.match(pattern, text):
                return True

        return False

    def clear_cache(self) -> None:
        """Clear the similarity cache."""
        self.cache.clear()

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get statistics about the cache.

        Returns:
            Dictionary with cache statistics
        """
        return {"cache_size": len(self.cache), "threshold": self.threshold}

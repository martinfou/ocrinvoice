"""Unit tests for the FuzzyMatcher class."""

import pytest
from unittest.mock import Mock, patch, MagicMock, call
from pathlib import Path
from typing import Dict, Any
import os

import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", "..", "src"))

from ocrinvoice.utils.fuzzy_matcher import FuzzyMatcher


class TestFuzzyMatcherInitialization:
    """Test FuzzyMatcher initialization and configuration."""

    def test_init_with_default_config(self):
        """Test initialization with default configuration."""
        matcher = FuzzyMatcher()

        assert matcher.threshold == 0.8
        assert matcher.case_sensitive is False
        assert matcher.normalize_whitespace is True
        assert matcher.remove_punctuation is True
        assert matcher.cache_size == 1000

    def test_init_with_custom_config(self):
        """Test initialization with custom configuration."""
        config = {
            "threshold": 0.9,
            "case_sensitive": True,
            "normalize_whitespace": False,
            "remove_punctuation": False,
            "cache_size": 500,
        }

        matcher = FuzzyMatcher(config)

        assert matcher.threshold == 0.9
        assert matcher.case_sensitive is True
        assert matcher.normalize_whitespace is False
        assert matcher.remove_punctuation is False
        assert matcher.cache_size == 500

    def test_init_with_invalid_threshold(self):
        """Test initialization with invalid threshold."""
        config = {"threshold": 1.5}  # Above 1.0

        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            FuzzyMatcher(config)

    def test_init_with_negative_threshold(self):
        """Test initialization with negative threshold."""
        config = {"threshold": -0.1}  # Below 0

        with pytest.raises(ValueError, match="Threshold must be between 0 and 1"):
            FuzzyMatcher(config)


class TestFuzzyMatcherTextPreprocessing:
    """Test FuzzyMatcher text preprocessing methods."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_preprocess_text_basic(self, matcher):
        """Test basic text preprocessing."""
        text = "  Hello,   World!  "
        result = matcher._preprocess_text(text)

        assert result == "hello world"

    def test_preprocess_text_case_sensitive(self, matcher):
        """Test text preprocessing with case sensitivity."""
        matcher.case_sensitive = True
        text = "  Hello,   World!  "
        result = matcher._preprocess_text(text)

        assert result == "Hello World"

    def test_preprocess_text_no_whitespace_normalization(self, matcher):
        """Test text preprocessing without whitespace normalization."""
        matcher.normalize_whitespace = False
        text = "  Hello,   World!  "
        result = matcher._preprocess_text(text)

        assert result == "hello   world"

    def test_preprocess_text_no_punctuation_removal(self, matcher):
        """Test text preprocessing without punctuation removal."""
        matcher.remove_punctuation = False
        text = "  Hello,   World!  "
        result = matcher._preprocess_text(text)

        assert result == "hello, world!"

    def test_preprocess_text_empty(self, matcher):
        """Test text preprocessing with empty text."""
        result = matcher._preprocess_text("")
        assert result == ""

    def test_preprocess_text_whitespace_only(self, matcher):
        """Test text preprocessing with whitespace-only text."""
        result = matcher._preprocess_text("   \n\t   ")
        assert result == ""

    def test_preprocess_text_with_special_characters(self, matcher):
        """Test text preprocessing with special characters."""
        text = "ABC Company, Inc. (LLC) - 123 Main St."
        result = matcher._preprocess_text(text)

        assert result == "abc company inc llc 123 main st"

    def test_preprocess_text_with_numbers(self, matcher):
        """Test text preprocessing with numbers."""
        text = "Invoice #12345 - Total: $1,234.56"
        result = matcher._preprocess_text(text)

        assert result == "invoice 12345 total 123456"


class TestFuzzyMatcherStringComparison:
    """Test FuzzyMatcher string comparison methods."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_calculate_similarity_exact_match(self, matcher):
        """Test similarity calculation with exact match."""
        similarity = matcher._calculate_similarity("hello", "hello")
        assert similarity == 1.0

    def test_calculate_similarity_high_similarity(self, matcher):
        """Test similarity calculation with high similarity."""
        similarity = matcher._calculate_similarity("hello", "helo")
        assert similarity > 0.8

    def test_calculate_similarity_low_similarity(self, matcher):
        """Test similarity calculation with low similarity."""
        similarity = matcher._calculate_similarity("hello", "world")
        assert similarity < 0.5

    def test_calculate_similarity_empty_strings(self, matcher):
        """Test similarity calculation with empty strings."""
        similarity = matcher._calculate_similarity("", "")
        assert similarity == 1.0

    def test_calculate_similarity_one_empty(self, matcher):
        """Test similarity calculation with one empty string."""
        similarity = matcher._calculate_similarity("hello", "")
        assert similarity == 0.0

    def test_calculate_similarity_case_difference(self, matcher):
        """Test similarity calculation with case differences."""
        similarity = matcher._calculate_similarity("Hello", "hello")
        assert similarity == 1.0  # Should be 1.0 after preprocessing

    def test_calculate_similarity_whitespace_difference(self, matcher):
        """Test similarity calculation with whitespace differences."""
        similarity = matcher._calculate_similarity("hello world", "hello  world")
        assert similarity == 1.0  # Should be 1.0 after preprocessing


class TestFuzzyMatcherBestMatchFinding:
    """Test FuzzyMatcher best match finding methods."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_find_best_match_success(self, matcher):
        """Test successful best match finding."""
        candidates = ["apple", "banana", "orange", "grape"]
        query = "appl"

        result, similarity = matcher.find_best_match(query, candidates)

        assert result == "apple"
        assert similarity > 0.8

    def test_find_best_match_exact_match(self, matcher):
        """Test best match finding with exact match."""
        candidates = ["apple", "banana", "orange"]
        query = "apple"

        result, similarity = matcher.find_best_match(query, candidates)

        assert result == "apple"
        assert similarity == 1.0

    def test_find_best_match_below_threshold(self, matcher):
        """Test best match finding when similarity is below threshold."""
        matcher.threshold = 0.9
        candidates = ["apple", "banana", "orange"]
        query = "xyz"

        result, similarity = matcher.find_best_match(query, candidates)

        assert result is None
        assert similarity < 0.9

    def test_find_best_match_empty_candidates(self, matcher):
        """Test best match finding with empty candidates list."""
        candidates = []
        query = "apple"

        result, similarity = matcher.find_best_match(query, candidates)

        assert result is None
        assert similarity == 0.0

    def test_find_best_match_empty_query(self, matcher):
        """Test best match finding with empty query."""
        candidates = ["apple", "banana", "orange"]
        query = ""

        result, similarity = matcher.find_best_match(query, candidates)

        assert result is None
        assert similarity == 0.0

    def test_find_best_match_multiple_similar_matches(self, matcher):
        """Test best match finding with multiple similar matches."""
        candidates = ["apple", "apples", "apple pie", "banana"]
        query = "apple"

        result, similarity = matcher.find_best_match(query, candidates)

        assert result in ["apple", "apples", "apple pie"]
        assert similarity == 1.0

    def test_find_best_match_with_typos(self, matcher):
        """Test best match finding with OCR typos."""
        candidates = ["ABC Company Inc.", "XYZ Corporation", "DEF Industries"]
        query = "ABC Compny Inc."  # Typo in "Company"

        result, similarity = matcher.find_best_match(query, candidates)

        assert result == "ABC Company Inc."
        assert similarity > 0.8


class TestFuzzyMatcherMultipleMatches:
    """Test FuzzyMatcher multiple match finding methods."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_find_all_matches_success(self, matcher):
        """Test successful finding of all matches."""
        candidates = ["apple", "apples", "banana", "orange", "grape"]
        query = "apple"

        results = matcher.find_all_matches(query, candidates, min_similarity=0.7)

        assert len(results) >= 2
        assert ("apple", 1.0) in results
        assert ("apples", 1.0) in results

    def test_find_all_matches_with_similarity_threshold(self, matcher):
        """Test finding all matches with similarity threshold."""
        candidates = ["apple", "apples", "banana", "orange"]
        query = "appl"

        results = matcher.find_all_matches(query, candidates, min_similarity=0.8)

        # Should only return matches above 0.8 similarity
        for _, similarity in results:
            assert similarity >= 0.8

    def test_find_all_matches_empty_candidates(self, matcher):
        """Test finding all matches with empty candidates."""
        candidates = []
        query = "apple"

        results = matcher.find_all_matches(query, candidates)

        assert results == []

    def test_find_all_matches_empty_query(self, matcher):
        """Test finding all matches with empty query."""
        candidates = ["apple", "banana", "orange"]
        query = ""

        results = matcher.find_all_matches(query, candidates)

        assert results == []

    def test_find_all_matches_sorted_by_similarity(self, matcher):
        """Test that matches are sorted by similarity."""
        candidates = ["apple", "apples", "banana", "orange"]
        query = "appl"

        results = matcher.find_all_matches(query, candidates)

        # Check that results are sorted by similarity (descending)
        similarities = [similarity for _, similarity in results]
        assert similarities == sorted(similarities, reverse=True)


class TestFuzzyMatcherCaching:
    """Test FuzzyMatcher caching functionality."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher({"cache_size": 5})

    def test_cache_hit(self, matcher):
        """Test cache hit functionality."""
        candidates = ["apple", "banana", "orange"]
        query = "appl"

        # First call should cache the result
        result1, similarity1 = matcher.find_best_match(query, candidates)

        # Second call should use cache
        result2, similarity2 = matcher.find_best_match(query, candidates)

        assert result1 == result2
        assert similarity1 == similarity2
        assert len(matcher._cache) == 1

    def test_cache_miss_different_query(self, matcher):
        """Test cache miss with different query."""
        candidates = ["apple", "banana", "orange"]

        # First call
        matcher.find_best_match("appl", candidates)

        # Second call with different query
        matcher.find_best_match("ban", candidates)

        assert len(matcher._cache) == 2

    def test_cache_miss_different_candidates(self, matcher):
        """Test cache miss with different candidates."""
        query = "appl"

        # First call
        matcher.find_best_match(query, ["apple", "banana"])

        # Second call with different candidates
        matcher.find_best_match(query, ["apple", "orange"])

        assert len(matcher._cache) == 2

    def test_cache_size_limit(self, matcher):
        """Test cache size limit enforcement."""
        candidates = ["apple", "banana", "orange"]

        # Add more items than cache size
        for i in range(10):
            matcher.find_best_match(f"query{i}", candidates)

        # Cache should not exceed size limit
        assert len(matcher._cache) <= matcher.cache_size

    def test_cache_clear(self, matcher):
        """Test cache clearing functionality."""
        candidates = ["apple", "banana", "orange"]

        # Add some items to cache
        matcher.find_best_match("appl", candidates)
        matcher.find_best_match("ban", candidates)

        assert len(matcher._cache) == 2

        # Clear cache
        matcher.clear_cache()

        assert len(matcher._cache) == 0


class TestFuzzyMatcherPerformance:
    """Test FuzzyMatcher performance characteristics."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_large_candidate_list_performance(self, matcher):
        """Test performance with large candidate list."""
        # Create a large list of candidates
        candidates = [f"company_{i}" for i in range(1000)]
        query = "company_500"

        # Should complete within reasonable time
        result, similarity = matcher.find_best_match(query, candidates)

        assert result == "company_500"
        assert similarity == 1.0

    def test_multiple_concurrent_requests(self, matcher):
        """Test handling of multiple concurrent requests."""
        import threading

        results = []
        errors = []

        def matching_worker():
            try:
                candidates = ["apple", "banana", "orange"]
                query = f"query_{threading.current_thread().name}"
                result, similarity = matcher.find_best_match(query, candidates)
                results.append((result, similarity))
            except Exception as e:
                errors.append(e)

        threads = []
        for i in range(10):
            thread = threading.Thread(target=matching_worker)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        assert len(results) == 10
        assert len(errors) == 0

    def test_cache_performance_improvement(self, matcher):
        """Test that caching improves performance."""
        import time

        candidates = ["apple", "banana", "orange"] * 100  # Large candidate list
        query = "appl"

        # First call (no cache)
        start_time = time.time()
        matcher.find_best_match(query, candidates)
        first_call_time = time.time() - start_time

        # Second call (with cache)
        start_time = time.time()
        matcher.find_best_match(query, candidates)
        second_call_time = time.time() - start_time

        # Second call should be faster
        assert second_call_time < first_call_time


class TestFuzzyMatcherErrorHandling:
    """Test FuzzyMatcher error handling."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_handle_invalid_input_types(self, matcher):
        """Test handling of invalid input types."""
        # Test with non-string query
        with pytest.raises(TypeError):
            matcher.find_best_match(123, ["apple", "banana"])

        # Test with non-list candidates
        with pytest.raises(TypeError):
            matcher.find_best_match("apple", "banana")

        # Test with non-string candidates
        with pytest.raises(TypeError):
            matcher.find_best_match("apple", ["apple", 123, "banana"])

    def test_handle_none_inputs(self, matcher):
        """Test handling of None inputs."""
        # Test with None query
        with pytest.raises(ValueError):
            matcher.find_best_match(None, ["apple", "banana"])

        # Test with None candidates
        with pytest.raises(ValueError):
            matcher.find_best_match("apple", None)

    def test_handle_empty_candidates_with_none_values(self, matcher):
        """Test handling of candidates list with None values."""
        candidates = ["apple", None, "banana"]

        with pytest.raises(ValueError):
            matcher.find_best_match("apple", candidates)


class TestFuzzyMatcherIntegration:
    """Integration tests for FuzzyMatcher."""

    @pytest.fixture
    def matcher(self):
        """Create a FuzzyMatcher instance for testing."""
        return FuzzyMatcher()

    def test_full_matching_workflow(self, matcher):
        """Test complete matching workflow."""
        # Simulate OCR text with potential errors
        ocr_text = "ABC Compny Inc."  # Typo in "Company"

        # Known company names
        known_companies = [
            "ABC Company Inc.",
            "XYZ Corporation",
            "DEF Industries",
            "GHI Solutions",
        ]

        # Find best match
        result, similarity = matcher.find_best_match(ocr_text, known_companies)

        assert result == "ABC Company Inc."
        assert similarity > 0.8

    def test_matching_with_preprocessing_workflow(self, matcher):
        """Test matching workflow with text preprocessing."""
        # Raw OCR text with various issues
        raw_text = "  ABC   Company,   Inc.   "
        known_companies = ["ABC Company Inc.", "XYZ Corporation"]

        # Find best match (should handle preprocessing automatically)
        result, similarity = matcher.find_best_match(raw_text, known_companies)

        assert result == "ABC Company Inc."
        assert similarity == 1.0

    def test_multiple_matches_workflow(self, matcher):
        """Test multiple matches workflow."""
        # OCR text that could match multiple companies
        ocr_text = "ABC Company"

        known_companies = [
            "ABC Company Inc.",
            "ABC Company LLC",
            "ABC Company Corp",
            "XYZ Corporation",
        ]

        # Find all matches above threshold
        results = matcher.find_all_matches(
            ocr_text, known_companies, min_similarity=0.8
        )

        assert len(results) >= 3
        # All results should be ABC Company variants
        for result, _ in results:
            assert "ABC Company" in result

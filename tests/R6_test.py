import pytest
from library_service import search_books_in_catalog
from conftest import test_setup

def test_search_books_matching_title(test_setup):
    """
    Test searching a book with an exact matching title, partial matching title, and a non-matching title
    """
    # Test exact matching title
    output1 = search_books_in_catalog("The Great Gatsby", "title")
    assert len(output1) == 1
    
    # Test partial matching title
    output2 = search_books_in_catalog("The Grea", "title")
    assert len(output2) == 1

    # Test non-matching title
    output3 = search_books_in_catalog("Non-Existing Title", "title")
    assert len(output3) == 0

def test_search_books_matching_author(test_setup):
    """
    Test searching a book with an exact matching author, partial matching author, and a non-matching author
    """
    # Test exact matching author
    output1 = search_books_in_catalog("F. Scott Fitzgerald", "author")
    assert len(output1) == 1
    
    # Test partial matching author
    output2 = search_books_in_catalog("Fitzgerald", "author")
    assert len(output2) == 1

    # Test non-matching author
    output3 = search_books_in_catalog("Non-exiting Author", "author")
    assert len(output3) == 0

def test_search_books_case_insensitive(test_setup):
    """
    Test searching a book with a partial matching title and author despite case-insensitivity
    """
    # Test partial matching title (case-insensitive)
    output1 = search_books_in_catalog("tHe gReAt gAt", "title")
    assert len(output1) == 1

    # Test partial matching title (case-insensitive) without matching spaces
    output2 = search_books_in_catalog("tHegReAtgAt", "title")
    assert len(output2) == 1

    # Test partial matching author (case-insensitive) with matching punctuation
    output3 = search_books_in_catalog("f. scOTt fItz", "author")
    assert len(output3) == 1

    # Test partial matching author (case-insensitive) without matching punctuation
    output4 = search_books_in_catalog("f scOTt fItz", "author")
    assert len(output4) == 1

def test_search_books_mismatching_types(test_setup):
    """
    Test searching a book with incorrectly matched search term and search type input
    """
    output = search_books_in_catalog("The Great Gatsby", "isbn")
    assert len(output) == 0

def test_search_books_matching_isbn(test_setup):
    """
    Test searching a book with matching and non-matching isbn
    """
    # Test exact matching isbn
    output1 = search_books_in_catalog("9780743273565", "isbn")
    assert len(output1) == 1
    assert output1[0]["isbn"] == "9780743273565"

    # Test non-matching isbn
    output2 = search_books_in_catalog("978074", "isbn")
    assert len(output2) == 0
    


import pytest
from playwright.sync_api import Page, expect

def test_add_and_verify_new_book(test_setup, page: Page):
    """
    E2E testing for adding and verifying successful addition of new book
    """
    # Navigate to homepage/catalog
    page.goto("http://localhost:5000/catalog")

    # Check that we're on catalog page
    expect(page.locator("h2", has_text="📖 Book Catalog")).to_be_visible()

    # Click "➕ Add New Book" button
    page.get_by_role("link", name="➕ Add New Book").click()

    # Wait for redirection to add_book
    page.wait_for_url("**/add_book")

    # Check that we're on add_book page
    expect(page.locator("h2", has_text="➕ Add New Book")).to_be_visible()

    # Add new book
    page.get_by_role("textbox", name="Title *").fill("Testing E2E")
    page.get_by_role("textbox", name="Author *").fill("Author Authors")
    page.get_by_role("textbox", name="ISBN *").fill("0987654321234")
    page.get_by_role("spinbutton", name="Total Copies *").fill("20")

    # Click "Add Book to Catalog" button
    page.get_by_role("button", name="Add Book to Catalog").click()

    # Wait for redirection to catalog
    page.wait_for_url("**/catalog")

    # Check that we were redirected back to the catalog page after successful addition
    expect(page.locator("h2", has_text="📖 Book Catalog")).to_be_visible()

    # Check that newly added book is visible in the table
    expect(page.locator("td", has_text="Testing E2E")).to_be_visible()
    expect(page.locator("td", has_text="Author Authors")).to_be_visible()
    expect(page.locator("td", has_text="0987654321234")).to_be_visible()
    expect(page.locator("td", has_text="20/20 Available")).to_be_visible()

def test_borrow_and_return_book(test_setup, page: Page):
    """
    E2E testing for borrowing a book, checking patron status to verify correct book has been borrowed for the correct user, and returning the book successfully 
    """
    # Navigate to homepage/catalog
    page.goto("http://localhost:5000/catalog")

    # Check that we're on catalog page
    expect(page.locator("h2", has_text="📖 Book Catalog")).to_be_visible()

    # Check that the book we want to borrow is in the table
    book_to_borrow = page.locator("tr", has_text="The Great Gatsby")
    expect(book_to_borrow).to_be_visible()

    # If the book is available, borrow book
    if not book_to_borrow.locator("td", has_text="Not Available").is_visible():

        # Fill in patron id
        book_to_borrow.locator("input[name='patron_id']").fill("135791")

        # Click "Borrow" button
        book_to_borrow.get_by_role("button", name="Borrow").click()

        # Check that success message gets displayed
        expect(page.locator("div.flash-success")).to_be_visible()
        expect(page.locator("div.flash-success")).to_contain_text("Successfully borrowed")

        # Check that correctly updated availability is shown
        expect(book_to_borrow.locator("td", has_text="2/3 Available")).to_be_visible()

    # Click "Patron Status" button
    page.get_by_role("link", name="👤 Patron Status").click()

    # Wait for redirection to catalog
    page.wait_for_url("**/patron_status")

    # Check that we were redirected to the patron status page
    expect(page.locator("h2", has_text="👤 Patron Status")).to_be_visible()

    # Enter patron id
    page.get_by_role("textbox", name="Patron ID:").fill("135791")

    # Click "🔍 Search" button
    page.get_by_role("button", name="🔍 Search").click()

    # Check that report was generated for correct patron
    expect(page.locator("h3", has_text="Patron Status Report for Patron #135791")).to_be_visible()

    # Check that the borrowed book is under "Currently Borrowed Books"
    expect(page.locator("td", has_text="The Great Gatsby").first).to_be_visible()

    # Click "Return Book" button
    page.get_by_role("link", name="↩️ Return Book").click()

    # Wait for redirection to catalog
    page.wait_for_url("**/return")

    # Check that we were redirected to the return book page
    expect(page.locator("h2", has_text="↩️ Return Book")).to_be_visible()

    # Enter patron id and book id for return
    page.get_by_role("textbox", name="Patron ID *").fill("135791")
    page.get_by_role("spinbutton", name="Book ID *").fill("1")

    # Click "Process Return" button
    page.get_by_role("button", name="Process Return").click()

    # Check that success message gets displayed
    expect(page.locator("div.flash-success")).to_be_visible()
    expect(page.locator("div.flash-success")).to_contain_text("You have successfully returned your book.")

    # Click "Catalog" button to go to catalog
    page.get_by_role("link", name="📖 Catalog").click()

    # Wait for redirection to catalog
    page.wait_for_url("**/catalog")

    # Check that we were redirected back to the catalog page after successful addition
    expect(page.locator("h2", has_text="📖 Book Catalog")).to_be_visible()

    # Check that correctly updated availability is shown
    updated_book= page.locator("tr", has_text="The Great Gatsby")
    expect(updated_book.locator("td", has_text="3/3 Available")).to_be_visible()

import pytest
from unittest.mock import Mock
from database import get_book_by_id
from services.library_service import pay_late_fees, refund_late_fee_payment, calculate_late_fee_for_book
from services.payment_service import PaymentGateway

def test_pay_late_fees_successful_payment(mocker):
    """
    Test successful payment.
    """
    # Stub database functions that return valid values
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Mocked method in gateway should return successful response
    mock_gateway.process_payment.return_value = (True, "txn_123", "success")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    # Payment processed successfully through gateway
    assert success == True
    assert "Payment successful" in msg
    assert txn == "txn_123"

    # Verify that method was called with the correct arguments
    mock_gateway.process_payment.assert_called_with(
        patron_id="123456",
        amount=10.50,
        description=f"Late fees for 'The Great Gatsby'"
    )

def test_pay_late_fees_declined_payment(mocker):
    """
    Test when payment is declined by gateway.
    """
    # Stub database functions that return valid values
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Mocked method in gateway should return unsuccessful response
    mock_gateway.process_payment.return_value = (False, "", "card declined")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    # Payment processed unsuccessfully through gateway
    assert success == False
    assert "Payment failed" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once()

def test_pay_late_fees_invalid_patron_id():
    """
    Test invalid patron ID.
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to pay late fee with invalid patron id
    success, msg, txn = pay_late_fees("id123", 1, mock_gateway)

    assert success == False
    assert "Invalid patron ID" in msg
    assert txn is None

    # Verify that gateway is not called
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_zero_late_fees(mocker):
    """
    Test zero late fees.
    """
    # Stub calculate_late_fee_for_book to simulate case when fee_amount is 0
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 0.0})

    mock_gateway = Mock(spec=PaymentGateway)
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "No late fees" in msg
    assert txn is None

    # Verify that gateway is not called
    mock_gateway.process_payment.assert_not_called()

def test_pay_late_fees_exception_handling(mocker):
    """
    Test network error exception handling.
    """
    # Stub database functions that return valid values
    mocker.patch("services.library_service.calculate_late_fee_for_book", return_value={"fee_amount": 10.50})
    mocker.patch("database.get_book_by_id", return_value={"title": "The Great Gatsby"})

    mock_gateway = Mock(spec=PaymentGateway)

    # Payment gateway should raise an exception
    mock_gateway.process_payment.side_effect = Exception("network error")
    success, msg, txn = pay_late_fees("123456", 1, mock_gateway)

    assert success == False
    assert "Payment processing error" in msg
    assert txn is None

    mock_gateway.process_payment.assert_called_once()

def test_refund_late_fee_successful_refund():
    """
    Test successful refund.
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Mocked method in gateway should return successful response
    mock_gateway.refund_payment.return_value = (True, "Refund processed successfully!")

    # Refund valid amount
    success, msg = refund_late_fee_payment("txn_123", 7.0, mock_gateway)

    assert success == True
    assert "Refund processed successfully!" in msg

    # Verify that method was called with the correct arguments
    mock_gateway.refund_payment.assert_called_with("txn_123", 7.0)

def test_refund_late_fee_invalid_transaction_id():
    """
    Test invalid transaction ID rejection.
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt refund with invalid transaction id
    success, msg = refund_late_fee_payment("", 7.0, mock_gateway)

    assert success == False
    assert "Invalid transaction ID" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_invalid_amount_negative():
    """
    Test invalid refund amount (negative).
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to refund invalid amount (negative)
    success, msg = refund_late_fee_payment("txn_123", -0.50, mock_gateway)

    assert success == False
    assert "must be greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_invalid_amount_zero():
    """
    Test invalid refund amount (zero).
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to refund invalid amount (0)
    success, msg = refund_late_fee_payment("txn_123", 0.0, mock_gateway)

    assert success == False
    assert "must be greater than 0" in msg

    mock_gateway.refund_payment.assert_not_called()

def test_refund_late_fee_invalid_amount_exceeds_max():
    """
    Test invalid refund amount (exceeds $15 maximum).
    """
    mock_gateway = Mock(spec=PaymentGateway)

    # Attempt to refund invalid amount (over $15)
    success, msg = refund_late_fee_payment("txn_123", 15.50, mock_gateway)

    assert success == False
    assert "exceeds maximum late fee" in msg

    mock_gateway.refund_payment.assert_not_called()

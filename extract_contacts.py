import re

def extract_emails(text):
    """Extracts email addresses from text and validates them."""
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)

    # ✅ Validate emails
    valid_emails = [email for email in emails if validate_email(email)]
    invalid_emails = list(set(emails) - set(valid_emails))

    return valid_emails, invalid_emails

def validate_email(email):
    """Validates an email format."""
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return re.match(email_pattern, email) is not None

def extract_phone_numbers(text):
    """Extracts phone numbers from text and validates them."""
    phone_pattern = r"\b\d{10,15}\b"  # Matches numbers between 10 to 15 digits
    phone_numbers = re.findall(phone_pattern, text)

    # ✅ Validate phone numbers
    valid_numbers = [num for num in phone_numbers if validate_phone_number(num)]
    invalid_numbers = list(set(phone_numbers) - set(valid_numbers))

    return valid_numbers, invalid_numbers

def validate_phone_number(phone):
    """Validates a phone number (checks if it's digits only and reasonable length)."""
    return phone.isdigit() and 10 <= len(phone) <= 15

# app/core/validators.py

"""
Core Validators Module
=====================

Custom Pydantic validators and validation functions used throughout the application.
Provides reusable validation logic for common data types and business rules.
"""

import re
import uuid
from typing import Any, Optional, List, Dict, Union
from decimal import Decimal, InvalidOperation
from datetime import datetime, date
from email_validator import validate_email as validate_email_format, EmailNotValidError
import phonenumbers
from phonenumbers import NumberParseException, PhoneNumberFormat


# =============================================================================
# UUID VALIDATORS
# =============================================================================

def validate_uuid(value: Any) -> str:
    """
    Validate UUID string format
    
    Args:
        value: Value to validate
        
    Returns:
        str: Valid UUID string
        
    Raises:
        ValueError: If not a valid UUID
    """
    if value is None:
        raise ValueError("UUID cannot be None")
    
    if isinstance(value, uuid.UUID):
        return str(value)
    
    if not isinstance(value, str):
        raise ValueError("UUID must be a string")
    
    try:
        # Parse and reformat to ensure standard format
        parsed_uuid = uuid.UUID(value)
        return str(parsed_uuid)
    except ValueError:
        raise ValueError(f"Invalid UUID format: {value}")


def validate_uuid_optional(value: Any) -> Optional[str]:
    """
    Validate optional UUID string format
    
    Args:
        value: Value to validate
        
    Returns:
        Optional[str]: Valid UUID string or None
    """
    if value is None or value == "":
        return None
    
    return validate_uuid(value)


# =============================================================================
# PERCENTAGE VALIDATORS  
# =============================================================================

def validate_percentage(
    value: Any, 
    min_value: float = 0.0, 
    max_value: float = 100.0, 
    allow_negative: bool = False
) -> Decimal:
    """
    Validate percentage values
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_negative: Whether negative values are allowed
        
    Returns:
        Decimal: Valid percentage value
        
    Raises:
        ValueError: If not a valid percentage
    """
    if value is None:
        raise ValueError("Percentage cannot be None")
    
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"Invalid percentage format: {value}")
    
    # Check negative values
    if not allow_negative and decimal_value < 0:
        raise ValueError("Percentage cannot be negative")
    
    # Check range
    if decimal_value < Decimal(str(min_value)):
        raise ValueError(f"Percentage must be at least {min_value}")
    
    if decimal_value > Decimal(str(max_value)):
        raise ValueError(f"Percentage cannot exceed {max_value}")
    
    return decimal_value


def validate_percentage_optional(
    value: Any, 
    min_value: float = 0.0, 
    max_value: float = 100.0, 
    allow_negative: bool = False
) -> Optional[Decimal]:
    """
    Validate optional percentage values
    """
    if value is None or value == "":
        return None
    
    return validate_percentage(value, min_value, max_value, allow_negative)


# =============================================================================
# CURRENCY VALIDATORS
# =============================================================================

def validate_currency(
    value: Any, 
    min_value: float = 0.0, 
    max_value: Optional[float] = None,
    allow_negative: bool = False,
    decimal_places: int = 2
) -> Decimal:
    """
    Validate currency/monetary values
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        allow_negative: Whether negative values are allowed
        decimal_places: Maximum decimal places allowed
        
    Returns:
        Decimal: Valid currency value
        
    Raises:
        ValueError: If not a valid currency amount
    """
    if value is None:
        raise ValueError("Currency amount cannot be None")
    
    try:
        decimal_value = Decimal(str(value))
    except (InvalidOperation, TypeError):
        raise ValueError(f"Invalid currency format: {value}")
    
    # Check decimal places
    if abs(decimal_value.as_tuple().exponent) > decimal_places:
        raise ValueError(f"Currency cannot have more than {decimal_places} decimal places")
    
    # Check negative values
    if not allow_negative and decimal_value < 0:
        raise ValueError("Currency amount cannot be negative")
    
    # Check minimum value
    if decimal_value < Decimal(str(min_value)):
        raise ValueError(f"Currency amount must be at least {min_value}")
    
    # Check maximum value
    if max_value is not None and decimal_value > Decimal(str(max_value)):
        raise ValueError(f"Currency amount cannot exceed {max_value}")
    
    return decimal_value


def validate_currency_code(value: Any) -> str:
    """
    Validate ISO 4217 currency codes
    
    Args:
        value: Currency code to validate
        
    Returns:
        str: Valid currency code
        
    Raises:
        ValueError: If not a valid currency code
    """
    if not isinstance(value, str):
        raise ValueError("Currency code must be a string")
    
    # Convert to uppercase
    code = value.upper().strip()
    
    if len(code) != 3:
        raise ValueError("Currency code must be exactly 3 characters")
    
    if not code.isalpha():
        raise ValueError("Currency code must contain only letters")
    
    # Basic validation - could be extended with ISO 4217 list
    common_currencies = {
        'USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 
        'AED', 'SAR', 'LBP', 'EGP', 'QAR', 'KWD', 'BHD', 'OMR'
    }
    
    # For now, accept any 3-letter code but could be restricted to known currencies
    return code


# =============================================================================
# EMAIL VALIDATORS
# =============================================================================

def validate_email(value: Any) -> str:
    """
    Validate email address format
    
    Args:
        value: Email to validate
        
    Returns:
        str: Valid email address
        
    Raises:
        ValueError: If not a valid email
    """
    if not isinstance(value, str):
        raise ValueError("Email must be a string")
    
    email = value.strip().lower()
    
    if not email:
        raise ValueError("Email cannot be empty")
    
    try:
        # Use email-validator library for comprehensive validation
        valid_email = validate_email_format(email)
        return valid_email.email
    except EmailNotValidError as e:
        raise ValueError(f"Invalid email format: {str(e)}")


# =============================================================================
# PHONE NUMBER VALIDATORS
# =============================================================================

def validate_phone_number(value: Any, country_code: str = "US") -> str:
    """
    Validate phone number format
    
    Args:
        value: Phone number to validate
        country_code: Default country code for parsing
        
    Returns:
        str: Formatted phone number
        
    Raises:
        ValueError: If not a valid phone number
    """
    if not isinstance(value, str):
        raise ValueError("Phone number must be a string")
    
    phone = value.strip()
    
    if not phone:
        raise ValueError("Phone number cannot be empty")
    
    try:
        # Parse phone number with country context
        parsed_number = phonenumbers.parse(phone, country_code)
        
        # Validate the parsed number
        if not phonenumbers.is_valid_number(parsed_number):
            raise ValueError("Invalid phone number")
        
        # Return in international format
        return phonenumbers.format_number(parsed_number, PhoneNumberFormat.E164)
        
    except NumberParseException as e:
        raise ValueError(f"Invalid phone number format: {str(e)}")


# =============================================================================
# NAME VALIDATORS
# =============================================================================

def validate_name(value: Any, min_length: int = 1, max_length: int = 100) -> str:
    """
    Validate person/entity name
    
    Args:
        value: Name to validate
        min_length: Minimum length required
        max_length: Maximum length allowed
        
    Returns:
        str: Valid name
        
    Raises:
        ValueError: If not a valid name
    """
    if not isinstance(value, str):
        raise ValueError("Name must be a string")
    
    name = value.strip()
    
    if len(name) < min_length:
        raise ValueError(f"Name must be at least {min_length} characters long")
    
    if len(name) > max_length:
        raise ValueError(f"Name cannot exceed {max_length} characters")
    
    # Check for valid characters (letters, spaces, hyphens, apostrophes)
    if not re.match(r"^[a-zA-Z\s\-'\.]+$", name):
        raise ValueError("Name contains invalid characters")
    
    # Check for consecutive spaces or special characters
    if re.search(r"[\s\-']{2,}", name):
        raise ValueError("Name contains consecutive special characters")
    
    return name


# =============================================================================
# DATE VALIDATORS
# =============================================================================

def validate_date_range(
    start_date: Any, 
    end_date: Any, 
    allow_same_date: bool = True
) -> tuple[date, date]:
    """
    Validate date range
    
    Args:
        start_date: Start date
        end_date: End date  
        allow_same_date: Whether start and end can be the same
        
    Returns:
        tuple: (start_date, end_date) as date objects
        
    Raises:
        ValueError: If invalid date range
    """
    if not isinstance(start_date, date):
        raise ValueError("Start date must be a date object")
    
    if not isinstance(end_date, date):
        raise ValueError("End date must be a date object")
    
    if end_date < start_date:
        raise ValueError("End date must be after start date")
    
    if not allow_same_date and end_date == start_date:
        raise ValueError("End date must be different from start date")
    
    return start_date, end_date


def validate_age(birth_date: Any, min_age: int = 0, max_age: int = 150) -> int:
    """
    Validate age based on birth date
    
    Args:
        birth_date: Date of birth
        min_age: Minimum allowed age
        max_age: Maximum allowed age
        
    Returns:
        int: Calculated age
        
    Raises:
        ValueError: If invalid age
    """
    if not isinstance(birth_date, date):
        raise ValueError("Birth date must be a date object")
    
    today = date.today()
    
    if birth_date > today:
        raise ValueError("Birth date cannot be in the future")
    
    # Calculate age
    age = today.year - birth_date.year
    
    # Adjust if birthday hasn't occurred this year
    if today.month < birth_date.month or (today.month == birth_date.month and today.day < birth_date.day):
        age -= 1
    
    if age < min_age:
        raise ValueError(f"Age must be at least {min_age}")
    
    if age > max_age:
        raise ValueError(f"Age cannot exceed {max_age}")
    
    return age


# =============================================================================
# TEXT VALIDATORS
# =============================================================================

def validate_text_length(
    value: Any, 
    min_length: int = 0, 
    max_length: int = 1000,
    strip_whitespace: bool = True
) -> str:
    """
    Validate text length
    
    Args:
        value: Text to validate
        min_length: Minimum length
        max_length: Maximum length
        strip_whitespace: Whether to strip leading/trailing whitespace
        
    Returns:
        str: Valid text
        
    Raises:
        ValueError: If invalid text length
    """
    if value is None:
        raise ValueError("Text cannot be None")
    
    if not isinstance(value, str):
        value = str(value)
    
    if strip_whitespace:
        value = value.strip()
    
    if len(value) < min_length:
        raise ValueError(f"Text must be at least {min_length} characters long")
    
    if len(value) > max_length:
        raise ValueError(f"Text cannot exceed {max_length} characters")
    
    return value


def validate_alphanumeric(value: Any, allow_spaces: bool = False) -> str:
    """
    Validate alphanumeric text
    
    Args:
        value: Text to validate
        allow_spaces: Whether spaces are allowed
        
    Returns:
        str: Valid alphanumeric text
        
    Raises:
        ValueError: If contains non-alphanumeric characters
    """
    if not isinstance(value, str):
        raise ValueError("Value must be a string")
    
    text = value.strip()
    
    if not text:
        raise ValueError("Text cannot be empty")
    
    if allow_spaces:
        pattern = r"^[a-zA-Z0-9\s]+$"
        error_msg = "Text can only contain letters, numbers, and spaces"
    else:
        pattern = r"^[a-zA-Z0-9]+$"
        error_msg = "Text can only contain letters and numbers"
    
    if not re.match(pattern, text):
        raise ValueError(error_msg)
    
    return text


# =============================================================================
# NUMERIC VALIDATORS
# =============================================================================

def validate_positive_number(value: Any, include_zero: bool = False) -> Union[int, float, Decimal]:
    """
    Validate positive numbers
    
    Args:
        value: Number to validate
        include_zero: Whether zero is considered positive
        
    Returns:
        Number: Valid positive number
        
    Raises:
        ValueError: If not positive
    """
    if value is None:
        raise ValueError("Number cannot be None")
    
    try:
        if isinstance(value, str):
            # Try to parse as decimal first, then int, then float
            try:
                num_value = Decimal(value)
            except InvalidOperation:
                num_value = float(value)
        else:
            num_value = value
    except (ValueError, TypeError):
        raise ValueError(f"Invalid number format: {value}")
    
    if include_zero:
        if num_value < 0:
            raise ValueError("Number must be positive or zero")
    else:
        if num_value <= 0:
            raise ValueError("Number must be positive")
    
    return num_value


def validate_integer_range(
    value: Any, 
    min_value: Optional[int] = None, 
    max_value: Optional[int] = None
) -> int:
    """
    Validate integer within range
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value
        max_value: Maximum allowed value
        
    Returns:
        int: Valid integer
        
    Raises:
        ValueError: If not valid integer in range
    """
    try:
        int_value = int(value)
    except (ValueError, TypeError):
        raise ValueError(f"Invalid integer format: {value}")
    
    if min_value is not None and int_value < min_value:
        raise ValueError(f"Integer must be at least {min_value}")
    
    if max_value is not None and int_value > max_value:
        raise ValueError(f"Integer cannot exceed {max_value}")
    
    return int_value


# =============================================================================
# BUSINESS-SPECIFIC VALIDATORS
# =============================================================================

def validate_policy_number(value: Any) -> str:
    """
    Validate insurance policy number format
    
    Args:
        value: Policy number to validate
        
    Returns:
        str: Valid policy number
        
    Raises:
        ValueError: If invalid format
    """
    if not isinstance(value, str):
        raise ValueError("Policy number must be a string")
    
    policy_num = value.strip().upper()
    
    if not policy_num:
        raise ValueError("Policy number cannot be empty")
    
    # Basic format: 2-3 letter prefix + 6-12 digits
    if not re.match(r"^[A-Z]{2,3}[0-9]{6,12}$", policy_num):
        raise ValueError("Invalid policy number format")
    
    return policy_num


def validate_national_id(value: Any, country: str = "US") -> str:
    """
    Validate national ID number
    
    Args:
        value: ID number to validate
        country: Country code for format validation
        
    Returns:
        str: Valid ID number
        
    Raises:
        ValueError: If invalid format
    """
    if not isinstance(value, str):
        raise ValueError("National ID must be a string")
    
    id_num = value.strip()
    
    if not id_num:
        raise ValueError("National ID cannot be empty")
    
    # Basic validation - could be extended for specific countries
    if country.upper() == "US":
        # SSN format: XXX-XX-XXXX or XXXXXXXXX
        ssn = re.sub(r"[^0-9]", "", id_num)
        if len(ssn) != 9:
            raise ValueError("Invalid SSN format")
        return f"{ssn[:3]}-{ssn[3:5]}-{ssn[5:]}"
    
    # Generic validation for other countries
    if not re.match(r"^[A-Z0-9\-]{5,20}$", id_num.upper()):
        raise ValueError("Invalid national ID format")
    
    return id_num.upper()


# =============================================================================
# EXPORT ALL VALIDATORS
# =============================================================================

__all__ = [
    # UUID validators
    'validate_uuid',
    'validate_uuid_optional',
    
    # Percentage validators
    'validate_percentage',
    'validate_percentage_optional',
    
    # Currency validators
    'validate_currency',
    'validate_currency_code',
    
    # Email validators
    'validate_email',
    
    # Phone validators
    'validate_phone_number',
    
    # Name validators
    'validate_name',
    
    # Date validators
    'validate_date_range',
    'validate_age',
    
    # Text validators
    'validate_text_length',
    'validate_alphanumeric',
    
    # Numeric validators
    'validate_positive_number',
    'validate_integer_range',
    
    # Business validators
    'validate_policy_number',
    'validate_national_id'
]
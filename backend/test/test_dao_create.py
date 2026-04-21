"""Integration tests for DAO.create method.

These tests verify the communication between the DAO and MongoDB,
focusing on whether the create method correctly enforces the validator
constraints defined for a collection.

Test cases are derived using the test design technique:

Conditions:
    C1: Data contains all required fields
    C2: Property values comply to bsonType constraints
    C3: Values of uniqueItems properties are unique

Test Cases:
    TC1: C1=yes, C2=yes, C3=yes → document created successfully
    TC2: C1=no,  C2=yes, C3=yes → WriteError (missing required field)
    TC3: C1=yes, C2=no,  C3=yes → WriteError (wrong data type)
    TC4: C1=yes, C2=yes, C3=no  → WriteError (duplicate uniqueItems value)
    TC5: C1=yes (+ extra fields), C2=yes, C3=yes → document created successfully
"""

import pytest
from pymongo.errors import WriteError


@pytest.mark.integration
class TestDAOCreate:

    def test_create_with_valid_data(self, sut):
        """TC1: All required fields present, correct types, unique values.
        Expected: document is created and returned with an _id field."""
        result = sut.create({"name": "Test Item"})

        assert result is not None
        assert "_id" in result
        assert result["name"] == "Test Item"

    def test_create_missing_required_field(self, sut):
        """TC2: Missing the required 'name' field.
        Expected: WriteError is raised."""
        with pytest.raises(WriteError):
            sut.create({"status": True})

    def test_create_wrong_data_type(self, sut):
        """TC3: 'name' field has wrong type (int instead of string).
        Expected: WriteError is raised."""
        with pytest.raises(WriteError):
            sut.create({"name": 123})

    def test_create_duplicate_unique_field(self, sut):
        """TC4: Inserting two documents with the same 'name' value,
        which is flagged as uniqueItems in the validator.
        Expected: WriteError is raised on the second insert."""
        sut.create({"name": "Duplicate"})

        with pytest.raises(WriteError):
            sut.create({"name": "Duplicate"})

    def test_create_with_extra_fields(self, sut):
        """TC5: All required fields present plus additional fields
        not defined in the validator schema.
        Expected: document is created successfully (MongoDB accepts extra fields)."""
        result = sut.create({"name": "Extra", "extra_field": "hello"})

        assert result is not None
        assert "_id" in result
        assert result["name"] == "Extra"
        assert result["extra_field"] == "hello"

    def test_create_with_valid_optional_field(self, sut):
        """TC6: Required field present plus optional 'status' field
        with correct boolean type.
        Expected: document is created successfully."""
        result = sut.create({"name": "With Status", "status": True})

        assert result is not None
        assert result["name"] == "With Status"
        assert result["status"] is True

    def test_create_optional_field_wrong_type(self, sut):
        """TC7: Required field present but optional 'status' field
        has wrong type (string instead of bool).
        Expected: WriteError is raised."""
        with pytest.raises(WriteError):
            sut.create({"name": "Bad Status", "status": "yes"})

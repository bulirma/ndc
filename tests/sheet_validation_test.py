import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic.validation import sheet as sheetval

def test_sheet_collection_valid_1():
    form_data = {
        'light-condition': 'flashlight',
        'quality': 'satisfactory',
    }
    result = sheetval.validate_sheet_collection_data(form_data)
    assert result.is_valid()

def test_sheet_collection_valid_2():
    form_data = {
        'light-condition': 'dark',
        'quality': 'poor',
    }
    result = sheetval.validate_sheet_collection_data(form_data)
    assert result.is_valid()

def test_sheet_collection_invalid_1():
    form_data = {
        'light-condition': 'cloudy',
        'quality': 'top',
    }
    result = sheetval.validate_sheet_collection_data(form_data)
    assert not result.is_valid()

def test_sheet_collection_invalid_2():
    form_data = {
        'light-condition': 'dimmed',
        'quality': 'bad',
    }
    result = sheetval.validate_sheet_collection_data(form_data)
    assert not result.is_valid()

"""
CLI Utilities
=============
Helper functions for the CLI interface.
"""

import pandas as pd
from .translations import MESSAGES, PRODUCT_FIELDS

def print_dataframe(data, columns=None):
    """
    Prints a list of dictionaries as a markdown table using pandas.
    
    Args:
        data (list): List of dictionaries containing the data.
        columns (list, optional): List of column names to display. 
                                  If None, all columns are displayed.
    """
    if not data:
        print(MESSAGES['no_results'])
        return

    try:
        df = pd.DataFrame(data)
        
        # Format datetime columns
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                # Format datetime objects to YYYY-MM-DD HH:MM
                # Use .dt accessor for series
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M')
                # Replace NaT with empty string
                df[col] = df[col].fillna('')
            # Also handle object columns that might contain datetimes (e.g. from peewee)
            elif df[col].dtype == 'object':
                 try:
                     # Try to convert to datetime and format, but only if it looks like a datetime
                     # This is a bit risky if mixed types, but let's try for known date columns
                     # Or better, check if the first non-null value is a datetime object
                     first_valid = df[col].dropna().iloc[0] if not df[col].dropna().empty else None
                     if hasattr(first_valid, 'strftime'):
                         df[col] = df[col].apply(lambda x: x.strftime('%Y-%m-%d %H:%M') if pd.notnull(x) and hasattr(x, 'strftime') else x)
                 except Exception:
                     pass # Ignore if conversion fails

        # Fill NaN values with empty string for better display
        df = df.fillna('')
        
        if columns:
            # Filter columns if they exist in the dataframe
            valid_columns = [col for col in columns if col in df.columns]
            if valid_columns:
                df = df[valid_columns]
        
        # Rename columns using translations
        df = df.rename(columns=PRODUCT_FIELDS)
        
        print(df.to_markdown(index=False))
    except Exception as e:
        print(f"Error printing table: {e}")

def print_success(message):
    """Prints a success message."""
    print(MESSAGES['result_format'].format(status=MESSAGES['success'], message=message))

def print_error(message):
    """Prints an error message."""
    print(MESSAGES['result_format'].format(status=MESSAGES['error'], message=message))

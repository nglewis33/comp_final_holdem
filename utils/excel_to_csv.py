#!/usr/bin/env python3

import os
import sys
import pandas as pd
import argparse

def excel_to_csv(excel_file, output_file=None, sheet_name=0, index=False):
    """
    Convert an Excel file to CSV format.
    
    Args:
        excel_file (str): Path to the Excel file
        output_file (str, optional): Path to the output CSV file. 
                                    If None, uses the same name as the Excel file with .csv extension
        sheet_name (str/int, optional): Name or index of the sheet to convert. Default is the first sheet.
        index (bool, optional): Whether to include the index column in the CSV. Default is False.
    
    Returns:
        str: Path to the created CSV file
    """
    try:
        # Read the Excel file
        print(f"Reading Excel file: {excel_file}")
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        
        # Determine output file name if not provided
        if output_file is None:
            base_name = os.path.splitext(excel_file)[0]
            output_file = f"{base_name}.csv"
        
        # Write to CSV
        print(f"Converting to CSV: {output_file}")
        df.to_csv(output_file, index=index)
        
        print(f"Conversion complete! CSV file saved at: {output_file}")
        return output_file
    
    except Exception as e:
        print(f"Error converting Excel to CSV: {str(e)}")
        return None

def main():
    """Command line interface for the excel_to_csv function."""
    parser = argparse.ArgumentParser(description='Convert an Excel file to CSV format')
    parser.add_argument('excel_file', help='Path to the Excel file to convert')
    parser.add_argument('-o', '--output', help='Path to the output CSV file (optional)')
    parser.add_argument('-s', '--sheet', default=0, 
                        help='Sheet name or index to convert (default: first sheet)')
    parser.add_argument('--index', action='store_true', 
                        help='Include index column in the CSV output')
    
    args = parser.parse_args()
    
    # Try to parse sheet as an integer if it's numeric
    try:
        sheet = int(args.sheet)
    except ValueError:
        sheet = args.sheet
    
    excel_to_csv(args.excel_file, args.output, sheet, args.index)

if __name__ == "__main__":
    main() 
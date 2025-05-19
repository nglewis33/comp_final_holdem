# Excel to CSV Converter

A simple Python utility to convert Excel files (.xlsx, .xls) to CSV format.

## Features

- Convert any Excel file to CSV format
- Specify which sheet to convert
- Option to include or exclude the index column
- Simple command-line interface
- Can also be imported and used as a module in other Python scripts

## Installation

1. Ensure you have Python 3.6+ installed
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Command Line

Basic usage:

```bash
python excel_to_csv.py your_excel_file.xlsx
```

This will convert the first sheet of `your_excel_file.xlsx` to `your_excel_file.csv`.

Options:

```bash
python excel_to_csv.py your_excel_file.xlsx -o output_file.csv -s "Sheet2" --index
```

Arguments:
- `excel_file`: Path to the Excel file to convert (required)
- `-o, --output`: Path to the output CSV file (optional)
- `-s, --sheet`: Sheet name or index to convert (default: first sheet)
- `--index`: Include index column in the CSV output (optional)

### As a Module

You can also import the script and use it in your own Python code:

```python
from excel_to_csv import excel_to_csv

# Convert Excel to CSV
csv_file = excel_to_csv(
    excel_file="your_excel_file.xlsx",
    output_file="output_file.csv",  # Optional
    sheet_name="Sheet1",            # Optional, default is first sheet
    index=False                     # Optional, default is False
)

print(f"CSV file created at: {csv_file}")
```

## Examples

1. Convert the first sheet of an Excel file:

```bash
python excel_to_csv.py data.xlsx
```

2. Convert a specific sheet by name:

```bash
python excel_to_csv.py data.xlsx -s "Sales Data"
```

3. Convert a specific sheet by index (0-based):

```bash
python excel_to_csv.py data.xlsx -s 2
```

4. Specify the output file name:

```bash
python excel_to_csv.py data.xlsx -o sales_data.csv
```

5. Include the index column in the output:

```bash
python excel_to_csv.py data.xlsx --index
```

## Requirements

- pandas
- openpyxl (for .xlsx files)
- xlrd (for .xls files) 
"""
JSON to Excel Converter
Extracts table data from JSON files and converts to Excel format
"""

import json
import pandas as pd
import os

# ==================== CONFIGURATION ====================
JSON_FILE = ""  # Change to your file name

# ==================== MAIN PROCESS ====================
def convert_json_to_excel(json_file):
    """Convert JSON table data to Excel file"""
    
    # Check if file exists
    if not os.path.exists(json_file):
        print(f"❌ Error: File '{json_file}' not found")
        return False
    
    try:
        # Load JSON
        print(f"Loading JSON file: {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        print(f"✓ JSON loaded successfully")
        
        # Find the table entry
        print("Searching for table data in JSON...")
        table_entry = next((item for item in data if item.get("type") == "table"), None)
        
        if table_entry and "data" in table_entry:
            table_name = table_entry.get("name", "output")
            table_data = table_entry["data"]
            
            print(f"✓ Found table: {table_name}")
            print(f"  Records: {len(table_data)}")
            
            # Convert to DataFrame
            df = pd.DataFrame(table_data)
            
            # Display info
            print(f"\nTable Structure:")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Rows: {len(df)}")
            
            # Generate output filename
            output_file = f"{table_name}.xlsx"
            
            # Save to Excel
            print(f"\nSaving to Excel: {output_file}")
            df.to_excel(output_file, index=False, engine='openpyxl')
            
            print(f"\n{'='*60}")
            print(f"✅ SUCCESS")
            print(f"{'='*60}")
            print(f"Input File  : {json_file}")
            print(f"Output File : {output_file}")
            print(f"Records     : {len(df)}")
            print(f"Columns     : {len(df.columns)}")
            print(f"{'='*60}")
            
            return True
        else:
            print("⚠ Could not find table data in JSON.")
            print("\nJSON Structure:")
            if isinstance(data, list):
                print(f"  Type: List with {len(data)} items")
                if len(data) > 0:
                    print(f"  First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
            elif isinstance(data, dict):
                print(f"  Type: Dictionary")
                print(f"  Keys: {list(data.keys())}")
            else:
                print(f"  Type: {type(data)}")
            
            return False
            
    except json.JSONDecodeError as e:
        print(f"❌ Error: Invalid JSON format - {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

# ==================== MAIN EXECUTION ====================
if __name__ == "__main__":
    print("=" * 60)
    print(" " * 15 + "JSON TO EXCEL CONVERTER")
    print("=" * 60)
    print()
    
    success = convert_json_to_excel(JSON_FILE)
    
    if not success:
        print("\n❌ Conversion failed. Please check the error messages above.")
    
    print()
import pandas as pd
import json

def create_product_fixtures(excel_file='product_data.xlsx', output_json='products_fixture.json'):
    # 1. Read the Excel file
    # Ensure invalid values (NA) are handled correctly
    try:
        df = pd.read_excel('product_data.xlsx')
    except FileNotFoundError:
        print(f"Error: File '{excel_file}' not found.")
        return

    fixtures = []

    # 2. Iterate through each row in the Excel sheet
    for index, row in df.iterrows():
        
        # Handle 'package_details': Parse string to JSON if it exists, else null
        package_details_raw = row['package_details']
        package_details = None

        if pd.notna(package_details_raw) and str(package_details_raw).strip() != "":
            try:
                # The Excel data looks like a JSON string, so we parse it
                # Using strings directly from Excel might contain single quotes instead of double
                # We replace single quotes with double quotes for valid JSON parsing if necessary
                cleaned_string = str(package_details_raw).replace("'", '"')
                package_details = json.loads(cleaned_string)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse package_details for ID {row['id']}. Setting to null.")
                package_details = None

        # 3. Construct the fixture object
        fixture = {
            "model": "products.product",
            "pk": int(row['id']),
            "fields": {
                "product_type": row['product_type'],
                "created_at": "2024-07-01T00:00:00Z", # Default static value
                "updated_at": "2024-07-01T00:00:00Z", # Default static value
                "product_group": int(row['product_group']),
                "code": str(row['code']).strip(),
                "name": str(row['name']).strip(),
                "price": int(row['price']) if pd.notna(row['price']) else 0,
                "package_details": package_details
            }
        }
        
        fixtures.append(fixture)

    # 4. Write to JSON file
    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=4)

    print(f"Successfully converted {len(fixtures)} items to {output_json}")

# --- Execution ---
if __name__ == "__main__":
    # Replace 'products.xlsx' with your actual file name
    create_product_fixtures('products.xlsx', 'products_fixture.json')
import pandas as pd
import json
def main():
    # 1. Load the Excel file
    df = pd.read_excel('customer_data.xlsx')

    # 2. Define default values
    defaults = {
        "ward_id": None,
        "is_active": True,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }

    fixtures = []

    # 3. Iterate through rows
    for index, row in df.iterrows():
        # Handle NaN values (empty cells) for province_id
        province_id = row['province_id']
        if pd.isna(province_id):
            province_id = None
        else:
            province_id = int(province_id)

        # Handle NaN values for address
        address = row['address']
        if pd.isna(address):
            address = ""

        fixture = {
            "model": "customers.Customer",
            "pk": int(row['id']),
            "fields": {
                "name": row['name'],
                "code": row['code'],
                "phone_number": str(row['phone_number']).replace('.0', ''), # Ensure string format
                "address": address,
                "province_id": province_id,
                **defaults # Unpack default values
            }
        }
        fixtures.append(fixture)

    # 4. Write to JSON file
    with open('customers_fixture.json', 'w', encoding='utf-8') as f:
        json.dump(fixtures, f, ensure_ascii=False, indent=4)

    print("Fixture JSON created successfully!")

if __name__ == "__main__":
    main()
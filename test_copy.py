import pandas as pd
from sqlalchemy import create_engine

def main (): 

    # 1. Database Connection Config
    # Replace these values with your actual database credentials
    DB_HOST = '139.162.30.203'        # e.g., 'localhost' or an IP address
    DB_NAME = 'fp'        # e.g., 'postgres'
    DB_USER = 'postgres'       # e.g., 'postgres'
    DB_PASS = 'jUsTjin74#!'       # e.g., 'password123'
    DB_PORT = '5432'                # Default is usually 5432

    # 2. Create the SQLAlchemy connection engine
    # Format: postgresql+psycopg2://user:password@host:port/dbname
    connection_str = f'postgresql+psycopg2://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
    engine = create_engine(connection_str)

    # 3. Define your SQL Query
    # Note: We use triple quotes (""") for multi-line strings.
    # Python handles the double quotes inside the string automatically.
    sql_query = """
    SELECT "createdDate", "tradeMarkName", id, "retailerId", code, name, "fullName", "categoryId", "categoryName", "allowsSale", type, "hasVariants", "basePrice", weight, "conversionValue", description, "modifiedDate", "isActive", "orderTemplate", "isLotSerialControl", "isBatchExpireControl", inventories, "productFormulas", "barCode", images, unit, "kiotId", "tradeMarkId", "taxType", attributes, "masterProductId"
	FROM public.products
    WHERE "kiotId" = 'fitpackhanoi';
    """

    try:
        print("Connecting to database and executing query...")
        
        # 4. Read data into a Pandas DataFrame
        df = pd.read_sql(sql_query, engine)
        
        # Check if data was retrieved
        if not df.empty:
            print(f"Successfully retrieved {len(df)} rows.")
            
            # 5. Save to Excel
            output_file = "product_data.xlsx"
            df.to_excel(output_file, index=False, engine='openpyxl')
            
            print(f"Data saved successfully to '{output_file}'")
        else:
            print("Query executed, but no results were found matching 'fitpackhanoi'.")

    except Exception as e:
        print("An error occurred:")
        print(e)


if __name__ == "__main__":
    main()
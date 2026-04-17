import pymysql
import ssl

# Aiven database connection details
config = {
    'host': 'mysql-277ebaee-leezagupta271-e93f.d.aivencloud.com',
    'user': 'avnadmin',
    'password': input('Enter your Aiven MySQL password: '),
    'database': 'defaultdb',
    'port': 13716,
    'ssl_verify_cert': False,
    'ssl_disabled': False
}

# Read SQL file
with open('database.sql', 'r') as f:
    sql_content = f.read()

# Connect and execute
try:
    connection = pymysql.connect(**config)
    cursor = connection.cursor()
    
    # Split and execute statements
    statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
    
    for statement in statements:
        print(f"Executing: {statement[:60]}...")
        cursor.execute(statement)
    
    connection.commit()
    print("\n✅ All tables created successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'cursor' in locals():
        cursor.close()
    if 'connection' in locals():
        connection.close()

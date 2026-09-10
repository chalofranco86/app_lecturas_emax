# test_connection.py
from app.models.database import execute_query

query = "SELECT * FROM inmuebles"
result = execute_query(query, fetch=True)
print(result)
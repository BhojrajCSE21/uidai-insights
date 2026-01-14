"""
Database connection and operations
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
import pandas as pd
from config.db_config import DB_URL
from config.config import *

class Database:
    def __init__(self):
        """Initialize database connection"""
        try:
            self.engine = create_engine(DB_URL)
            print("✅ Database connection established")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            raise
    
    def test_connection(self):
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT version();"))
                version = result.fetchone()[0]
                print(f"✅ PostgreSQL Version: {version}")
                return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False
    
    def load_data_to_db(self, df, table_name, if_exists='replace'):
        """
        Load DataFrame to PostgreSQL
        
        Args:
            df: pandas DataFrame
            table_name: Name of the table
            if_exists: 'replace', 'append', or 'fail'
        """
        try:
            df.to_sql(table_name, self.engine, if_exists=if_exists, index=False)
            print(f"✅ Loaded {len(df)} rows to table '{table_name}'")
            return True
        except Exception as e:
            print(f"❌ Failed to load data to '{table_name}': {e}")
            return False
    
    def read_from_db(self, table_name):
        """Read data from PostgreSQL table"""
        try:
            df = pd.read_sql(f"SELECT * FROM {table_name}", self.engine)
            print(f"✅ Retrieved {len(df)} rows from '{table_name}'")
            return df
        except Exception as e:
            print(f"❌ Failed to read from '{table_name}': {e}")
            return None
    
    def execute_query(self, query):
        """Execute custom SQL query"""
        try:
            df = pd.read_sql(query, self.engine)
            return df
        except Exception as e:
            print(f"❌ Query execution failed: {e}")
            return None
    
    def get_table_info(self, table_name):
        """Get information about table"""
        query = f"""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = '{table_name}';
        """
        return self.execute_query(query)

# Test the connection
if __name__ == "__main__":
    db = Database()
    db.test_connection()

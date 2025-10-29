import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    
    def connect(self, host=None, port=None, database=None, user=None, password=None):
        try:
            if all(param is None for param in [host, port, database, user, password]):
                host, port, database, user, password = "localhost", "5432", "postgres", "postgres", "1"
            
            self.connection = psycopg2.connect(
                host=host,
                port=port,
                database=database,
                user=user,
                password=password
            )
            return True
        except Exception as e:
            print(f"Error de conexión: {e}")
            return False
    
    def execute_query(self, query, params=None):
        # Método para ejecutar consultas
        pass
    
    def close(self):
        if self.connection:
            self.connection.close()
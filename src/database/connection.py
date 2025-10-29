import psycopg2

class DatabaseConnection:
    def __init__(self):
        self.connection = None
    
    def connect(self, host=None, port=None, database=None, user=None, password=None):
        try:
            if all(param is None for param in [host, port, database, user, password]):
                host, port, database, user, password = "localhost", "5432", "postgres", "postgres", "Roman_3119"
            
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
        
    def get_user_hash(self, username):
        """
        Busca el hash de contraseña para un nombre de usuario dado.
        Retorna el hash si el usuario existe, None si no.
        """
        if not self.connection:
            print("Error: No hay conexión a la base de datos activa.")
            return None
        
        query = "SELECT password_hash FROM users WHERE username = %s;"
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query, (username,))
                result = cursor.fetchone() # fetchone() retorna una tupla o None
                if result:
                    return result[0] # Retorna el primer elemento (el hash)
                else:
                    return None # Usuario no encontrado
        except Exception as e:
            print(f"Error al buscar usuario: {e}")
            # Considera propagar el error o loggearlo
            return None
    
    def execute_query(self, query, params=None):
        # Método para ejecutar consultas
        pass
    
    def close(self):
        if self.connection:
            self.connection.close()
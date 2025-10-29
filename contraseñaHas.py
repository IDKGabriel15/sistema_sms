# Script rápido para generar hash (ejecútalo una vez)
import bcrypt
import getpass # Para no mostrar la contraseña al escribir

password = getpass.getpass("Ingresa la contraseña para el nuevo usuario: ").encode('utf-8')
hashed = bcrypt.hashpw(password, bcrypt.gensalt())
print(f"Hash generado (copia esto en tu SQL): {hashed.decode('utf-8')}")
import smtplib
import time

# Configuración del correo
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_SENDER = "rspalerta@celeren.com"
EMAIL_PASSWORD = "qscxhzzdcmlflfcj"
EMAIL_RECEIVER = "leonardo.rojas@celeren.com"
LOG_FILE = "C:\\Users\\Leonardo Rojas\\Downloads\\archivo.log"  # Reemplaza con la ruta de tu archivo de logs

# Función para enviar el correo
def send_email(error_message):
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            subject = "Alerta: Se ha detectado un error en los logs"
            body = "Se ha detectado el siguiente error en los logs:\n\n{}".format(error_message)
            message = "Subject: {}\n\n{}".format(subject,body)
            server.sendmail(EMAIL_SENDER, EMAIL_RECEIVER, message)
            print("Correo enviado exitosamente.")
    except Exception as e:
        print("Error al enviar correo: {e}")


# Ruta del archivo de logs (cambia esto según tu necesidad)
LOG_FILE = "C:\\Users\\Leonardo Rojas\\Downloads\\archivo.log"

# Función para leer e imprimir líneas con "Failed"
def buscar_errores():
    try:
        with open(LOG_FILE, "r") as file:
            for line in file:
                if "Perro" in line:
                    print(line.strip())  # Imprime la línea sin espacios extra
    except FileNotFoundError:
        print("Error: El archivo '{LOG_FILE}' no existe.")
    except Exception as e:
        print("Ocurrió un error: {e}")

# Ejecutar la función
if __name__ == "__main__":
   #buscar_errores()
    send_email(buscar_errores())
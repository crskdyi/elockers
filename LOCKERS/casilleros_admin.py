# PROGRAMA: Aministrador de Casilleros.

# Librerías necesarias
import sqlite3
import sys
import os

try:
    # Crear base de datos si no existe
    conn = sqlite3.Connection('casilleros.db')
    cursor = conn.cursor()
    print('<< Conexion creada')

    tb_creation = """ 
        CREATE TABLE IF NOT EXISTS casilleros (
            id INT PRIMARY KEY,
            edificio INT,
            en_uso BOOL
        );
    """ 
    cursor.execute(tb_creation)
    print('<< Tabla casilleros creada.')

    tb_user_creation = """
        CREATE TABLE IF NOT EXISTS users (
            user STRING PRIMARY KEY,
            password STRING,
            last INT
        )
    """
    cursor.execute(tb_user_creation)
    
    # 1. Generar Edificio 5 (INSERT OR IGNORE evita sobrescribir reservas)
    for i in range(1, 101):
        cursor.execute("INSERT OR IGNORE INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", (5000 + i, 5, False)) 
    
    # 2. Generar Polideportivo (edificio 1)
    for i in range(1, 225):
        cursor.execute("INSERT OR IGNORE INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", (1000 + i, 1, False))
        
    conn.commit()
    print('<< Registros verificados/actualizados.')

except sqlite3.Error as error: 
    print(f'<< Error en la base de datos: {error}')  

loggedin=False
#Inicio de sesion --->>>
while loggedin==False:
    print("Presione 1 para registrarse o 0 para iniciar sesion: ", end='')
    register=input()
    if (register=="1"):
        print("   Ingrese su usuario: ", end='')
        user=input()
        print("   Ingrese su contraseña: ", end='')
        password=input()
        try:
            cursor.execute("INSERT INTO users (user, password, last) VALUES (?,?,?)", (user, password, 0))
            conn.commit()
        except sqlite3.IntegrityError as error:
            print("<< USUARIO YA EXISTENTE")
    else:
        print("Ingrese su usuario: ")
        user=input()
        print("Ingrese su contraseña: ")
        in_pass=input()
        cursor.execute("SELECT password FROM users WHERE user = ?", (user,))
        out_pass=cursor.fetchone()
        
        # Validar que el usuario exista antes de comprobar contraseña
        if out_pass and str(out_pass[0]) == in_pass: 
            loggedin=True
            os.system('clear' if os.name == 'posix' else 'cls') # Compatible con Windows y Mac/Linux
            print("<< Acceso concedido")
        else:
            print("<< Contraseña o usuario incorrectos")

# Escoger accion
opt = 0
while opt != "1" and opt !="0":

    print("Ingrese 1 para reservar, 0 para liberar.")
    opt = input("Escoge una opcion >> ")
    
    if opt=="1":
        # Código para la consulta simple --->
        cursor.execute("SELECT id, edificio FROM casilleros WHERE en_uso = 0")
        output = cursor.fetchall()
        print('Los casilleros Disponibles son: ')
        for row in output:
            print('   ', row[0], 'Edificio:', row[1])

        # Reservar --->>>
        id_res=0
        # NUEVA VALIDACIÓN: Permitir 5001-5100 (Ed. 5) y 1001-1224 (Polideportivo)
        while not ((5000 < int(id_res) <= 5100) or (1000 < int(id_res) <= 1224)):
            print("Ingrese el ID del casillero que desea reservar >>", end=' ')
            id_res=input()
            try:
                if id_res.lower() == "exit":
                    break
                    
                id_num = int(id_res)
                if not ((5000 < id_num <= 5100) or (1000 < id_num <= 1224)):
                    print("<< Ingrese un ID de casillero válido...")
                    id_res = 0 # Reiniciar para que siga el bucle
                    continue
                    
                cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = ?", (id_num, 0))
                disp=cursor.fetchone()
                if(disp==None):
                    print("<< Casillero Ocupado o no existe")
                else:
                    cursor.execute("UPDATE casilleros SET en_uso = ? WHERE id = ?", (1, id_num))
                    conn.commit()
                    print("<< Casillero reservado con éxito!")
                id_res=0
                
            except ValueError:
                id_res=0

    elif opt == "0": 
        # Si se selecciona la opcion de liberar
        cursor.execute("SELECT id, edificio FROM casilleros WHERE en_uso = 1")
        output = cursor.fetchall()
        print('Los casilleros Ocupados son: ')
        for row in output:
            print('   ', row[0], 'Edificio:', row[1])

        id_lib = 0
        # NUEVA VALIDACIÓN: Permitir 5001-5100 (Ed. 5) y 1001-1224 (Polideportivo)
        while not ((5000 < int(id_lib) <= 5100) or (1000 < int(id_lib) <= 1224)):
            print("Ingrese el ID del casillero que desea liberar >>", end=' ')
            id_lib=input()
            try: 
                if id_lib.lower() == "exit":
                    break
                    
                id_num = int(id_lib)
                if not ((5000 < id_num <= 5100) or (1000 < id_num <= 1224)):
                    print("<< Ingrese un ID de casillero válido...")
                    id_lib = 0 # Reiniciar
                    continue
                    
                cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = ?", (id_num, 1))
                ocup=cursor.fetchone()
                if(ocup==None):
                    print("<< Casillero No Ocupado")
                else:
                    cursor.execute("UPDATE casilleros SET en_uso = ? WHERE id = ?", (0, id_num))
                    conn.commit()
                    print("<< Casillero liberado con éxito!")
                id_lib=0
                
            except ValueError: 
                id_lib=0

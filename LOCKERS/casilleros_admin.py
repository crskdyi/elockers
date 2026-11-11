# PROGRAMA: Aministrador de Casilleros.

# Librerías necesarias1
import sqlite3
import sys
import os

try:
    # Crear base de datos si no existe
    conn = sqlite3.Connection('casilleros.db')
    cursor = conn.cursor()
    print('<< Conexion creada')

    #   Los tipos de variables que se utilizarán en nuestra base de datos serán:
    #   id: tipo ENTERO, y LLAVE PRIMARIA
    #   edificio: tipo ENTERO.
    #   en_uso: tipo BOOLEANO o ENTERO (sqlite no tiene tipo booleano nativo, pero si primero se pasa por python
    #   se puede utilizar True y False, pero en la tabla se guardarán automaticamente como 1 y 0)}
    #   (vease la variable siguiente, usada para crear la tabla)

    tb_creation = """ 
        CREATE TABLE IF NOT EXISTS casilleros (
            id INT PRIMARY KEY,
            edificio INT,
            en_uso BOOL
        );
    """ # crea la tabla casilleros si no existe
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
    
    # El siguiente bucle se utiliza para crear los casilleros del edificio 5 (10 filas y 10 columnas, así que son 100)
    # Líneas usadas para agregar los registros iniciales
    
    for i in range(1, 101):
        cursor.execute("INSERT INTO casilleros (id, edificio, en_uso) VALUES (?, ?, ?)", (5000 + i, 5, False)) # crear registros
    # Su utiliza este código para hacer que los casilleros pares salgan como OCUPADOS
    cursor.execute("UPDATE casilleros SET en_uso = 0")
    

    conn.commit()

except sqlite3.IntegrityError as error: # si ya existen los registros, generaran el error de integridad y sabremos que ya existen
    print('<< Registros existentes.')  

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
        if str(out_pass[0]) == in_pass: 
            loggedin=True
            os.system('clear')
            print("<< Acceso concedido")
        else:
            print("<< Contraseña o usuario incorrectos")

# Escoger accion

opt = 0
while opt != "1" and opt !="0":

    print("Ingrese 1 para reservar, 0 para liberar.")
    opt = input("Escoge una opcion >> ")
    if opt=="1":

        #   Código para la consulta simple --->
        cursor.execute("SELECT id, edificio FROM casilleros WHERE en_uso = 0")
        output = cursor.fetchall()
        print('Los casilleros Disponibles son: ')
        for row in output:
            print('   ', row[0], 'Edificio:', row[1])


        # Reservar --->>>
        id_res=0
        while int(id_res)<5000 or int(id_res)>5100:
            print("Ingrese el ID del casillero que desea reservar >>", end=' ')
            id_res=input()
            try:
                if int(id_res)<5000 or int(id_res)>5100:
                    print("<< Ingrese un ID de casillero válido...")
                cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = ?", (int(id_res), 0))
                disp=cursor.fetchone()
                if(disp==None):
                    print("<< Casillero Ocupado")
                else:
                    cursor.execute("UPDATE casilleros SET en_uso = ? WHERE id = ?", (1, int(id_res)))
                    conn.commit()
                    print("<< Casillero reservado con éxito!")
                id_res=0;
            except ValueError:
                if id_res=="exit":
                    break;

                else:
                    id_res=0
    else:
        if opt == "0": # Si se selecciona la opcion de liberar

            cursor.execute("SELECT id, edificio FROM casilleros WHERE en_uso = 1")
            output = cursor.fetchall()
            print('Los casilleros Ocupados son: ')
            for row in output:
                print('   ', row[0], 'Edificio:', row[1])

            id_lib = 0
            while int(id_lib)<5000 or int(id_lib)>5100:
                print("Ingrese el ID del casillero que desea liberar >>", end=' ')

                id_lib=input()
                try: # Intentar convertir el input en un ENTERO

                    # Si lo que se ingresó es un número menor a 5000 o mayor a 5100
                    if int(id_lib)<5000 or int(id_lib)>5100:
                        print("<< Ingrese un ID de casillero válido...")
                    cursor.execute("SELECT * FROM casilleros WHERE id = ? AND en_uso = ?", (int(id_lib), 1))
                    ocup=cursor.fetchone()
                    if(ocup==None): # Si no regresa ningun casillero
                        print("<< Casillero No Ocupado")
                    else: # Si SÍ encuentra el casillero ingresado
                        cursor.execute("UPDATE casilleros SET en_uso = ? WHERE id = ?", (0, int(id_lib)))
                        conn.commit()
                        print("<< Casillero liberado con éxito!")
                    id_lib=0;
                except ValueError: # Si el input no fue un entero
                    if id_lib=="exit": # Si el input en realidad es "exit" sale del bucle
                        break;

                    else:
                        id_lib=0


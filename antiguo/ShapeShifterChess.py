import gamelib
import random

AJ = 4 + 1 # ajuste en pixeles que surgen de la variacion entre las unidades y las unidades tablero (4) y (1) pixel que se pierde al mostrar en pantalla

def guardar_juego(juego):

    ''' recibe el estado del juego actual y lo guarda en el archivo partida_guardada.csv
    juego: lista de listas'''

    with open('partida_guardada.csv', 'w') as f_guardada:
        for i in range(len(juego[0])):
            f_guardada.write(f'{juego[0][i]};{juego[1][i][0]},{juego[1][i][1]}\n')

def cargar_juego(piezas):

    ''' recibe las piezas existentes y devuelve la partida previamente guardada en el archivo partida_guardada.csv
    piezas: tupla de cadenas '''

    juego = [[], []]
    try:
        with open('partida_guardada.csv') as f_guardada:

            for linea in f_guardada:
                linea = linea.rstrip().split(';')

                if linea[0] not in piezas: # la pieza guardada es inexistente
                    raise ValueError
                juego[0].append(linea[0])

                pos_x, pos_y = linea[1].split(',')
                pos_x, pos_y = int(pos_x), int(pos_y)
                if pos_x not in range(0, 8) or pos_y not in range(0, 8) or (pos_x, pos_y) in juego[1]: # la posicion es invalida o ya hay una pieza en esa posicion
                    raise ValueError
                juego[1].append((pos_x, pos_y))

            if len(juego[0]) < 2: # el archivo esta vacio o solo contiene una pieza
                raise ValueError

        return juego

    except:
        gamelib.say('Partida guardada corrupta, se iniciara una nueva partida.')
        return 

def guardar_config(config):

    '''recibe la configuracion actual y la guarda en el archivo configuracion.csv
    config: diccionario '''

    with open('configuracion.csv', 'w') as config_f:

        alto = config['alto']
        config_f.write(f'alto,{alto}\n')

        piezas = ';'.join(config['piezas'])
        config_f.write(f'piezas,{piezas}\n')

def cargar_config(piezas):

    '''recibe las piezas existentes y devuelve la configuracion previamente guardada en el archivo configuracion.csv,
    despues de agregarle claves y valores necesarios con la funcion ajustar_config()
    piezas: tupla de cadenas'''

    config = {}
    try:
        with open('configuracion.csv') as config_f:

            for linea in config_f:
                linea = linea.rstrip().split(',')
                config[linea[0]] = linea[1].split(';')
            config['alto'] = int(config['alto'][0])

        if config['alto'] not in (440, 520): #las dimensiones son invalidas
            raise ValueError

        for pieza in config['piezas']:
            if pieza not in piezas: #la pieza es inexistente
                raise ValueError

        return ajustar_config(config)

    except (FileNotFoundError, ValueError):
        if ValueError:
            gamelib.say('Archivo configuracion corrupto, se reiniciara la configuracion.')

        #crear el archivo o sobreescribirlo
        with open('configuracion.csv', 'w') as config_f:
            config_f.write('alto,520\n')
            config_f.write('piezas,caballo;alfil;torre;peon;rey;reina\n')

        return cargar_config(piezas)

    except:
        #sobreescribir el archvio si este posee un error desconocido
        gamelib.say('Error desconocido al cargar el archivo, se reiniciara la configuracion.')

        with open('configuracion.csv', 'w') as config_f:
            config_f.write('alto,520\n')
            config_f.write('piezas,caballo;alfil;torre;peon;rey;reina\n')

        return cargar_config(piezas)

def ajustar_config(config):

    ''' recibe la configuracion guardada y agrega claves y valores necesarios
    config: diccionario'''

    config['unidad'] = config['alto'] // 10
    config['u_tablero'] = config['unidad'] - 1
    config['ancho'] = config['unidad'] * 8

    return config

def juego_nuevo(movimientos, n_nivel, piezas):

    '''recibe los movimientos de las piezas y crea un juego nuevo para el numero de nivel dado
    movimientos:diccionario
    piezas:tupla de cadenas
    n_nivel: entero'''
    piezas_posibles = list(piezas)
    juego = [[], []] #juego[0] lista de piezas, juego[1] lista de posiciones
    mov_posible = random.choice(range(0, 8)), random.choice(range(0, 8))
    
    while len(juego[0]) < n_nivel + 2: 
        pieza = random.choice(piezas_posibles)

        if len(mov_posible) != 0: # solo si hay movimientos posibles se cambia la posicion
            pieza_x, pieza_y = mov_posible[0], mov_posible[1]

        juego[0].append(pieza)
        juego[1].append((pieza_x, pieza_y))
        #las piezas y sus posiciones estan ligadas por su indice dentro de su lista correspondiente

        mov_posible = [] 
        #se reinician los movimientos posibles

        for mov_x, mov_y in movimientos[pieza][0]:
            if 0 <= pieza_x + mov_x < 8 and 0 <= pieza_y + mov_y < 8 and (pieza_x + mov_x, pieza_y + mov_y) not in juego[1]:
                mov_posible.append((mov_x, mov_y))
        #se agregan todos los movimientos posibles sin extension

        if movimientos[pieza][1]: #pieza con movimiento extensible

            mov_posible_ext = []
            for ext in mov_posible:
                for k in range(2,8):
                    ext_x, ext_y = ext[0] * k, ext[1] * k
                    if 0 <= pieza_x + ext_x < 8 and 0 <= pieza_y + ext_y < 8 and (pieza_x + ext_x, pieza_y + ext_y) not in juego[1]:
                        #la posicion se encuentra dentro de los limites del tablero y no hay ninguna pieza ocupandola
                        mov_posible_ext.append((ext_x, ext_y))
                    else:
                        break
            mov_posible += mov_posible_ext

        if len(mov_posible) == 0: #no hay movimiento legal para la pieza especifica

            piezas_posibles.remove(pieza) 
            juego[0].pop()
            juego[1].pop()
            #se quita la pieza de la posicion actual y se quita de las piezas posibles para tal posicion

            if len(piezas_posibles) == 0 : #ninguna pieza en la posicion actual podria moverse

                juego = [[],[]]
                mov_posible = random.choice(range(0, 8)),random.choice(range(0, 8))
                piezas_posibles = list(piezas)
                #se borra el juego actual y se crea uno nuevo

            continue

        piezas_posibles = list(piezas) # se integran las piezas quitadas
        mov_posible = random.choice(mov_posible) # se elige uno de todos los movimientos posibles
        mov_posible = (mov_posible[0] + pieza_x, mov_posible[1] + pieza_y) #se ejecuta el movimiento elegido
    return juego

def saltar(juego, movimientos, n_nivel, config,salto, salto_x):
    alto, ancho, unidad, u_tablero = config['alto'], config['ancho'], config['unidad'], config['u_tablero']
    ac_y=20000
    t_2=0
    t=0
    salto = u_tablero//8 if salto == 3 else ( u_tablero//12 if salto == 2 else (u_tablero//16 if salto == 1 else 0 ))
    y = juego[1][0][1] * u_tablero + AJ + u_tablero - salto

    
    gamelib.draw_begin()
    #dibujar tablero
    y_in = u_tablero + AJ
    for y_fin in range(2 * u_tablero + AJ, u_tablero * 9 + AJ + 1, u_tablero):
        paridad = (y_fin // u_tablero) % 2 # valor para intercalar colores
        x_in = 5
        for x_fin in range(u_tablero + AJ, u_tablero * 8, 2 * u_tablero):
            gamelib.draw_rectangle(x_in + (paridad * u_tablero), y_in, x_fin + (paridad * u_tablero), y_fin, outline = 'black', width = '4', fill = '#2e2d3f')
            gamelib.draw_rectangle(x_in + u_tablero - (paridad * u_tablero), y_in, x_fin + u_tablero - (paridad * u_tablero), y_fin, outline = 'black', width = '4', fill = '#181818')
            x_in = x_fin + u_tablero
        y_in = y_fin

    #Dibujar titulo y adornos superiores
    gamelib.draw_rectangle(0, 0, ancho,unidad, fill='')
    gamelib.draw_image(f'img/titulo{alto}.gif', 0, 0)
    gamelib.draw_rectangle(4, 4, ancho, unidad - 6, outline = '#ff1955', width = '4', fill = '')
    gamelib.draw_rectangle(4, 4, ancho, unidad - 6, outline = 'black', width = '2', fill = '')

    #dibujar adornos inferiores
    gamelib.draw_rectangle(4, alto - unidad + 3, ancho, alto, outline = '#ff1955', width = '4', fill = '')
    gamelib.draw_rectangle(4, alto - unidad + 3, ancho, alto, outline = 'black', width = '2', fill = '')

    #divisor izquierda
    gamelib.draw_line(unidad // 2 + unidad * 2, alto - unidad + 4, unidad // 2 + unidad * 2, alto - 1, width = '4', fill = '#ff1955')
    gamelib.draw_line(unidad // 2 + unidad * 2, alto - unidad + 4, unidad // 2 + unidad * 2,  alto - 1, width = '2', fill = 'black')

    #divisor derecha
    gamelib.draw_line(unidad // 2 + unidad * 5, alto - unidad + 4, unidad // 2 + unidad * 5, alto - 1, width = '4', fill = '#ff1955')
    gamelib.draw_line(unidad // 2 + unidad * 5, alto - unidad + 4, unidad // 2 + unidad * 5, alto - 1, width = '2', fill = 'black')

    #bordes
    gamelib.draw_rectangle(2, 2, ancho + 1, alto + 1, outline = '#ff1955', width = '1', fill = '')

    #iconos inferiores 
    gamelib.draw_image(f'img/{n_nivel // 10}{alto}.gif', unidad // 2 + unidad * 3 - 12, alto - unidad + 3)
    gamelib.draw_image(f'img/{n_nivel % 10}{alto}.gif', unidad // 2 + unidad * 3 + 12, alto - unidad + 3)
    gamelib.draw_image(f'img/back{alto}.gif', 4, alto - unidad + 3)
    gamelib.draw_image(f'img/retry{alto}.gif', ancho - unidad * 2 - unidad // 2, alto - unidad + 3)

    #iluminacion de botones
    gamelib.draw_rectangle(4, alto - unidad + 4, unidad // 2 + unidad * 2 - 2, alto - 1, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')
    gamelib.draw_rectangle(unidad // 2 + unidad * 5, alto - unidad + 4, ancho - 2, alto - 1, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')

    #sobre iluminacion de botones, el archivo @img/vacio.xbm es un mapa de bits de 1x1 con su unico bit vacio, que permite dibujar formas con relleno y dejarlas invisibles
    #se usa debido a que la key activestipple no funciona correctamente si no hay un fill distinto del fill vacio -> ''
    #con esta implementacion la forma solo se puede ver cuando se cambia el stipple por el activestipple, permitiendo ver lo que hay debajo mientras la forma no este activa

    #dibujar piezas
    '''if t_2 < 2/60:
        y -= ac_y*(t**2)
    elif t_2 < 4/60:
        if t_2 == 2/60:
            t=0
        y += ac_y*(t**2)'''

    gamelib.draw_image(f'img/{juego[0][0]}_rojo{alto}.gif',  juego[1][0][0] * u_tablero + AJ - salto_x, y)
    gamelib.draw_rectangle(juego[1][0][0] * u_tablero + AJ, juego[1][0][1] * u_tablero + AJ + u_tablero, juego[1][0][0] * u_tablero + u_tablero, juego[1][0][1] * u_tablero + AJ + u_tablero*1.9,fill='#ff1955', stipple=f'@img/enojado3{alto}.xbm', width='0')

    for i in range(1,len(juego[0])):
        gamelib.draw_image(f'img/{juego[0][i]}_blanco{alto}.gif', juego[1][i][0] * u_tablero + AJ, juego[1][i][1] * u_tablero + AJ + u_tablero)
    

    #dibujar cuadrado de movimiento posible
    mov_posible = movimiento_posible(juego, movimientos)
    for x_cuad, y_cuad in mov_posible:
        gamelib.draw_rectangle(x_cuad * u_tablero + 7, y_cuad * u_tablero + 7 + u_tablero, x_cuad * u_tablero + 3 + u_tablero, y_cuad * u_tablero + 3 + 2 * u_tablero, outline = '#ff1955', width = '3', fill = '')
    '''time.sleep(1/60)
    t_2 += 1/60
    t+=1/60'''
    gamelib.draw_end()


def mostrar_tablero(juego, movimientos, n_nivel, config):

    '''dibuja la interfaz del juego activo, recibe los datos necesarios
    juego: lista de listas
    movimientos: diccionario
    n_nivel: entero
    config: diccionario'''

    alto, ancho, unidad, u_tablero = config['alto'], config['ancho'], config['unidad'], config['u_tablero']

    gamelib.draw_begin()

    #dibujar tablero
    y_in = u_tablero + AJ
    for y_fin in range(2 * u_tablero + AJ, u_tablero * 9 + AJ + 1, u_tablero):
        paridad = (y_fin // u_tablero) % 2 # valor para intercalar colores
        x_in = 5
        for x_fin in range(u_tablero + AJ, u_tablero * 8, 2 * u_tablero):
            gamelib.draw_rectangle(x_in + (paridad * u_tablero), y_in, x_fin + (paridad * u_tablero), y_fin, outline = 'black', width = '4', fill = '#2e2d3f')
            gamelib.draw_rectangle(x_in + u_tablero - (paridad * u_tablero), y_in, x_fin + u_tablero - (paridad * u_tablero), y_fin, outline = 'black', width = '4', fill = '#181818')
            x_in = x_fin + u_tablero
        y_in = y_fin

    #Dibujar titulo y adornos superiores
    gamelib.draw_rectangle(0, 0, ancho,unidad, fill='')
    gamelib.draw_image(f'img/titulo{alto}.gif', 0, 0)
    gamelib.draw_rectangle(4, 4, ancho, unidad - 6, outline = '#ff1955', width = '4', fill = '')
    gamelib.draw_rectangle(4, 4, ancho, unidad - 6, outline = 'black', width = '2', fill = '')

    #dibujar adornos inferiores
    gamelib.draw_rectangle(4, alto - unidad + 3, ancho, alto, outline = '#ff1955', width = '4', fill = '')
    gamelib.draw_rectangle(4, alto - unidad + 3, ancho, alto, outline = 'black', width = '2', fill = '')

    #divisor izquierda
    gamelib.draw_line(unidad // 2 + unidad * 2, alto - unidad + 4, unidad // 2 + unidad * 2, alto - 1, width = '4', fill = '#ff1955')
    gamelib.draw_line(unidad // 2 + unidad * 2, alto - unidad + 4, unidad // 2 + unidad * 2,  alto - 1, width = '2', fill = 'black')

    #divisor derecha
    gamelib.draw_line(unidad // 2 + unidad * 5, alto - unidad + 4, unidad // 2 + unidad * 5, alto - 1, width = '4', fill = '#ff1955')
    gamelib.draw_line(unidad // 2 + unidad * 5, alto - unidad + 4, unidad // 2 + unidad * 5, alto - 1, width = '2', fill = 'black')

    #bordes
    gamelib.draw_rectangle(2, 2, ancho + 1, alto + 1, outline = '#ff1955', width = '1', fill = '')

    #iconos inferiores 
    gamelib.draw_image(f'img/{n_nivel // 10}{alto}.gif', unidad // 2 + unidad * 3 - 12, alto - unidad + 3)
    gamelib.draw_image(f'img/{n_nivel % 10}{alto}.gif', unidad // 2 + unidad * 3 + 12, alto - unidad + 3)
    gamelib.draw_image(f'img/back{alto}.gif', 4, alto - unidad + 3)
    gamelib.draw_image(f'img/retry{alto}.gif', ancho - unidad * 2 - unidad // 2, alto - unidad + 3)

    #iluminacion de botones
    gamelib.draw_rectangle(4, alto - unidad + 4, unidad // 2 + unidad * 2 - 2, alto - 1, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')
    gamelib.draw_rectangle(unidad // 2 + unidad * 5, alto - unidad + 4, ancho - 2, alto - 1, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')

    #sobre iluminacion de botones, el archivo @img/vacio.xbm es un mapa de bits de 1x1 con su unico bit vacio, que permite dibujar formas con relleno y dejarlas invisibles
    #se usa debido a que la key activestipple no funciona correctamente si no hay un fill distinto del fill vacio -> ''
    #con esta implementacion la forma solo se puede ver cuando se cambia el stipple por el activestipple, permitiendo ver lo que hay debajo mientras la forma no este activa

    #dibujar piezas
    x, y = juego[1][0][0] * u_tablero + AJ, juego[1][0][1] * u_tablero + AJ + u_tablero
    for i in range(len(juego[0])):
        if i == 0:
            gamelib.draw_image(f'img/{juego[0][0]}_rojo{alto}.gif',  juego[1][0][0] * u_tablero + AJ, juego[1][0][1] * u_tablero + AJ + u_tablero)
            continue
        gamelib.draw_image(f'img/{juego[0][i]}_blanco{alto}.gif', juego[1][i][0] * u_tablero + AJ, juego[1][i][1] * u_tablero + AJ + u_tablero)

    #dibujar cuadrado de movimiento posible
    mov_posible = movimiento_posible(juego, movimientos)
    for x_cuad, y_cuad in mov_posible:
        gamelib.draw_rectangle(x_cuad * u_tablero + 7, y_cuad * u_tablero + 7 + u_tablero, x_cuad * u_tablero + 3 + u_tablero, y_cuad * u_tablero + 3 + 2 * u_tablero, outline = '#ff1955', width = '3', fill = '')

    gamelib.draw_end()

def mostrar_menu_principal(config, piezas):

    ''' recibe la configuracion y las piezas, dibuja el menu principal de la aplicacion
    config:diciconario
    piezas:tupla de cadenas'''

    alto, ancho, unidad, u_tablero = config['alto'], config['ancho'], config['unidad'], config['u_tablero']
    gamelib.draw_begin()
    
    #dibujar tablero de fondo
    y_in = 0
    for y_fin in range(u_tablero, u_tablero * 10 + 1, u_tablero):
        paridad = (y_fin // u_tablero) % 2
        x_in = 0
        for x_fin in range(u_tablero, u_tablero * 8, 2 * u_tablero):
            gamelib.draw_rectangle(x_in + (paridad * u_tablero) + AJ, y_in + AJ, x_fin + (paridad * u_tablero) + AJ, y_fin + AJ, outline = 'black', width = '4', fill = '#2e2d3f')
            gamelib.draw_rectangle(x_in + u_tablero - (paridad * u_tablero) + AJ, y_in + AJ, x_fin + u_tablero - (paridad * u_tablero) + AJ, y_fin + AJ, outline = 'black', width = '4', fill = '#181818')
            x_in = x_fin + u_tablero
        y_in = y_fin 

    #elegir y dibujar piezas aleatorias
    y_posible = list(range(0, 10))
    x_posible = list(range(0, 8))  
    piezas_fondo = random.choices(piezas, k = 11)
    for i in range(len(piezas_fondo)):
        y_fondo = random.choice(y_posible)
        x_fondo = random.choice(x_posible)
        if i == len(piezas_fondo) - 1:
            gamelib.draw_image(f'img/{piezas_fondo[i]}_rojo{alto}.gif', u_tablero * x_fondo + AJ, u_tablero * y_fondo + AJ)
            break
        gamelib.draw_image(f'img/{piezas_fondo[i]}_blanco{alto}.gif', u_tablero * x_fondo + AJ, u_tablero * y_fondo + AJ)
        y_posible.remove(y_fondo) if i % 2 == 0 else x_posible.remove(x_fondo) # se quitan posiciones ya utilizadas alternando entre x e y

    #bordes y titulo
    gamelib.draw_rectangle(2, 2 ,ancho + 1, alto + 1, outline = '#ff1955', width = '2', fill = '#181818', stipple = 'gray25')
    gamelib.draw_image(f'img/titulo{alto}.gif', 0, 6)

    # dibujar botones
    for i,boton in enumerate(('continuar','nuevapartida','opciones','salir')):
        n = 2 * (i + 1)
        #diseño de boton y texto
        gamelib.draw_rectangle(ancho // 4, unidad * (n - 1) + unidad // 2, ancho - ancho // 4, n * unidad + unidad // 2, outline = '#ff1955', width = '2', fill = '#2e2d3f')
        gamelib.draw_polygon([ancho // 4 + 1, unidad * (n - 1)  + unidad // 2 + 1, ancho - ancho // 4 - 1, unidad * (n - 1) + unidad // 2 + 1, ancho - ancho // 4 -1, n * unidad + unidad // 2 - 1], fill = '#181818')
        gamelib.draw_image(f'img/{boton}{alto}.gif', ancho // 4, unidad * (n - 1) + unidad // 2)

        #iluminacion de botones 
        gamelib.draw_rectangle(ancho//4, unidad * (n -  1) + unidad // 2, ancho - ancho // 4, n * unidad + unidad // 2, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')
    
    if not hay_guardada():
        #apagar boton continuar si no hay partida para continuar
        gamelib.draw_rectangle(ancho // 4 - 2, unidad + unidad // 2 - 2, ancho - ancho // 4 + 2, 2 * unidad + unidad // 2 + 2, fill = 'black', stipple = 'gray50')

def mostrar_menu_opciones(piezas, piezas_activas, config):

    '''recibe la configuracion y las piezas existentes y activas, dibuja el menu de opciones de la aplicacion
    piezas:tupla de cadenas
    piezas_activas: tupla de cadenas
    config: diccionario'''

    alto, unidad = config['alto'], config['unidad']

    gamelib.draw_begin()

    #bordes y fondo texturado
    gamelib.draw_rectangle(2, 2, config['ancho'] + 1, alto + 1, outline = '#ff1955', width = '2', fill = '#181818', stipple = '@img/shapeshifter.xbm')

    #seccion dimensiones
    gamelib.draw_image(f'img/dimensiones{alto}.gif', unidad * 2, unidad)
    gamelib.draw_rectangle (unidad * 2, unidad * 2, unidad * 6, unidad * 3, outline = '#ff1955', width = '2', fill = '')
    gamelib.draw_image(f'img/440{alto}.gif', unidad * 2, unidad * 2)
    gamelib.draw_image(f'img/520{alto}.gif', unidad * 4, unidad * 2)
    a, b = (4, 6) if alto == 440 else (2, 4) #cambia la posicion del rectangulo segun el valor actual de dimensiones
    gamelib.draw_rectangle (unidad * a, unidad * 2, unidad * b, unidad * 3, width = '0', fill = '#ff1955', stipple = 'gray12')
    gamelib.draw_image(f'img/piezas{alto}.gif', unidad * 2, unidad * 4)
    gamelib.draw_rectangle(unidad * 2 + unidad // 2,unidad * 6, unidad * 6 - unidad // 2, unidad * 8, outline = '#ff1955', width = '2', fill = '')

    #seccion piezas
    for n, pieza in enumerate(piezas):
        gamelib.draw_image (f'img/{pieza}_blanco{alto}.gif', unidad * (2 + n % 3) + unidad // 2, unidad * (5 + n // 3))
        if pieza in piezas_activas: 
            #2 filas de 3 columnas
            gamelib.draw_rectangle(unidad * (2 + n % 3) + unidad // 2, unidad * (5 + n // 3), unidad * (3 + n % 3) + unidad // 2, unidad * (6 + n // 3), outline = '#ff1955', width = '2', fill = '')
        else:
            gamelib.draw_rectangle(unidad * (2 + n % 3) + unidad // 2, unidad * (5 + n // 3), unidad * (3 + n % 3) + unidad // 2, unidad * (6 + n // 3), outline = '#ff1955', width = '2', fill = 'black', stipple = 'gray75')
    
    #boton volver
    gamelib.draw_rectangle(0, alto - unidad + unidad // 4, unidad * 3, alto + 1, outline = '#ff1955', width = '2', fill = '#181818', stipple = 'gray50')
    gamelib.draw_image(f'img/volver{alto}.gif', 0, alto - unidad + unidad // 4)
    gamelib.draw_rectangle(0, alto - unidad + unidad // 4 + 2, unidad * 3 - 2, alto + 1, width = '0', fill = '#ff1955',stipple = '@img/vacio.xbm', activestipple = 'gray25')

    gamelib.draw_end()

def movimiento_posible(juego, movimientos):

    ''' recibe el estado del juego actual y los movimientos de las piezas, devuelve los movimientos posibles de la pieza a mover
    juego: lista de listas
    movimientos:diccionario'''

    pieza = juego[0][0]
    pieza_x, pieza_y = juego[1][0]

    mov_posible = []
    for mov_x, mov_y in movimientos[pieza][0]:
        if (pieza_x + mov_x, pieza_y + mov_y) in juego[1]:
            mov_posible.append((pieza_x + mov_x, pieza_y + mov_y))
    #se agregan todos los movimientos posibles sin extension

    if movimientos[pieza][1]:#pieza con movimiento extensible

        mov_posible_ext = []
        for ext in movimientos[pieza][0]:
            for k in range(2, 8):
                if (pieza_x + (ext[0] * k), pieza_y + (ext[1] * k)) in juego[1]:
                    #alguna pieza se encuentra en la posicion
                    mov_posible_ext.append((pieza_x + (ext[0] * k), pieza_y + (ext[1] * k)))
        mov_posible += mov_posible_ext

    return mov_posible

def hay_guardada():
    '''devuelve True si hay una partida guardada y se puede abrir, caso contrario devuelve False'''
    try:
        with open('partida_guardada.csv') as partida:
            return True
    except:
        return False

def main():

    menu = 0 # 0 principal, 1 en juego, 2 opciones
    gamelib.title("Shape Shifter Chess")
    movimientos = {}
    piezas = ()

    #cargar el archivo de movimientos y las piezas
    with open('movimientos.csv') as mov:
        linea = next(mov, False)
        linea = linea.strip().split(',')
        while linea:
            pieza = linea[0]
            piezas += (linea[0],)
            movimientos[linea[0]] = [[]]
            extensible = True if linea[2] == 'true' else False
            movimientos[linea[0]].append(extensible)
            while linea and linea[0] == pieza:
                mov_x, mov_y = linea[1].split(';')
                movimientos[linea[0]][0].append((int(mov_x), int(mov_y))) 
                linea = next(mov, False)
                if linea:
                    linea = linea.strip().split(',')

    config = cargar_config(piezas)
    piezas_activas = tuple(config['piezas'])
    alto, ancho, unidad, u_tablero = config['alto'], config['ancho'], config['unidad'], config['u_tablero']
    gamelib.resize(ancho, alto)
    ev = 0
    salto=0
    saltin = 1
    salto_x = -1
    saltin_x = 1
    j=0
    gamelib.play_sound('audio/musica.wav')

    mostrar_menu_principal(config, piezas)

    while gamelib.loop(21):
        j+=1
        if j == 1100:
            j=0
            gamelib.play_sound('audio/musica.wav')

        ev = 0
        for evento in gamelib.get_events():
            if evento.type == gamelib.EventType.ButtonPress:
                ev = evento

        if menu == 0 and ev: #dentro del menu principal

            if not (ancho // 4 - 2 < ev.x < ancho - ancho // 4 + 2):
                #no se presiona ningun boton
                continue

            if unidad + unidad // 2 - 2 < ev.y < 2 * unidad + unidad // 2 + 2:
                #se presiona boton continuar
                if not hay_guardada():# no hay ninguna partida guardada
                    gamelib.play_sound('audio/bloquear.wav')
                    continue

                gamelib.play_sound('audio/empezar.wav')
                juego = cargar_juego(piezas)
                if juego == None: # la carga del juego fallo y se crea una nueva partida
                    juego = juego_nuevo(movimientos, 1, piezas_activas)

                n_nivel = len(juego[0]) - 2 #se define el nivel por la cantidad de piezas
                mostrar_tablero(juego, movimientos, n_nivel, config)
                guardar_juego(juego)
                menu = 1
                continue

            if unidad * 3 + unidad // 2 - 2 < ev.y < 4 * unidad + unidad // 2 + 2 :
                #se presiona boton nueva partida
                gamelib.play_sound('audio/empezar.wav')
                juego = juego_nuevo(movimientos, 1 ,piezas_activas)
                n_nivel = 1
                mostrar_tablero(juego, movimientos, n_nivel, config)
                guardar_juego(juego)
                menu = 1
                continue
            if unidad * 5 + unidad // 2 - 2 < ev.y < 6 * unidad + unidad // 2 + 2:
                #se presiona boton opciones
                gamelib.play_sound('audio/tap.wav')
                mostrar_menu_opciones(piezas, piezas_activas, config)
                menu = 2
                continue
            if unidad * 7 + unidad // 2 - 2 < ev.y < 8 * unidad + unidad // 2 + 2:
                #se presiona boton salir
                return
                
        if menu == 1: #dentro de una partida
            if not ev:
                saltar(juego, movimientos, n_nivel, config, salto,salto_x)
                salto = salto + saltin
                salto_x = salto_x + saltin_x
                if salto == 3:
                    saltin = -1
                if salto == 0:
                    saltin_x = -saltin_x
                    saltin = 1
                continue

            if 3 <= ev.x < unidad // 2 + unidad * 2 and alto - unidad + 2 < ev.y < alto + 1:
                #se presiona boton atras
                gamelib.play_sound('audio/atras.wav')
                mostrar_menu_principal(config, piezas)
                menu = 0
                continue
            if unidad // 2 + unidad * 5 - 1 <= ev.x < ancho and alto - unidad + 2 < ev.y < alto + 1:
                #se presiona boton reiniciar
                juego = cargar_juego(piezas)
                gamelib.play_sound('audio/reintentar.wav')
                n_nivel = len(juego[0]) - 2

            posicion = (ev.x - 5) //  u_tablero, (ev.y - 5 - u_tablero) // u_tablero #posicion del click en funcion de las unidades de tablero
            if posicion in  movimiento_posible(juego, movimientos):
                #se clickea sobre un movimiento posible
                i = juego[1].index(posicion) # se busca el indice co rrespondiente a esa posicion
                #como las piezas y las posiciones estan ligadas por sus indices en cada lista dentro de juego, saber el indice de la posicion
                #es tambien saber el indice de la pieza
                juego[0][0], juego[0][i] = juego[0][i], juego[0][0] 
                juego[1][0], juego[1][i] = juego[1][i], juego[1][0]
                #se intercambia la pieza actual con la pieza destino
                juego[0].pop(i)
                juego[1].pop(i)
                gamelib.play_sound('audio/comer.wav')
                if len(juego[0]) == 1:
                    #solo queda una pieza
                    gamelib.play_sound('audio/ganar.wav')
                    n_nivel += 1
                    juego = juego_nuevo(movimientos, n_nivel, piezas_activas)
                    guardar_juego(juego)
            saltar(juego, movimientos, n_nivel, config,salto,salto_x)

            salto = salto + saltin
            salto_x = salto_x + saltin_x

            if salto == 3:
                saltin = -1
            if salto == 0:
                saltin_x = -saltin_x
                saltin = 1
                

        if menu == 2 and ev:

            if 0 < ev.x < unidad * 3 and alto - unidad + unidad // 4 < ev.y <= alto + 2:
                #se presiona boton volver
                gamelib.play_sound('audio/atras.wav')
                mostrar_menu_principal(config, piezas)
                menu = 0
                continue
            a, b = (4, 6) if alto == 440 else (2, 4) # la posicion del boton a presionar depende del alto
            if unidad * a < ev.x < unidad * b and unidad * 2 < ev.y < unidad * 3:
                #se presiona el boton dimensiones
                gamelib.play_sound('audio/tap.wav')
                config['alto'] = 180 * b  - 140 * a #de las ecuaciones 4x + 6y = 520 , 2x + 4y = 440
                config = ajustar_config(config)
                guardar_config(config)
                alto, ancho, unidad, u_tablero = config['alto'], config['ancho'], config['unidad'], config['u_tablero']
                gamelib.resize(ancho, alto)
                mostrar_menu_opciones(piezas, piezas_activas, config)

            elif unidad * 2 + unidad // 2 < ev.x < unidad * 6 - unidad // 2 and unidad * 5 < ev.y < unidad * 8:
                #se clickea sobre la caja de piezas
                posicion = ev.x // unidad - 2 - (ev.x // (unidad // 2) - 1) % 2, ev.y // unidad -  5
                i = posicion[0] + 3 * posicion[1] 
                #cada numero de caja corresponde al indice correspondiente a cada pieza en config['piezas']
                if i >= len(piezas):
                    continue
                pieza = piezas[i]
                if pieza in config['piezas']:
                    #si la pieza clickeada esta en uso la quita(si es posible)
                    if len(config['piezas']) > 3:
                        #no se permite jugar con menos de 3 piezas
                        gamelib.play_sound('audio/tap.wav')
                        config['piezas'].remove(pieza)
                    else:
                        gamelib.play_sound('audio/bloquear.wav')
                else:
                    #si la pieza clickeada no estaba en uso la coloca en las piezas activas
                    gamelib.play_sound('audio/desbloquear.wav')
                    config['piezas'].insert(i, pieza)
                guardar_config(config)
                piezas_activas = tuple(config['piezas'])
                mostrar_menu_opciones(piezas, piezas_activas, config)

gamelib.init(main)
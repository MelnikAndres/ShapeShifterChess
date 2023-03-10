import gamelib
import random
import time

DIMENSIONES = (520, 440)
AJ = 4 + 1 # ajuste en pixeles que surgen de la variacion entre las unidades y las unidades tablero (4) y (1) pixel que se pierde al mostrar en pantalla

class Juego:
    ''' el constructor crea una instancia de Juego, que con la informacion recibida por las clases Menuprincipal, Menuopciones y Tablero, y los datos cargados,
     ejecuta y muestra en pantalla las acciones realizadas por el usuario.'''

    def __init__(self):
        #piezas
        self.piezas_jugables = self.cargar_piezas()

        #configuracion
        self.alto, self.ancho, self.unidad, self.u_tablero, self.piezas_activas = self.cargar_config()

        #pantallas
        self.menu_principal = Menuprincipal(self.unidad)
        self.menu_opciones = Menuopciones(self.unidad)
        self.tablero = None

        #estados
        self.menu_activo = 'Menuprincipal'
        self.principal_en_pantalla = 0

        #movimiento
        self.variacion_mov = 0.3
        self.movimiento_y = 0

    def mostrar_menu_princiapl(self):
        ''' Dibuja el menu principal en la pantalla'''
        gamelib.draw_begin()
        
        #dibujar tablero de fondo
        y_in = 0
        for y_fin in range(self.u_tablero, self.u_tablero * 10 + 1, self.u_tablero):
            paridad = (y_fin // self.u_tablero) % 2
            x_in = 0
            for x_fin in range(self.u_tablero, self.u_tablero * 8, 2 * self.u_tablero):
                gamelib.draw_rectangle(x_in + (paridad * self.u_tablero) + AJ, y_in + AJ, x_fin + (paridad * self.u_tablero) + AJ, y_fin + AJ, outline = 'black', width = '4', fill = '#2e2d3f')
                gamelib.draw_rectangle(x_in + self.u_tablero - (paridad * self.u_tablero) + AJ, y_in + AJ, x_fin + self.u_tablero - (paridad * self.u_tablero) + AJ, y_fin + AJ, outline = 'black', width = '4', fill = '#181818')
                x_in = x_fin + self.u_tablero
            y_in = y_fin 

        #elegir y dibujar piezas aleatorias
        y_posible = list(range(0, 10))
        x_posible = list(range(0, 8))  
        piezas_fondo = random.choices(list(self.piezas_jugables), k = 11)
        for i in range(len(piezas_fondo)):
            y_fondo = random.choice(y_posible)
            x_fondo = random.choice(x_posible)
            if i == len(piezas_fondo) - 1:
                gamelib.draw_image(f'img/{piezas_fondo[i]}_rojo{self.alto}.gif', self.u_tablero * x_fondo + AJ, self.u_tablero * y_fondo + AJ)
                break
            gamelib.draw_image(f'img/{piezas_fondo[i]}_blanco{self.alto}.gif', self.u_tablero * x_fondo + AJ, self.u_tablero * y_fondo + AJ)
            y_posible.remove(y_fondo) if i % 2 == 0 else x_posible.remove(x_fondo) # se quitan posiciones ya utilizadas alternando entre x e y

        #bordes y titulo
        gamelib.draw_rectangle(2, 2 ,self.ancho + 1, self.alto + 1, outline = '#ff1955', width = '2', fill = '#181818', stipple = 'gray25')
        gamelib.draw_image(f'img/titulo{self.alto}.gif', 0, 6)

        # dibujar botones
        for boton in self.menu_principal.botones:
            #diseño de boton y texto
            gamelib.draw_rectangle(self.menu_principal.botones_x[0] + 2, self.menu_principal.botones[boton]['y'][0], self.menu_principal.botones_x[1] - 2, self.menu_principal.botones[boton]['y'][1], outline = '#ff1955', width = '2', fill = '#2e2d3f')
            gamelib.draw_polygon([self.menu_principal.botones_x[0] + 4, self.menu_principal.botones[boton]['y'][0]+2, self.menu_principal.botones_x[1] - 4, self.menu_principal.botones[boton]['y'][0], self.menu_principal.botones_x[1] - 4, self.menu_principal.botones[boton]['y'][1]-2], fill = '#181818')
            gamelib.draw_image(f'img/{boton}{self.alto}.gif', self.menu_principal.botones_x[0] + 2, self.menu_principal.botones[boton]['y'][0])

            #iluminacion de botones 
            gamelib.draw_rectangle(self.menu_principal.botones_x[0] + 2, self.menu_principal.botones[boton]['y'][0]+2, self.menu_principal.botones_x[1] - 2, self.menu_principal.botones[boton]['y'][1]-2, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')
        
        if not hay_guardada():
            #apagar boton continuar si no hay partida para continuar
            gamelib.draw_rectangle(self.menu_principal.botones_x[0], self.menu_principal.botones['continuar']['y'][0]-2, self.menu_principal.botones_x[1] - 2, self.menu_principal.botones['continuar']['y'][1], fill = 'black', stipple = 'gray50')

    def mostrar_menu_opciones(self):
        '''dibuja el menu de opciones en la pantalla'''
        gamelib.draw_begin()

        #bordes y fondo texturado
        gamelib.draw_rectangle(2, 2, self.ancho + 1, self.alto + 1, outline = '#ff1955', width = '2', fill = '#181818', stipple = '@img/shapeshifter.xbm')

        #seccion dimensiones
        gamelib.draw_image(f'img/dimensiones{self.alto}.gif', self.unidad * 2, self.unidad)
        gamelib.draw_rectangle (self.unidad * 2, self.unidad * 2, self.unidad * 6, self.unidad * 3, outline = '#ff1955', width = '2', fill = '')
        gamelib.draw_image(f'img/440{self.alto}.gif', self.unidad * 2, self.unidad * 2)
        gamelib.draw_image(f'img/520{self.alto}.gif', self.unidad * 4, self.unidad * 2)
        
        a, b = (4, 6) if self.alto == 440 else (2, 4) #cambia la posicion del rectangulo segun el valor actual de dimensiones
        gamelib.draw_rectangle (self.unidad * a, self.unidad * 2, self.unidad * b, self.unidad * 3, width = '0', fill = '#ff1955', stipple = 'gray12')
        gamelib.draw_image(f'img/piezas{self.alto}.gif', self.unidad * 2, self.unidad * 4)
        gamelib.draw_rectangle(self.unidad * 2 + self.unidad // 2,self.unidad * 6, self.unidad * 6 - self.unidad // 2, self.unidad * 8, outline = '#ff1955', width = '2', fill = '')

        #seccion piezas
        for n, pieza in enumerate(list(self.piezas_jugables)):
            gamelib.draw_image (f'img/{pieza}_blanco{self.alto}.gif', self.unidad * (2 + n % 3) + self.unidad // 2, self.unidad * (5 + n // 3))
            if pieza in self.piezas_activas: 
                #2 filas de 3 columnas
                gamelib.draw_rectangle(self.unidad * (2 + n % 3) + self.unidad // 2, self.unidad * (5 + n // 3), self.unidad * (3 + n % 3) + self.unidad // 2, self.unidad * (6 + n // 3), outline = '#ff1955', width = '2', fill = '')
            else:
                gamelib.draw_rectangle(self.unidad * (2 + n % 3) + self.unidad // 2, self.unidad * (5 + n // 3), self.unidad * (3 + n % 3) + self.unidad // 2, self.unidad * (6 + n // 3), outline = '#ff1955', width = '2', fill = 'black', stipple = 'gray75')

        #boton volver
        gamelib.draw_rectangle(0, self.alto - self.unidad + self.unidad // 4, self.unidad * 3,self.alto + 1, outline = '#ff1955', width = '2', fill = '#181818', stipple = 'gray50')
        gamelib.draw_image(f'img/volver{self.alto}.gif', 0, self.alto - self.unidad + self.unidad // 4)
        gamelib.draw_rectangle(0, self.alto - self.unidad + self.unidad // 4 + 2, self.unidad * 3 - 2, self.alto + 1, width = '0', fill = '#ff1955',stipple = '@img/vacio.xbm', activestipple = 'gray25')

        gamelib.draw_end()

    def mostrar_tablero(self):
        ''' dibuja el tablero en la pantalla '''
        gamelib.draw_begin()

        #dibujar tablero
        y_in = self.u_tablero + AJ
        for y_fin in range(2 * self.u_tablero + AJ, self.u_tablero * 9 + AJ + 1, self.u_tablero):
            paridad = (y_fin // self.u_tablero) % 2 # valor para intercalar colores
            x_in = 5
            for x_fin in range(self.u_tablero + AJ, self.u_tablero * 8, 2 * self.u_tablero):
                gamelib.draw_rectangle(x_in + (paridad * self.u_tablero), y_in, x_fin + (paridad * self.u_tablero), y_fin, outline = 'black', width = '4', fill = '#2e2d3f')
                gamelib.draw_rectangle(x_in + self.u_tablero - (paridad * self.u_tablero), y_in, x_fin + self.u_tablero - (paridad * self.u_tablero), y_fin, outline = 'black', width = '4', fill = '#181818')
                x_in = x_fin + self.u_tablero
            y_in = y_fin

        #Dibujar titulo y adornos superiores
        gamelib.draw_rectangle(0, 0, self.ancho,self.unidad, fill='')
        gamelib.draw_image(f'img/titulo{self.alto}.gif', 0, 0)
        gamelib.draw_rectangle(4, 4, self.ancho, self.unidad - 6, outline = '#ff1955', width = '4', fill = '')
        gamelib.draw_rectangle(4, 4, self.ancho, self.unidad - 6, outline = 'black', width = '2', fill = '')

        #dibujar adornos inferiores
        gamelib.draw_rectangle(4, self.alto - self.unidad + 3, self.ancho, self.alto, outline = '#ff1955', width = '4', fill = '')
        gamelib.draw_rectangle(4, self.alto - self.unidad + 3, self.ancho, self.alto, outline = 'black', width = '2', fill = '')

        #divisor izquierda
        gamelib.draw_line(self.unidad // 2 + self.unidad * 2, self.alto - self.unidad + 4, self.unidad // 2 + self.unidad * 2, self.alto - 1, width = '4', fill = '#ff1955')
        gamelib.draw_line(self.unidad // 2 + self.unidad * 2, self.alto - self.unidad + 4, self.unidad // 2 + self.unidad * 2,  self.alto - 1, width = '2', fill = 'black')

        #divisor derecha
        gamelib.draw_line(self.unidad // 2 + self.unidad * 5, self.alto - self.unidad + 4, self.unidad // 2 + self.unidad * 5, self.alto - 1, width = '4', fill = '#ff1955')
        gamelib.draw_line(self.unidad // 2 + self.unidad * 5, self.alto - self.unidad + 4, self.unidad // 2 + self.unidad * 5, self.alto - 1, width = '2', fill = 'black')

        #bordes
        gamelib.draw_rectangle(2, 2, self.ancho + 1, self.alto + 1, outline = '#ff1955', width = '1', fill = '')

        #iconos inferiores 
        gamelib.draw_image(f'img/{self.tablero.nivel // 10}{self.alto}.gif', self.unidad // 2 + self.unidad * 3 - 12, self.alto - self.unidad + 3)
        gamelib.draw_image(f'img/{self.tablero.nivel % 10}{self.alto}.gif', self.unidad // 2 + self.unidad * 3 + 12, self.alto - self.unidad + 3)
        gamelib.draw_image(f'img/back{self.alto}.gif', 4, self.alto - self.unidad + 3)
        gamelib.draw_image(f'img/retry{self.alto}.gif', self.ancho - self.unidad * 2 - self.unidad // 2, self.alto - self.unidad + 3)

        #iluminacion de botones
        gamelib.draw_rectangle(4, self.alto - self.unidad + 4, self.unidad // 2 + self.unidad * 2 - 2, self.alto - 1, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')
        gamelib.draw_rectangle(self.unidad // 2 + self.unidad * 5, self.alto - self.unidad + 4, self.ancho - 2, self.alto - 1, width = '0', fill = '#ff1955', stipple = '@img/vacio.xbm', activestipple = 'gray25')

        #sobre iluminacion de botones, el archivo @img/vacio.xbm es un mapa de bits de 1x1 con su unico bit vacio, que permite dibujar formas con relleno y dejarlas invisibles
        #se usa debido a que la key activestipple no funciona correctamente si no hay un fill distinto del fill vacio -> ''
        #con esta implementacion la forma solo se puede ver cuando se cambia el stipple por el activestipple, permitiendo ver lo que hay debajo mientras la forma no este activa

        #dibujar piezas
        gamelib.draw_image(f'img/{self.tablero.piezas_nivel[0]}_sombra{self.alto}.gif',  self.tablero.posiciones_piezas[0][0] * self.u_tablero + AJ, self.tablero.posiciones_piezas[0][1] * self.u_tablero + AJ + self.u_tablero)
        gamelib.draw_image(f'img/{self.tablero.piezas_nivel[0]}_rojo{self.alto}.gif',  self.tablero.posiciones_piezas[0][0] * self.u_tablero + AJ, self.tablero.posiciones_piezas[0][1] * self.u_tablero + AJ + self.u_tablero + self.movimiento_y)

        self.movimiento_y -= self.variacion_mov
        if self.movimiento_y <= -self.u_tablero//12 or self.movimiento_y > 0 :
            self.variacion_mov = -self.variacion_mov

        for i in range(1, len(self.tablero.piezas_nivel)):
            gamelib.draw_image(f'img/{self.tablero.piezas_nivel[i]}_blanco{self.alto}.gif', self.tablero.posiciones_piezas[i][0] * self.u_tablero + AJ, self.tablero.posiciones_piezas[i][1] * self.u_tablero + AJ + self.u_tablero)

        #dibujar cuadrado de movimiento posible
        for x_cuad, y_cuad in self.tablero.mov_posibles:
            gamelib.draw_rectangle(x_cuad * self.u_tablero + 7, y_cuad * self.u_tablero + 7 + self.u_tablero, x_cuad * self.u_tablero + 3 + self.u_tablero, y_cuad * self.u_tablero + 3 + 2 * self.u_tablero, outline = '#ff1955', width = '3', fill = '')

        gamelib.draw_end()

    def mostrar_menu_actual(self):
        ''' dibuja el menu en el que el usuario se encuentra actualmente'''
        if self.menu_activo == 'Menuprincipal' and not self.principal_en_pantalla:
            self.principal_en_pantalla = 1
            self.mostrar_menu_princiapl()

        elif self.menu_activo == 'Menuopciones':
            self.principal_en_pantalla = 0
            self.mostrar_menu_opciones()
        elif self.menu_activo == 'Partida':

            self.principal_en_pantalla = 0
            self.mostrar_tablero()

    def modificar_dimensiones(self, nueva_dimension):

        ''' recibe un valor que representa la nueva alutra de la ventana, con el cual tambien se redefinen los valores dependientes de esta
        nueva_dimension : int'''

        if self.alto == nueva_dimension: # no hay necesidad de actualizar si el valor es el mismo que la ventana ya posee
            return

        self.alto = nueva_dimension
        self.unidad = self.alto // 10
        self.ancho = self.unidad * 8
        self.u_tablero = self.unidad - 1

        self.movimiento_y = 0 # evita que una pieza se encuentre en una posicion muy alta luego de cambiar de una altura mayor a una menor

        gamelib.resize(self.ancho, self.alto)
        self.menu_principal = Menuprincipal(self.unidad)
        self.menu_opciones = Menuopciones(self.unidad)

    def actualizar(self, x, y):
        ''' recibe 2 valores x, y que representan la posicion de un click en la pantalla y ejecuta la accion adecuada para tal click
        x: int
        y: int'''

        if self.menu_activo == 'Menuprincipal':
            accion = self.menu_principal.boton_presionado(x, y)

            if not accion:
                return

            if accion == 'Menuopciones':
                self.menu_activo = accion

            elif accion == 'Cerrar':
                self.menu_activo = None

            elif accion == 'cargartablero':
                self.tablero = Tablero(piezas = self.piezas_jugables, piezas_activas = self.piezas_activas, unidad = self.unidad, cargar = True)
                self.menu_activo = 'Partida'

            elif accion == 'nuevotablero':
                self.tablero = Tablero(piezas = self.piezas_jugables, piezas_activas = self.piezas_activas, unidad = self.unidad)
                self.menu_activo = 'Partida'

        elif self.menu_activo == 'Menuopciones':
            accion = self.menu_opciones.boton_presionado(x, y)

            if not accion:
                return

            if accion == 'Menuprincipal':
                self.menu_activo = accion

            elif accion == 'dimensionar, 520' or accion == 'dimensionar, 440' :
                nueva_dimension = int(accion.split(', ')[1])
                self.modificar_dimensiones(nueva_dimension)
                self.guardar_config()

            else: #formato f'pieza, {int()}'
                indice_pieza = int(accion.split(', ')[1])

                if indice_pieza >= len(self.piezas_jugables): #se clickea sobre la caja de piezas, pero esta no es perfectamente cuadrada
                    return

                pieza = list(self.piezas_jugables)[indice_pieza]

                if pieza in self.piezas_activas:
                    #si la pieza clickeada esta en uso la quita(si es posible)

                    if len(self.piezas_activas) > 3:
                        #no se permite jugar con menos de 3 piezas
                        gamelib.play_sound('audio/tap.wav')
                        self.piezas_activas.remove(pieza)

                    else:
                        gamelib.play_sound('audio/bloquear.wav')

                else:
                    #si la pieza clickeada no estaba en uso la coloca en las piezas activas
                    gamelib.play_sound('audio/desbloquear.wav')
                    self.piezas_activas.insert(indice_pieza, pieza)

                self.guardar_config()

        elif self.menu_activo == 'Partida':
            accion = self.tablero.realizar_accion(x, y)

            if accion == 'Menuprincipal':
                self.menu_activo = accion

            elif accion == 'reiniciar':
                self.tablero = Tablero(piezas = self.piezas_jugables, piezas_activas = self.piezas_activas, unidad = self.unidad, cargar = True)

            elif accion == 'ganar':
                self.tablero = Tablero(piezas = self.piezas_jugables, piezas_activas = self.piezas_activas, unidad = self.unidad, cargar = False, nivel = (self.tablero.nivel+1))

    def cargar_piezas(self):
        ''' carga las piezas y sus movimientos, del archivo movimientos.csv'''
        piezas = {}

        with open('movimientos.csv') as mov:
            #formato ejemplo: caballo,1;2,false

            linea = next(mov, False)
            linea = linea.strip().split(',')
            #ejemplo ['caballo', '1;2', 'false']

            while linea:

                pieza = linea[0]
                piezas[linea[0]] = [[]]
                extensible = True if linea[2] == 'true' else False

                piezas[linea[0]].append(extensible)
                while linea and linea[0] == pieza:

                    mov_x, mov_y = linea[1].split(';')
                    piezas[linea[0]][0].append((int(mov_x), int(mov_y))) 

                    linea = next(mov, False)
                    if linea:
                        linea = linea.strip().split(',')
        return piezas

    def cargar_config(self):
        '''carga la configuracion del usuario del archivo configuracion.csv o la reinicia si el archivo contiene un error'''
        config = {}
        try:
            with open('configuracion.csv') as config_f:

                for linea in config_f:
                    linea = linea.rstrip().split(',')
                    config[linea[0]] = linea[1].split(';')
                config['alto'] = int(config['alto'][0])

            if config['alto'] not in DIMENSIONES: #las dimensiones son invalidas
                raise ValueError

            for pieza in config['piezas']:
                if pieza not in self.piezas_jugables: #la pieza es inexistente
                    raise ValueError

            config['unidad'] = config['alto'] // 10
            config['u_tablero'] = config['unidad'] - 1
            config['ancho'] = config['unidad'] * 8

            return config['alto'], config['ancho'], config['unidad'], config['u_tablero'], config['piezas']

        except FileNotFoundError:
            #crear el archivo si no existe
            with open('configuracion.csv', 'w') as config_f:
                config_f.write('alto,520\n')
                config_f.write('piezas,caballo;alfil;torre;peon;rey;reina\n')

            return self.cargar_config()

        except ValueError:
            #sobreescribir el archvio si este esta corrupto
            gamelib.say('Archivo configuracion corrupto, se reiniciara la configuracion.')

            with open('configuracion.csv', 'w') as config_f:
                config_f.write('alto,520\n')
                config_f.write('piezas,caballo;alfil;torre;peon;rey;reina\n')

            return self.cargar_config()

    def guardar_config(self):
        ''' guarda la configuracion actual en el archivo configuracion.csv'''

        with open('configuracion.csv', 'w') as config_f:

            config_f.write(f'alto,{self.alto}\n')

            piezas = ';'.join(self.piezas_activas)
            config_f.write(f'piezas,{piezas}\n')

class Tablero:
    ''' contiene informacion cargada y los metodos necesarios para poder interpretar las acciones del usuario sobre el tablero de juego'''
    def __init__(self, piezas, piezas_activas, unidad, cargar = False, nivel = 1):

        #medidas
        self.unidad = unidad
        self.alto = unidad * 10
        self.ancho = unidad * 8



        #posiciones de botones
        boton_atras = ((3, unidad // 2 + unidad * 2), (self.alto - unidad + 2, self.alto + 1))
        boton_reiniciar = ((unidad // 2 + unidad * 5 - 1, self.ancho ), (self.alto - unidad + 2, self.alto + 1))
        self.botones = {'atras':{'x':boton_atras[0], 'y': boton_atras[1]}, 'reiniciar': {'x': boton_reiniciar[0], 'y': boton_reiniciar[1]}}

        #piezas existentes
        self.piezas_jugables = piezas

        #variables de nivel
        self.nivel = nivel
        self.piezas_activas = piezas_activas

        #piezas y posicion
        self.piezas_nivel = []
        self.posiciones_piezas = [] 

        #nuevo nivel
        if cargar:
            self.cargar_juego()
        else:
            self.juego_nuevo()
            self.guardar_juego()


        #movimientos 
        self.mov_posibles = self.movimientos_posibles()

    def juego_nuevo(self):
        '''crea un juego nuevo para el numero de nivel (self.nivel)'''

        piezas_posibles = list(self.piezas_activas)
        mov_posible = random.choice(range(0, 8)), random.choice(range(0, 8)) #mov_posible[0] : x , mov_posible[1] : y
        
        while len(self.piezas_nivel) < self.nivel + 2: 
            pieza = random.choice(piezas_posibles)

            if len(mov_posible) != 0: # solo si hay movimientos posibles se cambia la posicion
                pieza_x, pieza_y = mov_posible[0], mov_posible[1]

            self.piezas_nivel.append(pieza)
            self.posiciones_piezas.append((pieza_x, pieza_y))
            #las piezas y sus posiciones estan ligadas por su indice dentro de su lista correspondiente

            mov_posible = [] 
            #se reinician los movimientos posibles

            for mov_x, mov_y in self.piezas_jugables[pieza][0]:
                if 0 <= pieza_x + mov_x < 8 and 0 <= pieza_y + mov_y < 8 and (pieza_x + mov_x, pieza_y + mov_y) not in self.posiciones_piezas:
                    mov_posible.append((mov_x, mov_y))
            #se agregan todos los movimientos posibles sin extension

            if self.piezas_jugables[pieza][1]: #pieza con movimiento extensible

                mov_posible_ext = []
                for ext in mov_posible:
                    for k in range(2,8):
                        ext_x, ext_y = ext[0] * k, ext[1] * k
                        if 0 <= pieza_x + ext_x < 8 and 0 <= pieza_y + ext_y < 8 and (pieza_x + ext_x, pieza_y + ext_y) not in self.posiciones_piezas:
                            #la posicion se encuentra dentro de los limites del tablero y no hay ninguna pieza ocupandola
                            mov_posible_ext.append((ext_x, ext_y))
                        else:
                            break
                mov_posible += mov_posible_ext

            if len(mov_posible) == 0: #no hay movimiento legal para la pieza especifica

                piezas_posibles.remove(pieza) 
                self.piezas_nivel.pop()
                self.posiciones_piezas.pop()
                #se quita la pieza de la posicion actual y se quita de las piezas posibles para tal posicion

                if len(piezas_posibles) == 0 : #ninguna pieza en la posicion actual podria moverse

                    self.piezas_nivel = []
                    self.posiciones_piezas = [] 
                    mov_posible = random.choice(range(0, 8)),random.choice(range(0, 8))
                    piezas_posibles = list(self.piezas_activas)
                    #se borra el juego actual y se crea uno nuevo

                continue

            piezas_posibles = list(self.piezas_activas) # se integran las piezas quitadas
            mov_posible = random.choice(mov_posible) # se elige uno de todos los movimientos posibles
            mov_posible = (mov_posible[0] + pieza_x, mov_posible[1] + pieza_y) #se ejecuta el movimiento elegido

    def cargar_juego(self):
        ''' carga la ultima partida guardada del archivo partida_guardada.csv o inicia una nueva partida si tal archivo contiene un error'''
        try:
            with open('partida_guardada.csv') as f_guardada:

                for linea in f_guardada:
                    #formato ejemplo: reina;7,2
                    linea = linea.rstrip().split(';')
                    #formato ejemplo: ['reina', '7;2']

                    if linea[0] not in self.piezas_jugables: # la pieza guardada es inexistente
                        raise ValueError
                    self.piezas_nivel.append(linea[0])

                    pos_x, pos_y = linea[1].split(',')
                    pos_x, pos_y = int(pos_x), int(pos_y)
                    if pos_x not in range(0, 8) or pos_y not in range(0, 8) or (pos_x, pos_y) in self.posiciones_piezas: # la posicion es invalida o ya hay una pieza en esa posicion
                        raise ValueError
                    self.posiciones_piezas.append((pos_x, pos_y))

                if len(self.piezas_nivel) < 2: # el archivo esta vacio o solo contiene una pieza
                    raise ValueError
        except:

            gamelib.say('Partida guardada corrupta, se iniciara una nueva partida.')
            self.piezas_nivel = []
            self.posiciones_piezas = [] 
            self.juego_nuevo()

        finally:
            self.nivel = len(self.piezas_nivel) - 2

    def guardar_juego(self):
        ''' guarda la partida actual en el archivo partida_guardada.csv'''

        with open('partida_guardada.csv', 'w') as f_guardada:
            for i in range(len(self.piezas_nivel)):
                f_guardada.write(f'{self.piezas_nivel[i]};{self.posiciones_piezas[i][0]},{self.posiciones_piezas[i][1]}\n')

    def presionar_boton(self, boton):
        ''' devuelve la accion correspondiente a apretar el boton, boton
        boton: string'''

        if boton == 'atras':
            gamelib.play_sound('audio/atras.wav')
            return 'Menuprincipal'

        elif boton == 'reiniciar':
            gamelib.play_sound('audio/reintentar.wav')
            return 'reiniciar'

    def movimientos_posibles(self):
        ''' devuelve los movimientos posibles para la pieza que actualmente debe moverse'''

        pieza = self.piezas_nivel[0]
        pieza_x, pieza_y = self.posiciones_piezas[0]

        mov_posible = []
        for mov_x, mov_y in self.piezas_jugables[pieza][0]:
            if (pieza_x + mov_x, pieza_y + mov_y) in self.posiciones_piezas:
                mov_posible.append((pieza_x + mov_x, pieza_y + mov_y))
        #se agregan todos los movimientos posibles sin extension

        if self.piezas_jugables[pieza][1]:#pieza con movimiento extensible

            mov_posible_ext = []
            for ext in self.piezas_jugables[pieza][0]:
                for k in range(2, 8):
                    if (pieza_x + (ext[0] * k), pieza_y + (ext[1] * k)) in self.posiciones_piezas:
                        #alguna pieza se encuentra en la posicion
                        mov_posible_ext.append((pieza_x + (ext[0] * k), pieza_y + (ext[1] * k)))
            mov_posible += mov_posible_ext

        return mov_posible

    def realizar_movimiento(self, x , y):
        ''' recibe una posicion x, y que hace referencia a una posicion en el tablero y si tal posicion es la misma de un movimiento
        posible, lo ejecuta.
        x: int
        y: int'''

        self.u_tablero = self.unidad - 1

        posicion = (x - 5) //  self.u_tablero, (y - 5 - self.u_tablero) // self.u_tablero

        if posicion in  self.mov_posibles:
            gamelib.play_sound('audio/comer.wav')
            i = self.posiciones_piezas.index(posicion) # se busca el indice correspondiente a esa posicion
            #como las piezas y las posiciones estan ligadas por sus indices, saber el indice de la posicion
            #es tambien saber el indice de la pieza, pero solo las posiciones toman valores unicos.

            self.piezas_nivel[0], self.piezas_nivel[i] = self.piezas_nivel[i], self.piezas_nivel[0] 
            self.posiciones_piezas[0], self.posiciones_piezas[i] = self.posiciones_piezas[i], self.posiciones_piezas[0]
            #se intercambia la pieza actual con la pieza destino

            self.piezas_nivel.pop(i)
            self.posiciones_piezas.pop(i)
            self.mov_posibles = self.movimientos_posibles()
            if len(self.piezas_nivel) == 1:
                #solo queda una pieza
                gamelib.play_sound('audio/ganar.wav')
                return 'ganar'

    def realizar_accion(self, x , y):
        ''' recibe una posicion x, y  y devuelve la accion correspondiente a un click en esa posicion
        x: int
        y: int'''

        for boton in self.botones:
            if self.botones[boton]['x'][0] < x < self.botones[boton]['x'][1] and self.botones[boton]['y'][0] < y < self.botones[boton]['y'][1]:
                return self.presionar_boton(boton)
        return self.realizar_movimiento(x, y)

class Menuprincipal:
    ''' posee los metodos necesarios para poder interpretar las acciones del usuario sobre el menu principal'''
    def __init__(self, unidad):

        #medidas
        self.ancho = unidad * 8

        #posiciones de botones
        self.botones_x = (self.ancho // 4 - 2, self.ancho - self.ancho // 4 + 2)
        boton_continuar_y = (unidad + unidad // 2 - 2, 2 * unidad + unidad // 2 + 2)
        boton_nueva_partida_y = (unidad * 3 + unidad // 2 - 2, 4 * unidad + unidad // 2 + 2)
        boton_opciones_y = (unidad * 5 + unidad // 2 - 2, 6 * unidad + unidad // 2 + 2)
        boton_salir_y = (unidad * 7 + unidad // 2 - 2, 8 * unidad + unidad // 2 + 2)

        self.botones = {'continuar': {'x': self.botones_x, 'y': boton_continuar_y}, 'nuevapartida': {'x': self.botones_x, 'y': boton_nueva_partida_y}, 'opciones': {'x': self.botones_x, 'y': boton_opciones_y}, 'salir': {'x': self.botones_x, 'y': boton_salir_y}}

    def presionar_boton(self, boton):
        ''' devuelve la accion correspondiente a apretar el boton, boton
        boton: string'''

        if boton == 'continuar':
            if not hay_guardada():
                gamelib.play_sound('audio/bloquear.wav')
                return

            gamelib.play_sound('audio/empezar.wav')
            return 'cargartablero'

        elif boton == 'nuevapartida':
            gamelib.play_sound('audio/empezar.wav')
            return 'nuevotablero'

        elif boton == 'opciones':
            gamelib.play_sound('audio/tap.wav')
            return 'Menuopciones'

        else:
            return 'Cerrar'

    def boton_presionado(self, x, y):
        ''' recibe una posicion x, y  y devuelve la accion correspondiente a un click en esa posicion
        x: int
        y: int'''

        for boton in self.botones:
            if self.botones[boton]['x'][0] < x < self.botones[boton]['x'][1] and self.botones[boton]['y'][0] < y < self.botones[boton]['y'][1]:
                return self.presionar_boton(boton)

class Menuopciones:
    ''' posee los metodos necesarios para poder interpretar las acciones del usuario sobre el menu de opciones'''
    def __init__(self, unidad):

        #medidas
        self.unidad = unidad
        alto = unidad * 10

        #posiciones de botones
        boton_dimensiones520 = ((unidad * 4, unidad * 6),(unidad * 2, unidad * 3))
        boton_dimensiones440 = ((unidad * 2, unidad * 4),(unidad * 2, unidad * 3))
        boton_piezas = ((unidad * 2 + unidad // 2, unidad * 6 - unidad // 2),(unidad * 5, unidad * 8))
        boton_volver = ((0, unidad * 3),(alto - unidad + unidad // 4, alto + 2))

        self.botones = {'dimensiones520':{'x': boton_dimensiones520[0], 'y': boton_dimensiones520[1]}, 'dimensiones440':{'x': boton_dimensiones440[0], 'y': boton_dimensiones440[1]}, 'piezas':{'x':boton_piezas[0], 'y':boton_piezas[1]}, 'volver': {'x': boton_volver[0], 'y': boton_volver[1]}}

    def presionar_boton(self, boton, x, y):
        ''' recibe un boton y una posicion x, y y devuelve la accion correspondiente a apretar el boton, boton o 
        clickear sobre la posicion x, y
        x: int
        y: int
        boton: string'''

        if boton == 'dimensiones520':
            gamelib.play_sound('audio/tap.wav')
            return 'dimensionar, 520'
            

        elif boton == 'dimensiones440':
            gamelib.play_sound('audio/tap.wav')
            return 'dimensionar, 440'

        elif boton == 'volver':
            gamelib.play_sound('audio/atras.wav')
            return 'Menuprincipal'

        else: # se clickea sobre la caja de piezas
            posicion = x // self.unidad - 2 - (x // (self.unidad // 2) - 1) % 2, y // self.unidad -  5
            i = posicion[0] + 3 * posicion[1]
            return f'piezas, {i}'


    def boton_presionado(self, x, y):
        ''' recibe una posicion x, y  y devuelve la accion correspondiente a un click en esa posicion
        x: int
        y: int'''

        for boton in self.botones:
            if self.botones[boton]['x'][0] < x < self.botones[boton]['x'][1] and self.botones[boton]['y'][0] < y < self.botones[boton]['y'][1]:
                return self.presionar_boton(boton, x, y)

def hay_guardada():
    '''devuelve True si hay una partida guardada y se puede abrir, caso contrario devuelve False'''
    try:
        with open('partida_guardada.csv') as partida:
            return True
    except:
        return False

def main():
    gamelib.title("Shape Shifter Chess")
    juego = Juego()
    gamelib.resize(juego.ancho, juego.alto)
    juego.mostrar_menu_actual()

    while gamelib.loop(30) and juego.menu_activo:
        for ev in gamelib.get_events():

            if ev.type == gamelib.EventType.ButtonPress:
                x, y = ev.x, ev.y
                juego.actualizar(x, y)

            elif ev.type == gamelib.EventType.KeyPress and ev.key == 'Escape':
                return

        juego.mostrar_menu_actual()


gamelib.init(main)
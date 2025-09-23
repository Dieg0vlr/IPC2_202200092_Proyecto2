from modelo.tda.lista_simple import lista_simple

class invernadero:
    def __init__(self, nombre:str, numero_hileras:int, plantas_x_hilera:int):
        self.nombre = nombre or ""
        self.numero_hileras = numero_hileras
        self.plantas_x_hilera = plantas_x_hilera
        self.hileras = lista_simple()   
        self.drones = lista_simple()    
        self.planes = lista_simple()    

    def agregar_hilera(self, h):
        self.hileras.insertar_final(h)

    def agregar_dron(self, d):
        self.drones.insertar_final(d)

    def agregar_plan(self, p):
        self.planes.insertar_final(p)

    def buscar_plan(self, nombre:str):
        return self.planes.buscar_primero(lambda p: p.nombre == nombre)

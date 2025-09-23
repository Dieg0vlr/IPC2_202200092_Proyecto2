class planta:
    def __init__(self, hilera:int, posicion:int, litros_agua:int, gramos_fertilizante:int, nombre:str):
        self.hilera = hilera
        self.posicion = posicion
        self.litros_agua = litros_agua
        self.gramos_fertilizante = gramos_fertilizante
        self.nombre = nombre or ""

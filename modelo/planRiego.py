from modelo.tda.cola import cola

class instruccion:
    def __init__(self, hilera:int, posicion:int):
        self.hilera = hilera
        self.posicion = posicion

    def etiqueta(self):
        return f"H{self.hilera}-P{self.posicion}"

class plan_riego:
    def __init__(self, nombre:str):
        self.nombre = nombre or ""
        self.orden = cola()  # cola de instruccion

    def agregar(self, hilera:int, posicion:int):
        self.orden.encolar(instruccion(hilera, posicion))

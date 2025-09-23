from modelo.tda.lista_simple import lista_simple

class hilera:
    def __init__(self, numero:int):
        self.numero = numero
        self.plantas_lineales = lista_simple()  # contiene objetos tipo planta

    def agregar_planta(self, planta_obj):
        self.plantas_lineales.insertar_final(planta_obj)

    def obtener_planta(self, posicion:int):
        return self.plantas_lineales.obtener_en(posicion - 1)

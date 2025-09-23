class dron:
    def __init__(self, id:int, nombre:str, hilera_asignada:int):
        self.id = id
        self.nombre = nombre or ""
        self.hilera_asignada = hilera_asignada

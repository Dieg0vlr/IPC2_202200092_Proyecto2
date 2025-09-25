from .nodo import nodo

class lista_simple:
    def __init__(self):
        self.cabeza = None
        self.cola = None
        self._len = 0

    def esta_vacia(self):
        return self.cabeza is None
    

    def insertar_final(self, valor):
        nuevo = nodo(valor)
        if self.cabeza is None:
            self.cabeza = nuevo
            self.cola = nuevo
        else:
            self.cola.siguiente = nuevo
            self.cola = nuevo
        self._len += 1

    def longitud(self):
        return self._len

    def obtener_en(self, idx):
        if idx < 0 or idx >= self._len:
            raise IndexError("Indice fuera de rango")
        i = 0
        actual = self.cabeza
        while actual is not None:
            if i == idx:
                return actual.valor
            i +=1
            actual = actual.siguiente
        raise IndexError("Indice fuera de rango")

    def iterar(self):
        actual = self.cabeza
        while actual is not None:
            yield actual.valor
            actual = actual.siguiente

    def buscar_primero(self, predicado):
        actual = self.cabeza
        while actual is not None:
            if predicado(actual.valor):
                return actual.valor
            actual = actual.siguiente
        return None                        


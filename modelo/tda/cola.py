from .lista_simple import lista_simple

class cola:
    def __init__ (self):
        self._datos = lista_simple() #para usar la lista en esta clase

    def encolar(self, v):
        self._datos.insertar_final(v)

    def desencolar(self):
        if self.esta_vacia():
            return None
        nodo = self._datos.cabeza
        self._datos.cabeza = nodo.siguiente
        if self._datos.cabeza is None:
            self._datos.cola = None
        self._datos._len -= 1
        return nodo.valor


    def frente(self):
        return None if self._datos.esta_vacia() else self._datos.cabeza.valor

    def esta_vacia(self):
        return self._datos.esta_vacia()

    def longitud(self):
        return self._datos.longitud()

    def iterar(self):
        for v in self._datos.iterar():
            yield v

    def clonar(self):
        nueva = cola()
        for v in self._datos.iterar():
            nueva.encolar(v)
        return nueva
            
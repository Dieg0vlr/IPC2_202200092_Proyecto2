from modelo.tda.lista_simple import lista_simple

class paso_tiempo:
    def __init__(self, segundo:int):
        self.segundo = segundo
        self.acciones_por_dron = lista_simple()  

class estadistica_dron:
    def __init__(self, nombre:str):
        self.nombre = nombre
        self.litros = 0
        self.gramos = 0

class estadistica_proceso:
    def __init__(self):
        self.tiempo_optimo_seg = 0
        self.agua_total_l = 0
        self.fert_total_g = 0
        self.por_dron = lista_simple()  # estadistica_dron

class pos_dron_item:
    def __init__(self, nombre:str, pos:int):
        self.nombre = nombre
        self.pos = pos



class simulador:
    def _buscar_pos_item(self, lista_pos, nombre):
        return lista_pos.buscar_primero(lambda it: it.nombre == nombre)

    def _buscar_stats_item(self, lista_stats, nombre):
        return lista_stats.buscar_primero(lambda it: it.nombre == nombre)

    def _ya_finalizo(self, finalizados, nombre):
        return finalizados.buscar_primero(lambda s: s == nombre) is not None

    def _marcar_finalizado(self, finalizados, nombre):
        if not self._ya_finalizo(finalizados, nombre):
            finalizados.insertar_final(nombre)

    def _primera_instr_de_hilera(self, cola_instr, hilera):
        for instr in cola_instr.iterar():
            if instr.hilera == hilera:
                return instr
        return None

    def _frente(self, cola_instr):
        return None if cola_instr.esta_vacia() else cola_instr.frente()


    def simular(self, inv, plan):
        # posiciones por dron y estadisticas
        lista_pos = lista_simple()  # pos_dron_item
        stats = estadistica_proceso()
        finalizados = lista_simple()  # nombres de drones a los que ya les dimos "Fin"

        for d in inv.drones.iterar():
            lista_pos.insertar_final(pos_dron_item(d.nombre, 0))
            stats.por_dron.insertar_final(estadistica_dron(d.nombre))

        
        pendientes = plan.orden.clonar()

        timeline = lista_simple()
        t = 0

        # seguimos mientras haya instrucciones pendientes
        while not pendientes.esta_vacia():
            t += 1
            paso = paso_tiempo(t)

            instr_front = self._frente(pendientes)
            dron_frente = None
            if instr_front is not None:
                dron_frente = inv.drones.buscar_primero(lambda dd: dd.hilera_asignada == instr_front.hilera)

            rego_este_segundo = False
            if dron_frente is not None:
                pitem = self._buscar_pos_item(lista_pos, dron_frente.nombre)
                if pitem is not None and pitem.pos == instr_front.posicion:
                    # Regar una vez por segundo maximo
                    paso.acciones_por_dron.insertar_final(f"{dron_frente.nombre} Regar")
                    h_obj = inv.hileras.buscar_primero(lambda hh: hh.numero == instr_front.hilera)
                    if h_obj is not None:
                        pl = h_obj.plantas_lineales.obtener_en(instr_front.posicion - 1)
                        ed = self._buscar_stats_item(stats.por_dron, dron_frente.nombre)
                        if ed is not None:
                            ed.litros += pl.litros_agua
                            ed.gramos += pl.gramos_fertilizante
                    pendientes.desencolar()
                    rego_este_segundo = True

            # Acciones del resto de drones en paralelo
            for d in inv.drones.iterar():
                # si este dron ya “Regar” en este segundo, ya registramos su acción
                if not rego_este_segundo or d is None or dron_frente is None or d.nombre != dron_frente.nombre:
                    sig_instr = self._primera_instr_de_hilera(pendientes, d.hilera_asignada)
                    if sig_instr is None:
                        if not self._ya_finalizo(finalizados, d.nombre):
                            paso.acciones_por_dron.insertar_final(f"{d.nombre} Fin")
                            self._marcar_finalizado(finalizados, d.nombre)
                        continue

                    pitem = self._buscar_pos_item(lista_pos, d.nombre)
                    if pitem is None:
                        continue
                    objetivo = sig_instr.posicion

                    if pitem.pos < objetivo:
                        pitem.pos += 1
                        paso.acciones_por_dron.insertar_final(
                            f"{d.nombre} Adelante(H{d.hilera_asignada}P{pitem.pos})"
                        )
                    elif pitem.pos > objetivo:
                        pitem.pos -= 1
                        paso.acciones_por_dron.insertar_final(
                            f"{d.nombre} Atrás(H{d.hilera_asignada}P{pitem.pos})"
                        )
                    else:
                        paso.acciones_por_dron.insertar_final(f"{d.nombre} Esperar")

            timeline.insertar_final(paso)

        stats.tiempo_optimo_seg = t
        # totales
        for ed in stats.por_dron.iterar():
            stats.agua_total_l += ed.litros
            stats.fert_total_g += ed.gramos

        return stats, timeline
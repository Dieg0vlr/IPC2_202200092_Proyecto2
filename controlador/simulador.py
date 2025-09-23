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

def _buscar_pos_item(lista_pos, nombre):
    return lista_pos.buscar_primero(lambda it: it.nombre == nombre)

def _buscar_stats_item(lista_stats, nombre):
    return lista_stats.buscar_primero(lambda it: it.nombre == nombre)

class simulador:
    def simular(self, inv, plan):
        # posiciones por dron usando TDA
        lista_pos = lista_simple()  # pos_dron_item
        # estadisticas por dron
        stats = estadistica_proceso()

        for d in inv.drones.iterar():
            lista_pos.insertar_final(pos_dron_item(d.nombre, 0))
            stats.por_dron.insertar_final(estadistica_dron(d.nombre))

        timeline = lista_simple()
        t = 0

        orden = plan.orden.clonar()

        while not orden.esta_vacia():
            instr = orden.desencolar()
            # dron asignado a la hilera
            dsel = inv.drones.buscar_primero(lambda dd: dd.hilera_asignada == instr.hilera)
            if dsel is None:
                continue

            # mover hasta alcanzar la posicion requerida
            while True:
                pi = _buscar_pos_item(lista_pos, dsel.nombre)
                if pi is None:
                    break
                if pi.pos == instr.posicion:
                    break
                t += 1
                paso = paso_tiempo(t)
                direccion = 1 if pi.pos < instr.posicion else -1
                pi.pos += direccion
                # accion del dron seleccionado
                paso.acciones_por_dron.insertar_final(f"{dsel.nombre} Adelante (H{instr.hilera}P{pi.pos})")
                # los demas esperan
                for d in inv.drones.iterar():
                    if d.nombre != dsel.nombre:
                        paso.acciones_por_dron.insertar_final(f"{d.nombre} Esperar")
                timeline.insertar_final(paso)

            # riega un 1s, unico riego global
            t += 1
            paso_r = paso_tiempo(t)
            paso_r.acciones_por_dron.insertar_final(f"{dsel.nombre} Regar")
            for d in inv.drones.iterar():
                if d.nombre != dsel.nombre:
                    paso_r.acciones_por_dron.insertar_final(f"{d.nombre} Esperar")
            timeline.insertar_final(paso_r)

            # actualizar estadisticas por dron segun la planta objetivo
            h_obj = inv.hileras.buscar_primero(lambda hh: hh.numero == instr.hilera)
            if h_obj is not None:
                pl = h_obj.plantas_lineales.obtener_en(instr.posicion - 1)
                ed = _buscar_stats_item(stats.por_dron, dsel.nombre)
                if ed is not None:
                    ed.litros += pl.litros_agua
                    ed.gramos += pl.gramos_fertilizante

        # consolidar totales
        stats.tiempo_optimo_seg = t
        for ed in stats.por_dron.iterar():
            stats.agua_total_l += ed.litros
            stats.fert_total_g += ed.gramos

        return stats, timeline

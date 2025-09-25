from modelo.tda.lista_simple import lista_simple

class coordenada:
    def __init__(self, h:int, p:int):
        self.h = h
        self.p = p

class item_pos_dron:
    def __init__(self, nombre:str, pos:int):
        self.nombre = nombre
        self.pos = pos

class servicio_graphviz:
    def  __init__(self, simulador):
        self.sim = simulador

    # escapar comillas
    def _esc(self, s):
        if s is None:
            return ""
        t = ""
        for ch in str(s):
            if ch == '"':
                t += '\\"'
            else:
                t += ch
        return t

    def _buscar_dron_por_nombre(self, invernadero, nombre):
        return invernadero.drones.buscar_primero(lambda d: d.nombre == nombre)

    def _buscar_item_posicion(self, lista_pos, nombre):
        return lista_pos.buscar_primero(lambda it: it.nombre == nombre)
    
    def _esta_hecho(self, hechos, hilera, posicion):
        c = hechos.buscar_primero(lambda x: x.h == hilera and x.p == posicion)
        return c is not None

    def _obtener_hp_de_accion(self, accion):
        # espera "Adelante (H#P#)" dentro del string y devuelve (hilera, posicion) o (0, 0) si no hay match
        if accion is None:
            return 0, 0
        s = str(accion)
        i = 0
        n = len(s)
        # busca (
        while i < n and s[i] != '(':
            i += 1
        # busca H
        while i < n and (s[i] != 'H' and s[i] != 'h'):
            i+= 1
        if i >= n:
            return 0, 0
        i += 1
        # lee hilera
        hilera_buf = ""
        while i < n and s[i].isdigit():
            hilera_buf += s[i]; i += 1
        #buscar P
        while i < n and (s[i] != 'P' and s[i] != 'p'):
            i += 1
        if i >= n:
            return 0, 0
        i += 1
        posicion_buf = ""
        while i < n and s[i].isdigit():
            posicion_buf += s[i]; i += 1
        if hilera_buf and posicion_buf:
            return int(hilera_buf), int (posicion_buf)
        return 0, 0

    def _separar_nombre_accion(self, linea):
        # "DR01 Regar" -> ("DR01","Regar")
        # "DR01 Adelante (H1P2)" -> ("DR01","Adelante (H1P2)")
        if linea is None:
            return "", ""
        s = str(linea)
        i = 0
        n = len(s)
        while i < n and s[i] != " ":
            i += 1
        if i <= 0 or i >= n:
            return s, ""
        return s[:i], s[i+1:].strip()

    def _cola_restante_del_plan(self, plan, regados):
        # clonar cola y saltar 'regados'
        cola_copia = plan.orden.clonar()
        k = 0
        while k < regados and not cola_copia.esta_vacia():
            cola_copia.desencolar()
            k += 1
        return cola_copia

    def graficar_estado(self, invernadero, plan, t):
        # simula una vez para obtener el timeline
        stats, timeline = self.sim.simular(invernadero, plan)

        # estado parcial a tiempo t
        lista_pos = lista_simple()  # item_pos_dron
        hechos = lista_simple() # coordenada(h,p) regados
        for d in invernadero.drones.iterar():
            lista_pos.insertar_final(item_pos_dron(d.nombre, 0))

        regados_count = 0

        
        for paso in timeline.iterar():
            if paso.segundo > t:
                break
            # procesar acciones por dron en este segundo
            for linea in paso.acciones_por_dron.iterar():
                nombre, accion = self._separar_nombre_accion(linea)
                if nombre == "":
                    continue
                dron_ref = self._buscar_dron_por_nombre(invernadero, nombre)
                if dron_ref is None:
                    continue

                if accion == "Regar":
                    # usar posicion actual del dron y su hilera
                    pi = self._buscar_item_posicion(lista_pos, nombre)
                    if pi is not None:
                        self._marcar_hecho(hechos, dron_ref.hilera_asignada, pi.pos)
                        regados_count += 1
                else:
                    # si es "Adelante (...)" actualiza la posicion
                    hilera, posicion = self._obtener_hp_de_accion(accion)
                    if posicion > 0:
                        pi = self._buscar_item_posicion(lista_pos, nombre)
                        if pi is not None:
                            pi.pos = posicion

        cola_restante = self._cola_restante_del_plan(plan, regados_count)

        dot = "digraph TDAs {\n"
        dot += '  rankdir=LR;\n'
        dot += '  node [shape=box, style="rounded,filled", fillcolor="#f7f7f7", fontname="Arial"];\n'
        dot += '  edge [color="#888"];\n'

        dot += '  subgraph cluster_plan {\n'
        dot += '    label="cola del plan (frente a la izquierda)";\n'
        dot += '    color="#cccccc";\n'
        prev_id = ""
        idx = 0
        for instr in cola_restante.iterar():
            nid = f'plan_n{idx}'
            lab = f'H{instr.hilera}-P{instr.posicion}'
            # frente se marca diferente si idx==0
            fc = "#e3f2fd" if idx == 0 else "#f7f7f7"
            dot += f'    {nid} [label="{self._esc(lab)}", fillcolor="{fc}"];\n'
            if prev_id != "":
                dot += f'    {prev_id} -> {nid};\n'
            prev_id = nid
            idx += 1
        if idx == 0:
            dot += '    vacia [label="cola vacia", fillcolor="#fffbe6"];\n'
        dot += '  }\n'

        #  drones y posiciones
        dot += '  subgraph cluster_drones {\n'
        dot += '    label="drones y posiciones";\n'
        dot += '    color="#cccccc";\n'
        for d in invernadero.drones.iterar():
            pi = self._buscar_item_posicion(lista_pos, d.nombre)
            pos_txt = "P0"
            if pi is not None:
                pos_txt = "P" + str(pi.pos)
            dot += f'    "{self._esc(d.nombre)}" [label="{self._esc(d.nombre)}\\nHilera={d.hilera_asignada}\\nPos={pos_txt}", fillcolor="#e8f5e9"];\n'
        dot += '  }\n'

        # hileras y plantas
        dot += '  subgraph cluster_hileras {\n'
        dot += '    label="hileras y plantas";\n'
        dot += '    color="#cccccc";\n'

        for hobj in invernadero.hileras.iterar():
            dot += f'    subgraph cluster_h{hobj.numero} {{\n'
            dot += f'      label="H{hobj.numero}";\n'
            dot += '      color="#dddddd";\n'

            i = 1
            while i <= invernadero.plantas_x_hilera:
                filled = "#fff"
                if self._esta_hecho(hechos, hobj.numero, i):
                    filled = "#ffe0b2"  # regada
                nid = f'h{hobj.numero}p{i}'
                dot += f'      {nid} [label="P{i}", shape=circle, style="filled", fillcolor="{filled}"];\n'

                if i > 1:
                    dot += f'      h{hobj.numero}p{i-1} -> {nid} [color="#bbb"];\n'
                i += 1
            dot += '    }\n'
        dot += '  }\n'

        # opciones finales
        dot += f'  labelloc="t";\n'
        dot += f'  label="estado de TDAs en t={t}s";\n'
        dot += "}\n"
        return dot    







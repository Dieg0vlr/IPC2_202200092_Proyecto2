from xml.dom import minidom

from modelo.invernadero import invernadero
from modelo.hilera import hilera
from modelo.planta import planta
from modelo.dron import dron
from modelo.planRiego import plan_riego
from modelo.tda.lista_simple import lista_simple


class sistema:
    def __init__(self):
        self.invernaderos = lista_simple()

    #helpers
    def _text_of_first(self, parent, tag):
            nodes = parent.getElementsByTagName(tag)
            if not nodes: 
                return ""
            # concatenar solo nodos de texto
            txt = ""
            for n in nodes[0].childNodes:
                if n.nodeType == n.TEXT_NODE:
                    txt += n.nodeValue
            return (txt or "").strip()

    def _buscar_nombre_dron_en_lista_drones(self, lista_nodos, id_str):
        # recorre la lista de nodos; si no hay, retorna DR{id}
        if not lista_nodos:
            return f"DR{id_str}"
        for d in lista_nodos:
            if d.getAttribute("id") == id_str:
                return d.getAttribute("nombre") or f"DR{id_str}"
        # si no lo encontro en ningun nodo
        return f"DR{id_str}"

    def _parsear_plan_a_cola(self, contenido, pr):
        #lee pares Hx-Py
        i, n = 0, len(contenido)
        hbuf, pbuf = "", ""
        while i < n:
            ch = contenido[i]
            if ch in ("H", "h"):
                i += 1
                hbuf = ""
                while i < n and contenido[i].isdigit():
                    hbuf += contenido[i]; i += 1
            elif ch in ("P", "p"):
                i += 1
                pbuf = ""
                while i < n and contenido[i].isdigit():
                    pbuf += contenido[i]; i +=1
                if hbuf and pbuf:
                    pr.agregar(int(hbuf), int(pbuf))
                    hbuf, pbuf = "", ""
            else:
                i += 1

    #carga---
    def cargar_xml(self, ruta:str):
        doc = minidom.parse(ruta)
        root = doc.documentElement # configuracion

        # lista general de drones
        lista_drones_tag = root.getElementsByTagName("listaDrones")
        lista_drones = None
        if lista_drones_tag:
            lista_drones = lista_drones_tag[0].getElementsByTagName("dron")

        # invernaderos
        lista_inv_tag = root.getElementsByTagName("listaInvernaderos")
        if not lista_inv_tag:
            return
        for inv_tag in lista_inv_tag[0].getElementsByTagName("invernadero"):                                      
            nombre_inv = inv_tag.getAttribute("nombre") or "Invernadero"
            num_h = int(self._text_of_first(inv_tag, "numeroHileras") or "0")
            pxh = int(self._text_of_first(inv_tag, "plantasXhilera") or "0")

            inv_obj = invernadero(nombre_inv, num_h, pxh)

            # crear hileras
            for n in range(1, num_h + 1):
                inv_obj.agregar_hilera(hilera(n))

            # plantas
            lista_plantas = inv_tag.getElementsByTagName("listaPlantas")
            if lista_plantas:
                for p in lista_plantas[0].getElementsByTagName("planta"):
                    h = int(p.getAttribute("hilera") or "0")
                    pos = int(p.getAttribute("posicion") or "0")
                    litros = int(p.getAttribute("litrosAgua") or "0")
                    gramos = int(p.getAttribute("gramosFertilizante") or "0")
                    nombre_planta = ""
                    for n in p.childNodes:
                        if n.nodeType == n.TEXT_NODE:
                            nombre_planta += n.nodeValue or ""
                    nombre_planta = nombre_planta.strip()
                    pl = planta(h, pos, litros, gramos, nombre_planta)
                    h_obj = inv_obj.hileras.buscar_primero(lambda hh: hh.numero == h)
                    if h_obj:
                        h_obj.agregar_planta(pl)

            # asignacion de drones
            asg = inv_tag.getElementsByTagName("asignacionDrones")
            if asg:
                for ad in asg[0].getElementsByTagName("dron"):
                    did = ad.getAttribute("id") or ""
                    h_asig = int(ad.getAttribute("hilera") or "0")
                    nombre_dron = self._buscar_nombre_dron_en_lista_drones(lista_drones, did)
                    dr = dron(int(did or 0), nombre_dron, h_asig)
                    inv_obj.agregar_dron(dr)

            # planes de riego
            pls = inv_tag.getElementsByTagName("planesRiego")
            if pls:
                for plnode in pls[0].getElementsByTagName("plan"):
                    pr = plan_riego(plnode.getAttribute("nombre") or "")
                    # obtener texto del plan
                    contenido = ""
                    for n in plnode.childNodes:
                        if n.nodeType == n.TEXT_NODE:
                            contenido += n.nodeValue or ""
                    self._parsear_plan_a_cola(contenido.strip(), pr)
                    inv_obj.agregar_plan(pr)

            self.invernaderos.insertar_final(inv_obj)

    def buscar_invernadero(self, nombre:str):
        return self.invernaderos.buscar_primero(lambda inv: inv.nombre == nombre)                       

        
                    
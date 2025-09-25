from modelo.tda.lista_simple import lista_simple

class html_reporter:
    def __init__(self, simulador):
        self.sim = simulador

    def _esc(self, s):
        t = ""
        if s is None:
            return ""
        for ch in str(s):
            if ch == "&":
                t += "&amp;"
            elif ch == "<":
                t += "&lt;"
            elif ch == ">":
                t += "&gt;"
            elif ch == '"':
                t += "&quot;"
            else:
                t += ch
        return t

    def _accion_para_dron(self, dron_nombre, paso):
        # busca "DRxx ..." dentro de acciones_por_dron
        acc = ""
        for s in paso.acciones_por_dron.iterar():
            txt = str(s or "")
            # comparacion manual de prefijo dron + espacio
            ok = True
            i = 0
            while ok and i < len(dron_nombre):
                if i >= len(txt) or txt[i] != dron_nombre[i]:
                    ok = False
                i += 1
            if ok and len(txt) > len(dron_nombre):
                if txt[len(dron_nombre)] == " ":
                    acc = txt[len(dron_nombre)+1:].strip()
                    return acc
        return acc

    def _tabla_drones(self, inv):
        h = "<table border='1' cellpadding='6'><thead><tr>"
        h += "<th>Dron</th><th>Hilera</th></tr></thead><tbody>"
        for d in inv.drones.iterar():
            h += "<tr><td>" + self._esc(d.nombre) + "</td><td>" + self._esc(d.hilera_asignada) + "</td></tr>"
        h += "</tbody></table>"
        return h

    def _tabla_eficiencia(self, stats):
        h = "<table border='1' cellpadding='6'><thead><tr>"
        h += "<th>Dron</th><th>Litros</th><th>Gramos</th></tr></thead><tbody>"
        for ed in stats.por_dron.iterar():
            h += "<tr><td>" + self._esc(ed.nombre) + "</td>"
            h += "<td>" + self._esc(ed.litros) + "</td>"
            h += "<td>" + self._esc(ed.gramos) + "</td></tr>"
        h += "</tbody></table>"
        return h

    def _tabla_instrucciones(self, inv, timeline):
        # header dinamico: Tiempos + una columna por dron
        h = "<table border='1' cellpadding='6'><thead><tr>"
        h += "<th>Tiempo(s)</th>"
        for d in inv.drones.iterar():
            h += "<th>" + self._esc(d.nombre) + "</th>"
        h += "</tr></thead><tbody>"
        # filas por segundo
        for paso in timeline.iterar():
            h += "<tr><td>" + self._esc(paso.segundo) + "</td>"
            for d in inv.drones.iterar():
                act = self._accion_para_dron(d.nombre, paso)
                h += "<td>" + self._esc(act) + "</td>"
            h += "</tr>"
        h += "</tbody></table>"
        return h

    def generar_reporte_invernadero(self, inv, plan):
        # simula
        stats, timeline = self.sim.simular(inv, plan)

        css = (
            "body{font-family:Arial,Helvetica,sans-serif;margin:24px;color:#222}"
            "h1,h2{margin:8px 0}"
            "table{border-collapse:collapse;margin:12px 0;width:100%}"
            "th,td{border:1px solid #ccc;padding:6px;text-align:left}"
            "thead{background:#f4f4f4}"
            ".kpi{display:flex;gap:16px;margin:8px 0}"
            ".card{border:1px solid #e0e0e0;padding:10px;border-radius:8px}"
        )

        html = "<!doctype html><html><head><meta charset='utf-8'><title>Reporte Invernadero</title>"
        html += "<style>" + css + "</style></head><body>"
        html += "<h1>Reporte de riego</h1>"
        html += "<div class='card'>"
        html += "<div><b>Invernadero:</b> " + self._esc(inv.nombre) + "</div>"
        html += "<div><b>Plan:</b> " + self._esc(plan.nombre) + "</div>"
        html += "<div class='kpi'>"
        html += "<div><b>Tiempo optimo:</b> " + self._esc(stats.tiempo_optimo_seg) + " s</div>"
        html += "<div><b>Agua total:</b> " + self._esc(stats.agua_total_l) + " L</div>"
        html += "<div><b>Fertilizante total:</b> " + self._esc(stats.fert_total_g) + " g</div>"
        html += "</div></div>"

        html += "<h2>Drones por hilera</h2>"
        html += self._tabla_drones(inv)

        html += "<h2>Eficiencia por dron</h2>"
        html += self._tabla_eficiencia(stats)

        html += "<h2>Instrucciones por tiempo</h2>"
        html += self._tabla_instrucciones(inv, timeline)

        html += "</body></html>"
        return html

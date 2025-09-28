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
        acc = ""
        for s in paso.acciones_por_dron.iterar():
            txt = str(s or "")
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
        h = "<div class='card'><table class='tabla'><thead><tr>"
        h += "<th>Dron</th><th>Hilera</th></tr></thead><tbody>"
        for d in inv.drones.iterar():
            h += "<tr><td><span class='etiqueta'>" + self._esc(d.nombre) + "</span></td>"
            h += "<td>H" + self._esc(d.hilera_asignada) + "</td></tr>"
        h += "</tbody></table></div>"
        return h

    def _tabla_eficiencia(self, stats):
        h = "<div class='card'><table class='tabla'><thead><tr>"
        h += "<th>Dron</th><th>Litros</th><th>Gramos</th></tr></thead><tbody>"
        for ed in stats.por_dron.iterar():
            h += "<tr><td><span class='etiqueta'>" + self._esc(ed.nombre) + "</span></td>"
            h += "<td class='num'>" + self._esc(ed.litros) + "</td>"
            h += "<td class='num'>" + self._esc(ed.gramos) + "</td></tr>"
        h += "</tbody></table></div>"
        return h

    def _tabla_instrucciones(self, inv, timeline):
        h = "<div class='card'><div class='scroll-x'>"
        h += "<table class='tabla tabla-grande'><thead><tr>"
        h += "<th>Tiempo(s)</th>"
        for d in inv.drones.iterar():
            h += "<th>" + self._esc(d.nombre) + "</th>"
        h += "</tr></thead><tbody>"
        for paso in timeline.iterar():
            h += "<tr><td class='num'>" + self._esc(paso.segundo) + "</td>"
            for d in inv.drones.iterar():
                act = self._accion_para_dron(d.nombre, paso)
                cls = "chip"
                if act.startswith("Adelante"):
                    cls += " chip-azul"
                elif act.startswith("Atrás") or act.startswith("Atras"):
                    cls += " chip-amarillo"
                elif act == "Regar":
                    cls += " chip-verde"
                elif act == "Fin":
                    cls += " chip-rojo"
                elif act == "Esperar":
                    cls += " chip-gris"
                h += "<td><span class='" + cls + "'>" + self._esc(act) + "</span></td>"
            h += "</tr>"
        h += "</tbody></table></div></div>"
        return h

    def generar_reporte_invernadero(self, inv, plan):
        stats, timeline = self.sim.simular(inv, plan)

        # -- CSS --
        css = """
        :root{
          --verde:#4CAF50;
          --verde-osc:#3d8b40;
          --gris-borde:#ddd;
          --gris-fondo:#f7f7f7;
          --gris-texto:#333;
        }
        *{box-sizing:border-box}
        html,body{margin:0;padding:0;background:var(--gris-fondo);color:var(--gris-texto);font-family:Arial,Helvetica,sans-serif}
        .wrap{max-width:1000px;margin:24px auto;padding:0 16px}
        header{
          background:var(--verde);
          color:#fff;
          padding:14px 16px;
          border-radius:6px;
          display:flex;
          align-items:center;
          justify-content:space-between;
          gap:12px;
        }
        header h1{margin:0;font-size:20px}
        .sub{font-size:14px;opacity:.95}
        .kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin:12px 0}
        .kpi{
          border:1px solid var(--gris-borde);
          background:#fff;
          border-radius:6px;
          padding:10px 12px;
        }
        .kpi h3{margin:0 0 6px 0;font-size:13px;color:#555}
        .kpi .v{font-size:20px;font-weight:bold;color:var(--verde)}
        .grid{display:grid;gap:12px;margin-top:8px}
        @media(min-width:900px){ .grid{grid-template-columns:1fr 1fr} }
        .card{
          background:#fff;border:1px solid var(--gris-borde);border-radius:6px;padding:12px
        }
        .card h2{margin:0 0 8px 0;font-size:18px;color:#222}
        .tabla{width:100%;border-collapse:collapse}
        .tabla th,.tabla td{border:1px solid var(--gris-borde);padding:8px;text-align:left}
        .tabla thead th{background:#e9f5ea;color:#214423}
        .tabla tbody tr:nth-child(even){background:#fafafa}
        .tabla-grande{min-width:640px}
        .scroll-x{overflow:auto}
        .num{font-variant-numeric:tabular-nums}
        .etiqueta{
          display:inline-block;background:#ecf7ed;border:1px solid #cfe7d1;color:#2e5b31;
          padding:2px 6px;border-radius:999px;font-size:12px;font-weight:bold
        }
        .chip{
          display:inline-block;padding:3px 8px;border-radius:12px;border:1px solid #ccc;background:#f5f5f5;font-size:12px
        }
        .chip-verde{background:#eaf7ec;border-color:#cfe7d1;color:#2e5b31;font-weight:bold}
        .chip-azul{background:#eef5ff;border-color:#cfe0ff;color:#214b92}
        .chip-amarillo{background:#fff7e6;border-color:#ffe1a6;color:#7a5a00}
        .chip-rojo{background:#ffecec;border-color:#ffcccc;color:#8a1c1c;font-weight:bold}
        .chip-gris{background:#f1f1f1;border-color:#d9d9d9;color:#666}
        footer{margin-top:14px;text-align:center;color:#666;font-size:12px}
        """

        html = "<!doctype html><html><head><meta charset='utf-8'>"
        html += "<meta name='viewport' content='width=device-width, initial-scale=1.0'>"
        html += "<title>Reporte Invernadero</title><style>" + css + "</style></head><body>"
        html += "<div class='wrap'>"

        html += "<header>"
        html += "<h1>Reporte de riego</h1>"
        html += "<div class='sub'>Invernadero: <b>" + self._esc(inv.nombre) + "</b> &nbsp;|&nbsp; Plan: <b>" + self._esc(plan.nombre) + "</b></div>"
        html += "</header>"

        html += "<div class='kpis'>"
        html += "<div class='kpi'><h3>Tiempo óptimo</h3><div class='v'>" + self._esc(stats.tiempo_optimo_seg) + " s</div></div>"
        html += "<div class='kpi'><h3>Agua total</h3><div class='v'>" + self._esc(stats.agua_total_l) + " L</div></div>"
        html += "<div class='kpi'><h3>Fertilizante total</h3><div class='v'>" + self._esc(stats.fert_total_g) + " g</div></div>"
        html += "</div>"

        html += "<div class='grid'>"
        html += "<div class='card'><h2>Drones por hilera</h2>" + self._tabla_drones(inv) + "</div>"
        html += "<div class='card'><h2>Eficiencia por dron</h2>" + self._tabla_eficiencia(stats) + "</div>"
        html += "</div>"

        # Instrucciones
        html += "<div class='card' style='margin-top:12px'>"
        html += "<h2>Instrucciones por tiempo</h2>"
        html += self._tabla_instrucciones(inv, timeline)
        html += "</div>"

        html += "<footer>GuateRiegos 2.0 — Reporte generado automáticamente</footer>"
        html += "</div></body></html>"
        return html

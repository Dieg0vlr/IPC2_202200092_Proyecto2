from modelo.tda.lista_simple import lista_simple


class generador_xml:
    def __init__(self, simulador):
        self.sim = simulador

    def _attr(self, k, v):
        if v is None:
            v = ""
        s = str(v)
        s = s.replace("'", "&apos;")
        s = s.replace('"', "&quot;")
        return f'{k}="{s}"'

    def _etag(self, nombre, contenido):
        return f"<{nombre}>{contenido}</{nombre}>"

    def _line(self, txt):
        return txt + "\n"

    def generar_salida(self, ruta_salida, lista_invernaderos):
        out = lista_simple()  

        def emit(s): out.insertar_final(s)  

        emit(self._line("<?xml version='1.0'?>"))
        emit(self._line("<datosSalida>"))
        emit(self._line("  <listaInvernaderos>"))

        for inv in lista_invernaderos.iterar():
            emit(self._line(f"    <invernadero {self._attr('nombre', inv.nombre)} >"))
            emit(self._line("      <listaPlanes>"))

            for plan in inv.planes.iterar():
                stats, timeline = self.sim.simular(inv, plan)

                emit(self._line(f"        <plan {self._attr('nombre', plan.nombre)}>"))
                emit(self._line(f"          {self._etag('tiempoOptimoSegundos', stats.tiempo_optimo_seg)}"))
                emit(self._line(f"          {self._etag('aguaRequeridaLitros', stats.agua_total_l)}"))
                emit(self._line(f"          {self._etag('fertilizanteRequeridoGramos', stats.fert_total_g)}"))

                emit(self._line("          <eficienciaDronesRegadores>"))
                for ed in stats.por_dron.iterar():
                    emit(self._line(
                        f"            <dron {self._attr('nombre', ed.nombre)} "
                        f"{self._attr('litrosAgua', ed.litros)} "
                        f"{self._attr('gramosFertilizante', ed.gramos)}/>"))
                emit(self._line("          </eficienciaDronesRegadores>"))

                emit(self._line("          <instrucciones>"))
                for paso in timeline.iterar():
                    emit(self._line(f"            <tiempo {self._attr('segundos', paso.segundo)}>"))
                    for acc in paso.acciones_por_dron.iterar():

                        acc_str = str(acc)
                        sp = acc_str.split(" ", 1)
                        nombre = sp[0] if sp else ""
                        accion = sp[1] if len(sp) > 1 else ""

                        emit(self._line(
                            f"              <dron {self._attr('nombre', nombre)} "
                            f"{self._attr('accion', accion)}/>"))
                    emit(self._line("            </tiempo>"))
                emit(self._line("          </instrucciones>"))

                emit(self._line("        </plan>"))

            emit(self._line("      </listaPlanes>"))
            emit(self._line("    </invernadero>"))

        emit(self._line("  </listaInvernaderos>"))
        emit(self._line("</datosSalida>"))

        contenido = "".join(out.iterar())  
        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(contenido)

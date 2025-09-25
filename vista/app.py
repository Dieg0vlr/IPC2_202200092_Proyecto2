from flask import Flask, request, render_template_string, Response
from controlador.sistema import sistema
from controlador.simulador import simulador
from controlador.generador_xml import generador_xml
from controlador.html_reporter import html_reporter
from controlador.graphviz_service import servicio_graphviz


SIM = simulador()

GZ = servicio_graphviz(SIM)
HR = html_reporter(SIM)
GX = generador_xml(SIM)

app = Flask(__name__)
SYS = sistema()


TPL_HOME = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>GuateRiegos 2.0</title></head>
<body>
  <h1>GuateRiegos 2.0</h1>
  <form method="post" action="/cargar" enctype="multipart/form-data">
    <input type="file" name="xml">
    <button type="submit">Cargar XML</button>
  </form>
  <form method="get" action="/simular">
    <input name="inv" placeholder="nombre invernadero">
    <input name="plan" placeholder="nombre plan">
    <button type="submit">Simular</button>
  </form>
</body>
</html>
"""

@app.get("/")
def home():
    return render_template_string(TPL_HOME)

@app.post("/cargar")
def cargar():
    f = request.files.get("xml")
    if not f:
        return "No file uploaded", 400
    try:
        # Cambia la ruta según donde quieras guardar el archivo
        ruta = "archivos_prueba/entrada.xml"  # O usa ruta absoluta si es necesario
        f.save(ruta)

        # Ver el contenido del archivo cargado
        with open(ruta, 'r') as archivo:
            contenido = archivo.read()
            print("Contenido del archivo XML cargado:", contenido)  # Ver en consola

        # Intentar procesar el XML
        SYS.cargar_xml(ruta)
        return "Archivo XML cargado exitosamente"
    
    except Exception as e:
        import traceback
        traceback.print_exc()  # imprime todo el traceback en consola
        return f"Error al procesar el archivo XML: {str(e)}", 500



@app.get("/simular")
def simular():
    inv = SYS.buscar_invernadero(request.args.get("inv",""))
    if inv is None:
        return "invernadero no encontrado", 404
    plan = inv.buscar_plan(request.args.get("plan",""))
    if plan is None:
        return "plan no encontrado", 404
    stats, timeline = SIM.simular(inv, plan)

    filas_html = ""
    for p in timeline.iterar():
        fila = "<tr><td>" + str(p.segundo) + "</td><td>"
        # concatenar acciones
        accs = ""
        for a in p.acciones_por_dron.iterar():
            if accs:
                accs += " | "
            accs += a
        fila += accs + "</td></tr>"
        filas_html += fila

    html = """
    <h2>Simulacion</h2>
    <p>Tiempo optimo: """ + str(stats.tiempo_optimo_seg) + """s</p>
    <p>Agua total: """ + str(stats.agua_total_l) + """ L</p>
    <p>Fertilizante total: """ + str(stats.fert_total_g) + """ g</p>
    <table border="1" cellpadding="6">
      <thead><tr><th>t(s)</th><th>acciones</th></tr></thead>
      <tbody>""" + filas_html + """</tbody>
    </table>
    <p><a href="/">Volver</a></p>
    """
    return html


@app.get("/salida")
def salida():
    GX.generar_salida("salida.xml", SYS.invernaderos)
    return "salida.xml generado"


TPL_HOME = """
<!doctype html>
<html>
<head><meta charset="utf-8"><title>GuateRiegos 2.0</title></head>
<body>
  <h1>GuateRiegos 2.0</h1>
  
  <form method="post" action="/cargar" enctype="multipart/form-data">
    <input type="file" name="xml">
    <button type="submit">Cargar XML</button>
  </form>

  <form method="get" action="/simular">
    <input name="inv" placeholder="nombre invernadero">
    <input name="plan" placeholder="nombre plan">
    <button type="submit">Simular</button>
  </form>

  <form method="get" action="/salida">
    <button type="submit">Generar salida XML</button>
  </form>
</body>
</html>
"""



@app.get("/reporte")
def reporte():
    inv = SYS.buscar_invernadero(request.args.get("inv",""))
    if inv is None:
        return "invernadero no encontrado", 404
    plan = inv.buscar_plan(request.args.get("plan",""))
    if plan is None:
        return "plan no encontrado", 404
    html = HR.generar_reporte_invernadero(inv, plan)
    return html

@app.get("/grafo")
def grafo():
    inv = SYS.buscar_invernadero(request.args.get("inv",""))
    if inv is None:
        return "invernadero no encontrado", 404
    plan = inv.buscar_plan(request.args.get("plan",""))
    if plan is None:
        return "plan no encontrado", 404
    try:
        t = int(request.args.get("t","0") or "0")
    except:
        t = 0
    dot = GZ.graficar_estado(inv, plan, t)

    # opcional: guardar .dot en disco
    try:
        with open(f"grafo_t{t}.dot", "w", encoding="utf-8") as f:
            f.write(dot)
    except:
        # no hacer nada si no se puede escribir
        pass

    return Response(dot, mimetype="text/plain")



if __name__ == "__main__":
    app.run(debug=True)

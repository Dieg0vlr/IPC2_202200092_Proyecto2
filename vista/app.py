from flask import Flask, request, render_template_string
from controlador.sistema import sistema
from controlador.simulador import simulador
from controlador.generador_xml import generador_xml

GX = generador_xml(SIM)
app = Flask(__name__)
SYS = sistema()
SIM = simulador()

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
        return "no file", 400
    ruta = "/tmp/entrada.xml"
    f.save(ruta)
    SYS.cargar_xml(ruta)
    return "ok"

@app.get("/simular")
def simular():
    inv = SYS.buscar_invernadero(request.args.get("inv",""))
    if inv is None:
        return "invernadero no encontrado", 404
    plan = inv.buscar_plan(request.args.get("plan",""))
    if plan is None:
        return "plan no encontrado", 404
    stats, timeline = SIM.simular(inv, plan)
    # render super simple
    filas = []
    for p in timeline.iterar():
        fila = f"<tr><td>{p.segundo}</td><td>"
        accs = []
        for a in p.acciones_por_dron.iterar():
            accs.append(a)
        fila += " | ".join(accs)
        fila += "</td></tr>"
        filas.append(fila)
    html = f"""
    <h2>Simulacion</h2>
    <p>Tiempo optimo: {stats.tiempo_optimo_seg}s</p>
    <p>Agua total: {stats.agua_total_l} L</p>
    <p>Fertilizante total: {stats.fert_total_g} g</p>
    <table border="1" cellpadding="6">
      <thead><tr><th>t(s)</th><th>acciones</th></tr></thead>
      <tbody>{"".join(filas)}</tbody>
    </table>
    <p><a href="/">Volver</a></p>
    """
    return html

@app.get("/salida")
def salida():
    GX.generar_salida("salida.xml", SYS.invernaderos)
    return "salida.xml generado"


if __name__ == "__main__":
    app.run(debug=True)

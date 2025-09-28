from flask import Flask, request, render_template_string, Response
from controlador.sistema import sistema
from controlador.simulador import simulador
from controlador.generador_xml import generador_xml
from controlador.html_reporter import html_reporter
from controlador.graphviz_service import servicio_graphviz
from flask import send_file
import os


SIM = simulador()

GZ = servicio_graphviz(SIM)
HR = html_reporter(SIM)
GX = generador_xml(SIM)

app = Flask(__name__)
SYS = sistema()


TPL_HOME = """
<!doctype html>
<html lang="es">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GuateRiegos 2.0</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f7f6;
            margin: 0;
            padding: 0;
        }
        h1 {
            text-align: center;
            background-color: #4CAF50;
            color: white;
            padding: 20px;
        }
        h2 {
            text-align: center;
            color: #333;
        }
        .container {
            width: 80%;
            margin: 20px auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
            border-radius: 8px;
        }
        form {
            display: flex;
            flex-direction: column;
            gap: 15px;
        }
        input[type="text"], input[type="file"] {
            padding: 10px;
            font-size: 16px;
            width: 100%;
            border-radius: 5px;
            border: 1px solid #ddd;
        }
        button {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
            border-radius: 5px;
            transition: background-color 0.3s;
        }
        button:hover {
            background-color: #45a049;
        }
        .result-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        .result-table th, .result-table td {
            border: 1px solid #ddd;
            padding: 10px;
            text-align: center;
        }
        .result-table th {
            background-color: #4CAF50;
            color: white;
        }
        .result-table td {
            background-color: #f9f9f9;
        }
        .center {
            text-align: center;
        }
        .back-button {
            display: inline-block;
            background-color: #f44336;
            color: white;
            padding: 10px 20px;
            font-size: 16px;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
            text-align: center;
        }
        .back-button:hover {
            background-color: #e53935;
        }
    </style>
</head>
<body>

    <h1>GuateRiegos 2.0</h1>

    <div class="container">
        <form method="post" action="/cargar" enctype="multipart/form-data">
            <h2>Cargar Archivo XML</h2>
            <input type="file" name="xml" required>
            <button type="submit">Cargar XML</button>
        </form>

        <form method="get" action="/simular">
            <h2>Simular Proceso de Riego</h2>
            <input name="inv" placeholder="Nombre del invernadero" required>
            <input name="plan" placeholder="Nombre del plan de riego" required>
            <button type="submit">Simular</button>
        </form>

                <form method="get" action="/reporte">
            <h2>Reporte HTML</h2>
            <input name="inv" placeholder="Nombre del invernadero" required>
            <input name="plan" placeholder="Nombre del plan de riego" required>
            <button type="submit">Generar Reporte HTML</button>
        </form>

        <form method="get" action="/grafo">
            <h2>Graphviz (.dot)</h2>
            <input name="inv" placeholder="Nombre del invernadero" required>
            <input name="plan" placeholder="Nombre del plan de riego" required>
            <input name="t" type="number" min="0" placeholder="Segundo t (opcional)">
            <button type="submit">Generar .dot</button>
        </form>

        <form method="get" action="/salida">
            <button type="submit">Generar Salida XML</button>
        </form>
    </div>



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
        ruta = "archivos_prueba/entrada.xml"  
        f.save(ruta)

        # Ver el contenido del archivo cargado
        with open(ruta, 'r') as archivo:
            contenido = archivo.read()
            print("Contenido del archivo XML cargado:", contenido) 

        # procesa el XML
        SYS.cargar_xml(ruta)
        
        success_html = """
        <!doctype html>
        <html lang="es">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Archivo XML Cargado</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background-color: #f4f7f6;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    color: #4CAF50;
                }
                .message {
                    background-color: #dff0d8;
                    padding: 20px;
                    color: #3c763d;
                    font-size: 18px;
                    border: 1px solid #d6e9c6;
                    border-radius: 5px;
                }
                .back-button {
                    display: inline-block;
                    background-color: #f44336;
                    color: white;
                    padding: 10px 20px;
                    font-size: 16px;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }
                .back-button:hover {
                    background-color: #e53935;
                }
            </style>
        </head>
        <body>
            <h1>Archivo XML Cargado Exitosamente</h1>
            <div class="message">
                <p>El archivo XML se cargó correctamente.</p>
            </div>
            <a href="/" class="back-button">Volver</a>
        </body>
        </html>
        """
        return success_html

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
    <!doctype html>
    <html lang="es">
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Simulación GuateRiegos</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background-color: #f7f7f7;
                margin: 0;
                padding: 0;
                text-align: center;
            }
            h1 {
                background-color: #4CAF50;
                color: white;
                padding: 20px;
                margin-bottom: 30px;
            }
            h2 {
                font-size: 24px;
                color: #333;
            }
            .container {
                width: 80%;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
                border-radius: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 20px;
                margin-bottom: 20px;
            }
            th, td {
                padding: 12px 20px; 
                text-align: center; 
                border: 1px solid #ddd;
            }
            th {
                background-color: #f2f2f2; 
                color: #333;
            }
            td {
                background-color: #fff;
                color: #333;
            }
            tr:hover {
                background-color: #f1f1f1; 
            }
            .back-button {
                display: inline-block;
                background-color: #f44336;
                color: white;
                padding: 10px 20px;
                font-size: 16px;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }
            .back-button:hover {
                background-color: #e53935;
            }
        </style>
    </head>
    <body>
        <h1>Simulación de Riego - GuateRiegos 2.0</h1>
        <div class="container">
            <h2>Resultados de la Simulación</h2>
            <p><strong>Tiempo óptimo:</strong> """ + str(stats.tiempo_optimo_seg) + """s</p>
            <p><strong>Agua total:</strong> """ + str(stats.agua_total_l) + """ L</p>
            <p><strong>Fertilizante total:</strong> """ + str(stats.fert_total_g) + """ g</p>
            <table>
                <thead>
                    <tr>
                        <th>t(s)</th>
                        <th>Acciones</th>
                    </tr>
                </thead>
                <tbody>
                    """ + filas_html + """
                </tbody>
            </table>
            <a href="/" class="back-button">Volver</a>
        </div>
    </body>
    </html>
    """
    return html



@app.get("/salida")
def salida():
    ruta_salida = "salida.xml"
    
    GX.generar_salida(ruta_salida, SYS.invernaderos)
    
    if not os.path.exists(ruta_salida):
        return "Error: el archivo salida.xml no se ha generado correctamente", 500
    
    return send_file(ruta_salida, as_attachment=True)


@app.get("/reporte")
def reporte():
    inv = SYS.buscar_invernadero(request.args.get("inv",""))
    if inv is None:
        return "invernadero no encontrado", 404
    plan = inv.buscar_plan(request.args.get("plan",""))
    if plan is None:
        return "plan no encontrado", 404
    html = HR.generar_reporte_invernadero(inv, plan)
    html += """
    <div class="center">
        <a href="/" class="back-button">Volver</a>
    </div>
    """
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

    try:
        with open(f"grafo_t{t}.dot", "w", encoding="utf-8") as f:
            f.write(dot)
    except:
        pass

    return Response(dot, mimetype="text/plain")



if __name__ == "__main__":
    app.run(debug=True)

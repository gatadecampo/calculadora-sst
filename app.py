from flask import Flask, request, jsonify, render_template_string
import math

app = Flask(__name__)

# 1. Función para formatear minutos decimales a hh:mm:ss
def formatear_tiempo(minutos_decimales):
    segundos_totales = int(round(minutos_decimales * 60))
    horas = segundos_totales // 3600
    minutos = (segundos_totales % 3600) // 60
    segundos = segundos_totales % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

# 2. El motor de cálculo en Python (Reglas de negocio actualizadas)
FORMULAS = {
    "manual": lambda x: x / 100,
    "recursos_pdf": lambda x: x / 40,  
    "recursos_diagramas": lambda x: x / 60,  
    "glosario": lambda x: (x * 48) / 60,
    "evaluacion": lambda x: x * 2.5,
    "storyline": lambda x: x * 4,
    "aplicaciones_practicas": lambda x: x * 2.5
}

# 3. Interfaz Gráfica (HTML + CSS)
HTML_INTERFAZ = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bukplay SST</title>
    <style>
        :root {
            --buk-blue-dark: #11347A;   
            --buk-blue-logo: #2B52C3;   
            --buk-blue-sst: #3B5998;    
            --buk-blue-light: #E3ECFB;  
            --buk-orange: #FFAB00;      
            --text-dark: #1A2530;
            --card-bg: #FFFFFF;
        }

        body { 
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            background-color: var(--buk-blue-light); 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            height: 100vh; 
            margin: 0; 
        }

        .card { 
            background: var(--card-bg); 
            padding: 40px; 
            border-radius: 20px; 
            box-shadow: 0 20px 25px -5px rgba(17, 52, 122, 0.15), 0 10px 10px -5px rgba(17, 52, 122, 0.1); 
            width: 100%; 
            max-width: 440px; 
            border-top: 6px solid var(--buk-blue-dark);
            position: relative;
        }

        .header-container {
            text-align: center;
            margin-bottom: 30px;
        }

        .title-row {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .mascota {
            width: 150px;
            height: auto;
            border-radius: 50%;
            background-color: #fff;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }

        h2 { 
            color: var(--buk-blue-logo); 
            margin: 0;
            font-size: 45px;
            font-weight: 800;
            letter-spacing: -1px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }
        
        h2 span.sst-badge {
            background-color: var(--buk-blue-sst);
            color: white;
            font-size: 20px;
            padding: 5px 14px;
            border-radius: 8px;
            font-weight: 700;
            letter-spacing: 0.5px;
        }

        p.subtitle {
            color: var(--buk-blue-dark);
            font-size: 14px;
            text-align: center;
            margin: 8px 0 0 0;
            font-weight: 600;
            opacity: 0.8;
        }

        .group { margin-bottom: 24px; }

        label { 
            display: block; 
            margin-bottom: 8px; 
            font-weight: 700; 
            color: var(--buk-blue-dark); 
            font-size: 14px;
        }

        select, input { 
            width: 100%; 
            padding: 14px; 
            border: 2px solid #D2DCF0; 
            border-radius: 10px; 
            box-sizing: border-box; 
            font-size: 15px; 
            color: var(--text-dark);
            background-color: #FFF;
            font-weight: 500;
            transition: all 0.2s ease;
        }

        select:focus, input:focus {
            outline: none;
            border-color: var(--buk-blue-logo);
            box-shadow: 0 0 0 4px rgba(43, 82, 195, 0.15);
        }

        .result-box { 
            background-color: var(--buk-blue-dark); 
            padding: 22px; 
            border-radius: 12px; 
            text-align: center; 
            margin-top: 15px; 
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
        }

        .result-box label {
            color: #FFFFFF;
            font-weight: 600;
            margin-bottom: 6px;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 1px;
            opacity: 0.9;
        }

        .result-box span { 
            display: block; 
            font-size: 42px; 
            font-weight: 900; 
            color: var(--buk-orange); 
            text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        }
    </style>
</head>
<body>

<div class="card">
    <div class="header-container">
        <h2>Bukplay <span class="sst-badge">SST</span></h2>
        <img src="/static/ESETIN_4.png" alt="Mascota Esetín" class="mascota">
        <p class="subtitle">Calculadora de tiempos en andragogía</p>
    </div>

    <div class="group">
        <label for="tipoRecurso">Tipo de recurso educativo</label>
        <select id="tipoRecurso">
            <option value="manual" data-unit="Palabras">Manual</option>
            <option value="recursos_pdf" data-unit="Palabras">Recursos obligatorios (pdf interactivo y guías de aplicación interactiva)</option>
            <option value="recursos_diagramas" data-unit="Palabras">Recursos obligatorios (checklist, diagramas de flujo, infografías)</option>
            <option value="glosario" data-unit="Conceptos clave">Glosario</option>
            <option value="evaluacion" data-unit="Preguntas">Evaluación</option>
            <option value="storyline" data-unit="Slides">Storyline</option>
            <option value="aplicaciones_practicas" data-unit="Palabras">Aplicaciones prácticas (tipo matriz)</option>
        </select>
    </div>

    <div class="group">
        <label id="labelInsumo" for="cantidad">Cantidad (Palabras)</label>
        <input type="number" id="cantidad" min="0" value="0">
    </div>

    <div class="result-box">
        <label>Tiempo estimado de lectura y estudio</label>
        <span id="resultado">00:00:00</span>
    </div>
</div>

<script>
    const selectRecurso = document.getElementById('tipoRecurso');
    const inputCantidad = document.getElementById('cantidad');
    const labelInsumo = document.getElementById('labelInsumo');
    const txtResultado = document.getElementById('resultado');

    async function enviarDatosAPython() {
        const recurso = selectRecurso.value;
        const cantidad = parseFloat(inputCantidad.value) || 0;
        
        const unidad = selectRecurso.options[selectRecurso.selectedIndex].getAttribute('data-unit');
        labelInsumo.textContent = `Cantidad (${unidad})`;

        try {
            const respuesta = await fetch('/api/calcular', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tipo_recurso: recurso, cantidad: cantidad })
            });
            
            const data = await respuesta.json(); 
            
            if (data.success) {
                txtResultado.textContent = data.tiempo_formateado;
            }
        } catch (error) {
            console.error("Error al conectar con Flask:", error);
        }
    }

    selectRecurso.addEventListener('change', enviarDatosAPython);
    inputCantidad.addEventListener('input', enviarDatosAPython);
    
    // Llamar una vez al inicio para que el label coincida con la primera opción
    enviarDatosAPython();
</script>

</body>
</html>
"""

# 4. Ruta principal
@app.route('/')
def inicio():
    return render_template_string(HTML_INTERFAZ)

# 5. Ruta API
@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    datos = request.get_json()
    tipo_recurso = datos.get('tipo_recurso', '').lower()
    cantidad = float(datos.get('cantidad', 0))
    
    if tipo_recurso in FORMULAS:
        tiempo_calculado = FORMULAS[tipo_recurso](cantidad)
        tiempo_formateado = formatear_tiempo(tiempo_calculado)
        
        return jsonify({
            "success": True, 
            "tiempo_formateado": tiempo_formateado        
        })
    
    return jsonify({"success": False, "error": "Recurso no válido"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8080)

from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. El motor de cálculo en Python (Reglas de negocio)
FORMULAS = {
    "manual": lambda x: x / 100,
    "recursos_diagramas": lambda x: x / 60,  # Checklist, diagramas de flujo, infografías SST
    "glosario": lambda x: (x * 48) / 60,
    "evaluacion": lambda x: x * 2.5,
    "storyline": lambda x: x * 4,
    "recursos_pdf": lambda x: x * 2.5 
}

# 2. Interfaz Gráfica basada en "Templates Motion Graphics diseño SST_2.docx"
HTML_INTERFAZ = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bukplay SST</title>
    <style>
        :root {
            --buk-blue-dark: #11347A;   /* Azul profundo de portadas Estilo A */
            --buk-blue-logo: #2B52C3;   /* Azul del isotipo de Bukplay */
            --buk-blue-sst: #3B5998;    /* Azul del badge SST */
            --buk-blue-light: #E3ECFB;  /* Fondo periwinkle suave de cortinas */
            --buk-orange: #FFAB00;      /* Naranja/Amarillo para destacar texto importante */
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

        h2 { 
            color: var(--buk-blue-logo); 
            margin: 0;
            font-size: 32px;
            font-weight: 800;
            letter-spacing: -1px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }
        
        /* El contenedor de la sigla SST calcado del logo original */
        h2 span.sst-badge {
            background-color: var(--buk-blue-sst);
            color: white;
            font-size: 14px;
            padding: 4px 12px;
            border-radius: 8px;
            font-weight: 700;
            letter-spacing: 0.5px;
            display: inline-block;
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

        /* Al hacer foco, se ilumina con el azul de la marca */
        select:focus, input:focus {
            outline: none;
            border-color: var(--buk-blue-logo);
            box-shadow: 0 0 0 4px rgba(43, 82, 195, 0.15);
        }

        /* Caja de resultado inspirada en el bloque de títulos destacados */
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

        /* El número final se destaca en naranja brillante tal como en las diapositivas */
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
        <p class="subtitle">Calculadora de tiempos de lectura y estudio</p>
    </div>
    
    <div class="group">
        <label for="tipoRecurso">Tipo de recurso educativo</label>
        <select id="tipoRecurso">
            <option value="manual" data-unit="Palabras">Manuales y Textos Base</option>
            <option value="recursos_diagramas" data-unit="Palabras">Diagramas y Esquemas (PHVA, IPERV, Árbol)</option>
            <option value="recursos_pdf" data-unit="Palabras">PDF Interactivos y Guías de Aplicación</option>
            <option value="glosario" data-unit="Conceptos clave">Glosario de Conceptos Clave</option>
            <option value="evaluacion" data-unit="Preguntas">Evaluaciones y Cuestionarios SST</option>
            <option value="storyline" data-unit="Slides">Módulos Interactivos Storyline / SCORM</option>
        </select>
    </div>

    <div class="group">
        <label id="labelInsumo" for="cantidad">Cantidad (Palabras)</label>
        <input type="number" id="cantidad" min="0" value="0">
    </div>

    <div class="result-box">
        <label>Tiempo estimado de ejecución</label>
        <span id="resultado">0.0 min</span>
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
                txtResultado.textContent = `${data.tiempo} min`;
            }
        } catch (error) {
            console.error("Error al conectar con Flask:", error);
        }
    }

    selectRecurso.addEventListener('change', enviarDatosAPython);
    inputCantidad.addEventListener('input', enviarDatosAPython);
</script>

</body>
</html>
"""

# 3. Ruta principal
@app.route('/')
def inicio():
    return render_template_string(HTML_INTERFAZ)

# 4. Ruta API
@app.route('/api/calcular', methods=['POST'])
def api_calcular():
    datos = request.get_json()
    tipo_recurso = datos.get('tipo_recurso', '').lower()
    cantidad = float(datos.get('cantidad', 0))
    
    if tipo_recurso in FORMULAS:
        tiempo_calculado = FORMULAS[tipo_recurso](cantidad)
        return jsonify({
            "success": True, 
            "tiempo": round(tiempo_calculado, 1)
        })
    
    return jsonify({"success": False, "error": "Recurso no válido"}), 400

if __name__ == '__main__':
    app.run(debug=False, port=5005)
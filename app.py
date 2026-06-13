from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# 1. El motor de cálculo en Python (Reglas de negocio)
FORMULAS = {
    "manual": lambda x: x / 100,
    "recursos_checklist": lambda x: x / 60,
    "glosario": lambda x: (x * 48) / 60,
    "evaluacion": lambda x: x * 2.5,
    "storyline": lambda x: x * 4,
    "recursos_pdf": lambda x: x * 2.5 
}

# 2. Interfaz Gráfica (HTML + CSS + JS)
HTML_INTERFAZ = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Calculadora de Lectura y Estudio SST</title>
    <style>
        body { font-family: sans-serif; background-color: #f4f7f6; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 100%; max-width: 400px; }
        h2 { text-align: center; color: #2c3e50; margin-top: 0; }
        .group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: bold; color: #555; }
        select, input { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 6px; box-sizing: border-box; font-size: 16px; }
        .result-box { background-color: #eef9f5; border-left: 5px solid #2ecc71; padding: 15px; border-radius: 4px; text-align: center; margin-top: 25px; }
        .result-box span { display: block; font-size: 24px; font-weight: bold; color: #27ae60; }
    </style>
</head>
<body>

<div class="card">
    <h2>Calculadora SST</h2>
    
    <div class="group">
        <label for="tipoRecurso">Tipo de Recurso</label>
        <select id="tipoRecurso">
            <option value="manual" data-unit="Palabras">Manual</option>
            <option value="recursos_checklist" data-unit="Palabras">Recursos obligatorios (checklist, diagramas)</option>
            <option value="glosario" data-unit="Conceptos clave">Glosario</option>
            <option value="evaluacion" data-unit="Preguntas">Evaluación</option>
            <option value="storyline" data-unit="Slides">Storyline</option>
            <option value="recursos_pdf" data-unit="Palabras">Recursos obligatorios (pdf interactivo)</option>
        </select>
    </div>

    <div class="group">
        <label id="labelInsumo" for="cantidad">Cantidad (Palabras)</label>
        <input type="number" id="cantidad" min="0" value="0">
    </div>

    <div class="result-box">
        <label>Tiempo de ejecución estimado:</label>
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
        
        // Cambia la etiqueta del input dinámicamente
        const unidad = selectRecurso.options[selectRecurso.selectedIndex].getAttribute('data-unit');
        labelInsumo.textContent = `Cantidad (${unidad})`;

        try {
            const respuesta = await fetch('/api/calcular', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ tipo_recurso: recurso, cantidad: cantidad })
            });
            
            // ¡AQUÍ ESTÁ LA CORRECCIÓN! Usamos .json() en vez de .get_json()
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
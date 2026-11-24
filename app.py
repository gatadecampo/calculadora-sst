from __future__ import annotations

from flask import Flask, jsonify, render_template_string, request

# Importamos el generador de CSS oficial de la guía Buk 2026
from buk_brand import css

app = Flask(__name__)


# 1. Función para formatear minutos decimales a hh:mm:ss (sin cambios)
def formatear_tiempo(minutos_decimales: float) -> str:
    segundos_totales = int(round(minutos_decimales * 60))
    horas = segundos_totales // 3600
    minutos = (segundos_totales % 3600) // 60
    segundos = segundos_totales % 60
    return f"{horas:02d}:{minutos:02d}:{segundos:02d}"


# 2. Motor de cálculo en Python (Reglas de negocio intactas)
FORMULAS = {
    "manual": lambda x: x / 100,
    "recursos_pdf": lambda x: x / 40,
    "recursos_diagramas": lambda x: x / 60,
    "glosario": lambda x: (x * 48) / 60,
    "evaluacion": lambda x: x * 2.5,
    "storyline": lambda x: x * 4,
    "aplicaciones_practicas": lambda x: x * 2.5,
}


# 3. Interfaz Gráfica (HTML + CSS conectado a variables de buk_brand.py)
HTML_INTERFAZ = """
<!DOCTYPE html>
<html lang="es" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bukplay SST · Calculadora</title>
    <style>
        /* Inyección automática de Urbanist, paleta Buk 2026 y temas claro/oscuro */
        {{ brand_css | safe }}

        * {
            box-sizing: border-box;
        }

        body {
            background-color: var(--buk-bg);
            color: var(--buk-text);
            font-family: var(--buk-font);
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            margin: 0;
            padding: 20px;
            transition: background-color 0.25s ease, color 0.25s ease;
        }

        /* Botón superior derecho para alternar entre modo claro (#FFFFFF) y oscuro (#04047F) */
        .theme-toggle {
            position: fixed;
            top: 18px;
            right: 22px;
            background-color: var(--buk-surface);
            color: var(--buk-text);
            border: 1px solid var(--buk-border);
            border-radius: var(--buk-radius-control);
            padding: 8px 14px;
            font-family: var(--buk-font);
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            z-index: 100;
        }

        /* Tarjeta principal con estética Buk (.buk-card: esquinas 24px y borde azul) */
        .card {
            background-color: var(--buk-surface);
            color: var(--buk-text);
            padding: 36px;
            border-radius: var(--buk-radius-card);
            border: 1.5px solid var(--buk-border);
            width: 100%;
            max-width: 440px;
            position: relative;
        }

        .header-container {
            text-align: center;
            margin-bottom: 28px;
        }

        h2 {
            color: var(--buk-primary);
            margin: 0 0 14px 0;
            font-size: 40px;
            font-weight: 600; /* Urbanist SemiBold según guía Buk */
            line-height: 0.95;
            letter-spacing: -0.02em;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
        }

        h2 span.sst-badge {
            background-color: var(--buk-primary);
            color: var(--buk-on-primary);
            font-size: 16px;
            padding: 6px 12px;
            border-radius: var(--buk-radius-control);
            font-weight: 600;
            letter-spacing: 0.04em;
        }

        .mascota {
            width: 130px;
            height: auto;
            border-radius: 50%;
            background-color: #FFFFFF;
            border: 2px solid var(--buk-border);
            padding: 4px;
        }

        p.subtitle {
            color: var(--buk-text-muted);
            font-size: 15px;
            text-align: center;
            margin: 12px 0 0 0;
            font-weight: 400;
        }

        .group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: var(--buk-text);
            font-size: 14px;
        }

        select, input {
            width: 100%;
            padding: 13px 14px;
            border: 1.5px solid var(--buk-border);
            border-radius: var(--buk-radius-control);
            font-family: var(--buk-font);
            font-size: 15px;
            color: var(--buk-text);
            background-color: var(--buk-bg);
            font-weight: 400;
            transition: box-shadow 0.2s ease;
        }

        select:focus, input:focus {
            outline: none;
            box-shadow: 0 0 0 3px rgba(0, 89, 255, 0.2);
        }

        /* Caja de resultado: usa el par primario oficial de Buk con contraste garantizado */
        .result-box {
            background-color: var(--buk-primary);
            color: var(--buk-on-primary);
            padding: 22px;
            border-radius: var(--buk-radius-control);
            text-align: center;
            margin-top: 24px;
        }

        .result-box label {
            color: var(--buk-on-primary);
            font-weight: 600;
            margin-bottom: 6px;
            text-transform: uppercase;
            font-size: 11px;
            letter-spacing: 0.08em;
            opacity: 0.9;
        }

        .result-box span {
            display: block;
            font-size: 42px;
            font-weight: 600;
            line-height: 1;
            color: var(--buk-on-primary);
        }

        /* Pie de página fijo en la esquina inferior izquierda */
        .footer {
            position: fixed;
            bottom: 15px;
            left: 25px;
            font-family: var(--buk-font);
            font-size: 14px;
            font-weight: 600;
            color: var(--buk-text);
            background-color: var(--buk-surface);
            border: 1px solid var(--buk-border);
            padding: 5px 12px;
            border-radius: var(--buk-radius-control);
            z-index: 100;
        }
    </style>
</head>
<body>

<button type="button" class="theme-toggle" id="btnTema">🌙 Modo oscuro</button>

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

<div class="footer">Autoría: Daniela Puig</div>

<script>
    const selectRecurso = document.getElementById('tipoRecurso');
    const inputCantidad = document.getElementById('cantidad');
    const labelInsumo = document.getElementById('labelInsumo');
    const txtResultado = document.getElementById('resultado');
    const btnTema = document.getElementById('btnTema');

    // Alterna el atributo data-theme que escucha buk_brand.css()
    btnTema.addEventListener('click', () => {
        const html = document.documentElement;
        const esOscuro = html.getAttribute('data-theme') === 'dark';
        html.setAttribute('data-theme', esOscuro ? 'light' : 'dark');
        btnTema.textContent = esOscuro ? '🌙 Modo oscuro' : '☀️ Modo claro';
    });

    async function enviarDatosAPython() {
        const recurso = selectRecurso.value;
        const cantidad = Math.max(0, parseFloat(inputCantidad.value) || 0);

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

    // Inicializa la etiqueta y el cálculo al cargar la página
    enviarDatosAPython();
</script>

</body>
</html>
"""


# 4. Ruta principal
@app.route("/")
def inicio():
    return render_template_string(HTML_INTERFAZ, brand_css=css("light"))


# 5. Ruta API con validación básica de entrada
@app.route("/api/calcular", methods=["POST"])
def api_calcular():
    datos = request.get_json(silent=True) or {}
    tipo_recurso = str(datos.get("tipo_recurso", "")).lower()

    try:
        cantidad = max(0.0, float(datos.get("cantidad", 0)))
    except (TypeError, ValueError):
        return jsonify({"success": False, "error": "Cantidad inválida"}), 400

    if tipo_recurso in FORMULAS:
        tiempo_calculado = FORMULAS[tipo_recurso](cantidad)
        tiempo_formateado = formatear_tiempo(tiempo_calculado)
        return jsonify({
            "success": True,
            "tiempo_formateado": tiempo_formateado,
        })

    return jsonify({"success": False, "error": "Recurso no válido"}), 400


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True, port=8080)

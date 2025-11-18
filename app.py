from flask import Flask, render_template, request
import json

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query")
    paginas = int(request.form.get("paginas", 1))
    
    if not query:
        return render_template(
            "resultado.html",
            query=query,
            resultados=[],
            total=0,
            error="Por favor ingresa una palabra clave"
        )
    
    try:
        # Resultados de demostración - Scraping será integrado próximamente
        resultados = [
            {
                'titulo': f'Posición {i} - {query}',
                'empresa': f'Empresa Ejemplo {i}',
                'url': '#',
                'fuente': 'Demo',
                'tipo': 'Publicación de empleo'
            }
            for i in range(1, min(paginas * 5 + 1, 11))
        ]
        
        return render_template(
            "resultado.html",
            query=query,
            resultados=resultados,
            total=len(resultados)
        )
    
    except Exception as e:
        return render_template(
            "resultado.html",
            query=query,
            resultados=[],
            total=0,
            error=f"Error durante la búsqueda: {str(e)}"
        )

if __name__ == "__main__":
    app.run(debug=True)

from flask import Flask, render_template, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import re
from datetime import datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

# Simulación de scraper para Indeed
def scrape_indeed(query, pages=1):
    """
    Scraper simplificado para Indeed.
    Por limitaciones de scraping, retorna datos de ejemplo realistas.
    """
    try:
        results = []
        
        # Datos de ejemplo - en producción, usar Selenium o API válida
        sample_jobs = [
            {
                "title": f"Especialista en {query.upper()} - Buenos Aires",
                "company": "Tech Argentina SA",
                "location": "Buenos Aires, CABA",
                "salary": "$80.000 - $120.000",
                "description": f"Buscamos profesional con experiencia en {query}",
                "link": "https://indeed.com/jobs",
                "source": "Indeed"
            },
            {
                "title": f"Developer {query.upper()} Senior",
                "company": "Innovation Labs",
                "location": "Córdoba",
                "salary": "$100.000 - $150.000",
                "description": f"Empresa en crecimiento busca {query} senior",
                "link": "https://indeed.com/jobs",
                "source": "Indeed"
            }
        ]
        
        # Repetir resultados según páginas solicitadas
        for page in range(pages):
            for job in sample_jobs:
                results.append({
                    **job,
                    "page": page + 1,
                    "retrieved_at": datetime.now().isoformat()
                })
        
        return results
    except Exception as e:
        return {"error": str(e)}

# Simulación de scraper para LinkedIn
def scrape_linkedin(query, pages=1):
    """
    Scraper simplificado para LinkedIn.
    Por limitaciones de ToS, retorna datos de ejemplo realistas.
    """
    try:
        results = []
        
        sample_jobs = [
            {
                "title": f"Analista {query.upper()}",
                "company": "Enterprise Solutions",
                "location": "La Plata",
                "salary": "$70.000 - $100.000",
                "description": f"Posición de {query} en empresa líder del sector",
                "link": "https://linkedin.com/jobs",
                "source": "LinkedIn"
            },
            {
                "title": f"{query.upper()} Engineer",
                "company": "Digital Transformation Co",
                "location": "Mendoza",
                "salary": "$90.000 - $130.000",
                "description": f"Ingeniero/a con expertise en {query} requerido/a",
                "link": "https://linkedin.com/jobs",
                "source": "LinkedIn"
            }
        ]
        
        for page in range(pages):
            for job in sample_jobs:
                results.append({
                    **job,
                    "page": page + 1,
                    "retrieved_at": datetime.now().isoformat()
                })
        
        return results
    except Exception as e:
        return {"error": str(e)}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/buscar", methods=["POST"])
def buscar():
    try:
        query = request.form.get("query", "").strip()
        paginas = int(request.form.get("paginas", 1))
        
        # Validación básica
        if not query:
            return render_template("resultado.html", query=query, resultados=[], total=0, error="Por favor ingresa una palabra clave")
        
        if paginas < 1 or paginas > 10:
            paginas = 1
        
        # Scrapear desde ambas fuentes
        resultados_indeed = scrape_indeed(query, paginas)
        resultados_linkedin = scrape_linkedin(query, paginas)
        
        # Combinar resultados
        resultados = []
        if isinstance(resultados_indeed, list):
            resultados.extend(resultados_indeed)
        if isinstance(resultados_linkedin, list):
            resultados.extend(resultados_linkedin)
        
        # Log de búsqueda (solo para debugging)
        print(f"[{datetime.now()}] Búsqueda: {query} | Páginas: {paginas} | Resultados: {len(resultados)}")
        
        return render_template(
            "resultado.html",
            query=query,
            resultados=resultados,
            total=len(resultados)
        )
    
    except ValueError:
        return render_template("resultado.html", query="", resultados=[], total=0, error="Número de páginas inválido")
    except Exception as e:
        print(f"Error en buscar: {str(e)}")
        return render_template("resultado.html", query="", resultados=[], total=0, error=f"Error: {str(e)}")

@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404

@app.errorhandler(500)
def server_error(error):
    return {"error": "Error interno del servidor"}, 500

if __name__ == "__main__":
    app.run(debug=False)

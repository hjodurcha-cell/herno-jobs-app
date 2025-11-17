from flask import Flask, render_template, request
import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import quote
import time
import random

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

def get_headers():
    """Retorna headers para evitar bloqueos"""
    headers = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    ]
    return {'User-Agent': random.choice(headers)}

def scrape_indeed(query, pages=1):
    """Scrape jobs desde Indeed Argentina"""
    results = []
    try:
        for page in range(pages):
            url = f"https://ar.indeed.com/jobs?q={quote(query)}&start={page*10}"
            response = requests.get(url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            jobs = soup.find_all('div', class_='job_seen')
            
            for job in jobs:
                try:
                    title_elem = job.find('h2', class_='jobTitle')
                    title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                    
                    company_elem = job.find('span', class_='companyName')
                    company = company_elem.get_text(strip=True) if company_elem else 'N/A'
                    
                    location_elem = job.find('div', class_='companyLocation')
                    location = location_elem.get_text(strip=True) if location_elem else 'N/A'
                    
                    link_elem = job.find('h2').find('a')
                    link = 'https://ar.indeed.com' + link_elem['href'] if link_elem else '#'
                    
                    results.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'Indeed Argentina'
                    })
                except:
                    continue
            
            time.sleep(random.uniform(1, 3))
    except Exception as e:
        print(f"Error en Indeed: {e}")
    
    return results

def scrape_linkedin(query, pages=1):
    """Scrape jobs desde LinkedIn Argentina"""
    results = []
    try:
        # Intentar scraping directo de LinkedIn
        url = f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location=Argentina"
        
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # LinkedIn tiene estructura compleja, intentar parsear posteos
        job_cards = soup.find_all('div', class_='job-card')
        
        if not job_cards:
            # Si no encuentra con 'job-card', intentar con 'jobs-search'            
            job_cards = soup.find_all('div', {'class': 'base-card'})
        
        for i, card in enumerate(job_cards[:10]):  # Primeros 10
            try:
                title_elem = card.find('h3', class_='base-search-card__title')
                title = title_elem.get_text(strip=True) if title_elem else 'N/A'
                
                company_elem = card.find('h4', class_='base-search-card__subtitle')
                company = company_elem.get_text(strip=True) if company_elem else 'N/A'
                
                location_elem = card.find('span', class_='job-search-card__location')
                location = location_elem.get_text(strip=True) if location_elem else 'Argentina'
                
                link_elem = card.find('a', class_='base-card__full-link')
                link = link_elem['href'] if link_elem else url
                
                if title != 'N/A' and company != 'N/A':
                    results.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': link,
                        'source': 'LinkedIn'
                    })
            except:
                continue
        
        # Si no se encontraron resultados, devolver link de búsqueda
        if not results:
            results.append({
                'title': f'Buscar "{query}" en LinkedIn',
                'company': 'LinkedIn',
                'location': 'Argentina',
                'link': url,
                'source': 'LinkedIn Search Link'
            })
    except Exception as e:
        print(f"Error en LinkedIn: {e}")
        # Fallback: devolver link de búsqueda
        results.append({
            'title': f'Buscar "{query}" en LinkedIn',
            'company': 'LinkedIn',
            'location': 'Argentina',
            'link': f"https://www.linkedin.com/jobs/search/?keywords={quote(query)}&location=Argentina",
            'source': 'LinkedIn Search Link'
        })
    
    return results

@app.route("/buscar", methods=["POST"])
def buscar():
    query = request.form.get("query")
    paginas = int(request.form.get("paginas", 1))
    
    try:
        # Obtener resultados de Indeed
        indeed_results = scrape_indeed(query, paginas)
        # Obtener resultados de LinkedIn
        linkedin_results = scrape_linkedin(query, paginas)
        # Combinar resultados
        resultados = indeed_results + linkedin_results
        
        if not resultados:
            resultados = [{
                'title': f'No se encontraron resultados para "{query}"',
                'company': 'Sistema',
                'location': 'Argentina',
                'link': '#',
                'source': 'Sistema'
            }]
    except Exception as e:
        return f"<h2>Error en la búsqueda:</h2><pre>{str(e)}</pre>"
    
    return render_template(
        "resultado.html",
        query=query,
        resultados=resultados,
        titulo=f"Resultados - {query}"
    )

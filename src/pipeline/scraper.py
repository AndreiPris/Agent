#!/usr/bin/env python3
"""
XOFlowers Website Scraper
Sarcina: Extrage toate produsele de pe xoflowers.md și le salvează în products.json

Autor: Echipa XOFlowers AI, Principal: Vladimir (Scraping & Structurare)
Data: 2025
"""

import requests
from bs4 import BeautifulSoup
import json
import time
import logging
from typing import List, Dict, Optional
from urllib.parse import urljoin, urlparse
import re

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class XOFlowersScraper:
    """
    Scraper pentru site-ul XOFlowers.md
    Extrage informații despre produse: nume, preț, imagine, link, categorie
    """
    
    def __init__(self, base_url: str = "https://xoflowers.md"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.products = []
        
    def get_page(self, url: str) -> Optional[BeautifulSoup]:
        """Obține și parsează o pagină web"""
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Eroare la accesarea paginii {url}: {e}")
            return None
    
    def extract_product_info(self, product_element, category: str = "General") -> Optional[Dict]:
        """
        Extrage informațiile despre un produs din elementul HTML
        """
        try:
            # Extractors - adaptează în funcție de structura reală a site-ului
            title_elem = product_element.find(['h2', 'h3', '.product-title', '.title'])
            price_elem = product_element.find(['.price', '.cost', '.amount'])
            image_elem = product_element.find('img')
            link_elem = product_element.find('a')
            
            # Numele produsului
            title = title_elem.get_text(strip=True) if title_elem else "Produs fără nume"
            
            # Prețul - extrage numerele din text
            price_text = price_elem.get_text(strip=True) if price_elem else "0"
            price_match = re.search(r'(\\d+(?:\\.\\d+)?)', price_text.replace(',', '.'))
            price = float(price_match.group(1)) if price_match else 0.0
            
            # Imaginea
            image_url = ""
            if image_elem:
                image_src = image_elem.get('src') or image_elem.get('data-src')
                if image_src:
                    image_url = urljoin(self.base_url, image_src)
            
            # Linkul către produs
            product_url = ""
            if link_elem:
                href = link_elem.get('href')
                if href:
                    product_url = urljoin(self.base_url, href)
            
            # Descripția (dacă există)
            desc_elem = product_element.find(['.description', '.desc', 'p'])
            description = desc_elem.get_text(strip=True) if desc_elem else ""
            
            return {
                "id": f"product_{len(self.products) + 1:04d}",
                "title": title,
                "description": description,
                "price": price,
                "currency": "MDL",
                "category": category,
                "image_url": image_url,
                "product_url": product_url,
                "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
        except Exception as e:
            logger.error(f"Eroare la extragerea informațiilor despre produs: {e}")
            return None
    
    def scrape_category_page(self, category_url: str, category_name: str) -> List[Dict]:
        """Extrage toate produsele dintr-o categorie"""
        logger.info(f"Scraping categoria: {category_name} de la {category_url}")
        
        soup = self.get_page(category_url)
        if not soup:
            return []
        
        # Selectori pentru produse - adaptează în funcție de structura site-ului
        product_selectors = [
            '.product-item',
            '.product',
            '.product-card',
            '.item',
            '[data-product]'
        ]
        
        products_found = []
        
        for selector in product_selectors:
            product_elements = soup.select(selector)
            if product_elements:
                logger.info(f"Găsite {len(product_elements)} produse cu selectorul {selector}")
                
                for element in product_elements:
                    product_info = self.extract_product_info(element, category_name)
                    if product_info and product_info['title'] != "Produs fără nume":
                        products_found.append(product_info)
                        
                break  # Folosește primul selector care găsește produse
        
        # Paginare - caută linkuri către pagina următoare
        next_page = soup.find(['a'], string=re.compile(r'Next|Următoarea|»|>'))
        if next_page and next_page.get('href'):
            next_url = urljoin(category_url, next_page['href'])
            logger.info(f"Găsită pagina următoare: {next_url}")
            products_found.extend(self.scrape_category_page(next_url, category_name))
        
        return products_found
    
    def discover_categories(self) -> List[Dict[str, str]]:
        """
        Descoperă categoriile de produse de pe site
        """
        logger.info("Descoperind categoriile de produse...")
        
        # Categorii cunoscute pentru XOFlowers
        known_categories = [
            {"name": "Buchete", "url": f"{self.base_url}/bouquets/"},
            {"name": "Trandafiri", "url": f"{self.base_url}/roses/"},
            {"name": "Bujori", "url": f"{self.base_url}/peonies/"},
            {"name": "Premium", "url": f"{self.base_url}/premium/"},
            {"name": "Chando", "url": f"{self.base_url}/chando/"},
            {"name": "Accesorii", "url": f"{self.base_url}/accessories/"},
            {"name": "Cadouri", "url": f"{self.base_url}/gifts/"},
        ]
        
        # Încearcă să descoperi categorii din meniul principal
        soup = self.get_page(self.base_url)
        if soup:
            menu_links = soup.find_all('a', href=True)
            for link in menu_links:
                href = link['href']
                text = link.get_text(strip=True)
                
                # Filtrează linkurile care par să fie categorii
                if (len(text) > 3 and 
                    any(keyword in href.lower() for keyword in ['category', 'cat', 'products', 'flowers']) and
                    not any(skip in href.lower() for skip in ['admin', 'login', 'cart', 'checkout'])):
                    
                    category_url = urljoin(self.base_url, href)
                    known_categories.append({"name": text, "url": category_url})
        
        return known_categories
    
    def scrape_all_products(self) -> List[Dict]:
        """
        Metodă principală - extrage toate produsele de pe site
        """
        logger.info("🌸 Începând scraping-ul complet al XOFlowers...")
        
        # Descoperă categoriile
        categories = self.discover_categories()
        
        all_products = []
        
        for category in categories:
            try:
                logger.info(f"📂 Procesând categoria: {category['name']}")
                category_products = self.scrape_category_page(category['url'], category['name'])
                all_products.extend(category_products)
                
                # Pauză între categorii pentru a fi respectuoși
                time.sleep(2)
                
            except Exception as e:
                logger.error(f"Eroare la procesarea categoriei {category['name']}: {e}")
                continue
        
        # Elimină duplicatele pe baza URL-ului
        unique_products = []
        seen_urls = set()
        
        for product in all_products:
            if product['product_url'] not in seen_urls:
                unique_products.append(product)
                seen_urls.add(product['product_url'])
        
        logger.info(f"✅ Scraping complet! Găsite {len(unique_products)} produse unice")
        return unique_products
    
    def save_to_json(self, products: List[Dict], filename: str = "data/products.json"):
        """Salvează produsele în fișierul JSON"""
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(products, f, ensure_ascii=False, indent=2)
            logger.info(f"💾 Produsele au fost salvate în {filename}")
        except Exception as e:
            logger.error(f"Eroare la salvarea în {filename}: {e}")

def main():
    """Funcția principală"""
    scraper = XOFlowersScraper()
    
    # Extrage toate produsele
    products = scraper.scrape_all_products()
    
    if products:
        # Salvează în JSON
        scraper.save_to_json(products)
        
        # Afișează statistici
        categories = list(set(p['category'] for p in products))
        print(f"\\n📊 STATISTICI SCRAPING:")
        print(f"   🌸 Total produse: {len(products)}")
        print(f"   📁 Categorii găsite: {len(categories)}")
        print(f"   💰 Preț mediu: {sum(p['price'] for p in products if p['price'] > 0) / len([p for p in products if p['price'] > 0]):.2f} MDL")
        
        for category in categories:
            count = len([p for p in products if p['category'] == category])
            print(f"      - {category}: {count} produse")
    
    else:
        print("❌ Nu s-au găsit produse. Verifică structura site-ului.")

if __name__ == "__main__":
    main()

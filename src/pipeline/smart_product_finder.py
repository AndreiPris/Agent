#!/usr/bin/env python3
"""
XOFlowers Smart Product Finder cu DrissionPage
1. Testează linkul din CSV cu browser real
2. Dacă nu funcționează, testează multiple variante
3. Caută pe site cu browser automation
4. Înlocuiește cu URL funcțional
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup, Tag
import time
import re
from urllib.parse import urljoin, quote
from typing import Optional, Dict, List
from DrissionPage import ChromiumPage, ChromiumOptions
import random

import re

class SmartProductFinder:
    def __init__(self):
        self.base_url = "https://xoflowers.md"
        self.base_url_en = "https://xoflowers.md/en"
        self.search_url_ro = "https://xoflowers.md/search"
        self.search_url_en = "https://xoflowers.md/en/search"
        
        # Configurare DrissionPage
        self.options = ChromiumOptions()
        self.options.headless(False)  # Vizibil pentru debug
        self.options.set_argument('--no-sandbox')
        self.options.set_argument('--disable-dev-shm-usage')
        self.options.set_argument('--disable-gpu')
        self.options.set_user_agent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
        
        # Inițializare browser
        self.page = None
        self.init_browser()
        
        # Session pentru backup
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.working_products: List[Dict] = []
        self.fixed_products: List[Dict] = []
        self.not_found_products: List[Dict] = []
        
    def init_browser(self):
        """Inițializează browserul DrissionPage"""
        try:
            self.page = ChromiumPage(addr_or_opts=self.options)
            print("✅ Browser DrissionPage inițializat cu succes")
        except Exception as e:
            print(f"❌ Eroare la inițializarea browserului: {e}")
            self.page = None
            
    def close_browser(self):
        """Închide browserul"""
        if self.page:
            try:
                self.page.quit()
                print("✅ Browser închis")
            except:
                pass
        
    def test_original_url(self, url: str) -> bool:
        """Testează dacă URL-ul original funcționează cu DrissionPage"""
        if not url or url.strip() == '':
            return False
            
        if not self.page:
            print("    ❌ Browser nu este disponibil, folosesc requests")
            return self.test_url_with_requests(url)
            
        try:
            print(f"    🌐 Testez cu browser: {url[:60]}...")
            
            # Navighează la URL
            self.page.get(url, timeout=15)
            time.sleep(2)  # Așteaptă încărcarea
            
            # Verifică dacă s-a încărcat complet
            if not self.page.title:
                print("    ❌ Pagina nu s-a încărcat (fără title)")
                return False
            
            title = self.page.title.lower()
            page_source = self.page.html.lower()
            
            print(f"    📄 Title: {self.page.title[:50]}...")
            
            # VERIFICARE 1: Nu e pagină de eroare
            error_indicators = [
                "ne pare rău, pagina pe care ați căutat-o nu a fost găsită",
                "we are sorry, the page you requested was not found",
                "page not found",
                "404 error",
                "pagina nu a fost găsită",
                "sorry, the page",
                "page you requested was not found",
                "error 404",
                "not found"
            ]
            
            for error in error_indicators:
                if error in title or error in page_source:
                    print(f"    ❌ Pagină de eroare detectată: {error[:30]}...")
                    return False
            
            # VERIFICARE 2: Are conținut de produs real
            product_content_indicators = [
                'descriere', 'description', 'caracteristici', 'ingredients', 'ingrediente',
                'ml', 'dimensiune', 'size', 'culoare', 'color', 'material',
                'preț', 'price', 'lei', 'mdl', 'cost', 'buy', 'cumpără',
                'add to cart', 'adaugă în coș', 'comandă', 'order',
                'disponibil', 'available', 'stoc', 'stock', 'livrare', 'delivery'
            ]
            
            found_content = [ind for ind in product_content_indicators if ind in page_source]
            
            if len(found_content) < 3:
                print(f"    ❌ Conținut insuficient de produs (găsit doar {len(found_content)} indicatori)")
                return False
            
            # VERIFICARE 3: Title-ul trebuie să fie specific
            generic_titles = [
                'home', 'acasă', 'category', 'categorie', 
                'bouquets', 'baskets', 'search', 'căutare',
                'error', 'eroare', 'not found'
            ]
            
            title_valid = True
            if any(generic in title for generic in generic_titles):
                print(f"    ❌ Title generic detectat")
                title_valid = False
            
            # Verifică dacă title-ul conține cuvinte relevante pentru produs
            product_words = ['aroma', 'bouquet', 'basket', 'box', 'deffuser', 'flower', 'diffuser']
            has_product_words = any(word in title for word in product_words)
            
            if not has_product_words:
                print(f"    ⚠️ Title nu conține cuvinte specifice de produs")
            
            # VERIFICARE 4: Structura HTML de produs
            html_indicators = [
                'single-product', 'product-single', 'product-detail',
                'product-page', 'item-page', '"@type": "product"',
                'schema.org/product', 'product-description', 'product-info'
            ]
            
            found_html = [ind for ind in html_indicators if ind in page_source]
            
            # VERIFICARE 5: Nu e categorie (prea multe link-uri de produse)
            product_links = page_source.count('href=')
            is_category = product_links > 100
            
            if is_category:
                print(f"    ❌ Pare categorie ({product_links} link-uri)")
                return False
            
            # VERIFICARE 6: Verifică elemente vizuale specifice
            try:
                # Caută butoane de cumpărare
                buy_buttons = self.page.eles('xpath://button[contains(text(), "Buy") or contains(text(), "Cumpără") or contains(text(), "Add to cart")]')
                price_elements = self.page.eles('xpath://*[contains(text(), "lei") or contains(text(), "MDL") or contains(@class, "price")]')
                
                has_buy_elements = len(buy_buttons) > 0 or len(price_elements) > 0
                
                if has_buy_elements:
                    print(f"    ✅ Elemente de cumpărare detectate (butoane: {len(buy_buttons)}, preturi: {len(price_elements)})")
                else:
                    print(f"    ⚠️ Nu am găsit elemente clare de cumpărare")
                    
            except Exception as e:
                print(f"    ⚠️ Eroare la verificarea elementelor vizuale: {e}")
                has_buy_elements = False
            
            # DECIZIE FINALĂ
            has_valid_content = len(found_content) >= 3
            has_valid_structure = len(found_html) > 0 or has_product_words
            is_valid_product = has_valid_content and has_valid_structure and title_valid and not is_category
            
            if is_valid_product:
                print(f"    ✅ Pagină de produs validă!")
                print(f"        - Conținut: {len(found_content)} indicatori")
                print(f"        - Structură HTML: {len(found_html)} indicatori")
                print(f"        - Title valid: {title_valid}")
                print(f"        - Elemente cumpărare: {has_buy_elements}")
                return True
            else:
                print(f"    ❌ Nu pare pagină de produs validă")
                print(f"        - Conținut: {len(found_content)}/3 minim")
                print(f"        - Structură HTML: {len(found_html)} indicatori")
                print(f"        - Title valid: {title_valid}")
                print(f"        - Este categorie: {is_category}")
                return False
                
        except Exception as e:
            print(f"    ❌ Eroare browser pentru {url}: {e}")
            # Fallback la requests
            return self.test_url_with_requests(url)
    
    def test_url_with_requests(self, url: str) -> bool:
        """Fallback cu requests dacă browserul nu funcționează"""
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                content = response.text.lower()
                
                # Verificări de bază
                error_indicators = [
                    "page not found", "404 error", "pagina nu a fost găsită"
                ]
                
                for error in error_indicators:
                    if error in content:
                        return False
                
                product_indicators = ['preț', 'price', 'lei', 'buy', 'cumpără']
                found = [ind for ind in product_indicators if ind in content]
                
                return len(found) >= 2
            return False
        except:
            return False
    
    def test_url_variants_enhanced(self, original_url: str) -> Optional[str]:
        """Testează multiple variante ale URL-ului cu DrissionPage"""
        if not original_url:
            return None
        
        print(f"    🔄 Testez variante extinse pentru: {original_url}")
        
        # Generează toate variantele posibile
    def generate_all_url_variants(self, original_url: str) -> List[str]:
        """Generează toate variantele posibile de URL-uri pentru testare, acoperind toate tiparele identificate în analiză."""
        base_url = "https://xoflowers.md/"
        variants = []


        # 1. Prefixuri lipsă: with-flowers, with-roses, with-hydrangea
        def add_prefix_variants(url, prefix, patterns):
            for pat in patterns:
                if pat in url:
                    name_part = url.split(pat)[-1].rstrip('/')
                    variants.append(f"{base_url}{prefix}{name_part}")
                    variants.append(f"{base_url}en/{prefix}{name_part}")

        add_prefix_variants(original_url, 'box-with-flowers-', ['/box-'])
        add_prefix_variants(original_url, 'basket-with-flowers-', ['/basket-'])
        add_prefix_variants(original_url, 'box-with-roses-', ['/box-roses-', '/box-little-miss'])
        add_prefix_variants(original_url, 'basket-with-roses-', ['/basket-poma-rosa', '/basket-azalia'])
        add_prefix_variants(original_url, 'box-with-hydrangea-', ['box-hydrangea-'])

        # 1b. Adaugă variante cu/ fără articolul "the", "a", "an" la început sau între cuvinte
        def add_article_variants(url):
            articles = ["the", "a", "an"]
            url_parts = url.replace(base_url, "").split("-")
            for i in range(len(url_parts)):
                for art in articles:
                    # Adaugă articolul înainte de fiecare cuvânt
                    new_parts = url_parts[:i] + [art] + url_parts[i:]
                    variant = base_url + "-".join(new_parts)
                    variants.append(variant)
            # Elimină articolele dacă există
            for art in articles:
                if f"-{art}-" in url:
                    variants.append(url.replace(f"-{art}-", "-"))
                if url.startswith(base_url + art + "-"):
                    variants.append(url.replace(base_url + art + "-", base_url))

        add_article_variants(original_url)

        # 1c. Adaugă/ elimină prepoziții "of", "in", "with", "and" între cuvinte
        def add_preposition_variants(url):
            preps = ["of", "in", "with", "and"]
            url_parts = url.replace(base_url, "").split("-")
            for i in range(1, len(url_parts)):
                for prep in preps:
                    # Adaugă prepoziția între cuvinte
                    new_parts = url_parts[:i] + [prep] + url_parts[i:]
                    variant = base_url + "-".join(new_parts)
                    variants.append(variant)
            # Elimină prepozițiile dacă există
            for prep in preps:
                if f"-{prep}-" in url:
                    variants.append(url.replace(f"-{prep}-", "-"))

        add_preposition_variants(original_url)

        # 1d. Sinonime și corecții subtile de cuvinte
        synonym_map = {
            "bouquet": ["buchet", "bouqet", "bouqeuet"],
            "buchet": ["bouquet"],
            "box": ["cutie"],
            "basket": ["cos"],
            "glints": ["glimpses", "glimpse"],
            "glimpses": ["glints"],
            "hanna": ["hannah"],
            "hannah": ["hanna"],
            "paints": ["paint"],
            "paint": ["paints"],
        }
        for word, syns in synonym_map.items():
            if word in original_url:
                for syn in syns:
                    variants.append(original_url.replace(word, syn))

        # 12. Prepoziții lipsă (ex: cloud-tenderness → cloud-of-tenderness)
        prepozitii = [
            ('cloud-tenderness', 'cloud-of-tenderness'),
            ('garden-eden', 'garden-of-eden'),
            ('princess-heart', 'princess-of-heart'),
            ('basket-princess-heart', 'composition-in-a-basket-princess-of-heart'),
            ('basket-garden-eden', 'basket-garden-of-eden'),
            ('bouquet-cloud-tenderness', 'bouquet-cloud-of-tenderness'),
        ]
        for pat, real in prepozitii:
            if pat in original_url:
                variants.append(original_url.replace(pat, real))

        # 13. Structuri complexe pentru compoziții
        if 'basket-princess-heart' in original_url:
            variants.append(f"{base_url}composition-in-a-basket-princess-of-heart")
        if 'basket-glints-summer' in original_url:
            variants.append(f"{base_url}basket-with-flowers-glimpses-of-summer")
        if 'basket-glimpses-summer' in original_url:
            variants.append(f"{base_url}basket-with-flowers-glints-of-summer")

        # 2. Articolul "the" lipsă
        if re.search(r'romance-morning', original_url):
            variants.append(f"{base_url}bouquet-the-romance-of-the-morning")
        if re.search(r'magnificence-roses', original_url):
            variants.append(f"{base_url}basket-with-flowers-the-magnificence-of-roses")
        if re.search(r'lilac-meadow', original_url):
            variants.append(f"{base_url}box-with-flowers-the-lilac-meadow")

        # 3. Structuri speciale
        if 'cachepot-' in original_url:
            name_part = original_url.split('cachepot-')[-1].rstrip('/')
            variants.append(f"{base_url}composition-in-a-cachepot-{name_part}")
        if 'basket-i-miss-you' in original_url:
            variants.append(f"{base_url}flowers-in-basket-i-miss-you")
        if 'box-eleanor' in original_url:
            variants.append(f"{base_url}flower-box-eleanor")

        # 4. Corecții de nume
        if 'montreal-mix' in original_url:
            variants.append(f"{base_url}bouquet-mondial-mix")
        if re.search(r'fresh-lily-35ml', original_url):
            variants.append(f"{base_url}aroma-deffuser-amethyst-love-mini-fresh-lily-35-ml")

        # 5. Prefixuri de tip produs
        if 'difuzor-de-aroma-floral-intimacy-yellow-10ml' in original_url:
            variants.append(f"{base_url}aroma-deffuser-floral-intimacy-yellow-10ml")
        if 'difuzor-de-aroma-royal-guard-10ml' in original_url:
            variants.append(f"{base_url}difuzor-de-aroma-pentru-automobil-royal-guard-10ml")

        # 6. Versiuni alternative/redirectări
        if 'floral-intimacy-liliac-10ml' in original_url:
            variants.append(f"{base_url}en/aroma-deffuser-floral-intimacy-liliac-10ml")

        # 7. Sufixe și extensii
        if re.search(r'blue-sky/?$', original_url):
            variants.append(f"{base_url}bouquet-blue-sky/n/")

        # 8. Restul logicii existente (difuzoare, buchete, etc.)
        if '/difuzor-de-aroma-' in original_url:
            product_part = original_url.replace('https://xoflowers.md/difuzor-de-aroma-', '').rstrip('/')
            variants.extend([
                f"{base_url}aroma-deffuser-{product_part.replace('-10ml', '').replace('-35ml', '').replace('-100ml', '').replace('-200ml', '')}",
                f"{base_url}aroma-deffuser-{product_part}",
                f"{base_url}aroma-deffuser-{product_part.replace('ml', '-ml')}",
                f"{base_url}difuzor-aroma-{product_part}",
                f"{base_url}diffuser-{product_part}",
                f"{base_url}aroma-diffuser-{product_part}",
                f"{base_url}chando-{product_part}",
                f"{base_url}home-fragrance-{product_part}",
                f"{base_url}en/aroma-deffuser-{product_part}",
                f"{base_url}en/diffuser-{product_part}",
                f"{base_url}en/home-fragrance-{product_part}",
                f"{base_url}{product_part}",
                f"{base_url}product/{product_part}",
                f"{base_url}products/{product_part}",
            ])
        elif any(keyword in original_url for keyword in ['/bouquet-', '/basket-', '/box-', '/bouquet', '/basket']):
            product_part = original_url.replace('https://xoflowers.md/', '').rstrip('/')
            if 'buoquet' in original_url:
                corrected_url = original_url.replace('buoquet', 'bouquet')
                variants.append(corrected_url)
                base_part = corrected_url.replace('https://xoflowers.md/', '').rstrip('/')
            else:
                base_part = product_part
            # Generează variante cu /n/ la final pentru orice produs relevant
            for n_count in range(1, 16):
                n_pattern = "/n/" * n_count
                n_pattern = n_pattern.rstrip('/')
                variants.append(f"{base_url}{base_part}{'/' if n_pattern else ''}{n_pattern}")
            variants.append(f"{base_url}{base_part}")
            if '/bouquet-' in original_url:
                name_part = base_part.replace('bouquet-', '')
                base_variants = [
                    f"bouquet-{name_part}",
                    f"bouquet-with-flowers-{name_part}",
                    f"flower-bouquet-{name_part}",
                    f"buchet-{name_part}",
                ]
            elif '/basket-' in original_url:
                name_part = base_part.replace('basket-', '')
                base_variants = [
                    f"basket-{name_part}",
                    f"basket-with-flowers-{name_part}",
                    f"flower-basket-{name_part}",
                    f"cos-{name_part}",
                ]
            elif '/box-' in original_url:
                name_part = base_part.replace('box-', '')
                base_variants = [
                    f"box-{name_part}",
                    f"box-with-flowers-{name_part}",
                    f"flower-box-{name_part}",
                    f"cutie-{name_part}",
                ]
            else:
                base_variants = [base_part]
            for base_variant in base_variants:
                variants.append(f"{base_url}{base_variant}")
                for n_count in range(1, 13):
                    n_pattern = "/n/" * n_count
                    n_pattern = n_pattern.rstrip('/')
                    variants.append(f"{base_url}{base_variant}{'/' if n_pattern else ''}{n_pattern}")
                variants.append(f"{base_url}en/{base_variant}")

        # fallback pentru orice alt caz
        if not any(keyword in original_url for keyword in ['/bouquet-', '/basket-', '/box-', '/bouquet', '/basket', '/difuzor-de-aroma-']):
            product_part = original_url.replace('https://xoflowers.md/', '').rstrip('/')
            for n_count in range(1, 16):
                n_pattern = "/n/" * n_count
                n_pattern = n_pattern.rstrip('/')
                variants.append(f"{base_url}{product_part}{'/' if n_pattern else ''}{n_pattern}")
            variants.extend([
                f"{base_url}{product_part}",
                f"{base_url}en/{product_part}",
                f"{base_url}product/{product_part}",
                f"{base_url}en/product/{product_part}",
                f"{base_url}products/{product_part}",
                f"{base_url}en/products/{product_part}",
            ])

        # Elimină duplicate și păstrează ordinea
        unique_variants = []
        for variant in variants:
            if variant not in unique_variants and variant != original_url:
                unique_variants.append(variant)
        return unique_variants[:50]  # Limitează la 50 de variante pentru eficiență
            variants.extend([
                f"{base_url}{product_part}",
                f"{base_url}en/{product_part}",
                f"{base_url}product/{product_part}",
                f"{base_url}en/product/{product_part}",
                f"{base_url}products/{product_part}",
                f"{base_url}en/products/{product_part}",
            ])

        # Elimină duplicate și păstrează ordinea
        unique_variants = []
        for variant in variants:
            if variant not in unique_variants and variant != original_url:
                unique_variants.append(variant)
        return unique_variants[:50]  # Limitează la 50 de variante pentru eficiență
    
    def extract_search_terms(self, product_name: str) -> List[str]:
        """Extrage termenii de căutare din numele produsului"""
        search_terms = []
        
        # 1. Extrage numele din ghilimele
        quotes_match = re.search(r'"([^"]*)"', product_name)
        if quotes_match:
            search_terms.append(quotes_match.group(1))
        
        # 2. Extrage cuvinte cheie importante
        # Elimină cuvinte comune
        common_words = ['bouquet', 'basket', 'box', 'with', 'flowers', 'roses', 'buchet', 'cos', 'cutie', 'de', 'cu', 'și', 'sau']
        clean_name = re.sub(r'["\']', '', product_name)
        words = clean_name.split()
        important_words = [w for w in words if w.lower() not in common_words and len(w) > 2]
        
        # 3. Diferite combinații de cuvinte
        if important_words:
            # Prima 2-3 cuvinte importante
            search_terms.append(' '.join(important_words[:3]))
            # Primul cuvânt important
            search_terms.append(important_words[0])
            # Ultimul cuvânt important (adesea numele)
            if len(important_words) > 1:
                search_terms.append(important_words[-1])
        
        # 4. Numele complet fără cuvinte comune
        if important_words:
            search_terms.append(' '.join(important_words))
        
        # Elimină duplicate și filtrează
        unique_terms = []
        for term in search_terms:
            if term and len(term.strip()) > 2 and term not in unique_terms:
                unique_terms.append(term.strip())
        
        return unique_terms[:5]  # Max 5 termeni
    
    def search_product_by_name(self, product_name: str) -> Optional[Dict]:
        """Caută produsul pe site după numele/cuvintele cheie"""
        search_terms = self.extract_search_terms(product_name)
        
        print(f"    🔍 Termeni de căutare: {search_terms}")
        
        for term in search_terms:
            # Încearcă în română
            result = self.perform_search(term, 'ro')
            if result:
                print(f"    ✅ Găsit în română cu '{term}'")
                return result
            
            # Încearcă în engleză
            result = self.perform_search(term, 'en')
            if result:
                print(f"    ✅ Găsit în engleză cu '{term}'")
                return result
        
        # Dacă nu găsește prin search, încearcă prin categorii
        return self.search_in_categories(search_terms[0] if search_terms else product_name)
    
    def perform_search(self, search_term: str, language: str = 'ro') -> Optional[Dict]:
        """Efectuează căutarea pe site"""
        try:
            search_url = self.search_url_en if language == 'en' else self.search_url_ro
            
            # Încearcă GET
            search_params = {'q': search_term}
            response = self.session.get(search_url, params=search_params, timeout=10)
            
            if response.status_code == 200:
                result = self.parse_search_results(response.text, search_term, language)
                if result:
                    return result
            
            # Încearcă POST
            search_data = {'search': search_term}
            response = self.session.post(search_url, data=search_data, timeout=10)
            
            if response.status_code == 200:
                result = self.parse_search_results(response.text, search_term, language)
                if result:
                    return result
                
        except Exception as e:
            print(f"    ❌ Eroare search '{search_term}' în {language}: {e}")
            
        return None
    
    def parse_search_results(self, html_content: str, search_term: str, language: str) -> Optional[Dict]:
        """Analizează rezultatele căutării"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Selectori pentru linkurile de produse
            selectors = [
                'a[href*="/product/"]',
                'a[href*="/bouquet"]',
                'a[href*="/basket"]',
                'a[href*="/box"]',
                '.product-item a',
                '.search-result a',
                '.product a',
                'a[href*="xoflowers.md"]'
            ]
            
            for selector in selectors:
                links = soup.select(selector)
                for link in links:
                    if isinstance(link, Tag):
                        href = link.get('href')
                        if href and isinstance(href, str):
                            base_url = self.base_url_en if language == 'en' else self.base_url
                            full_url = urljoin(base_url, href)
                            
                            if self.is_valid_product_url(full_url):
                                title = link.get_text(strip=True) or ''
                                
                                # Verifică potrivirea și funcționalitatea
                                if self.matches_search_term(title, search_term) and self.test_original_url(full_url):
                                    return {
                                        'url': full_url,
                                        'title': title,
                                        'search_term': search_term,
                                        'method': f'search_{language}',
                                        'language': language
                                    }
            
        except Exception as e:
            print(f"    ❌ Eroare parsare rezultate: {e}")
            
        return None
    
    def search_in_categories(self, search_term: str) -> Optional[Dict]:
        """Caută în categoriile principale"""
        categories = ['/bouquets', '/baskets', '/boxes', '/roses', '/peonies']
        
        for category in categories:
            for language in ['ro', 'en']:
                try:
                    if language == 'en':
                        url = f"{self.base_url_en}{category}"
                    else:
                        url = f"{self.base_url}{category}"
                    
                    response = self.session.get(url, timeout=10)
                    
                    if response.status_code == 200:
                        result = self.search_in_category_page(response.text, search_term, category, language)
                        if result:
                            return result
                            
                except Exception:
                    continue
                    
        return None
    
    def search_in_category_page(self, html_content: str, search_term: str, category: str, language: str) -> Optional[Dict]:
        """Caută în pagina unei categorii"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            product_links = soup.find_all('a', href=True)
            
            for link in product_links:
                if isinstance(link, Tag):
                    href = link.get('href')
                    title = link.get_text(strip=True)
                    
                    if href and isinstance(href, str) and self.is_valid_product_url(href):
                        if self.matches_search_term(title, search_term):
                            base_url = self.base_url_en if language == 'en' else self.base_url
                            full_url = urljoin(base_url, href)
                            
                            if self.test_original_url(full_url):
                                return {
                                    'url': full_url,
                                    'title': title,
                                    'search_term': search_term,
                                    'method': f'category_{category}_{language}',
                                    'category': category,
                                    'language': language
                                }
        except Exception:
            pass
            
        return None
    
    def is_valid_product_url(self, url: str) -> bool:
        """Verifică dacă URL-ul pare a fi un produs valid"""
        invalid_patterns = [
            '/cart', '/checkout', '/login', '/register',
            '/contact', '/about', '/search', '/category'
        ]
        return not any(pattern in url.lower() for pattern in invalid_patterns)
    
    def matches_search_term(self, title: str, search_term: str) -> bool:
        """Verifică dacă titlul se potrivește cu termenul căutat"""
        if not title or not search_term:
            return False
            
        title_lower = title.lower()
        search_lower = search_term.lower()
        
        # Check direct
        if search_lower in title_lower:
            return True
        
        # Check cuvinte individuale
        search_words = search_lower.split()
        title_words = title_lower.split()
        
        matches = sum(1 for word in search_words if any(word in title_word for title_word in title_words))
        return matches >= max(1, len(search_words) // 2)
    
    def process_products(self, csv_file: str, max_products: Optional[int] = None):
        """Procesează produsele cu noua logică"""
        try:
            df = pd.read_csv(csv_file)
            print(f"✅ Încărcat {len(df)} produse din CSV")
            
            if max_products:
                df = df.head(max_products)
                print(f"🔍 Procesând primele {max_products} produse pentru test...")
            
            total = len(df)
            print("=" * 80)
            
            for idx, (_, row) in enumerate(df.iterrows(), 1):
                # Adaptare pentru noul format CSV
                if 'primary_text' in row:
                    product_name = str(row.get('primary_text', '')).strip()
                elif 'name' in row:
                    product_name = str(row.get('name', '')).strip()
                else:
                    product_name = str(row.get('chunk_id', '')).strip()
                
                original_url = str(row.get('url', '')).strip()
                category = str(row.get('category', ''))
                price = str(row.get('price', ''))
                
                if not product_name:
                    continue
                
                print(f"\n🔍 {idx}/{total}: {product_name[:50]}...")
                print(f"    🔗 URL original: {original_url[:60]}...")
                
                # PASUL 1: Testează URL-ul original
                if self.test_original_url(original_url):
                    print(f"    ✅ URL original funcționează!")
                    
                    self.working_products.append({
                        'original_name': product_name,
                        'url': original_url,
                        'title': product_name,
                        'category': category,
                        'price': price,
                        'status': 'original_working',
                        'method': 'original_url',
                        'found': True
                    })
                else:
                    print(f"    ❌ URL original nu funcționează")
                    
                    # PASUL 2: Testează variații sistematice de URL
                    print(f"    🔄 Testez variații de URL...")
                    url_variant = self.test_url_variants_enhanced(original_url)
                    
                    if url_variant:
                        print(f"    ✅ GĂSIT prin variație URL: {url_variant}")
                        
                        self.fixed_products.append({
                            'original_name': product_name,
                            'url': url_variant,
                            'title': product_name,
                            'original_url': original_url,
                            'category': category,
                            'price': price,
                            'status': 'fixed_url_variant',
                            'method': 'url_variant',
                            'found': True
                        })
                    else:
                        print(f"    🔍 Caut pe site prin nume...")
                        
                        # PASUL 3: Caută pe site dacă variațiile URL nu funcționează
                        result = self.search_product_by_name(product_name)
                        
                        if result:
                            print(f"    ✅ GĂSIT și FIXAT prin căutare: {result['url']}")
                            print(f"    📋 Metodă: {result['method']}")
                            
                            result.update({
                                'original_name': product_name,
                                'original_url': original_url,
                                'category': category,
                                'price': price,
                                'status': 'fixed_by_search',
                                'found': True
                            })
                            
                            self.fixed_products.append(result)
                        else:
                            print(f"    ❌ NU GĂSIT pe site")
                            
                            self.not_found_products.append({
                                'original_name': product_name,
                                'original_url': original_url,
                                'category': category,
                                'price': price,
                                'status': 'not_found',
                                'found': False
                            })
                
                # Progres la fiecare 25 de produse
                if idx % 25 == 0:
                    working_count = len(self.working_products)
                    fixed_count = len(self.fixed_products)
                    not_found_count = len(self.not_found_products)
                    total_processed = working_count + fixed_count + not_found_count
                    success_rate = ((working_count + fixed_count) / total_processed * 100) if total_processed > 0 else 0
                    
                    print(f"\n📊 PROGRES {idx}/{total} ({idx/total*100:.1f}%):")
                    print(f"   ✅ Originale funcționale: {working_count}")
                    print(f"   🔧 Fixate prin variații/căutare: {fixed_count}")
                    print(f"   ❌ Nu găsite: {not_found_count}")
                    print(f"   📈 Rata de succes: {success_rate:.1f}%")
                    print("   " + "─" * 50)
                
                # Pauză între cereri
                time.sleep(0.3)
            
            # Salvează rezultatele
            self.save_results()
            
        except Exception as e:
            print(f"❌ Eroare la procesarea produselor: {e}")
        finally:
            # Închide browserul la final
            self.close_browser()
    
    def save_results(self):
        """Salvează rezultatele în fișiere separate"""
        try:

            def get_validation_level(reason):
                if not isinstance(reason, str):
                    return "UNKNOWN"
                # Caz manual
                if "adăugat manual" in reason or "confirmat funcțional" in reason:
                    return "MANUAL"
                # Extrage valori
                m = re.search(r'conținut:(\d+), HTML:(\d+), title:(True|False), preț:(\d+), cumpărare:(True|False), individual:(\d+)', reason)
                if not m:
                    return "UNKNOWN"
                cont, html, title, pret, cump, indiv = m.groups()
                cont = int(cont)
                html = int(html)
                pret = int(pret)
                indiv = int(indiv)
                title = title == "True"
                cump = cump == "True"
                # Criterii STRONG
                if cont >= 15 and html >= 2 and pret >= 1 and cump and indiv >= 1:
                    if title:
                        return "STRONG"
                    else:
                        # Acceptă title:False doar dacă restul e foarte bun
                        if cont >= 18 and html >= 4:
                            return "STRONG_WEAK_TITLE"
                        else:
                            return "WEAK"
                # Criterii WEAK
                if cont >= 10 and html >= 1 and pret >= 1 and cump:
                    return "WEAK"
                return "UNKNOWN"

            def add_validation_level(products):
                for prod in products:
                    reason = prod.get('reason', '')
                    prod['validation_level'] = get_validation_level(reason)
                return products

            if self.working_products:
                working_df = pd.DataFrame(add_validation_level(self.working_products))
                working_df.to_csv('working_original_products.csv', index=False)
                print(f"\n✅ Salvat {len(self.working_products)} produse cu URL-uri originale funcționale în 'working_original_products.csv'")

            if self.fixed_products:
                fixed_df = pd.DataFrame(add_validation_level(self.fixed_products))
                fixed_df.to_csv('fixed_products.csv', index=False)
                print(f"🔧 Salvat {len(self.fixed_products)} produse cu URL-uri fixate în 'fixed_products.csv'")

            if self.not_found_products:
                not_found_df = pd.DataFrame(add_validation_level(self.not_found_products))
                not_found_df.to_csv('not_found_products.csv', index=False)
                print(f"❌ Salvat {len(self.not_found_products)} produse negăsite în 'not_found_products.csv'")

            # Statistici
            total = len(self.working_products) + len(self.fixed_products) + len(self.not_found_products)
            if total > 0:
                working_rate = (len(self.working_products) / total) * 100
                fixed_rate = (len(self.fixed_products) / total) * 100
                success_rate = ((len(self.working_products) + len(self.fixed_products)) / total) * 100

                print(f"\n📊 STATISTICI:")
                print(f"   URL-uri originale funcționale: {len(self.working_products)} ({working_rate:.1f}%)")
                print(f"   URL-uri fixate: {len(self.fixed_products)} ({fixed_rate:.1f}%)")
                print(f"   Nu găsite: {len(self.not_found_products)} ({100 - success_rate:.1f}%)")
                print(f"   RATA TOTALĂ DE SUCCES: {success_rate:.1f}%")

        except Exception as e:
            print(f"❌ Eroare la salvarea rezultatelor: {e}")

if __name__ == "__main__":
    print("🎯 XOFlowers Smart Product Finder cu DrissionPage")
    print("1. Testează URL original cu browser real")
    print("2. Testează multiple variante cu pauze")
    print("3. Caută pe site cu browser automation") 
    print("4. Înlocuiește cu URL funcțional")
    print("=" * 60)
    import pandas as pd
    import shutil
    CSV_PATH = r"c:\Users\user\Downloads\Telegram Desktop\chunks_data.csv"
    BACKUP_PATH = CSV_PATH + ".bak"
    TEST_OUTPUT = r"c:\Users\user\Desktop\XOFlowers agents\products_working_control_chunks.csv"
    try:
        # Backup original
        shutil.copy(CSV_PATH, BACKUP_PATH)
        print(f"🔒 Backup creat: {BACKUP_PATH}")

        # Încarcă CSV-ul existent
        df = pd.read_csv(CSV_PATH)
        print(f"📄 Încărcat {len(df)} produse din CSV-ul de lucru")

        # Rulează finder pe primele 50 produse
        finder = SmartProductFinder()
        finder.process_products(
            csv_file=CSV_PATH,
            max_products=50
        )

        # Salvează doar produsele găsite (originale sau fixate) într-un fișier de control
        working = finder.working_products
        fixed = finder.fixed_products
        all_found = working + fixed
        if all_found:
            out_df = pd.DataFrame(all_found)
            out_df.to_csv(TEST_OUTPUT, index=False)
            print(f"✅ Salvat rezultate control în: {TEST_OUTPUT}")
        else:
            print("❗ Nu s-au găsit produse funcționale în primele 50")

    except KeyboardInterrupt:
        print("\n🛑 Procesare oprită de utilizator")
        if 'finder' in locals():
            finder.close_browser()
    except Exception as e:
        print(f"❌ Eroare critică: {e}")
        if 'finder' in locals():
            finder.close_browser()

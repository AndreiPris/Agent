#!/usr/bin/env python3
"""
XOFlowers ChromaDB Populator
Task Andrei: Încarcă products_enriched.json în ChromaDB cu metadata structurată

Autor: Andrei (Baza de Date)
Data: 2025
"""

import json
import os
import time
import logging
import re
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
import pandas as pd
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

class ChromaDBPopulator:
    """
    Populează ChromaDB cu produse îmbunătățite și metadata structurată
    Permite filtrări rapide: preț, categorie, culori
    """
    
    def __init__(self, db_path: str = None):
        # Configurează calea bazei de date
        self.db_path = db_path or os.getenv('CHROMADB_PATH', './chroma_db_flowers')
        
        # Inițializează ChromaDB
        self.client = chromadb.PersistentClient(path=self.db_path)
        
        # Modelul de embeddings (multilingv pentru RO/EN/RU)
        self.embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Colecția principală
        self.collection_name = "xoflowers_products"
        self.collection = None
        
        # Statistici
        self.processed_count = 0
        self.success_count = 0
        self.error_count = 0
        
        # Dicționare pentru extragerea metadatelor
        self.color_keywords = {
            'roșu': ['roșu', 'roșie', 'red', 'crimson', 'scarlet', 'burgundy'],
            'roz': ['roz', 'pink', 'magenta', 'fuchsia', 'pudrat'],
            'alb': ['alb', 'albă', 'white', 'ivory', 'cream'],
            'galben': ['galben', 'galbenă', 'yellow', 'gold', 'auriu'],
            'violet': ['violet', 'violetă', 'purple', 'lavender', 'lilac'],
            'albastru': ['albastru', 'albastră', 'blue', 'navy', 'cerulean'],
            'verde': ['verde', 'green', 'emerald', 'mint'],
            'portocaliu': ['portocaliu', 'orange', 'coral', 'peach'],
            'negru': ['negru', 'neagră', 'black'],
            'multicolor': ['multicolor', 'mixed', 'mixt', 'colorat']
        }
        
        logger.info(f"ChromaDB Populator inițializat. Baza de date: {self.db_path}")
    
    def setup_collection(self) -> bool:
        """
        Configurează colecția ChromaDB
        """
        try:
            # Șterge colecția existentă dacă există
            try:
                self.client.delete_collection(name=self.collection_name)
                logger.info(f"Colecția existentă '{self.collection_name}' a fost ștearsă")
            except:
                pass  # Colecția nu există
            
            # Creează colecția nouă
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "XOFlowers products with enriched descriptions and structured metadata"}
            )
            
            logger.info(f"✅ Colecția '{self.collection_name}' a fost creată cu succes")
            return True
            
        except Exception as e:
            logger.error(f"❌ Eroare la configurarea colecției: {e}")
            return False
    
    def extract_colors_from_text(self, text: str) -> List[str]:
        """
        Extrage culorile din textul descrierii
        """
        if not text:
            return []
        
        text_lower = text.lower()
        found_colors = []
        
        for color, keywords in self.color_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    if color not in found_colors:
                        found_colors.append(color)
                    break  # Găsit culoarea, treci la următoarea
        
        return found_colors
    
    def extract_price_tier(self, price: float) -> str:
        """
        Determină categoria de preț
        """
        if price == 0:
            return "nedefinit"
        elif price < 500:
            return "economic"
        elif price < 1500:
            return "mediu"
        elif price < 3000:
            return "premium"
        else:
            return "luxury"
    
    def normalize_category(self, category: str) -> str:
        """
        Normalizează categoria pentru consistență
        """
        if not category:
            return "general"
        
        category_lower = category.lower()
        
        # Mapări pentru categorii
        category_mapping = {
            'buchete': 'buchete',
            'bouquet': 'buchete',
            'trandafiri': 'trandafiri',
            'roses': 'trandafiri',
            'bujori': 'bujori',
            'peonies': 'bujori',
            'premium': 'premium',
            'chando': 'difuzoare',
            'accesorii': 'accesorii',
            'accessories': 'accesorii',
            'cadouri': 'cadouri',
            'gifts': 'cadouri',
            'valentine': 'valentine',
            'mourning': 'doliu'
        }
        
        for key, value in category_mapping.items():
            if key in category_lower:
                return value
        
        return category.lower()
    
    def create_metadata(self, product: Dict) -> Dict[str, Any]:
        """
        Creează metadata structurată pentru un produs
        SARCINA LUI ANDREI: Aici se face magia filtrării rapide!
        """
        
        # Textul complet pentru analiză
        full_text = f"{product.get('title', '')} {product.get('description', '')}"
        
        # Extrage culorile
        colors = self.extract_colors_from_text(full_text)
        
        # Prețul ca număr (crucial pentru filtrări)
        price = float(product.get('price', 0))
        price_tier = self.extract_price_tier(price)
        
        # Categoria normalizată
        category = self.normalize_category(product.get('category', ''))
        
        # Metadata structurată
        metadata = {
            # Câmpuri pentru filtrare rapidă
            'price': price,
            'price_tier': price_tier,
            'category': category,
            'main_colors': colors,  # Lista de culori principale
            
            # Informații de bază
            'title': product.get('title', ''),
            'original_category': product.get('category', ''),
            'currency': product.get('currency', 'MDL'),
            
            # URLs și identificatori
            'product_id': product.get('id', ''),
            'image_url': product.get('image_url', ''),
            'product_url': product.get('product_url', ''),
            
            # Metadata de procesare
            'has_enriched_description': 'enriched_by' in product,
            'scraped_at': product.get('scraped_at', ''),
            'enriched_at': product.get('enriched_at', ''),
            
            # Pentru debugging
            'total_colors_found': len(colors),
            'description_length': len(product.get('description', '')),
        }
        
        return metadata
    
    def create_searchable_text(self, product: Dict) -> str:
        """
        Creează textul care va fi folosit pentru căutare semantică
        """
        # Combină toate informațiile relevante
        parts = []
        
        # Titlul (de 2 ori pentru importanță)
        title = product.get('title', '')
        if title:
            parts.append(title)
            parts.append(title)  # Dublează importanța titlului
        
        # Descrierea îmbunătățită
        description = product.get('description', '')
        if description:
            parts.append(description)
        
        # Categoria
        category = product.get('category', '')
        if category:
            parts.append(f"Categorie: {category}")
        
        # Prețul în text pentru căutări de tipul "ieftin", "scump"
        price = product.get('price', 0)
        if price > 0:
            price_text = f"Preț {price} lei"
            if price < 500:
                price_text += " ieftin economic accesibil"
            elif price > 2000:
                price_text += " premium scump luxury de lux"
            parts.append(price_text)
        
        return " ".join(parts)
    
    def add_product_to_db(self, product: Dict) -> bool:
        """
        Adaugă un produs în ChromaDB
        """
        try:
            # Creează textul pentru căutare
            searchable_text = self.create_searchable_text(product)
            
            # Creează embedding-ul
            embedding = self.embedding_model.encode([searchable_text])[0].tolist()
            
            # Creează metadata-ul structurat
            metadata = self.create_metadata(product)
            
            # Adaugă în colecție
            product_id = product.get('id', f"product_{self.processed_count}")
            
            self.collection.add(
                embeddings=[embedding],
                documents=[searchable_text],
                metadatas=[metadata],
                ids=[product_id]
            )
            
            self.success_count += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Eroare la adăugarea produsului {product.get('id', 'unknown')}: {e}")
            self.error_count += 1
            return False
    
    def populate_database(self, input_file: str = "data/products_enriched.json") -> bool:
        """
        Populează întreaga bază de date ChromaDB
        """
        logger.info("🗄️  Începând popularea ChromaDB cu produse îmbunătățite...")
        
        try:
            # Verifică dacă fișierul există
            if not os.path.exists(input_file):
                logger.error(f"❌ Fișierul {input_file} nu există!")
                logger.info("   Rulează mai întâi image_enricher.py pentru a crea acest fișier.")
                return False
            
            # Configurează colecția
            if not self.setup_collection():
                return False
            
            # Încarcă produsele
            with open(input_file, 'r', encoding='utf-8') as f:
                products = json.load(f)
            
            if not products:
                logger.error("❌ Nu s-au găsit produse în fișierul de intrare")
                return False
            
            logger.info(f"📦 Găsite {len(products)} produse de procesat")
            
            # Procesează fiecare produs
            for i, product in enumerate(products):
                self.processed_count += 1
                
                logger.info(f"📥 Procesând {self.processed_count}/{len(products)}: {product.get('title', 'Fără nume')}")
                
                success = self.add_product_to_db(product)
                
                if success:
                    # Afișează detalii despre metadata pentru primele produse
                    if i < 3:
                        metadata = self.create_metadata(product)
                        logger.info(f"   📊 Metadata: preț={metadata['price']}, "
                                  f"culori={metadata['main_colors']}, "
                                  f"categorie={metadata['category']}")
                
                # Progres la fiecare 50 de produse
                if (i + 1) % 50 == 0:
                    self._show_progress_stats(i + 1, len(products))
            
            # Statistici finale
            self._show_final_stats(len(products))
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Eroare la popularea bazei de date: {e}")
            return False
    
    def _show_progress_stats(self, current: int, total: int):
        """Afișează progresul"""
        percentage = (current / total) * 100
        logger.info(f"📈 Progres: {current}/{total} ({percentage:.1f}%) - "
                   f"Succese: {self.success_count}, Erori: {self.error_count}")
    
    def _show_final_stats(self, total_products: int):
        """Afișează statisticile finale"""
        success_rate = (self.success_count / total_products) * 100 if total_products > 0 else 0
        
        print(f"\\n📊 STATISTICI POPULARE CHROMADB:")
        print(f"   🗄️  Total produse procesate: {self.processed_count}")
        print(f"   ✅ Adăugate cu succes: {self.success_count}")
        print(f"   ❌ Erori: {self.error_count}")
        print(f"   📈 Rata de succes: {success_rate:.1f}%")
        print(f"   🏠 Locația bazei de date: {self.db_path}")
        
        if self.success_count > 0:
            print(f"\\n🎉 Felicitări Andrei! Baza de date este gata!")
            print(f"   Acum se pot face filtrări de tipul 'buchete roșii sub 1000 lei' în milisecunde!")
    
    def test_search_capabilities(self):
        """
        Testează capacitățile de căutare ale bazei de date
        """
        if not self.collection:
            logger.error("❌ Colecția nu este inițializată")
            return
        
        print(f"\\n🔍 TESTÂND CAPACITĂȚILE DE CĂUTARE:")
        
        test_queries = [
            "buchete roșii",
            "trandafiri albi ieftini",
            "flori pentru aniversare",
            "premium scump luxury"
        ]
        
        for query in test_queries:
            try:
                # Căutare semantică
                embedding = self.embedding_model.encode([query]).tolist()
                results = self.collection.query(
                    query_embeddings=embedding,
                    n_results=3,
                    include=["metadatas", "documents", "distances"]
                )
                
                print(f"\\n   Query: '{query}'")
                if results['metadatas'] and results['metadatas'][0]:
                    for i, metadata in enumerate(results['metadatas'][0]):
                        distance = results['distances'][0][i]
                        print(f"      {i+1}. {metadata['title']} (preț: {metadata['price']} lei, "
                              f"culori: {metadata['main_colors']}, distanță: {distance:.3f})")
                else:
                    print(f"      Nu s-au găsit rezultate")
                    
            except Exception as e:
                print(f"      Eroare la testarea query-ului '{query}': {e}")

def main():
    """Funcția principală - Sarcina lui Andrei"""
    
    print("🗄️  XOFlowers ChromaDB Populator - Sarcina lui Andrei")
    print("=" * 70)
    
    try:
        populator = ChromaDBPopulator()
        
        # Populează baza de date
        success = populator.populate_database()
        
        if success:
            # Testează capacitățile de căutare
            populator.test_search_capabilities()
            
            print("\\n🎉 MISIUNE ÎMPLINITĂ CU SUCCES!")
            print("   ChromaDB este populată și optimizată pentru filtrări rapide!")
            print("   Acum Aurel poate să implementeze logica de căutare în core_logic.py!")
        else:
            print("\\n❌ A apărut o problemă în timpul populării bazei de date.")
            
    except Exception as e:
        logger.error(f"Eroare în funcția principală: {e}")
        print(f"\\n❌ Eroare critică: {e}")

if __name__ == "__main__":
    main()

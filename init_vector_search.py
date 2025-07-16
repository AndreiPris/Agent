# ОБНОВЛЕННЫЙ ФАЙЛ: init_vector_search.py 
# Заменить существующий файл

"""
Inițializarea căutării vectoriale pentru noul CSV
"""

import sys
import os

# Adăugăm calea către src
sys.path.insert(0, 'src')

def main():
    print("🌸 Inițializarea căutării vectoriale XOFlowers (CSV nou)")
    print("=" * 60)
    
    # Verificăm dependențele
    print("1. Verificăm dependențele...")
    try:
        import chromadb
        print("✅ ChromaDB instalat")
    except ImportError:
        print("❌ ChromaDB nu este instalat. Executați: pip install chromadb")
        return False
    
    try:
        import sentence_transformers
        print("✅ SentenceTransformers instalat")
    except ImportError:
        print("❌ SentenceTransformers nu este instalat. Executați: pip install sentence-transformers")
        return False
    
    # Verificăm fișierele de date
    print("\n2. Verificăm fișierele de date...")
    
    new_csv = "data/final_products_case_standardized.csv"
    old_csv = "data/chunks_data.csv"
    
    csv_file = None
    if os.path.exists(new_csv):
        csv_file = new_csv
        print(f"✅ Fișierul nou găsit: {new_csv}")
    elif os.path.exists(old_csv):
        csv_file = old_csv
        print(f"⚠️ Folosim fișierul vechi: {old_csv}")
    else:
        print("❌ Niciun fișier CSV nu a fost găsit!")
        print(f"   Căutăm: {new_csv}")
        print(f"   Căutăm: {old_csv}")
        return False
    
    # Verificăm structura CSV-ului
    print(f"\n3. Analizăm structura CSV-ului...")
    try:
        import csv
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            
            print(f"📊 Coloane găsite: {len(headers)}")
            for header in headers:
                print(f"   • {header}")
            
            # Contorizăm produsele
            product_count = 0
            valid_count = 0
            
            for row in reader:
                if row.get('chunk_type') == 'product':
                    product_count += 1
                    # Verificăm dacă produsul este valid
                    if (row.get('product_exists', 'false').lower() == 'true' and 
                        row.get('primary_text', '').strip() and 
                        row.get('price', '0') != '0'):
                        valid_count += 1
            
            print(f"🌸 Total produse: {product_count}")
            print(f"✅ Produse valide: {valid_count}")
            
    except Exception as e:
        print(f"❌ Eroare la citirea CSV: {e}")
        return False
    
    # Inițializăm căutarea
    print("\n4. Inițializăm căutarea vectorială...")
    try:
        from database.vector_search import vector_search
        print("✅ Căutarea vectorială creată")
        
        # Încărcăm datele
        print("\n5. Încărcăm produsele...")
        if csv_file == new_csv:
            vector_search.load_products_from_csv("final_products_case_standardized.csv")
        else:
            vector_search.load_products_from_csv("chunks_data.csv")
        
        # Verificăm statisticile
        print("\n6. Verificăm statisticile...")
        stats = vector_search.get_stats()
        
        if 'error' in stats:
            print(f"❌ Eroare statistici: {stats['error']}")
        else:
            print(f"✅ Statistici database:")
            print(f"   • Total produse: {stats.get('total_products', 0)}")
            print(f"   • Produse verificate: {stats.get('verified_products', 0)}")
            print(f"   • URL-uri funcționale: {stats.get('functional_urls', 0)}")
            print(f"   • Categorii: {stats.get('categories_count', 0)}")
            
            # Afișăm categoriile
            categories = stats.get('categories', [])
            if categories:
                print(f"\n📂 Categorii găsite:")
                for i, category in enumerate(categories, 1):
                    print(f"   {i}. {category}")
        
        # Testăm căutarea
        print("\n7. Testăm căutarea...")
        test_queries = ["trandafiri", "buchet", "flori pentru mama"]
        
        for query in test_queries:
            results = vector_search.search(query, limit=2)
            print(f"   '{query}' → {len(results)} rezultate")
            
            for result in results:
                verified = "✅" if result.get('is_verified') == 'true' else "⚠️"
                functional = "🔗" if result.get('url_functional') == 'true' else "❌"
                print(f"      {verified}{functional} {result['name'][:40]}...")
        
        print(f"\n🎉 Căutarea vectorială este gata de funcționare!")
        print(f"📊 Folosind fișierul: {csv_file}")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la inițializare: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Inițializarea finalizată cu succes!")
        print("🚀 Sistemul este gata pentru căutări vectoriale!")
    else:
        print("\n❌ Inițializarea a eșuat!")
        print("🔧 Verificați erorile de mai sus și reîncercați.")
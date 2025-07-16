"""
Исправленная инициализация векторного поиска для универсальной системы
"""

import sys
import os

# Adăugăm calea către src
sys.path.insert(0, 'src')

def main():
    print("🌍 Inițializarea sistemului universal XOFlowers")
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
            
            # Contorizăm produsele (ИСПРАВЛЕНО: проверяем "True" с большой буквы)
            product_count = 0
            valid_count = 0
            
            for row in reader:
                if row.get('chunk_type') == 'product':
                    product_count += 1
                    # ИСПРАВЛЕНО: проверяем "True" вместо "true"
                    if (row.get('product_exists', 'False') == 'True' and 
                        row.get('primary_text', '').strip() and 
                        row.get('price', '0') != '0'):
                        valid_count += 1
            
            print(f"🌸 Total produse: {product_count}")
            print(f"✅ Produse valide: {valid_count}")
            
    except Exception as e:
        print(f"❌ Eroare la citirea CSV: {e}")
        return False
    
    # Inițializăm sistemul universal
    print("\n4. Inițializăm sistemul universal...")
    try:
        from database.vector_search import universal_search
        print("✅ Sistemul universal creat")
        
        # Încărcăm datele
        print("\n5. Încărcăm produsele în ambele coллекции...")
        if csv_file == new_csv:
            universal_search.load_products_from_csv("final_products_case_standardized.csv")
        else:
            universal_search.load_products_from_csv("chunks_data.csv")
        
        # Verificăm statisticile
        print("\n6. Verificăm statisticile...")
        stats = universal_search.get_stats()
        
        if 'error' in stats:
            print(f"❌ Eroare statistici: {stats['error']}")
        else:
            print(f"✅ Statistici sistem:")
            print(f"   🛍️ Total produse: {stats.get('total_products', 0)}")
            print(f"   🌸 Produse florale: {stats.get('flower_products', 0)}")
            print(f"   ✅ Produse verificate: {stats.get('verified_products', 0)}")
            print(f"   🔗 URL-uri funcționale: {stats.get('functional_urls', 0)}")
            print(f"   📂 Categorii: {stats.get('categories_count', 0)}")
            
            # Afișăm categoriile
            categories = stats.get('categories', [])
            if categories:
                print(f"\n📂 Categorii disponibile:")
                flower_cats = []
                other_cats = []
                
                for category in categories:
                    if any(word in category for word in ['Bouquet', 'Rose', 'Peonies', 'Wedding', 'Bride', 'Premium']):
                        flower_cats.append(category)
                    else:
                        other_cats.append(category)
                
                if flower_cats:
                    print(f"   🌸 Categorii florale:")
                    for i, category in enumerate(flower_cats, 1):
                        print(f"      {i}. {category}")
                
                if other_cats:
                    print(f"   🎁 Alte categorii:")
                    for i, category in enumerate(other_cats, 1):
                        print(f"      {i}. {category}")
        
        # Testăm căutarea
        print("\n7. Testăm căutarea universală...")
        
        test_queries = [
            ("trandafiri roșii", "flowers"),
            ("difuzor aromă", "all_products"), 
            ("cadou frumos", "smart")
        ]
        
        for query, search_type in test_queries:
            print(f"\n   🔍 Test '{query}' ({search_type}):")
            
            if search_type == "flowers":
                results = universal_search.search_flowers_only(query, limit=2)
            elif search_type == "all_products":
                results = universal_search.search_all_products(query, limit=2)
            else:
                results = universal_search.smart_search(query, limit=2)
            
            print(f"      Găsite: {len(results)} rezultate")
            
            for i, result in enumerate(results, 1):
                verified = "✅" if result.get('is_verified') else "⚠️"
                source = result.get('source', 'N/A')
                print(f"      {i}. {verified} [{source}] {result['name'][:50]}...")
                print(f"         💰 {result['price']} MDL | 📂 {result['category']}")
        
        print(f"\n🎉 Sistemul universal este gata de funcționare!")
        print(f"📊 Folosind fișierul: {csv_file}")
        print(f"🚀 Capabilități: căutare flowers + all products + smart detection")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare la inițializare: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Inițializarea finalizată cu succes!")
        print("🌍 Sistemul universal este gata!")
        print("\n💡 Funcții disponibile:")
        print("   🧠 smart_search() - detectează automat tipul")
        print("   🌸 search_flowers_only() - doar flori")
        print("   🛍️ search_all_products() - toate produsele")
    else:
        print("\n❌ Inițializarea a eșuat!")
        print("🔧 Verificați erorile de mai sus și reîncercați.")
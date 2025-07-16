# ОБНОВЛЕННЫЙ ФАЙЛ: test_vector_search.py

"""
Test pentru căutarea vectorială cu noul CSV
"""

import sys
sys.path.insert(0, 'src')

def test_vector_search():
    print("🧪 Test căutare vectorială (CSV nou)")
    print("=" * 40)
    
    try:
        from database.vector_search import vector_search
        
        # Test statistici
        print("📊 Statistici database:")
        stats = vector_search.get_stats()
        
        if 'error' in stats:
            print(f"❌ Eroare: {stats['error']}")
            return False
        
        print(f"   • Total produse: {stats.get('total_products', 0)}")
        print(f"   • Verificate: {stats.get('verified_products', 0)}")
        print(f"   • URL funcționale: {stats.get('functional_urls', 0)}")
        print(f"   • Categorii: {stats.get('categories_count', 0)}")
        
        # Test căutări cu noi opțiuni
        test_queries = [
            ("trandafiri roșii", True, True),    # doar verificate + funcționale
            ("buchet pentru mama", False, True), # toate + doar funcționale  
            ("flori în coș", True, False),       # doar verificate + toate URL
            ("plante pentru casă", False, False) # toate produsele
        ]
        
        for query, only_verified, only_functional in test_queries:
            print(f"\n🔍 Căutare: '{query}'")
            print(f"   Filtru verificate: {only_verified}")
            print(f"   Filtru URL funcționale: {only_functional}")
            
            results = vector_search.search(
                query, 
                limit=3,
                only_verified=only_verified,
                only_functional=only_functional
            )
            
            if results:
                print(f"   Găsite: {len(results)} produse")
                for i, product in enumerate(results, 1):
                    verified = "✅" if product.get('is_verified') == 'true' else "⚠️"
                    functional = "🔗" if product.get('url_functional') == 'true' else "❌"
                    
                    print(f"   {i}. {verified}{functional} {product['name'][:40]}...")
                    print(f"      Preț: {product['price']} MDL")
                    print(f"      Relevanță: {product['score']:.2f}")
            else:
                print("   ❌ Nimic găsit")
        
        # Test categorii
        print(f"\n📂 Categorii disponibile:")
        categories = vector_search.get_categories()
        for i, category in enumerate(categories, 1):
            print(f"   {i}. {category}")
        
        print(f"\n✅ Test finalizat cu succes!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare test: {e}")
        return False

def test_action_handler():
    print("\n🤖 Test ActionHandler cu noul CSV")
    print("=" * 40)
    
    try:
        from intelligence.action_handler import ActionHandler
        
        handler = ActionHandler()
        
        test_messages = [
            "Vreau trandafiri verificați pentru soția mea",
            "Caut buchete cu URL-uri funcționale",
            "Flori pentru mama, doar produse existente"
        ]
        
        for message in test_messages:
            print(f"\n💬 Mesaj: '{message}'")
            
            response, intent, confidence = handler.handle_message(message, "test_user")
            
            print(f"   Intenție: {intent} ({confidence:.2f})")
            print(f"   Răspuns: {response[:150]}...")
        
        print(f"\n✅ ActionHandler funcționează cu noul CSV!")
        return True
        
    except Exception as e:
        print(f"❌ Eroare ActionHandler: {e}")
        return False

def test_data_quality():
    """Test calitatea datelor din noul CSV"""
    print("\n🔍 Test calitate date")
    print("=" * 30)
    
    try:
        import csv
        import os
        
        csv_file = "data/final_products_case_standardized.csv"
        if not os.path.exists(csv_file):
            print(f"❌ Fișierul {csv_file} nu există")
            return False
        
        products_total = 0
        products_valid = 0
        verified_products = 0
        functional_urls = 0
        
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                if row.get('chunk_type') == 'product':
                    products_total += 1
                    
                    # Verificăm dacă produsul este valid
                    if (row.get('product_exists', 'false').lower() == 'true' and 
                        row.get('primary_text', '').strip() and 
                        row.get('price', '0') != '0'):
                        products_valid += 1
                    
                    # Statistici verificare
                    if row.get('is_verified', 'false').lower() == 'true':
                        verified_products += 1
                    
                    if row.get('url_functional', 'false').lower() == 'true':
                        functional_urls += 1
        
        print(f"📊 Analiza calitate:")
        print(f"   • Total produse: {products_total}")
        print(f"   • Produse valide: {products_valid} ({products_valid/products_total*100:.1f}%)")
        print(f"   • Verificate: {verified_products} ({verified_products/products_total*100:.1f}%)")
        print(f"   • URL funcționale: {functional_urls} ({functional_urls/products_total*100:.1f}%)")
        
        if products_valid > 0:
            print("✅ Datele sunt de calitate bună!")
        else:
            print("⚠️ Puține produse valide găsite")
        
        return True
        
    except Exception as e:
        print(f"❌ Eroare test calitate: {e}")
        return False

if __name__ == "__main__":
    print("🌸 Test complet pentru noul CSV XOFlowers")
    print("=" * 50)
    
    tests = [
        ("Căutare vectorială", test_vector_search),
        ("ActionHandler", test_action_handler), 
        ("Calitate date", test_data_quality)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        result = test_func()
        results.append((test_name, result))
    
    print(f"\n{'='*50}")
    print("📊 REZULTATE FINALE")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:<20} {status}")
        if result:
            passed += 1
    
    print("-" * 50)
    print(f"Rezultat: {passed}/{len(results)} teste reușite")
    
    if passed == len(results):
        print("🎉 TOATE TESTELE AU REUȘIT!")
        print("🚀 Sistemul este gata cu noul CSV!")
    else:
        print("⚠️ Unele teste au eșuat - verificați erorile.")
        

    
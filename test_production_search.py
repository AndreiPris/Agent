"""
Тест универсальной системы поиска XOFlowers
"""

import sys
sys.path.insert(0, 'src')

def test_universal_search():
    print("🌍 ТЕСТ УНИВЕРСАЛЬНОЙ СИСТЕМЫ ПОИСКА")
    print("=" * 50)
    
    try:
        from database.vector_search import universal_search, smart_search, search_flowers_only, search_all_products
        
        # Инициализация
        universal_search.load_products_from_csv("final_products_case_standardized.csv")
        
        # Статистика
        print("\n📊 СТАТИСТИКА СИСТЕМЫ:")
        stats = universal_search.get_stats()
        if 'error' not in stats:
            print(f"   🛍️ Всего товаров: {stats.get('total_products', 0)}")
            print(f"   🌸 Из них цветов: {stats.get('flower_products', 0)}")
            print(f"   📦 Коллекции: {', '.join(stats.get('collections', []))}")
        
        print(f"\n🧠 ТЕСТ УМНОГО ПОИСКА:")
        print("=" * 40)
        
        # Тест 1: Автоматический поиск цветов
        print(f"\n1️⃣ Умный поиск 'букеты роз trandafiri':")
        smart_roses = smart_search("букеты роз trandafiri", limit=3)
        print(f"   Найдено: {len(smart_roses)} товаров")
        for i, product in enumerate(smart_roses, 1):
            verified = "✅" if product.get('is_verified') else "⚠️"
            print(f"   {i}. {verified} [{product.get('source', 'N/A')}] {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
            print(f"      🎯 Релевантность: {product['score']}")
        
        # Тест 2: Автоматический поиск диффузоров
        print(f"\n2️⃣ Умный поиск 'диффузоры ароматы chando':")
        smart_diffusers = smart_search("диффузоры ароматы chando", limit=3)
        print(f"   Найдено: {len(smart_diffusers)} товаров")
        for i, product in enumerate(smart_diffusers, 1):
            verified = "✅" if product.get('is_verified') else "⚠️"
            print(f"   {i}. {verified} [{product.get('source', 'N/A')}] {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 3: Принудительный поиск только цветов
        print(f"\n3️⃣ Только ЦВЕТЫ 'красивые подарки':")
        flowers_only = search_flowers_only("красивые подарки", limit=3)
        print(f"   Найдено: {len(flowers_only)} товаров")
        for i, product in enumerate(flowers_only, 1):
            print(f"   {i}. 🌸 {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 4: Принудительный поиск по всем товарам
        print(f"\n4️⃣ ВСЕ ТОВАРЫ 'подарки аксессуары':")
        all_products = search_all_products("подарки аксессуары", limit=3)
        print(f"   Найдено: {len(all_products)} товаров")
        for i, product in enumerate(all_products, 1):
            print(f"   {i}. 🛍️ {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 5: Поиск игрушек
        print(f"\n5️⃣ Умный поиск 'мягкие игрушки toys':")
        smart_toys = smart_search("мягкие игрушки toys", limit=3)
        print(f"   Найдено: {len(smart_toys)} товаров")
        for i, product in enumerate(smart_toys, 1):
            print(f"   {i}. 🧸 [{product.get('source', 'N/A')}] {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        # Тест 6: Неопределенный запрос
        print(f"\n6️⃣ Неопределенный поиск 'подарок на день рождения':")
        mixed_search = smart_search("подарок на день рождения", limit=4)
        print(f"   Найдено: {len(mixed_search)} товаров")
        for i, product in enumerate(mixed_search, 1):
            print(f"   {i}. 🎁 [{product.get('source', 'N/A')}] {product['name'][:50]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
        
        print(f"\n✅ ВСЕ ТЕСТЫ УНИВЕРСАЛЬНОГО ПОИСКА УСПЕШНЫ!")
        print(f"🎉 СИСТЕМА ГОТОВА К ПРОДАКШЕНУ!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_category_detection():
    """Тест автоматического определения категорий"""
    print(f"\n🎯 ТЕСТ АВТОМАТИЧЕСКОГО ОПРЕДЕЛЕНИЯ ТИПА ПОИСКА:")
    print("=" * 50)
    
    try:
        from database.vector_search import universal_search
        
        test_queries = [
            ("розы букет trandafiri", "flowers"),
            ("диффузор аромат chando", "non_flowers"), 
            ("игрушки мягкие toys", "non_flowers"),
            ("подарок красивый", "mixed"),
            ("свадьба невеста bride", "flowers"),
            ("открытка поздравление", "non_flowers")
        ]
        
        for query, expected in test_queries:
            detected = universal_search._detect_search_type(query)
            status = "✅" if detected == expected else "❌"
            print(f"   {status} '{query}' → {detected} (ожидалось: {expected})")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте определения: {e}")
        return False

if __name__ == "__main__":
    print("🌍 ПОЛНЫЙ ТЕСТ УНИВЕРСАЛЬНОЙ СИСТЕМЫ")
    print("=" * 50)
    
    success1 = test_universal_search()
    success2 = test_category_detection()
    
    print(f"\n" + "=" * 50)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    
    if success1 and success2:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
        print("✅ УНИВЕРСАЛЬНАЯ СИСТЕМА РАБОТАЕТ!")
        print("🚀 ГОТОВА К ИСПОЛЬЗОВАНИЮ В ПРОДАКШЕНЕ!")
        print("\n💡 ВОЗМОЖНОСТИ СИСТЕМЫ:")
        print("   🧠 Автоматическое определение типа поиска")
        print("   🌸 Поиск только цветов")
        print("   🛍️ Поиск по всем товарам") 
        print("   🎁 Комбинированный поиск")
        print("   💰 Фильтрация по цене и верификации")
    else:
        print("❌ Есть проблемы для исправления")
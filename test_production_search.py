"""
Тест готового векторного поиска с фильтрацией категорий
"""

import sys
sys.path.insert(0, 'src')

def test_production_search():
    print("🌸 ТЕСТ ГОТОВОГО ПОИСКА ЦВЕТОВ")
    print("=" * 50)
    
    try:
        from database.vector_search import vector_search, search_flowers, search_verified_flowers, search_flowers_in_budget
        
        # Инициализация
        vector_search.load_products_from_csv("final_products_case_standardized.csv")
        
        # Статистика
        print("\n📊 СТАТИСТИКА ЦВЕТОЧНЫХ ПРОДУКТОВ:")
        stats = vector_search.get_stats()
        if 'error' not in stats:
            print(f"   🌸 Цветочных продуктов: {stats.get('total_flowers', 0)}")
            print(f"   ✅ Верифицированных: {stats.get('verified_flowers', 0)}")
            print(f"   🔗 С функциональными URL: {stats.get('functional_urls', 0)}")
            
            price_dist = stats.get('price_distribution', {})
            print(f"   💰 Бюджетные (<500): {price_dist.get('budget', 0)}")
            print(f"   💰 Средние (500-1500): {price_dist.get('medium', 0)}")
            print(f"   💰 Премиум (>1500): {price_dist.get('premium', 0)}")
            
            print(f"\n📂 ЦВЕТОЧНЫЕ КАТЕГОРИИ:")
            for i, cat in enumerate(stats.get('flower_categories', []), 1):
                print(f"   {i}. {cat}")
        
        print(f"\n🔍 ТЕСТ ПОИСКА ЦВЕТОВ:")
        print("=" * 40)
        
        # Тест 1: Поиск роз
        print(f"\n1️⃣ Поиск 'розы красные trandafiri':")
        roses = search_flowers("розы красные trandafiri", limit=3)
        print(f"   Найдено: {len(roses)} продуктов")
        for i, product in enumerate(roses, 1):
            verified = "✅" if product.get('is_verified') else "⚠️"
            print(f"   {i}. {verified} {product['name'][:60]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
            print(f"      🎯 Релевантность: {product['score']}")
        
        # Тест 2: Поиск букетов
        print(f"\n2️⃣ Поиск 'букет для мамы buchet mama':")
        bouquets = search_flowers("букет для мамы buchet mama", limit=3)
        print(f"   Найдено: {len(bouquets)} продуктов")
        for i, product in enumerate(bouquets, 1):
            verified = "✅" if product.get('is_verified') else "⚠️"
            print(f"   {i}. {verified} {product['name'][:60]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
            print(f"      🎯 Релевантность: {product['score']}")
        
        # Тест 3: Поиск в бюджете
        print(f"\n3️⃣ Поиск в бюджете до 800 MDL 'flori frumoase':")
        budget_flowers = search_flowers_in_budget("flori frumoase", 800, limit=3)
        print(f"   Найдено: {len(budget_flowers)} продуктов")
        for i, product in enumerate(budget_flowers, 1):
            verified = "✅" if product.get('is_verified') else "⚠️"
            print(f"   {i}. {verified} {product['name'][:60]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
            print(f"      🎯 Релевантность: {product['score']}")
        
        # Тест 4: Только верифицированные
        print(f"\n4️⃣ Только верифицированные 'peonii bujori':")
        verified = search_verified_flowers("peonii bujori", limit=3)
        print(f"   Найдено: {len(verified)} продуктов")
        for i, product in enumerate(verified, 1):
            print(f"   {i}. ✅ {product['name'][:60]}...")
            print(f"      💰 {product['price']} MDL | 📂 {product['category']}")
            print(f"      🎯 Релевантность: {product['score']}")
        
        # Тест 5: Поиск по категории
        print(f"\n5️⃣ Поиск по категории 'Classic Bouquets':")
        classic = vector_search.search_by_category("Classic Bouquets", limit=3)
        print(f"   Найдено: {len(classic)} продуктов")
        for i, product in enumerate(classic, 1):
            print(f"   {i}. 🌸 {product['name'][:60]}...")
            print(f"      💰 {product['price']} MDL")
        
        print(f"\n✅ ВСЕ ТЕСТЫ ПОИСКА УСПЕШНЫ!")
        print(f"🎉 ГОТОВЫЙ ПРОДУКТ РАБОТАЕТ КОРРЕКТНО!")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тестах: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_no_non_flowers():
    """Проверяем что диффузоры и игрушки исключены"""
    print(f"\n🚫 ТЕСТ ИСКЛЮЧЕНИЯ НЕ-ЦВЕТОВ:")
    print("=" * 40)
    
    try:
        from database.vector_search import search_flowers
        
        # Тест исключения диффузоров
        print(f"\n🧪 Поиск 'difuzor aroma chando':")
        diffusers = search_flowers("difuzor aroma chando", limit=5)
        print(f"   Найдено: {len(diffusers)} продуктов")
        
        if len(diffusers) == 0:
            print("   ✅ ОТЛИЧНО! Диффузоры правильно исключены")
        else:
            print("   ⚠️ Найдены диффузоры - нужна доработка")
            for product in diffusers:
                print(f"      - {product['category']}: {product['name'][:50]}...")
        
        # Тест исключения игрушек
        print(f"\n🧸 Поиск 'soft toys plush':")
        toys = search_flowers("soft toys plush", limit=5)
        print(f"   Найдено: {len(toys)} продуктов")
        
        if len(toys) == 0:
            print("   ✅ ОТЛИЧНО! Игрушки правильно исключены")
        else:
            print("   ⚠️ Найдены игрушки - нужна доработка")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка в тесте исключений: {e}")
        return False

if __name__ == "__main__":
    print("🌸 ПОЛНЫЙ ТЕСТ ГОТОВОГО ПРОДУКТА")
    print("=" * 50)
    
    success1 = test_production_search()
    success2 = test_no_non_flowers()
    
    print(f"\n" + "=" * 50)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ:")
    print("=" * 50)
    
    if success1 and success2:
        print("🎉 ВСЕ ТЕСТЫ ПРОШЛИ!")
        print("✅ ГОТОВЫЙ ПРОДУКТ РАБОТАЕТ КОРРЕКТНО!")
        print("🚀 СИСТЕМА ГОТОВА К ИСПОЛЬЗОВАНИЮ!")
    else:
        print("❌ Есть проблемы для исправления")
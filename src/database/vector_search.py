"""
ГОТОВЫЙ векторный поиск для XOFlowers с корректной фильтрацией
Исключает диффузоры, игрушки и аксессуары - показывает только ЦВЕТЫ
"""

import os
import csv
import chromadb
from sentence_transformers import SentenceTransformer

class ProductionVectorSearch:
    def __init__(self):
        # Создаем базу данных ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db_flowers")
        
        # Загружаем модель для создания векторов
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Создаем коллекцию для продуктов
        try:
            self.collection = self.client.create_collection("products")
        except:
            self.collection = self.client.get_collection("products")
        
        # Категории ЦВЕТОВ (исключаем аксессуары)
        self.flower_categories = {
            "Author'S Bouquets",
            "Classic Bouquets", 
            "French Roses",
            "Mono/Duo Bouquets",
            "Basket / Boxes With Flowers",
            "Bride'S Bouquet",
            "Premium",
            "Peonies",
            "Mourning Flower Arrangement",
            "St. Valentine'S Day"
        }
        
        # Категории которые НЕ цветы (исключаем из поиска)
        self.non_flower_categories = {
            "Chando",  # Диффузоры
            "Soft Toys",  # Игрушки
            "Greeting Card",  # Открытки
            "Additional Accessories / Vases",  # Аксессуары
            "Sweets"  # Сладости
        }
        
        print("✅ Production vector search initialized with category filtering")
    
    def load_products_from_csv(self, csv_filename="final_products_case_standardized.csv"):
        """Загружаем только ЦВЕТОЧНЫЕ продукты из CSV"""
        csv_path = f"data/{csv_filename}"
        
        if not os.path.exists(csv_path):
            csv_path = "data/chunks_data.csv"
            if not os.path.exists(csv_path):
                print("❌ Файлы данных не найдены!")
                return
            print(f"⚠️ Используем старый файл: {csv_path}")
        else:
            print(f"✅ Используем новый файл: {csv_path}")
        
        products = []
        total_rows = 0
        valid_products = 0
        excluded_products = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                total_rows += 1
                
                # Проверяем что это продукт
                if row.get('chunk_type') != 'product':
                    continue
                
                # ИСКЛЮЧАЕМ НЕ-ЦВЕТОЧНЫЕ категории
                category = row.get('category', '')
                if category in self.non_flower_categories:
                    excluded_products += 1
                    continue
                
                # Фильтруем только существующие продукты
                if not self._is_valid_product(row):
                    continue
                
                valid_products += 1
                
                # Создаем улучшенный текст для поиска
                search_text = self._create_enhanced_search_text(row)
                
                # Выбираем лучший URL
                best_url = self._get_best_url(row)
                
                product = {
                    'id': row.get('chunk_id', f'product_{valid_products}'),
                    'text': search_text,
                    'name': row.get('primary_text', '')[:150],
                    'price': self._parse_price(row.get('price', '0')),
                    'category': category,
                    'flowers': row.get('flower_type', ''),
                    'url': best_url,
                    'collection_id': row.get('collection_id', ''),
                    'is_verified': row.get('is_verified', 'False'),
                    'url_functional': row.get('url_functional', 'False'),
                    'product_exists': row.get('product_exists', 'False'),
                    'is_flower_product': 'True'  # Маркируем как цветочный продукт
                }
                
                products.append(product)
        
        print(f"📊 Обработано строк: {total_rows}")
        print(f"🌸 Цветочных продуктов: {valid_products}")
        print(f"🚫 Исключено не-цветов: {excluded_products}")
        
        # Добавляем только цветочные продукты в ChromaDB
        if products:
            self._add_products_to_db(products)
        else:
            print("❌ Цветочные продукты не найдены!")
    
    def _create_enhanced_search_text(self, row):
        """Создаем улучшенный текст для поиска цветов"""
        parts = []
        
        # Основной текст
        primary_text = row.get('primary_text', '')
        if primary_text:
            parts.append(primary_text)
        
        # Тип цветов с акцентом
        flower_type = row.get('flower_type', '')
        if flower_type and flower_type != 'Difuzor aromă':
            parts.append(f"Цветы: {flower_type}")
        
        # Категория (только цветочные)
        category = row.get('category', '')
        if category in self.flower_categories:
            if 'Bouquet' in category:
                parts.append("Букет цветов")
            elif 'Rose' in category:
                parts.append("Розы тандафири")
            elif 'Peonies' in category:
                parts.append("Пионы бujori")
            elif 'Basket' in category:
                parts.append("Корзина цветов кош")
            elif 'Wedding' in category or 'Bride' in category:
                parts.append("Свадебные цветы nuntă")
        
        # Цена
        price = self._parse_price(row.get('price', '0'))
        if price > 0:
            parts.append(f"Цена: {price} MDL")
        
        # Добавляем ключевые слова для лучшего поиска
        parts.append("flori buchete cadou")
        
        return " | ".join(parts)
    
    def search_flowers(self, query, limit=5, price_max=None, verified_only=False):
        """
        Поиск ТОЛЬКО цветочных продуктов с улучшенной фильтрацией
        
        Args:
            query: поисковый запрос
            limit: максимум результатов
            price_max: максимальная цена
            verified_only: только верифицированные
        """
        try:
            # Базовые фильтры - только цветочные продукты
            where_conditions = {
                "is_flower_product": "True"
            }
            
            # Дополнительные фильтры
            additional_filters = []
            
            if verified_only:
                additional_filters.append({"is_verified": "True"})
            
            if price_max:
                additional_filters.append({"price": {"$lte": price_max}})
            
            # Объединяем фильтры
            if additional_filters:
                where_conditions = {
                    "$and": [where_conditions] + additional_filters
                }
            
            # Выполняем поиск
            search_params = {
                'query_texts': [query],
                'n_results': limit,
                'where': where_conditions
            }
            
            results = self.collection.query(**search_params)
            
            products = []
            if results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    metadata = results['metadatas'][0][i]
                    
                    # Дополнительная проверка что это цветы
                    if metadata.get('category') in self.non_flower_categories:
                        continue
                    
                    product = {
                        'id': results['ids'][0][i],
                        'name': metadata['name'],
                        'price': metadata['price'],
                        'category': metadata['category'],
                        'flowers': metadata['flowers'],
                        'url': metadata['url'],
                        'score': round(1 - results['distances'][0][i], 3),
                        'text': results['documents'][0][i],
                        'is_verified': metadata.get('is_verified') == 'True',
                        'url_functional': metadata.get('url_functional') == 'True'
                    }
                    products.append(product)
            
            # Сортируем по релевантности
            products.sort(key=lambda x: x['score'], reverse=True)
            
            return products
            
        except Exception as e:
            print(f"❌ Ошибка поиска цветов: {e}")
            return []
    
    def search_by_category(self, category, limit=10):
        """Поиск по конкретной цветочной категории"""
        try:
            if category not in self.flower_categories:
                print(f"⚠️ Категория '{category}' не является цветочной")
                return []
            
            where_conditions = {
                "$and": [
                    {"category": category},
                    {"is_flower_product": "True"}
                ]
            }
            
            results = self.collection.get(
                where=where_conditions,
                limit=limit
            )
            
            products = []
            if results['metadatas']:
                for i, metadata in enumerate(results['metadatas']):
                    product = {
                        'id': results['ids'][i],
                        'name': metadata['name'],
                        'price': metadata['price'],
                        'category': metadata['category'],
                        'flowers': metadata['flowers'],
                        'url': metadata['url']
                    }
                    products.append(product)
            
            return products
            
        except Exception as e:
            print(f"❌ Ошибка поиска по категории: {e}")
            return []
    
    def get_popular_flowers(self, limit=10):
        """Получить популярные цветочные продукты"""
        try:
            # Популярные категории в порядке приоритета
            popular_categories = [
                "Classic Bouquets",
                "French Roses", 
                "Author'S Bouquets",
                "Premium"
            ]
            
            products = []
            for category in popular_categories:
                category_products = self.search_by_category(category, limit=3)
                products.extend(category_products)
                if len(products) >= limit:
                    break
            
            return products[:limit]
            
        except Exception as e:
            print(f"❌ Ошибка получения популярных: {e}")
            return []
    
    def search_in_budget(self, query, max_price, limit=5):
        """Поиск цветов в заданном бюджете"""
        return self.search_flowers(
            query=query,
            limit=limit,
            price_max=max_price,
            verified_only=False
        )
    
    # Остальные методы остаются те же
    def _is_valid_product(self, row):
        """Проверяем валидность продукта"""
        if row.get('product_exists', 'False') != 'True':
            return False
        
        if not row.get('primary_text', '').strip():
            return False
        
        price = self._parse_price(row.get('price', '0'))
        if price <= 0:
            return False
        
        return True
    
    def _get_best_url(self, row):
        """Выбираем лучший URL для продукта"""
        if row.get('url_fixed') and row.get('url_fixed').strip():
            return row['url_fixed']
        elif row.get('url') and row.get('url').strip():
            return row['url']
        elif row.get('original_url') and row.get('original_url').strip():
            return row['original_url']
        else:
            return ""
    
    def _parse_price(self, price_str):
        """Парсим цену из строки"""
        if not price_str:
            return 0
        
        import re
        clean_price = re.sub(r'[^\d.]', '', str(price_str))
        
        try:
            return float(clean_price)
        except:
            return 0
    
    def _add_products_to_db(self, products):
        """Добавляем продукты в базу данных"""
        try:
            # Очищаем старые данные
            self.client.delete_collection("products")
            self.collection = self.client.create_collection("products")
        except:
            pass
        
        # Подготавливаем данные
        ids = [p['id'] for p in products]
        documents = [p['text'] for p in products]
        metadatas = [{
            'name': p['name'],
            'price': p['price'],
            'category': p['category'],
            'flowers': p['flowers'],
            'url': p['url'],
            'collection_id': p['collection_id'],
            'is_verified': p['is_verified'],
            'url_functional': p['url_functional'],
            'product_exists': p['product_exists'],
            'is_flower_product': p['is_flower_product']
        } for p in products]
        
        # Добавляем в ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Загружено {len(products)} ЦВЕТОЧНЫХ продуктов в ChromaDB!")
    
    def get_stats(self):
        """Получаем статистику только цветочных продуктов"""
        try:
            all_results = self.collection.get(
                where={"is_flower_product": "True"}
            )
            
            total_count = len(all_results['ids']) if all_results['ids'] else 0
            
            verified_count = 0
            functional_count = 0
            categories = set()
            price_ranges = {"budget": 0, "medium": 0, "premium": 0}
            
            if all_results['metadatas']:
                for metadata in all_results['metadatas']:
                    if metadata.get('is_verified') == 'True':
                        verified_count += 1
                    if metadata.get('url_functional') == 'True':
                        functional_count += 1
                    if metadata.get('category'):
                        categories.add(metadata['category'])
                    
                    # Анализ цен
                    price = metadata.get('price', 0)
                    if price < 500:
                        price_ranges["budget"] += 1
                    elif price < 1500:
                        price_ranges["medium"] += 1
                    else:
                        price_ranges["premium"] += 1
            
            return {
                'total_flowers': total_count,
                'verified_flowers': verified_count,
                'functional_urls': functional_count,
                'flower_categories': sorted(list(categories)),
                'price_distribution': price_ranges
            }
            
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {'error': str(e)}
    
    def get_flower_categories(self):
        """Получаем список только цветочных категорий"""
        return sorted(list(self.flower_categories))

# Создаем глобальный экземпляр ГОТОВОГО поиска
vector_search = ProductionVectorSearch()

# Удобные функции для использования
def search_flowers(query, limit=5):
    """Поиск цветов (основная функция)"""
    return vector_search.search_flowers(query, limit)

def search_verified_flowers(query, limit=5):
    """Поиск только верифицированных цветов"""
    return vector_search.search_flowers(query, limit, verified_only=True)

def search_flowers_in_budget(query, max_price, limit=5):
    """Поиск цветов в бюджете"""
    return vector_search.search_in_budget(query, max_price, limit)

def get_popular_flowers(limit=10):
    """Популярные цветы"""
    return vector_search.get_popular_flowers(limit)
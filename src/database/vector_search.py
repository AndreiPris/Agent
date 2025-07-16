"""
УНИВЕРСАЛЬНАЯ система поиска XOFlowers
Поддерживает поиск как по цветам, так и по всем товарам
"""

import os
import csv
import chromadb
from sentence_transformers import SentenceTransformer

class UniversalXOFlowersSearch:
    def __init__(self):
        # Создаем базу данных ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db_flowers")
        
        # Загружаем модель для создания векторов
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Создаем ДВЕ коллекции
        try:
            # Коллекция только для цветов
            self.flowers_collection = self.client.create_collection("flowers_only")
        except:
            self.flowers_collection = self.client.get_collection("flowers_only")
            
        try:
            # Коллекция для ВСЕХ товаров
            self.all_products_collection = self.client.create_collection("all_products")
        except:
            self.all_products_collection = self.client.get_collection("all_products")
        
        # Категории товаров
        self.flower_categories = {
            "Author'S Bouquets", "Classic Bouquets", "French Roses",
            "Mono/Duo Bouquets", "Basket / Boxes With Flowers",
            "Bride'S Bouquet", "Premium", "Peonies",
            "Mourning Flower Arrangement", "St. Valentine'S Day"
        }
        
        self.non_flower_categories = {
            "Chando",  # Диффузоры
            "Soft Toys",  # Игрушки
            "Greeting Card",  # Открытки
            "Additional Accessories / Vases",  # Аксессуары
            "Sweets"  # Сладости
        }
        
        # Ключевые слова для автоматического определения типа поиска
        self.flower_keywords = {
            'ro': ['flori', 'buchet', 'trandafiri', 'bujori', 'nuntă', 'aniversare', 'cadou'],
            'en': ['flowers', 'bouquet', 'roses', 'peonies', 'wedding', 'birthday', 'gift'],
            'ru': ['цветы', 'букет', 'розы', 'пионы', 'свадьба', 'день рождения', 'подарок']
        }
        
        self.non_flower_keywords = {
            'ro': ['difuzor', 'aromă', 'jucărie', 'felicitare', 'dulciuri', 'ciocolată'],
            'en': ['diffuser', 'aroma', 'toy', 'card', 'sweets', 'chocolate'],
            'ru': ['диффузор', 'аромат', 'игрушка', 'открытка', 'сладости', 'шоколад']
        }
        
        print("✅ Universal XOFlowers search system initialized")
    
    def load_products_from_csv(self, csv_filename="final_products_case_standardized.csv"):
        """Загружаем ВСЕ продукты в обе коллекции"""
        csv_path = f"data/{csv_filename}"
        
        if not os.path.exists(csv_path):
            csv_path = "data/chunks_data.csv"
            if not os.path.exists(csv_path):
                print("❌ Файлы данных не найдены!")
                return
            print(f"⚠️ Используем старый файл: {csv_path}")
        else:
            print(f"✅ Используем новый файл: {csv_path}")
        
        all_products = []
        flower_products = []
        total_rows = 0
        valid_products = 0
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                total_rows += 1
                
                # Проверяем что это продукт
                if row.get('chunk_type') != 'product':
                    continue
                
                # Фильтруем только существующие продукты
                if not self._is_valid_product(row):
                    continue
                
                valid_products += 1
                category = row.get('category', '')
                
                # Создаем базовый продукт
                product = self._create_product_object(row, valid_products)
                
                # Добавляем ВСЕ валидные продукты в общую коллекцию
                all_products.append(product)
                
                # Добавляем только цветы в цветочную коллекцию
                if category in self.flower_categories:
                    flower_product = product.copy()
                    flower_product['search_text'] = self._create_flower_search_text(row)
                    flower_product['is_flower'] = 'True'
                    flower_products.append(flower_product)
        
        print(f"📊 Обработано строк: {total_rows}")
        print(f"✅ Всего товаров: {len(all_products)}")
        print(f"🌸 Из них цветов: {len(flower_products)}")
        
        # Загружаем в обе коллекции
        if all_products:
            self._add_products_to_collection(all_products, self.all_products_collection, "all_products")
        
        if flower_products:
            self._add_products_to_collection(flower_products, self.flowers_collection, "flowers_only")
    
    # Методы обратной совместимости со старым интерфейсом
    def search(self, query, limit=5, only_verified=False, only_functional=False):
        """Обратная совместимость со старым интерфейсом"""
        return self.smart_search(query, limit)
    
    def get_categories(self):
        """Обратная совместимость - получаем все категории"""
        try:
            all_results = self.all_products_collection.get()
            categories = set()
            
            if all_results['metadatas']:
                for metadata in all_results['metadatas']:
                    if metadata.get('category'):
                        categories.add(metadata['category'])
            
            return sorted(list(categories))
        except Exception as e:
            print(f"❌ Ошибка получения категорий: {e}")
            return []

    def smart_search(self, query, limit=5, force_flowers_only=False, force_all_products=False, 
                    price_min=None, price_max=None, budget=None):
        """
        УМНЫЙ поиск с поддержкой цены
        
        Args:
            query: поисковый запрос
            limit: максимум результатов
            force_flowers_only: принудительно искать только цветы
            force_all_products: принудительно искать по всем товарам
            price_min: минимальная цена
            price_max: максимальная цена
            budget: бюджет (автоматически устанавливает price_max)
        """
        # Если указан бюджет, устанавливаем максимальную цену
        if budget and not price_max:
            price_max = budget
        
        # Извлекаем цену из запроса если не указана явно
        if not price_min and not price_max and not budget:
            extracted_budget = self._extract_price_from_query(query)
            if extracted_budget:
                price_max = extracted_budget
                print(f"💰 Автоматически извлечен бюджет: {price_max} MDL")
        
        if force_flowers_only:
            return self.search_flowers_only(query, limit, price_min, price_max)
        elif force_all_products:
            return self.search_all_products(query, limit, price_min=price_min, price_max=price_max)
        else:
            # Автоматическое определение типа поиска
            search_type = self._detect_search_type(query)
            
            if search_type == "flowers":
                print(f"🌸 Автоматический поиск по ЦВЕТАМ для: '{query}'")
                return self.search_flowers_only(query, limit, price_min, price_max)
            elif search_type == "non_flowers":
                print(f"🎁 Автоматический поиск по ВСЕМ ТОВАРАМ для: '{query}'")
                return self.search_all_products(query, limit, price_min=price_min, price_max=price_max)
            else:
                # Неопределенный запрос - комбинированный поиск
                print(f"🔍 Комбинированный поиск с фильтром цены для: '{query}'")
                return self.combined_search(query, limit, price_min, price_max)
    
    def search_flowers_only(self, query, limit=5, price_min=None, price_max=None, verified_only=False):
        """Поиск ТОЛЬКО по цветам с фильтром цены"""
        try:
            where_conditions = {"is_flower": "True"}
            
            additional_filters = []
            if verified_only:
                additional_filters.append({"is_verified": "True"})
            
            # Добавляем фильтры по цене
            if price_min is not None:
                additional_filters.append({"price": {"$gte": price_min}})
            if price_max is not None:
                additional_filters.append({"price": {"$lte": price_max}})
            
            if additional_filters:
                where_conditions = {
                    "$and": [where_conditions] + additional_filters
                }
            
            results = self.flowers_collection.query(
                query_texts=[query],
                n_results=limit,
                where=where_conditions
            )
            
            return self._format_results(results, "🌸 ЦВЕТЫ")
            
        except Exception as e:
            print(f"❌ Ошибка поиска цветов: {e}")
            return []
    
    def search_all_products(self, query, limit=5, category_filter=None, price_min=None, price_max=None):
        """Поиск по ВСЕМ товарам с фильтром цены"""
        try:
            where_conditions = {}
            additional_filters = []
            
            if category_filter:
                additional_filters.append({"category": category_filter})
            
            # Добавляем фильтры по цене
            if price_min is not None:
                additional_filters.append({"price": {"$gte": price_min}})
            if price_max is not None:
                additional_filters.append({"price": {"$lte": price_max}})
            
            if additional_filters:
                where_conditions = {"$and": additional_filters}
            
            search_params = {
                'query_texts': [query],
                'n_results': limit
            }
            
            if where_conditions:
                search_params['where'] = where_conditions
            
            results = self.all_products_collection.query(**search_params)
            
            return self._format_results(results, "🛍️ ВСЕ ТОВАРЫ")
            
        except Exception as e:
            print(f"❌ Ошибка поиска всех товаров: {e}")
            return []
    
    def combined_search(self, query, limit=5, price_min=None, price_max=None):
        """Комбинированный поиск - цветы + другие товары с фильтром цены"""
        flower_limit = max(1, limit // 2)
        other_limit = limit - flower_limit
        
        flowers = self.search_flowers_only(query, flower_limit, price_min, price_max)
        others = self.search_all_products(query, other_limit, price_min=price_min, price_max=price_max)
        
        # Объединяем и сортируем по релевантности
        all_results = flowers + others
        all_results.sort(key=lambda x: x.get('score', 0), reverse=True)
        
        return all_results[:limit]
    
    def _extract_price_from_query(self, query):
        """Извлекаем цену/бюджет из запроса пользователя"""
        import re
        
        query_lower = query.lower()
        
        # Паттерны для извлечения цены на румынском, русском и английском
        price_patterns = [
            # Румынский
            r'până la (\d+)\s*(?:lei|mdl|md)',
            r'sub (\d+)\s*(?:lei|mdl|md)',
            r'mai ieftin de (\d+)\s*(?:lei|mdl|md)',
            r'buget(?:ul)?\s*(?:de|până la)?\s*(\d+)\s*(?:lei|mdl|md)',
            r'maxim\s*(\d+)\s*(?:lei|mdl|md)',
            r'(\d+)\s*(?:lei|mdl|md)\s*maxim',
            
            # Русский
            r'до (\d+)\s*(?:лей|mdl|md)',
            r'не более (\d+)\s*(?:лей|mdl|md)',
            r'в пределах (\d+)\s*(?:лей|mdl|md)',
            r'бюджет\s*(?:до)?\s*(\d+)\s*(?:лей|mdl|md)',
            r'максимум\s*(\d+)\s*(?:лей|mdl|md)',
            
            # Английский
            r'under (\d+)\s*(?:mdl|lei|md)',
            r'up to (\d+)\s*(?:mdl|lei|md)',
            r'max (\d+)\s*(?:mdl|lei|md)',
            r'budget\s*(?:of)?\s*(\d+)\s*(?:mdl|lei|md)',
            
            # Общие числовые паттерны
            r'(\d+)\s*(?:лей|lei|mdl|md)',
            r'(\d+)\s*maximum',
            r'(\d+)\s*max'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query_lower)
            if match:
                try:
                    price = int(match.group(1))
                    # Проверяем разумность цены (от 10 до 50000 MDL)
                    if 10 <= price <= 50000:
                        return price
                except (ValueError, IndexError):
                    continue
        
        return None
    
    def search_by_price_range(self, price_min, price_max, query="", limit=10, flowers_only=False):
        """Поиск товаров в ценовом диапазоне"""
        if flowers_only:
            return self.search_flowers_only(query or "flori frumoase", limit, price_min, price_max)
        else:
            return self.search_all_products(query or "cadou frumos", limit, price_min=price_min, price_max=price_max)
    
    def search_budget_flowers(self, budget, query="flori frumoase", limit=10):
        """Поиск цветов в заданном бюджете"""
        print(f"💰 Поиск цветов до {budget} MDL")
        return self.search_flowers_only(query, limit, price_max=budget)
    
    def search_budget_gifts(self, budget, query="cadou frumos", limit=10):
        """Поиск подарков в заданном бюджете"""
        print(f"🎁 Поиск подарков до {budget} MDL")
        return self.search_all_products(query, limit, price_max=budget)
    
    def get_price_suggestions(self, query="", flowers_only=False):
        """Получить предложения по ценовым категориям"""
        price_ranges = [
            {"name": "Бюджетные", "min": 0, "max": 500, "emoji": "💰"},
            {"name": "Средние", "min": 500, "max": 1500, "emoji": "💎"},
            {"name": "Премиум", "min": 1500, "max": 3000, "emoji": "👑"},
            {"name": "Люкс", "min": 3000, "max": 10000, "emoji": "💎✨"}
        ]
        
        suggestions = []
        for price_range in price_ranges:
            products = self.search_by_price_range(
                price_range["min"], 
                price_range["max"], 
                query, 
                limit=3, 
                flowers_only=flowers_only
            )
            
            if products:
                suggestions.append({
                    "range": price_range,
                    "products": products,
                    "count": len(products)
                })
        
        return suggestions
    
    def _detect_search_type(self, query):
        """Определяем тип поиска по ключевым словам"""
        query_lower = query.lower()
        
        flower_score = 0
        non_flower_score = 0
        
        # Проверяем ключевые слова для цветов
        for lang, keywords in self.flower_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    flower_score += 1
        
        # Проверяем ключевые слова для не-цветов
        for lang, keywords in self.non_flower_keywords.items():
            for keyword in keywords:
                if keyword in query_lower:
                    non_flower_score += 2  # Больший вес для точного совпадения
        
        if non_flower_score > flower_score:
            return "non_flowers"
        elif flower_score > 0:
            return "flowers"
        else:
            return "mixed"
    
    def _create_product_object(self, row, product_id):
        """Создаем объект продукта"""
        return {
            'id': row.get('chunk_id', f'product_{product_id}'),
            'search_text': self._create_universal_search_text(row),
            'name': row.get('primary_text', '')[:150],
            'price': self._parse_price(row.get('price', '0')),
            'category': row.get('category', ''),
            'flowers': row.get('flower_type', ''),
            'url': self._get_best_url(row),
            'collection_id': row.get('collection_id', ''),
            'is_verified': row.get('is_verified', 'False'),
            'url_functional': row.get('url_functional', 'False'),
            'product_exists': row.get('product_exists', 'False')
        }
    
    def _create_universal_search_text(self, row):
        """Создаем универсальный поисковый текст"""
        parts = []
        
        # Основной текст
        if row.get('primary_text'):
            parts.append(row['primary_text'])
        
        # Категория
        if row.get('category'):
            parts.append(f"Категория: {row['category']}")
        
        # Тип продукта
        if row.get('flower_type'):
            parts.append(f"Тип: {row['flower_type']}")
        
        # Цена
        price = self._parse_price(row.get('price', '0'))
        if price > 0:
            parts.append(f"Цена: {price} MDL")
        
        return " | ".join(parts)
    
    def _create_flower_search_text(self, row):
        """Создаем поисковый текст с акцентом на цветы"""
        parts = []
        
        if row.get('primary_text'):
            parts.append(row['primary_text'])
        
        # Цветочные ключевые слова
        flower_type = row.get('flower_type', '')
        if flower_type and 'Difuzor' not in flower_type:
            parts.append(f"Цветы: {flower_type}")
        
        category = row.get('category', '')
        if 'Bouquet' in category:
            parts.append("Букет цветов flori buchet")
        elif 'Rose' in category:
            parts.append("Розы trandafiri roses")
        elif 'Peonies' in category:
            parts.append("Пионы bujori peonies")
        
        price = self._parse_price(row.get('price', '0'))
        if price > 0:
            parts.append(f"Цена: {price} MDL")
        
        return " | ".join(parts)
    
    def _format_results(self, results, source_label):
        """Форматируем результаты поиска"""
        products = []
        if results['documents'][0]:
            for i in range(len(results['documents'][0])):
                metadata = results['metadatas'][0][i]
                
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
                    'url_functional': metadata.get('url_functional') == 'True',
                    'source': source_label
                }
                products.append(product)
        
        products.sort(key=lambda x: x['score'], reverse=True)
        return products
    
    def _add_products_to_collection(self, products, collection, collection_name):
        """Добавляем продукты в коллекцию"""
        try:
            # Очищаем коллекцию
            self.client.delete_collection(collection_name)
            collection = self.client.create_collection(collection_name)
            
            # Обновляем ссылку
            if collection_name == "flowers_only":
                self.flowers_collection = collection
            else:
                self.all_products_collection = collection
        except:
            pass
        
        # Подготавливаем данные
        ids = [p['id'] for p in products]
        documents = [p['search_text'] for p in products]
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
            'is_flower': p.get('is_flower', 'False')
        } for p in products]
        
        # Добавляем в ChromaDB
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Загружено {len(products)} продуктов в коллекцию '{collection_name}'")
    
    # Вспомогательные методы (те же что и раньше)
    def _is_valid_product(self, row):
        if row.get('product_exists', 'False') != 'True':
            return False
        if not row.get('primary_text', '').strip():
            return False
        price = self._parse_price(row.get('price', '0'))
        if price <= 0:
            return False
        return True
    
    def _get_best_url(self, row):
        if row.get('url_fixed') and row.get('url_fixed').strip():
            return row['url_fixed']
        elif row.get('url') and row.get('url').strip():
            return row['url']
        elif row.get('original_url') and row.get('original_url').strip():
            return row['original_url']
        else:
            return ""
    
    def _parse_price(self, price_str):
        if not price_str:
            return 0
        import re
        clean_price = re.sub(r'[^\d.]', '', str(price_str))
        try:
            return float(clean_price)
        except:
            return 0
    
    def get_stats(self):
        """Получаем статистику по обеим коллекциям (обратная совместимость)"""
        try:
            all_results = self.all_products_collection.get()
            flower_results = self.flowers_collection.get()
            
            total_count = len(all_results['ids']) if all_results['ids'] else 0
            flower_count = len(flower_results['ids']) if flower_results['ids'] else 0
            
            verified_count = 0
            functional_count = 0
            categories = set()
            
            # Анализируем метаданные всех продуктов
            if all_results['metadatas']:
                for metadata in all_results['metadatas']:
                    if metadata.get('is_verified') == 'True':
                        verified_count += 1
                    if metadata.get('url_functional') == 'True':
                        functional_count += 1
                    if metadata.get('category'):
                        categories.add(metadata['category'])
            
            return {
                'total_products': total_count,
                'verified_products': verified_count,
                'functional_urls': functional_count,
                'categories_count': len(categories),
                'categories': sorted(list(categories)),
                'flower_products': flower_count,
                'collections': ['all_products', 'flowers_only']
            }
            
        except Exception as e:
            print(f"❌ Ошибка получения статистики: {e}")
            return {'error': str(e)}

# Создаем глобальный экземпляр универсального поиска
universal_search = UniversalXOFlowersSearch()

# Удобные функции для использования с поддержкой цены
def smart_search(query, limit=5, budget=None, price_min=None, price_max=None):
    """Умный поиск - автоматически определяет тип с поддержкой цены"""
    return universal_search.smart_search(query, limit, budget=budget, price_min=price_min, price_max=price_max)

def search_flowers_only(query, limit=5, budget=None, price_min=None, price_max=None):
    """Поиск только цветов с фильтром цены"""
    return universal_search.search_flowers_only(query, limit, price_min, price_max or budget)

def search_all_products(query, limit=5, budget=None, price_min=None, price_max=None):
    """Поиск по всем товарам с фильтром цены"""
    return universal_search.search_all_products(query, limit, price_min=price_min, price_max=price_max or budget)

def search_gifts_and_accessories(query, limit=5, budget=None):
    """Поиск подарков и аксессуаров с бюджетом"""
    return universal_search.search_all_products(query, limit, price_max=budget)

def search_budget_flowers(budget, query="flori frumoase", limit=10):
    """Поиск цветов в бюджете"""
    return universal_search.search_budget_flowers(budget, query, limit)

def search_budget_gifts(budget, query="cadou frumos", limit=10):
    """Поиск подарков в бюджете"""
    return universal_search.search_budget_gifts(budget, query, limit)

def search_by_price_range(price_min, price_max, query="", limit=10, flowers_only=False):
    """Поиск в ценовом диапазоне"""
    return universal_search.search_by_price_range(price_min, price_max, query, limit, flowers_only)

def get_price_suggestions(query="", flowers_only=False):
    """Получить предложения по ценовым категориям"""
    return universal_search.get_price_suggestions(query, flowers_only)

# Обратная совместимость
vector_search = universal_search

def search_flowers(query, limit=5, budget=None):
    """Обратная совместимость с поддержкой бюджета"""
    return universal_search.search_flowers_only(query, limit, price_max=budget)

def search_flowers_in_budget(query, max_price, limit=5):
    """Поиск цветов в бюджете (обратная совместимость)"""
    return universal_search.search_budget_flowers(max_price, query, limit)
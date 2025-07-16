# ОБНОВЛЕННЫЙ ФАЙЛ: src/database/vector_search.py
# Заменить существующий файл на этот код

"""
Простой векторный поиск для XOFlowers (обновлен для нового CSV)
"""

import os
import csv
import chromadb
from sentence_transformers import SentenceTransformer

class SimpleVectorSearch:
    def __init__(self):
        # Создаем базу данных ChromaDB
        self.client = chromadb.PersistentClient(path="./chroma_db")
        
        # Загружаем модель для создания векторов
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Создаем коллекцию для продуктов
        try:
            self.collection = self.client.create_collection("products")
        except:
            self.collection = self.client.get_collection("products")
        
        print("✅ Векторный поиск готов!")
    
    def load_products_from_csv(self, csv_filename="final_products_case_standardized.csv"):
        """Загружаем продукты из нового CSV файла"""
        csv_path = f"data/{csv_filename}"
        
        if not os.path.exists(csv_path):
            # Попробуем старый файл как fallback
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
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                total_rows += 1
                
                # Проверяем что это продукт
                if row.get('chunk_type') != 'product':
                    continue
                
                # Фильтруем только существующие и верифицированные продукты
                if not self._is_valid_product(row):
                    continue
                
                valid_products += 1
                
                # Создаем текст для поиска
                search_text = self._create_search_text(row)
                
                # Выбираем лучший URL
                best_url = self._get_best_url(row)
                
                product = {
                    'id': row.get('chunk_id', f'product_{valid_products}'),
                    'text': search_text,
                    'name': row.get('primary_text', '')[:100],
                    'price': self._parse_price(row.get('price', '0')),
                    'category': row.get('category', ''),
                    'flowers': row.get('flower_type', ''),
                    'url': best_url,
                    'collection_id': row.get('collection_id', ''),
                    'is_verified': row.get('is_verified', 'false'),
                    'url_functional': row.get('url_functional', 'false'),
                    'product_exists': row.get('product_exists', 'false')
                }
                
                products.append(product)
        
        print(f"📊 Обработано строк: {total_rows}")
        print(f"🌸 Валидных продуктов: {valid_products}")
        
        # Добавляем все продукты в ChromaDB
        if products:
            self._add_products_to_db(products)
        else:
            print("❌ Продукты не найдены!")
    
    def _is_valid_product(self, row):
        """Проверяем что продукт валиден для индексации"""
        # Проверяем что продукт существует
        product_exists = str(row.get('product_exists', 'false')).lower()
        if product_exists == 'false':
            return False
        
        # Проверяем что есть описание
        if not row.get('primary_text', '').strip():
            return False
        
        # Проверяем что есть цена
        price = row.get('price', '0')
        if not price or price == '0':
            return False
        
        return True
    
    def _create_search_text(self, row):
        """Создаем текст для поиска из данных продукта"""
        parts = []
        
        # Основное описание
        if row.get('primary_text'):
            parts.append(row['primary_text'])
        
        # Тип цветов
        if row.get('flower_type'):
            parts.append(row['flower_type'])
        
        # Категория
        if row.get('category'):
            parts.append(row['category'])
        
        return ' | '.join(parts)
    
    def _get_best_url(self, row):
        """Выбираем лучший URL из доступных"""
        # Проверяем функциональность URL
        url_functional = str(row.get('url_functional', 'false')).lower() == 'true'
        
        if url_functional and row.get('url'):
            return row['url']
        
        # Если основной URL не работает, пробуем original_url
        if row.get('original_url'):
            return row['original_url']
        
        # Fallback к обычному URL
        return row.get('url', '')
    
    def _parse_price(self, price_str):
        """Парсим цену из строки"""
        if not price_str:
            return '0'
        
        # Если уже число
        try:
            float(price_str)
            return str(price_str)
        except:
            pass
        
        # Извлекаем числа из строки
        import re
        numbers = re.findall(r'\d+', str(price_str))
        if numbers:
            return numbers[0]
        
        return '0'
    
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
            'product_exists': p['product_exists']
        } for p in products]
        
        # Добавляем в ChromaDB
        self.collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Загружено {len(products)} продуктов в ChromaDB!")
    
    def search(self, query, limit=5, only_verified=True, only_functional=True):
        """Поиск продуктов с дополнительными фильтрами"""
        try:
            # Строим фильтры для поиска
            where_conditions = {}
            
            if only_verified:
                where_conditions["is_verified"] = "true"
            
            if only_functional:
                where_conditions["url_functional"] = "true"
            
            # Выполняем поиск
            search_params = {
                'query_texts': [query],
                'n_results': limit
            }
            
            # Добавляем фильтры если есть
            if where_conditions:
                search_params['where'] = where_conditions
            
            results = self.collection.query(**search_params)
            
            products = []
            if results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    product = {
                        'id': results['ids'][0][i],
                        'name': results['metadatas'][0][i]['name'],
                        'price': results['metadatas'][0][i]['price'],
                        'category': results['metadatas'][0][i]['category'],
                        'flowers': results['metadatas'][0][i]['flowers'],
                        'url': results['metadatas'][0][i]['url'],
                        'score': 1 - results['distances'][0][i],  # Релевантность
                        'is_verified': results['metadatas'][0][i].get('is_verified', 'false'),
                        'url_functional': results['metadatas'][0][i].get('url_functional', 'false')
                    }
                    products.append(product)
            
            return products
        
        except Exception as e:
            print(f"❌ Ошибка поиска: {e}")
            # Fallback поиск без фильтров
            try:
                results = self.collection.query(
                    query_texts=[query],
                    n_results=limit
                )
                
                products = []
                if results['documents'][0]:
                    for i in range(len(results['documents'][0])):
                        product = {
                            'id': results['ids'][0][i],
                            'name': results['metadatas'][0][i]['name'],
                            'price': results['metadatas'][0][i]['price'],
                            'category': results['metadatas'][0][i]['category'],
                            'flowers': results['metadatas'][0][i]['flowers'],
                            'url': results['metadatas'][0][i]['url'],
                            'score': 1 - results['distances'][0][i]
                        }
                        products.append(product)
                
                return products
            except:
                return []
    
    def get_categories(self):
        """Получить все категории"""
        try:
            all_results = self.collection.get()
            categories = set()
            
            for metadata in all_results['metadatas']:
                categories.add(metadata['category'])
            
            return sorted(list(categories))
        except:
            return []
    
    def get_stats(self):
        """Получить статистику базы данных"""
        try:
            all_results = self.collection.get()
            total_products = len(all_results['ids'])
            
            verified_count = 0
            functional_urls = 0
            categories = set()
            
            for metadata in all_results['metadatas']:
                if metadata.get('is_verified') == 'true':
                    verified_count += 1
                if metadata.get('url_functional') == 'true':
                    functional_urls += 1
                categories.add(metadata['category'])
            
            return {
                'total_products': total_products,
                'verified_products': verified_count,
                'functional_urls': functional_urls,
                'categories_count': len(categories),
                'categories': sorted(list(categories))
            }
        except Exception as e:
            return {'error': str(e)}

# Создаем глобальный объект поиска
vector_search = SimpleVectorSearch()
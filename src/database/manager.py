"""
Database Manager for XOFlowers AI Agent
Manages ChromaDB connections and operations
"""

import os
import sys
import json
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add config to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'config'))

try:
    import chromadb
    from chromadb.config import Settings
    from sentence_transformers import SentenceTransformer
    HAS_CHROMADB = True
except ImportError:
    chromadb = None
    SentenceTransformer = None
    HAS_CHROMADB = False

from settings import DATABASE


class DatabaseManager:
    """
    Advanced database manager for XOFlowers AI Agent
    Handles ChromaDB operations and vector search
    """
    
    def __init__(self, db_path: str = None):
        """
        Initialize database manager
        
        Args:
            db_path: Path to ChromaDB database
        """
        self.db_path = db_path or DATABASE.get('chromadb_path', './chroma_db_flowers')
        self.embedding_model_name = DATABASE.get('embedding_model', 'all-MiniLM-L6-v2')
        self.collections = DATABASE.get('collections', {})
        
        # Initialize components
        self.client = None
        self.embedding_model = None
        self.initialized = False
        
        # Initialize if ChromaDB is available
        if HAS_CHROMADB:
            self._initialize_database()
    
    def _initialize_database(self):
        """Initialize ChromaDB client and embedding model"""
        try:
            # Initialize ChromaDB client
            self.client = chromadb.PersistentClient(path=self.db_path)
            
            # Initialize embedding model
            self.embedding_model = SentenceTransformer(self.embedding_model_name)
            
            self.initialized = True
            print(f"✅ Database initialized successfully at {self.db_path}")
            
        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            self.initialized = False
    
    def get_collection(self, collection_name: str):
        """Get or create a collection"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        try:
            # Try to get existing collection
            collection = self.client.get_collection(name=collection_name)
            return collection
        except Exception:
            # Create new collection if it doesn't exist
            return self.client.create_collection(name=collection_name)
    
    def add_documents(self, collection_name: str, documents: List[Dict[str, Any]]):
        """
        Add documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to add
        """
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        collection = self.get_collection(collection_name)
        
        # Prepare data for insertion
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            ids.append(doc.get('id', f"{collection_name}_{i}"))
            texts.append(doc.get('text', ''))
            metadatas.append(doc.get('metadata', {}))
        
        # Add to collection
        collection.add(
            documents=texts,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"✅ Added {len(documents)} documents to {collection_name}")
    
    def search_documents(self, collection_name: str, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for documents in a collection
        
        Args:
            collection_name: Name of the collection to search
            query: Search query
            n_results: Number of results to return
            
        Returns:
            List of search results
        """
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        collection = self.get_collection(collection_name)
        
        # Perform search
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['documents'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            })
        
        return formatted_results
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """Get statistics about a collection"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        collection = self.get_collection(collection_name)
        count = collection.count()
        
        return {
            'name': collection_name,
            'count': count,
            'embedding_model': self.embedding_model_name
        }
    
    def list_collections(self) -> List[str]:
        """List all available collections"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def delete_collection(self, collection_name: str):
        """Delete a collection"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        self.client.delete_collection(name=collection_name)
        print(f"🗑️ Deleted collection: {collection_name}")
    
    def backup_database(self, backup_path: str):
        """Create a backup of the database"""
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        
        # Implementation for backup
        # This is a placeholder - actual implementation depends on requirements
        print(f"📦 Creating backup at {backup_path}")
    
    def health_check(self) -> Dict[str, Any]:
        """Perform health check on database"""
        health_status = {
            'initialized': self.initialized,
            'chromadb_available': HAS_CHROMADB,
            'db_path': self.db_path,
            'embedding_model': self.embedding_model_name,
            'timestamp': datetime.now().isoformat()
        }
        
        if self.initialized:
            try:
                collections = self.list_collections()
                health_status['collections'] = collections
                health_status['collection_count'] = len(collections)
                health_status['status'] = 'healthy'
            except Exception as e:
                health_status['status'] = 'error'
                health_status['error'] = str(e)
        else:
            health_status['status'] = 'not_initialized'
        
        return health_status


# Global database instance
db_manager = DatabaseManager()


def get_database() -> DatabaseManager:
    """Get the global database manager instance"""
    return db_manager

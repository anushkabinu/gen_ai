"""
Phone Cache using ChromaDB with Sentence Transformers
Stores scraped phones to avoid re-scraping already cached data
Uses sentence-transformers for semantic search
"""
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import pandas as pd
import json
import logging
from typing import List, Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

class PhoneCache:
    """Manages phone data caching using ChromaDB with sentence-transformers"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize ChromaDB client with sentence-transformers
        
        Args:
            persist_directory: Directory to store ChromaDB data
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(path=str(self.persist_directory))
        
        # Use sentence-transformers for embeddings
        # Using 'all-MiniLM-L6-v2' - fast and efficient for semantic search
        self.embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
            model_name="all-MiniLM-L6-v2"
        )
        
        # Check if collection exists with different embedding function
        try:
            existing_collections = [col.name for col in self.client.list_collections()]
            if "phone_cache" in existing_collections:
                # Delete old collection if it exists with default embeddings
                try:
                    self.client.delete_collection("phone_cache")
                    logger.info("🔄 Deleted old collection, recreating with sentence-transformers")
                except:
                    pass
        except:
            pass
        
        # Create collection with sentence-transformers
        self.collection = self.client.get_or_create_collection(
            name="phone_cache",
            embedding_function=self.embedding_function,
            metadata={"description": "Cached scraped phone data with semantic search"}
        )
        
        logger.info(f"✅ Phone Cache initialized with sentence-transformers. {self.collection.count()} phones in cache")
    
    def search_in_cache(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Search for phones in cache by query
        
        Args:
            query: Search query (brand, model, etc.)
            limit: Maximum results to return
            
        Returns:
            List of cached phone dictionaries
        """
        try:
            count = self.collection.count()
            if count == 0:
                logger.info(f"📭 No cached results for query: '{query}' (cache empty)")
                return []

            n_results = min(limit, count)

            # Prefer using explicit embeddings for faster, deterministic nearest-neighbour search
            try:
                query_emb = self.embedding_function.embed_documents([query])
                results = self.collection.query(
                    query_embeddings=query_emb,
                    n_results=n_results,
                    include=["metadatas", "distances", "ids", "documents"]
                )
            except Exception:
                # Fallback to text query if embedding call fails
                results = self.collection.query(
                    query_texts=[query],
                    n_results=n_results,
                    include=["metadatas", "distances", "ids", "documents"]
                )

            if not results.get('ids') or len(results['ids'][0]) == 0:
                logger.info(f"📭 No cached results for query: '{query}'")
                return []

            # Convert results to list of dicts and include a relevance score
            cached_phones = []
            ids_list = results['ids'][0]
            metadatas = results['metadatas'][0]
            distances = results.get('distances', [[]])[0] if results.get('distances') is not None else [None] * len(ids_list)

            for i, phone_id in enumerate(ids_list):
                metadata = metadatas[i] if i < len(metadatas) else {}
                distance = distances[i] if i < len(distances) else None
                if distance is not None:
                    # Convert distance to an intuitive score (higher is better)
                    try:
                        score = round(max(0.0, (1.0 - float(distance))) * 100.0, 2)
                    except Exception:
                        score = None
                    metadata['_distance'] = float(distance)
                    metadata['_score'] = score

                cached_phones.append(metadata)

            logger.info(f"✅ Found {len(cached_phones)} cached phones for query: '{query}'")
            return cached_phones

        except Exception as e:
            logger.error(f"❌ Error searching cache: {e}")
            return []
    
    def add_phones(self, phones: List[Dict]) -> int:
        """
        Add phones to cache
        
        Args:
            phones: List of phone dictionaries
            
        Returns:
            Number of phones added
        """
        if not phones:
            return 0

        try:
            ids = []
            documents = []
            metadatas = []

            # Get existing ids to avoid re-adding duplicates
            existing_ids = set()
            try:
                all_items = self.collection.get(include=["ids"])
                for batch in all_items.get('ids', []):
                    for existing in batch:
                        existing_ids.add(existing)
            except Exception:
                existing_ids = set()

            for phone in phones:
                # Prefer using a deterministic ID from full_name and url if possible
                base = phone.get('full_name') or f"{phone.get('brand','')}_{phone.get('model','')}"
                url_part = phone.get('url', '')
                uid = f"{base}__{url_part}" if url_part else base
                phone_id = (
                    uid.replace(' ', '_').replace('/', '_').replace(':', '_').lower()
                )

                if phone_id in existing_ids:
                    # Skip duplicates
                    continue

                # Create searchable document (concatenate important fields)
                doc = " ".join([
                    str(phone.get('full_name', '')),
                    str(phone.get('brand', '')),
                    str(phone.get('model', '')),
                    str(phone.get('processor', '')),
                    str(phone.get('description', ''))
                ])

                # Store full phone data in metadata (include description)
                metadata = {
                    'full_name': str(phone.get('full_name', '')),
                    'brand': str(phone.get('brand', '')),
                    'model': str(phone.get('model', '')),
                    'price': int(phone.get('price', 0)),
                    'rating': float(phone.get('rating', 0)),
                    'ram': int(phone.get('ram', 0)),
                    'storage': int(phone.get('storage', 0)),
                    'camera_mp': int(phone.get('camera_mp', 0)),
                    'battery_mah': int(phone.get('battery_mah', 0)),
                    'display_inches': float(phone.get('display_inches', 0)),
                    'processor': str(phone.get('processor', '')),
                    'category': str(phone.get('category', '')),
                    'source': str(phone.get('source', '')),
                    'url': str(phone.get('url', '')),
                    'description': str(phone.get('description', 'N/A'))
                }

                ids.append(phone_id)
                documents.append(doc.lower())
                metadatas.append(metadata)

            if not ids:
                logger.info("ℹ️ No new phones to add to cache (all duplicates)")
                return 0

            # Add to collection (upsert to avoid duplicates)
            self.collection.upsert(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )

            logger.info(f"✅ Added {len(ids)} phones to cache. Total: {self.collection.count()}")
            return len(ids)

        except Exception as e:
            logger.error(f"❌ Error adding phones to cache: {e}")
            return 0
    
    def get_all_cached_phones(self) -> pd.DataFrame:
        """
        Get all cached phones as DataFrame
        
        Returns:
            DataFrame of all cached phones
        """
        try:
            count = self.collection.count()
            if count == 0:
                return pd.DataFrame()
            
            # Get all items from collection
            results = self.collection.get()
            
            if not results['ids']:
                return pd.DataFrame()
            
            # Convert to DataFrame
            phones_list = results['metadatas']
            df = pd.DataFrame(phones_list)
            
            logger.info(f"📦 Retrieved {len(df)} phones from cache")
            return df

        except Exception as e:
            logger.error(f"❌ Error getting cached phones: {e}")
            return pd.DataFrame()

    def bulk_ingest_from_file(self, file_path: str) -> int:
        """
        Bulk ingest phones from a JSON file. The file should contain a list of phone dicts.

        Args:
            file_path: Path to JSON file containing scraped phones

        Returns:
            Number of phones added
        """
        try:
            p = Path(file_path)
            if not p.exists():
                logger.error(f"❌ File not found: {file_path}")
                return 0

            with p.open('r', encoding='utf-8') as fh:
                data = json.load(fh)

            if not isinstance(data, list):
                logger.error("❌ Expected a list of phone objects in JSON file")
                return 0

            added = self.add_phones(data)
            logger.info(f"📥 Bulk ingested {added} phones from {file_path}")
            return added
        except Exception as e:
            logger.error(f"❌ Error ingesting file {file_path}: {e}")
            return 0
    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        try:
            count = self.collection.count()
            
            if count == 0:
                return {
                    'total_phones': 0,
                    'brands': [],
                    'price_range': (0, 0)
                }
            
            df = self.get_all_cached_phones()
            
            return {
                'total_phones': count,
                'brands': sorted(df['brand'].unique().tolist()) if not df.empty else [],
                'price_range': (int(df['price'].min()), int(df['price'].max())) if not df.empty else (0, 0)
            }
        except Exception as e:
            logger.error(f"❌ Error getting cache stats: {e}")
            return {
                'total_phones': 0,
                'brands': [],
                'price_range': (0, 0)
            }

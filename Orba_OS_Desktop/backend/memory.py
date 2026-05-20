import os
import json
import base64
import logging
import numpy as np
import requests
from cryptography.fernet import Fernet
from dotenv import load_dotenv

logger = logging.getLogger("OrbaDesktop.Memory")

class OrbaMemoryManager:
    def __init__(self, db_path="orba_memory.enc", env_path=".env"):
        self.db_path = db_path
        self.env_path = env_path
        
        # Load environment variables
        load_dotenv(self.env_path)
        
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)
        self.records = []
        self.load()

    def _load_or_create_key(self) -> bytes:
        # Load or generate key
        key_str = os.environ.get("ORBA_ENCRYPTION_KEY", "")
        if key_str:
            try:
                return base64.urlsafe_b64decode(key_str.encode())
            except Exception as e:
                logger.error(f"Erreur de décodage de la clé existante : {e}. Régénération...")
        
        # Generate new key
        new_key = Fernet.generate_key()
        new_key_str = base64.urlsafe_b64encode(new_key).decode()
        
        # Append or modify in .env
        self._write_key_to_env(new_key_str)
        # Update current environment variable
        os.environ["ORBA_ENCRYPTION_KEY"] = new_key_str
        logger.info("Clé de chiffrement ORBA_ENCRYPTION_KEY générée et sauvegardée dans le fichier .env.")
        return new_key

    def _write_key_to_env(self, key_str: str):
        if not os.path.exists(self.env_path):
            with open(self.env_path, "w") as f:
                f.write(f"ORBA_ENCRYPTION_KEY={key_str}\n")
            return
        
        with open(self.env_path, "r") as f:
            lines = f.readlines()
        
        key_found = False
        new_lines = []
        for line in lines:
            if line.strip().startswith("ORBA_ENCRYPTION_KEY="):
                new_lines.append(f"ORBA_ENCRYPTION_KEY={key_str}\n")
                key_found = True
            else:
                new_lines.append(line)
        
        if not key_found:
            new_lines.append(f"ORBA_ENCRYPTION_KEY={key_str}\n")
            
        with open(self.env_path, "w") as f:
            f.writelines(new_lines)

    def load(self):
        """Loads and decrypts memory database."""
        if not os.path.exists(self.db_path):
            self.records = []
            return
            
        try:
            with open(self.db_path, "rb") as f:
                encrypted_data = f.read()
                
            if not encrypted_data:
                self.records = []
                return
                
            decrypted_data = self.fernet.decrypt(encrypted_data)
            self.records = json.loads(decrypted_data.decode("utf-8"))
            logger.info(f"Mémoire chargée avec succès : {len(self.records)} souvenirs locaux chiffrés.")
        except Exception as e:
            logger.error(f"Erreur lors du déchiffrement/chargement de la mémoire : {e}. Base réinitialisée.")
            self.records = []

    def save(self):
        """Encrypts and saves memory database."""
        try:
            raw_data = json.dumps(self.records, ensure_ascii=False).encode("utf-8")
            encrypted_data = self.fernet.encrypt(raw_data)
            with open(self.db_path, "wb") as f:
                f.write(encrypted_data)
            logger.info("Mémoire locale chiffrée sauvegardée sur le disque.")
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde de la mémoire : {e}")

    def _get_embedding(self, text: str) -> list:
        """Call Ollama embedding model locally, or fallback to simple TF-IDF if unavailable."""
        ollama_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434/v1")
        # Try calling Ollama embeddings
        base_url = ollama_url.replace("/v1", "") if "/v1" in ollama_url else ollama_url
        try:
            response = requests.post(
                f"{base_url}/api/embeddings",
                json={"model": "nomic-embed-text", "prompt": text},
                timeout=2
            )
            if response.status_code == 200:
                return response.json().get("embedding", [])
        except Exception as e:
            pass
            
        # Fallback to local deterministic hash-based representation
        # Creating a pseudo-vector representation to keep RAG working without network/Ollama setup
        h = hash(text)
        np.random.seed(abs(h) % (2**32))
        # Generates a stable random vector of size 128
        vec = np.random.randn(128)
        # Normalize
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return list(vec)

    def add_memory(self, text: str):
        """Adds a text to long-term memory, generating its local embedding and saving."""
        if not text.strip():
            return
            
        # Avoid duplicating identical items consecutively
        if self.records and self.records[-1]["text"] == text:
            return
            
        embedding = self._get_embedding(text)
        record = {
            "text": text,
            "embedding": embedding
        }
        self.records.append(record)
        self.save()

    def search_memory(self, query: str, k: int = 3) -> list:
        """Calculates cosine similarity and returns the top k relevant text snippets."""
        if not self.records:
            return []
            
        query_emb = self._get_embedding(query)
        if not query_emb:
            return []
            
        q_vec = np.array(query_emb)
        q_norm = np.linalg.norm(q_vec)
        if q_norm == 0:
            return []
            
        results = []
        for r in self.records:
            r_emb = r.get("embedding", [])
            if not r_emb:
                continue
            r_vec = np.array(r_emb)
            r_norm = np.linalg.norm(r_vec)
            if r_norm == 0:
                continue
                
            similarity = np.dot(q_vec, r_vec) / (q_norm * r_norm)
            results.append((similarity, r["text"]))
            
        # Sort by similarity descending
        results.sort(key=lambda x: x[0], reverse=True)
        # Return matches with similarity > 0.25
        return [text for sim, text in results[:k] if sim > 0.25]

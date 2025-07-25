"""
AI and LLM integration tools for the Python MCP Server.

This module provides tools for working with various AI models, LLMs,
vector databases, and machine learning frameworks.
"""

import os
import json
import traceback
from typing import Dict, Any, List, Optional, Union
from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety

@log_tool_execution("ai_chat")
def ai_chat(prompt: str, model: str = "gpt-3.5-turbo", provider: str = "openai") -> Dict[str, Any]:
    """
    Chat with various AI models (OpenAI, Anthropic, etc.).
    
    Args:
        prompt: The prompt to send to the AI
        model: Model name (gpt-4, gpt-3.5-turbo, claude-3, etc.)
        provider: AI provider (openai, anthropic)
        
    Returns:
        Dict with AI response and metadata
    """
    try:
        if not prompt:
            raise ValueError("prompt is required")
            
        if provider == "openai":
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1000
            )
            
            return {
                "status": "success",
                "result": {
                    "response": response.choices[0].message.content,
                    "model": model,
                    "provider": provider,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "completion_tokens": response.usage.completion_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            }
            
        elif provider == "anthropic":
            import anthropic
            client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
            
            response = client.messages.create(
                model=model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return {
                "status": "success",
                "result": {
                    "response": response.content[0].text,
                    "model": model,
                    "provider": provider,
                    "usage": {
                        "input_tokens": response.usage.input_tokens,
                        "output_tokens": response.usage.output_tokens
                    }
                }
            }
            
        else:
            raise ValueError(f"Unsupported provider: {provider}")
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "ai_chat"
        }

@log_tool_execution("embeddings_create")
def create_embeddings(texts: List[str], model: str = "text-embedding-ada-002") -> Dict[str, Any]:
    """
    Create embeddings for text using various embedding models.
    
    Args:
        texts: List of texts to embed
        model: Embedding model name
        
    Returns:
        Dict with embeddings and metadata
    """
    try:
        if not texts:
            raise ValueError("texts list cannot be empty")
            
        if model.startswith("text-embedding"):
            # OpenAI embeddings
            import openai
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            
            response = client.embeddings.create(
                model=model,
                input=texts
            )
            
            embeddings = [data.embedding for data in response.data]
            
            return {
                "status": "success",
                "result": {
                    "embeddings": embeddings,
                    "model": model,
                    "dimensions": len(embeddings[0]) if embeddings else 0,
                    "usage": {
                        "prompt_tokens": response.usage.prompt_tokens,
                        "total_tokens": response.usage.total_tokens
                    }
                }
            }
            
        else:
            # Sentence transformers
            from sentence_transformers import SentenceTransformer
            
            model_instance = SentenceTransformer(model)
            embeddings = model_instance.encode(texts).tolist()
            
            return {
                "status": "success",
                "result": {
                    "embeddings": embeddings,
                    "model": model,
                    "dimensions": len(embeddings[0]) if embeddings else 0
                }
            }
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "embeddings_create"
        }

@log_tool_execution("vector_search")
def vector_search(query: str, collection: str = "default", top_k: int = 5, 
                 vector_db: str = "chromadb") -> Dict[str, Any]:
    """
    Search a vector database for similar content.
    
    Args:
        query: Search query
        collection: Collection/index name
        top_k: Number of results to return
        vector_db: Vector database type (chromadb, faiss, pinecone)
        
    Returns:
        Dict with search results
    """
    try:
        if not query:
            raise ValueError("query is required")
            
        if vector_db == "chromadb":
            import chromadb
            client = chromadb.Client()
            collection_obj = client.get_or_create_collection(collection)
            
            results = collection_obj.query(
                query_texts=[query],
                n_results=top_k
            )
            
            return {
                "status": "success",
                "result": {
                    "documents": results["documents"][0],
                    "distances": results["distances"][0],
                    "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                    "ids": results["ids"][0],
                    "collection": collection,
                    "vector_db": vector_db
                }
            }
            
        elif vector_db == "pinecone":
            import pinecone
            
            # Initialize Pinecone (requires PINECONE_API_KEY and PINECONE_ENVIRONMENT)
            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT")
            )
            
            index = pinecone.Index(collection)
            
            # Note: This requires query vector, would need embedding step
            # This is a simplified example
            return {
                "status": "success",
                "result": {
                    "message": "Pinecone search requires query embedding",
                    "collection": collection,
                    "vector_db": vector_db
                }
            }
            
        else:
            raise ValueError(f"Unsupported vector database: {vector_db}")
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "vector_search"
        }

@log_tool_execution("ml_train")
def train_ml_model(data_code: str, model_type: str = "sklearn", 
                  target_column: str = "target") -> Dict[str, Any]:
    """
    Train a machine learning model on provided data.
    
    Args:
        data_code: Python code that creates a pandas DataFrame named 'df'
        model_type: Type of model (sklearn, xgboost, lightgbm)
        target_column: Name of target column
        
    Returns:
        Dict with training results and model metrics
    """
    try:
        if not data_code:
            raise ValueError("data_code is required")
            
        # Validate code safety
        safety_check = validate_code_safety(data_code)
        if not safety_check["is_safe"]:
            raise ValueError(f"Code safety violation: {safety_check['reason']}")
            
        # Execute data preparation code
        exec_globals = {
            'pd': __import__('pandas'),
            'np': __import__('numpy'),
            'sklearn': __import__('sklearn'),
            'xgboost': __import__('xgboost', fromlist=['']),
            'lightgbm': __import__('lightgbm')
        }
        
        exec(data_code, exec_globals)
        
        if 'df' not in exec_globals:
            raise ValueError("Data code must create a DataFrame named 'df'")
            
        df = exec_globals['df']
        
        if target_column not in df.columns:
            raise ValueError(f"Target column '{target_column}' not found in DataFrame")
            
        # Prepare features and target
        X = df.drop(columns=[target_column])
        y = df[target_column]
        
        # Split data
        from sklearn.model_selection import train_test_split
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        if model_type == "sklearn":
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.metrics import accuracy_score, classification_report
            
            model = RandomForestClassifier(random_state=42)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            return {
                "status": "success",
                "result": {
                    "model_type": model_type,
                    "accuracy": accuracy,
                    "feature_count": len(X.columns),
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "feature_names": list(X.columns),
                    "target_column": target_column
                }
            }
            
        elif model_type == "xgboost":
            import xgboost as xgb
            from sklearn.metrics import accuracy_score
            
            model = xgb.XGBClassifier(random_state=42)
            model.fit(X_train, y_train)
            
            y_pred = model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            
            return {
                "status": "success",
                "result": {
                    "model_type": model_type,
                    "accuracy": accuracy,
                    "feature_count": len(X.columns),
                    "training_samples": len(X_train),
                    "test_samples": len(X_test),
                    "feature_importance": dict(zip(X.columns, model.feature_importances_)),
                    "target_column": target_column
                }
            }
            
        else:
            raise ValueError(f"Unsupported model type: {model_type}")
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "ml_train"
        }

@log_tool_execution("nlp_analyze")
def analyze_text(text: str, analysis_type: str = "sentiment") -> Dict[str, Any]:
    """
    Perform NLP analysis on text using various libraries.
    
    Args:
        text: Text to analyze
        analysis_type: Type of analysis (sentiment, entities, summary, keywords)
        
    Returns:
        Dict with analysis results
    """
    try:
        if not text:
            raise ValueError("text is required")
            
        if analysis_type == "sentiment":
            from textblob import TextBlob
            
            blob = TextBlob(text)
            
            return {
                "status": "success",
                "result": {
                    "sentiment": {
                        "polarity": blob.sentiment.polarity,
                        "subjectivity": blob.sentiment.subjectivity
                    },
                    "analysis_type": analysis_type,
                    "text_length": len(text)
                }
            }
            
        elif analysis_type == "entities":
            import spacy
            
            # Load English model (requires: python -m spacy download en_core_web_sm)
            try:
                nlp = spacy.load("en_core_web_sm")
            except OSError:
                return {
                    "status": "error",
                    "error": "spaCy English model not installed. Run: python -m spacy download en_core_web_sm"
                }
            
            doc = nlp(text)
            entities = [(ent.text, ent.label_, ent.start_char, ent.end_char) for ent in doc.ents]
            
            return {
                "status": "success",
                "result": {
                    "entities": entities,
                    "analysis_type": analysis_type,
                    "entity_count": len(entities)
                }
            }
            
        elif analysis_type == "keywords":
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            
            # Simple keyword extraction using TF-IDF
            vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text])
            
            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]
            
            keywords = [(feature_names[i], scores[i]) for i in np.argsort(scores)[::-1] if scores[i] > 0]
            
            return {
                "status": "success", 
                "result": {
                    "keywords": keywords,
                    "analysis_type": analysis_type,
                    "keyword_count": len(keywords)
                }
            }
            
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "nlp_analyze"
        }

@log_tool_execution("computer_vision")
def analyze_image(image_path: str, analysis_type: str = "objects") -> Dict[str, Any]:
    """
    Perform computer vision analysis on images.
    
    Args:
        image_path: Path to image file
        analysis_type: Type of analysis (objects, faces, text, features)
        
    Returns:
        Dict with analysis results
    """
    try:
        if not image_path:
            raise ValueError("image_path is required")
            
        import cv2
        import numpy as np
        from PIL import Image
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
            
        if analysis_type == "objects":
            # Simple object detection using OpenCV
            # This is a basic example - real object detection would use YOLO, etc.
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Use Haar cascades for face detection as example
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            return {
                "status": "success",
                "result": {
                    "faces_detected": len(faces),
                    "face_coordinates": faces.tolist(),
                    "image_shape": image.shape,
                    "analysis_type": analysis_type
                }
            }
            
        elif analysis_type == "features":
            # Extract basic image features
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            
            # Calculate basic statistics
            mean_intensity = np.mean(gray)
            std_intensity = np.std(gray)
            
            # Detect edges
            edges = cv2.Canny(gray, 100, 200)
            edge_count = np.sum(edges > 0)
            
            return {
                "status": "success",
                "result": {
                    "mean_intensity": float(mean_intensity),
                    "std_intensity": float(std_intensity),
                    "edge_pixels": int(edge_count),
                    "image_shape": image.shape,
                    "analysis_type": analysis_type
                }
            }
            
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
            
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "traceback": traceback.format_exc(),
            "tool": "computer_vision"
        }

"""
AI and LLM integration tools for the Python MCP Server.

This module provides tools for working with various AI models, LLMs,
vector databases, and machine learning frameworks.
"""

import os
import traceback
from typing import Any

from ..utils.logging import log_tool_execution
from ..utils.security import validate_code_safety


@log_tool_execution("ai_chat")
def ai_chat(prompt: str, model: str = "gpt-3.5-turbo", provider: str = "openai") -> dict[str, Any]:
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
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
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

            # Extract text from response content blocks
            response_text = ""
            for content_block in response.content:
                # Check if it's a text block using getattr to avoid attribute errors
                if getattr(content_block, 'type', None) == 'text':
                    response_text = getattr(content_block, 'text', '')
                    break
                # Fallback for blocks that might have text but no type
                elif hasattr(content_block, 'text') and getattr(content_block, 'type', None) != 'tool_use':
                    response_text = getattr(content_block, 'text', '')
                    break

            if not response_text and response.content:
                # Last resort: convert to string
                response_text = str(response.content[0])

            return {
                "status": "success",
                "result": {
                    "response": response_text,
                    "model": model,
                    "provider": provider,
                    "usage": {
                        "input_tokens": response.usage.input_tokens if response.usage else 0,
                        "output_tokens": response.usage.output_tokens if response.usage else 0
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
def create_embeddings(texts: list[str], model: str = "text-embedding-ada-002") -> dict[str, Any]:
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
                        "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                        "total_tokens": response.usage.total_tokens if response.usage else 0
                    }
                }
            }

        else:
            # Sentence transformers (optional dependency)
            try:
                from sentence_transformers import SentenceTransformer  # type: ignore

                model_instance = SentenceTransformer(model)
                embeddings = model_instance.encode(texts).tolist()

                return {
                    "status": "success",
                    "result": {
                        "embeddings": embeddings,
                        "model": model,
                        "provider": "sentence_transformers",
                        "dimensions": len(embeddings[0]) if embeddings else 0
                    }
                }
            except ImportError:
                return {
                    "status": "error",
                    "error": "sentence_transformers not installed. Install with: pip install sentence-transformers",
                    "traceback": "Missing optional dependency"
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
                 vector_db: str = "chromadb") -> dict[str, Any]:
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
            try:
                import chromadb  # type: ignore
            except ImportError:
                return {
                    "status": "error",
                    "error": "chromadb not installed. Install with: pip install chromadb",
                    "traceback": "Missing optional dependency"
                }

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
            try:
                import pinecone  # type: ignore
            except ImportError:
                return {
                    "status": "error",
                    "error": "pinecone not installed. Install with: pip install pinecone-client",
                    "traceback": "Missing optional dependency"
                }

            # Initialize Pinecone (requires PINECONE_API_KEY and PINECONE_ENVIRONMENT)
            pinecone.init(
                api_key=os.getenv("PINECONE_API_KEY"),
                environment=os.getenv("PINECONE_ENVIRONMENT")
            )

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
                  target_column: str = "target") -> dict[str, Any]:
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
        try:
            from sklearn.model_selection import train_test_split  # type: ignore
        except ImportError:
            return {
                "status": "error",
                "error": "scikit-learn not installed. Install with: pip install scikit-learn",
                "traceback": "Missing optional dependency"
            }

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        if model_type == "sklearn":
            try:
                from sklearn.ensemble import RandomForestClassifier  # type: ignore
                from sklearn.metrics import accuracy_score  # type: ignore
            except ImportError:
                return {
                    "status": "error",
                    "error": "scikit-learn not installed. Install with: pip install scikit-learn",
                    "traceback": "Missing optional dependency"
                }

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
            try:
                import xgboost as xgb  # type: ignore
                from sklearn.metrics import accuracy_score  # type: ignore
            except ImportError:
                return {
                    "status": "error",
                    "error": "xgboost or scikit-learn not installed. Install with: pip install xgboost scikit-learn",
                    "traceback": "Missing optional dependency"
                }

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
                    "feature_importance": dict(zip(X.columns, model.feature_importances_, strict=False)),
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
def analyze_text(text: str, analysis_type: str = "sentiment") -> dict[str, Any]:
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
            try:
                from textblob import TextBlob  # type: ignore
            except ImportError:
                return {
                    "status": "error",
                    "error": "textblob not installed. Install with: pip install textblob",
                    "traceback": "Missing optional dependency"
                }

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
            try:
                import spacy  # type: ignore
            except ImportError:
                return {
                    "status": "error",
                    "error": "spacy not installed. Install with: pip install spacy",
                    "traceback": "Missing optional dependency"
                }

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
            try:
                import numpy as np  # type: ignore
                from sklearn.feature_extraction.text import (
                    TfidfVectorizer,  # type: ignore
                )
            except ImportError:
                return {
                    "status": "error",
                    "error": "scikit-learn or numpy not installed. Install with: pip install scikit-learn numpy",
                    "traceback": "Missing optional dependency"
                }

            # Simple keyword extraction using TF-IDF
            vectorizer = TfidfVectorizer(max_features=10, stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([text])

            feature_names = vectorizer.get_feature_names_out()
            scores = tfidf_matrix.toarray()[0]  # type: ignore[attr-defined]

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
def analyze_image(image_path: str, analysis_type: str = "objects") -> dict[str, Any]:
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

        try:
            import cv2  # type: ignore
            import numpy as np  # type: ignore
        except ImportError:
            return {
                "status": "error",
                "error": "opencv-python or numpy not installed. Install with: pip install opencv-python numpy",
                "traceback": "Missing optional dependency"
            }

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

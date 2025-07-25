#!/usr/bin/env python3
"""Test script to verify type warnings are suppressed and functionality works."""

def test_all_optional_dependencies():
    """Test that all optional dependency functions work correctly."""
    print("Testing all optional dependency handling...")

    try:
        from src.mcp_server.tools.ai_tools import (
            analyze_image,
            analyze_text,
            create_embeddings,
            train_ml_model,
            vector_search,
        )
        print("✅ All AI tools imported successfully")

        # Test sentence transformers
        result = create_embeddings(['test'], 'sentence-transformers/all-MiniLM-L6-v2')
        assert result["status"] == "error"
        assert "sentence_transformers not installed" in result["error"]
        print("✅ SentenceTransformers handling works")

        # Test ChromaDB
        result = vector_search('test', vector_db='chromadb')
        assert result["status"] == "error"
        assert "chromadb not installed" in result["error"]
        print("✅ ChromaDB handling works")

        # Test Pinecone
        result = vector_search('test', vector_db='pinecone')
        assert result["status"] == "error"
        assert "pinecone not installed" in result["error"]
        print("✅ Pinecone handling works")

        # Test ML dependencies (sklearn is required first)
        result = train_ml_model('import pandas as pd; df = pd.DataFrame({"a": [1,2], "target": [0,1]})',
                               model_type='xgboost')
        assert result["status"] == "error"
        assert "sklearn" in result["error"] or "xgboost" in result["error"]
        print("✅ ML dependencies handling works")

        # Test TextBlob
        result = analyze_text('test text', analysis_type='sentiment')
        assert result["status"] == "error"
        assert "textblob not installed" in result["error"]
        print("✅ TextBlob handling works")

        # Test Spacy
        result = analyze_text('test text', analysis_type='entities')
        assert result["status"] == "error"
        assert "spacy not installed" in result["error"]
        print("✅ Spacy handling works")

        # Test OpenCV
        result = analyze_image('nonexistent.jpg', analysis_type='objects')
        assert result["status"] == "error"
        assert "opencv-python" in result["error"]
        print("✅ OpenCV handling works")

        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run the test."""
    print("🧪 Testing optional dependency handling with type ignore comments...\n")

    if test_all_optional_dependencies():
        print("\n🎉 All optional dependencies handled correctly!")
        print("📝 Type warnings should now be suppressed in your IDE/editor.")
        return 0
    else:
        print("\n⚠️ Some tests failed.")
        return 1

if __name__ == "__main__":
    exit(main())

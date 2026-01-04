r"""
Script để test kết nối Database, Redis và Qdrant

Cách chạy:
1. Với conda environment:
   conda activate taichinh
   python test_connections.py

2. Dùng Python trực tiếp từ conda:
   C:\Users\ADMIN\anaconda3\envs\taichinh\python.exe test_connections.py

3. Hoặc dùng script helper:
   run_test.bat (Windows)
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.conf import settings
from django.db import connection
from django.core.cache import cache
from app.qdrant_client import get_qdrant_service


def test_postgresql():
    """Test PostgreSQL connection"""
    print("\n" + "="*50)
    print("Testing PostgreSQL Connection...")
    print("="*50)
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"[OK] PostgreSQL Connected!")
            print(f"   Version: {version[0]}")
            return True
    except Exception as e:
        print(f"[FAIL] PostgreSQL Connection Failed: {e}")
        return False


def test_redis():
    """Test Redis connection"""
    print("\n" + "="*50)
    print("Testing Redis Connection...")
    print("="*50)
    try:
        # Test cache set/get
        test_key = "test_connection"
        test_value = "Hello Redis!"
        cache.set(test_key, test_value, 30)
        retrieved = cache.get(test_key)
        
        if retrieved == test_value:
            print("[OK] Redis Connected!")
            print(f"   Test value: {retrieved}")
            cache.delete(test_key)
            return True
        else:
            print("[FAIL] Redis: Value mismatch")
            return False
    except Exception as e:
        print(f"[FAIL] Redis Connection Failed: {e}")
        return False


def test_qdrant():
    """Test Qdrant connection"""
    print("\n" + "="*50)
    print("Testing Qdrant Connection...")
    print("="*50)
    try:
        # Get collection info
        qdrant_service = get_qdrant_service()
        info = qdrant_service.get_collection_info()
        if info:
            print("[OK] Qdrant Connected!")
            print(f"   Collection: {settings.QDRANT_COLLECTION_NAME}")
            print(f"   Points count: {info.get('points_count', 'N/A')}")
            return True
        else:
            print("[WARNING] Qdrant: Could not get collection info")
            return False
    except Exception as e:
        print(f"[FAIL] Qdrant Connection Failed: {e}")
        return False


def main():
    """Run all connection tests"""
    # Set UTF-8 encoding for Windows console
    import sys
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    
    print("\n[TEST] Testing All Connections...")
    print(f"PostgreSQL: {settings.DATABASES['default']['HOST']}:{settings.DATABASES['default']['PORT']}")
    print(f"Redis: {settings.REDIS_HOST}:{settings.REDIS_PORT}")
    print(f"Qdrant: {settings.QDRANT_URL}")
    
    results = {
        "PostgreSQL": test_postgresql(),
        "Redis": test_redis(),
        "Qdrant": test_qdrant(),
    }
    
    print("\n" + "="*50)
    print("[SUMMARY] Test Results Summary")
    print("="*50)
    for service, status in results.items():
        status_icon = "[OK]" if status else "[FAIL]"
        print(f"{status_icon} {service}: {'PASS' if status else 'FAIL'}")
    
    all_passed = all(results.values())
    if all_passed:
        print("\n[SUCCESS] All connections successful!")
    else:
        print("\n[WARNING] Some connections failed. Please check your configuration.")
        print("Note: Make sure Docker services are running: docker-compose up -d")
    
    return all_passed


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


try:
    from dotenv import load_dotenv
    print("✅ Importación EXITOSA")
    print("📦 Versión:", load_dotenv.__module__)
except ImportError as e:
    print("❌ Error:", e)
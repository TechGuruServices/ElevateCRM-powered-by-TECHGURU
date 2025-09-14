"""
Simple seed script runner for development
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("🌱 Starting seed script...")
    try:
        # Import after path setup
        print("📦 Importing seed_database...")
        from app.scripts.seed_data import seed_database
        print("📦 Importing asyncio...")
        import asyncio
        
        print("🚀 Running seeding...")
        # Run the seeding
        result = asyncio.run(seed_database())
        if result:
            print("✅ Seeding completed successfully!")
        else:
            print("❌ Seeding failed!")
            
    except Exception as e:
        print(f"❌ Error running seed script: {e}")
        import traceback
        traceback.print_exc()

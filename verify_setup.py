"""
Comprehensive setup verification script
"""
import sys
import os

print("=" * 60)
print("🔍 SMART GADGET ADVISOR - SYSTEM CHECK")
print("=" * 60)

# 1. Check Python version
print(f"\n✅ Python Version: {sys.version}")

# 2. Check required packages
print("\n📦 Checking Required Packages:")
packages = [
    'streamlit',
    'pandas',
    'numpy',
    'requests',
    'dotenv',
    'google.generativeai'
]

for package in packages:
    try:
        if package == 'dotenv':
            __import__('dotenv')
        else:
            __import__(package)
        print(f"   ✅ {package}")
    except ImportError:
        print(f"   ❌ {package} - NOT INSTALLED")

# 3. Check .env file
print("\n🔑 Checking Environment Variables:")
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv('GOOGLE_API_KEY')
if api_key:
    print(f"   ✅ GOOGLE_API_KEY: {api_key[:20]}...{api_key[-4:]}")
else:
    print("   ❌ GOOGLE_API_KEY not found in .env")

# 4. Test Agents
print("\n🤖 Testing Agents:")
try:
    from agents import DataFetchAgent, RecommenderAgent, ChatAdvisorAgent
    print("   ✅ All agents imported successfully")
    
    # Test DataFetchAgent
    data_agent = DataFetchAgent()
    print(f"   ✅ DataFetchAgent: {len(data_agent.phone_database)} phones loaded")
    
    # Test RecommenderAgent
    rec_agent = RecommenderAgent()
    gemini_status = "✅ ACTIVE" if rec_agent.model else "⚠️ Not configured"
    print(f"   ✅ RecommenderAgent: Gemini {gemini_status}")
    
    # Test ChatAdvisorAgent
    chat_agent = ChatAdvisorAgent()
    gemini_status = "✅ ACTIVE" if chat_agent.model else "⚠️ Not configured"
    print(f"   ✅ ChatAdvisorAgent: Gemini {gemini_status}")
    
except Exception as e:
    print(f"   ❌ Error: {e}")

# 5. Test Gemini API
print("\n🧪 Testing Gemini API Connection:")
try:
    import google.generativeai as genai
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Say 'Gemini API is working!' in exactly 4 words")
        print(f"   ✅ Gemini Response: {response.text[:50]}")
    else:
        print("   ⚠️ No API key found")
except Exception as e:
    print(f"   ❌ Gemini API Error: {e}")

# 6. Test Phone Database
print("\n📱 Testing Phone Database:")
try:
    phones = data_agent.phone_database
    print(f"   ✅ Total Phones: {len(phones)}")
    print(f"   ✅ Brands: {', '.join(phones['brand'].unique()[:5])}...")
    print(f"   ✅ Price Range: ₹{phones['price'].min():,} - ₹{phones['price'].max():,}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 7. Test Recommendation
print("\n🎯 Testing Recommendation System:")
try:
    test_phones = data_agent.fetch_phones(min_price=20000, max_price=50000)
    recommendations = rec_agent.recommend_phones(test_phones, priority='Performance', top_n=3)
    print(f"   ✅ Found {len(recommendations)} recommendations")
    if len(recommendations) > 0:
        top_phone = recommendations.iloc[0]
        print(f"   ✅ Top Pick: {top_phone['full_name']} - ₹{top_phone['price']:,}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "=" * 60)
print("✅ SYSTEM CHECK COMPLETE")
print("=" * 60)
print("\n💡 To run the app: streamlit run app.py")

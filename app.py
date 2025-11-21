"""
Smart Gadget Advisor - Main Streamlit Application
AI-powered smartphone recommendation system with on-demand web scraping
"""
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
import os
import sys

# Add the agents directory to the path
sys.path.append(os.path.dirname(__file__))

# Import agents
from agents.fetch_data import DataFetchAgent
from agents.recommend import RecommenderAgent
from agents.chat_agent import ChatAdvisorAgent

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Smart Gadget Advisor",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stCheckbox {
        padding: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_agent' not in st.session_state:
    st.session_state.data_agent = DataFetchAgent()
    st.session_state.recommend_agent = RecommenderAgent()
    st.session_state.chat_agent = ChatAdvisorAgent()
    st.session_state.recommendations = None
    st.session_state.chat_history = []

# Header
st.markdown('<h1 class="main-header">📱 Smart Gadget Advisor</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Find Your Perfect Phone with AI-Powered Live Search</p>', unsafe_allow_html=True)

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Cache status
    if st.session_state.data_agent.cache:
        cache_stats = st.session_state.data_agent.cache.get_cache_stats()
        st.info(f"💾 Cache: {cache_stats['total_phones']} phones")
        if cache_stats['total_phones'] > 0:
            with st.expander("📊 Cache Details"):
                st.write(f"**Brands:** {len(cache_stats['brands'])}")
                st.write(f"**Price Range:** ₹{cache_stats['price_range'][0]:,} - ₹{cache_stats['price_range'][1]:,}")
    
    # Database status
    db_size = len(st.session_state.data_agent.phone_database)
    if db_size > 0:
        st.success(f"✅ {db_size} phones loaded")
    
    st.divider()
    
    # Number of recommendations
    top_n = st.slider("Number of results", 3, 10, 5)
    
    st.divider()
    st.caption("🤖 AI Status")
    if st.session_state.chat_agent.model:
        st.success("✅ Gemini AI Active")

# Main Content
st.info("💡 **How it works:** Enter what you're looking for below, and we'll scrape live data from Flipkart to find the best matches!")

# Phone Name / Brand Search
st.subheader("🔍 What phone are you looking for?")
search_query = st.text_input(
    "Phone name or brand",
    placeholder="e.g., 'iPhone 15', 'Samsung Galaxy S24', 'gaming phone', or leave empty for all smartphones",
    help="Be specific for better results. Leave empty to search all smartphones."
)

st.divider()

# Requirements with Checkboxes
st.subheader("📋 Your Requirements")
st.write("Check the boxes for requirements that matter to you:")

col1, col2 = st.columns(2)

with col1:
    st.markdown("#### 🎯 Performance & Storage")
    
    use_ram = st.checkbox("Minimum RAM", value=True)
    min_ram = st.number_input(
        "RAM (GB)",
        min_value=2,
        max_value=24,
        value=6,
        step=2,
        disabled=not use_ram,
        help="Recommended: 6GB+ for smooth performance"
    )
    
    use_storage = st.checkbox("Minimum Storage", value=True)
    min_storage = st.number_input(
        "Storage (GB)",
        min_value=32,
        max_value=1024,
        value=128,
        step=32,
        disabled=not use_storage,
        help="Recommended: 128GB+ for apps and media"
    )
    
    use_processor = st.checkbox("Processor Type")
    processor_pref = st.text_input(
        "Processor preference",
        placeholder="e.g., Snapdragon, MediaTek, Apple",
        disabled=not use_processor
    )

with col2:
    st.markdown("#### 📸 Camera & Display")
    
    use_camera = st.checkbox("Minimum Camera", value=True)
    min_camera = st.number_input(
        "Camera (MP)",
        min_value=8,
        max_value=200,
        value=48,
        step=12,
        disabled=not use_camera,
        help="Recommended: 48MP+ for quality photos"
    )
    
    use_display = st.checkbox("Minimum Display Size")
    min_display = st.number_input(
        "Display (inches)",
        min_value=4.0,
        max_value=8.0,
        value=6.0,
        step=0.1,
        format="%.1f",
        disabled=not use_display,
        help="Recommended: 6.0+ inches"
    )

st.divider()

col3, col4 = st.columns(2)

with col3:
    st.markdown("#### 🔋 Battery")
    use_battery = st.checkbox("Minimum Battery", value=True)
    min_battery = st.number_input(
        "Battery (mAh)",
        min_value=3000,
        max_value=7000,
        value=4500,
        step=500,
        disabled=not use_battery,
        help="Recommended: 4500mAh+ for all-day use"
    )

with col4:
    st.markdown("#### 💰 Budget")
    use_budget = st.checkbox("Maximum Budget", value=True)
    max_price = st.number_input(
        "Budget (₹)",
        min_value=5000,
        max_value=200000,
        value=30000,
        step=5000,
        disabled=not use_budget,
        help="Your maximum budget"
    )

st.divider()

# Search Button
col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
with col_btn2:
    search_button = st.button(
        "🚀 Find My Perfect Phone", 
        type="primary", 
        use_container_width=True
    )

# Handle Search
if search_button:
    with st.spinner("🔍 Checking cache and scraping if needed... This will take 5-40 seconds"):
        
        # Build search query
        if not search_query or search_query.strip() == "":
            search_query_final = "smartphone"
        else:
            search_query_final = search_query
        
        # Scrape live data (reduced to 8 for faster results)
        scraped_df = st.session_state.data_agent.scrape_live_phones(
            query=search_query_final,
            max_phones=8,
            max_budget=max_price if use_budget else None
        )
        
        if not scraped_df.empty:
            st.success(f"✅ Scraped {len(scraped_df)} phones from Flipkart!")
            
            # Build filter dict (only include checked requirements)
            filters = {
                'brands': None,
                'max_price': max_price if use_budget else None,
                'min_ram': min_ram if use_ram else None,
                'min_camera': min_camera if use_camera else None,
                'min_battery': min_battery if use_battery else None,
                'min_storage': min_storage if use_storage else None,
                'min_display': min_display if use_display else None
            }
            
            # Filter by specs
            phones_df = st.session_state.data_agent.fetch_phones_by_specs(**filters)
            
            if len(phones_df) == 0:
                st.warning("😕 No phones match your exact specifications. Showing all scraped phones:")
                phones_df = scraped_df
            
            # Get recommendations (sorted by price and rating)
            recommendations = st.session_state.recommend_agent.recommend_phones(
                phones_df,
                priority='Value for Money',
                top_n=min(top_n, len(phones_df))
            )
            
            st.session_state.recommendations = recommendations.to_dict('records')
            st.success(f"🎉 Here are the top {len(st.session_state.recommendations)} recommendations for you!")
            
        else:
            st.error("❌ No phones found. Try different search terms.")

# Display Recommendations
if st.session_state.recommendations:
    st.divider()
    st.header("🏆 Your Personalized Recommendations")
    
    for idx, phone in enumerate(st.session_state.recommendations, 1):
        score = phone.get('recommendation_score', 0)
        with st.expander(f"**{idx}. {phone['full_name']}** - ₹{phone['price']:,} | Score: {score:.1f}/100", expanded=(idx==1)):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.markdown(f"### {phone['full_name']}")
                st.markdown(f"**Category:** {phone['category']}")
                st.markdown(f"**Rating:** {'⭐' * int(phone['rating'])} ({phone['rating']}/5)")
                if 'source' in phone:
                    st.caption(f"🌐 Source: {phone['source']}")
                
            with col2:
                st.metric("💰 Price", f"₹{phone['price']:,}")
                st.metric("📈 AI Score", f"{score:.1f}/100")
                
            with col3:
                st.metric("🎯 Match", f"{score:.0f}%")
                if 'url' in phone and phone['url']:
                    st.link_button("🛒 View on Flipkart", phone['url'], use_container_width=True)
                    st.caption("Click to buy")
            
            st.markdown("---")
            st.markdown("**📱 Specifications:**")
            
            spec_cols = st.columns(4)
            with spec_cols[0]:
                st.metric("RAM", f"{phone['ram']} GB")
                st.metric("Storage", f"{phone['storage']} GB")
            with spec_cols[1]:
                st.metric("Camera", f"{phone['camera_mp']} MP")
                st.metric("Display", f"{phone['display_inches']}\"")
            with spec_cols[2]:
                st.metric("Battery", f"{phone['battery_mah']} mAh")
            with spec_cols[3]:
                st.write("**Processor:**")
                st.write(phone['processor'])
            
            # Show product description from Flipkart
            if 'description' in phone and phone['description'] and phone['description'] != 'N/A':
                st.markdown("---")
                st.markdown("**📝 Product Description:**")
                # Truncate long descriptions
                description = phone['description']
                if len(description) > 300:
                    with st.expander("Read full description"):
                        st.write(description)
                    st.write(description[:300] + "...")
                else:
                    st.write(description)
            
            # Show URL details
            if 'url' in phone and phone['url']:
                st.markdown("---")
                with st.expander("🔗 Product Link Details"):
                    st.text_input("Flipkart URL", phone['url'], disabled=True, label_visibility="collapsed")
                    st.caption("Copy this URL to share or save for later")
            
            if 'explanation' in phone:
                st.info(f"**💡 Why this phone?** {phone['explanation']}")
    
    # Chat Section
    st.divider()
    st.header("💬 Ask AI About These Phones")
    
    user_question = st.text_input(
        "Ask anything about these recommendations",
        placeholder="e.g., 'Which is best for gaming?', 'Compare top 2 phones', 'Is the camera good?'"
    )
    
    if st.button("Ask AI", type="secondary"):
        if user_question:
            with st.spinner("🤖 AI is thinking..."):
                response = st.session_state.chat_agent.chat(
                    user_question,
                    st.session_state.recommendations
                )
                st.session_state.chat_history.append({
                    'question': user_question,
                    'answer': response
                })
    
    # Display chat history
    if st.session_state.chat_history:
        st.divider()
        for chat in st.session_state.chat_history[-3:]:  # Show last 3
            st.markdown(f"**You:** {chat['question']}")
            st.markdown(f"**AI:** {chat['answer']}")
            st.divider()
    
    # Clear button
    if st.button("🔄 Start New Search", use_container_width=True):
        st.session_state.recommendations = None
        st.session_state.chat_history = []
        st.rerun()

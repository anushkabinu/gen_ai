"""
Smart Gadget Advisor - Main Streamlit Application
AI-powered smartphone recommendation system with multi-agent architecture
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
    .phone-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
    }
    .user-message {
        background: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background: #f5f5f5;
        margin-right: 2rem;
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
st.markdown('<p class="sub-header">AI-Powered Smartphone Recommendations with Multi-Agent Intelligence</p>', unsafe_allow_html=True)

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Settings")
    
    # Check if database has data
    db_size = len(st.session_state.data_agent.phone_database)
    
    if db_size > 0:
        st.success(f"✅ {db_size} phones in database")
    else:
        st.info("� Enter your requirements below to search live!")
    
    # Get available brands
    all_brands = st.session_state.data_agent.get_all_brands()
    
    # Priority selection
    st.subheader("⭐ What matters most?")
    priority = st.selectbox(
        "Select your priority",
        options=['Performance', 'Camera', 'Battery', 'Display', 'Value for Money'],
        index=4
    )
    
    # Show priority explanation
    explanation = st.session_state.recommend_agent.get_priority_explanation(priority)
    st.info(f"ℹ️ {explanation}")
    
    # Number of recommendations
    top_n = st.slider("Number of recommendations", 3, 10, 5)
    
    # Specs Requirements
    st.subheader("� Desired Specs")
    
    col1, col2 = st.columns(2)
    
    with col1:
        min_ram = st.number_input(
            "Minimum RAM (GB)",
            min_value=0,
            max_value=24,
            value=0,
            step=2,
            disabled=(db_size == 0),
            help="0 = any RAM"
        )
        
        min_camera = st.number_input(
            "Minimum Camera (MP)",
            min_value=0,
            max_value=200,
            value=0,
            step=12,
            disabled=(db_size == 0),
            help="0 = any camera"
        )
        
        min_battery = st.number_input(
            "Minimum Battery (mAh)",
            min_value=0,
            max_value=7000,
            value=0,
            step=500,
            disabled=(db_size == 0),
            help="0 = any battery"
        )
    
    with col2:
        min_storage = st.number_input(
            "Minimum Storage (GB)",
            min_value=0,
            max_value=1024,
            value=0,
            step=64,
            disabled=(db_size == 0),
            help="0 = any storage"
        )
        
        min_display = st.number_input(
            "Minimum Display (inches)",
            min_value=0.0,
            max_value=8.0,
            value=0.0,
            step=0.5,
            format="%.1f",
            disabled=(db_size == 0),
            help="0 = any display size"
        )
        
        max_price = st.number_input(
            "Max Budget (₹)",
            min_value=0,
            max_value=200000,
            value=0,
            step=5000,
            disabled=(db_size == 0),
            help="0 = no budget limit"
        )
    
    # Priority selection
    st.subheader("⭐ What matters most?")
    priority = st.selectbox(
        "Select your priority",
        options=['Performance', 'Camera', 'Battery', 'Display', 'Value for Money'],
        index=4
    )
    
    # Show priority explanation
    explanation = st.session_state.recommend_agent.get_priority_explanation(priority)
    st.info(f"ℹ️ {explanation}")
    
    # Number of recommendations
    top_n = st.slider("Number of recommendations", 3, 10, 5)
    
    # Get recommendations button
    recommend_button = st.button(
        "🔍 Get Recommendations", 
        type="primary", 
        use_container_width=True,
        disabled=(db_size == 0),
        help="Scrape phones first if database is empty" if db_size == 0 else None
    )
    
    if recommend_button:
        with st.spinner("🤖 AI agents are analyzing smartphones for you..."):
            # Build filter dict
            filters = {
                'brands': selected_brands if selected_brands else None,
                'max_price': max_price if max_price > 0 else None,
                'min_ram': min_ram if min_ram > 0 else None,
                'min_camera': min_camera if min_camera > 0 else None,
                'min_battery': min_battery if min_battery > 0 else None,
                'min_storage': min_storage if min_storage > 0 else None,
                'min_display': min_display if min_display > 0 else None
            }
            
            # Fetch data with spec filters
            phones_df = st.session_state.data_agent.fetch_phones_by_specs(**filters)
            
            if len(phones_df) == 0:
                st.error("😕 No phones found matching your criteria. Try adjusting your filters or scrape more phones.")
            else:
                # Get recommendations
                recommendations = st.session_state.recommend_agent.recommend_phones(
                    phones_df,
                    priority=priority,
                    top_n=top_n
                )
                
                st.session_state.recommendations = recommendations.to_dict('records')
                st.success(f"✅ Found {len(st.session_state.recommendations)} great options for you!")
    
    # Clear recommendations
    if st.button("🔄 Clear Results", use_container_width=True):
        st.session_state.recommendations = None
        st.session_state.chat_history = []
        st.rerun()
    
    # Live Data Scraping Section
    st.divider()
    st.subheader("🌐 Scrape Live Data")
    st.caption("👉 **Start here!** This section is always available")
    
    with st.form("scrape_form"):
        scrape_query = st.text_input(
            "Search Flipkart for:",
            value="smartphone",
            help="e.g., 'iphone', 'samsung galaxy', 'gaming phone'"
        )
        max_phones_scrape = st.slider("Max phones to scrape", 5, 30, 15)
        scrape_button = st.form_submit_button("🔄 Scrape Live Phones from Flipkart", type="primary", use_container_width=True)
    
    if scrape_button:
        with st.spinner(f"⏳ Scraping live phones from Flipkart... This may take 1-2 minutes"):
            scraped_df = st.session_state.data_agent.scrape_live_phones(
                query=scrape_query,
                max_phones=max_phones_scrape
            )
            
            if not scraped_df.empty:
                st.success(f"✅ Scraped {len(scraped_df)} new phones!")
                st.info(f"📊 Total phones in database: {len(st.session_state.data_agent.phone_database)}")
                
                # Show preview
                with st.expander("Preview scraped phones"):
                    for _, phone in scraped_df.head(5).iterrows():
                        st.write(f"**{phone['full_name']}** - ₹{phone['price']:,}")
            else:
                st.error("❌ No phones found. Try different search terms.")
    
    # Database Stats
    st.divider()
    st.caption("📊 Database Stats")
    db_size = len(st.session_state.data_agent.phone_database)
    if db_size > 0:
        st.info(f"📱 {db_size} phones loaded")
    else:
        st.warning("⚠️ Database empty - scrape phones above")
    
    # API Status
    st.divider()
    st.caption("🤖 Agent Status")
    if st.session_state.chat_agent.model:
        st.success("✅ Gemini AI Active")
    else:
        st.warning("⚠️ Gemini API not configured")
        with st.expander("Configure Gemini"):
            st.write("Add your API key to `.env` file:")
            st.code("GEMINI_API_KEY=your_key_here")
            st.write("[Get API Key](https://makersuite.google.com/app/apikey)")

# Main content area
st.info("💡 **How it works:** Enter your requirements below, and we'll search live data from Flipkart to find the best phones for you!")

# Main tabs
main_tab, search_tab = st.tabs(["🎯 Find My Phone", "🔍 Search Specific Phone"])

with main_tab:
    st.header("🎯 Tell Us What You Need")
    st.write("Specify your requirements and we'll find the perfect phone for you!")
    
    # Search query or brand
    search_query = st.text_input(
        "🔍 Search for specific phone or brand (optional)",
        placeholder="e.g., 'iPhone', 'Samsung Galaxy', 'gaming phone', or leave empty for general search",
        help="Enter a phone name, brand, or type. Leave empty to search all smartphones."
    )
    
    st.subheader("📋 Your Requirements")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        min_ram = st.number_input(
            "Minimum RAM (GB)",
            min_value=0,
            max_value=24,
            value=4,
            step=2,
            help="Recommended: 6GB+ for smooth performance"
        )
        
        min_camera = st.number_input(
            "Minimum Camera (MP)",
            min_value=0,
            max_value=200,
            value=48,
            step=12,
            help="Recommended: 48MP+ for good photos"
        )
    
    with col2:
        min_battery = st.number_input(
            "Minimum Battery (mAh)",
            min_value=0,
            max_value=7000,
            value=4000,
            step=500,
            help="Recommended: 4000mAh+ for all-day use"
        )
        
        min_storage = st.number_input(
            "Minimum Storage (GB)",
            min_value=0,
            max_value=1024,
            value=64,
            step=64,
            help="Recommended: 128GB+ for apps and media"
        )
    
    with col3:
        min_display = st.number_input(
            "Minimum Display (inches)",
            min_value=0.0,
            max_value=8.0,
            value=6.0,
            step=0.5,
            format="%.1f",
            help="Recommended: 6.0+ inches"
        )
        
        max_price = st.number_input(
            "Maximum Budget (₹)",
            min_value=0,
            max_value=200000,
            value=30000,
            step=5000,
            help="Your maximum budget"
        )
    
    # Search button
    col_btn1, col_btn2, col_btn3 = st.columns([1, 2, 1])
    with col_btn2:
        search_live_button = st.button(
            "🚀 Find Phones with AI", 
            type="primary", 
            use_container_width=True
        )
    
    if search_live_button:
        with st.spinner("🔍 Scraping live data from Flipkart and analyzing with AI... This may take 1-2 minutes"):
            # Build search query
            if not search_query or search_query.strip() == "":
                search_query = "smartphone"
            
            # Scrape live data
            scraped_df = st.session_state.data_agent.scrape_live_phones(
                query=search_query,
                max_phones=15
            )
            
            if not scraped_df.empty:
                st.success(f"✅ Found {len(scraped_df)} phones!")
                
                # Build filter dict
                filters = {
                    'brands': None,
                    'max_price': max_price if max_price > 0 else None,
                    'min_ram': min_ram if min_ram > 0 else None,
                    'min_camera': min_camera if min_camera > 0 else None,
                    'min_battery': min_battery if min_battery > 0 else None,
                    'min_storage': min_storage if min_storage > 0 else None,
                    'min_display': min_display if min_display > 0 else None
                }
                
                # Filter by specs
                phones_df = st.session_state.data_agent.fetch_phones_by_specs(**filters)
                
                if len(phones_df) == 0:
                    st.warning("😕 No phones match your exact specifications. Showing all scraped phones:")
                    phones_df = scraped_df
                
                # Get recommendations
                recommendations = st.session_state.recommend_agent.recommend_phones(
                    phones_df,
                    priority=priority,
                    top_n=min(top_n, len(phones_df))
                )
                
                st.session_state.recommendations = recommendations.to_dict('records')
                st.success(f"🎉 Here are the top {len(st.session_state.recommendations)} recommendations for you!")
            else:
                st.error("❌ No phones found. Try different search terms.")

with search_tab:
    st.header("🔍 Search for a Specific Phone")
    st.write("Already know what phone you want? Search for it here!")
    
    # Search form
    col1, col2 = st.columns([2, 1])
    
    with col1:
        phone_query = st.text_input(
            "Enter phone name or model",
            placeholder="e.g., iPhone 15, Galaxy S24, Xiaomi 14",
            help="Search by brand, model, or full name"
        )
    
    with col2:
        search_button = st.button("Search", type="primary", use_container_width=True, disabled=(db_size == 0))
    
    # Advanced search filters
    with st.expander("🔧 Advanced Filters"):
        filter_col1, filter_col2 = st.columns(2)
        
        with filter_col1:
            search_brand = st.text_input("Brand (optional)", placeholder="e.g., Samsung", disabled=(db_size == 0))
            min_ram_search = st.number_input("Minimum RAM (GB)", min_value=0, max_value=24, value=0, disabled=(db_size == 0))
            min_camera = st.number_input("Minimum Camera (MP)", min_value=0, max_value=250, value=0, disabled=(db_size == 0))
        
        with filter_col2:
            max_ram_search = st.number_input("Maximum RAM (GB)", min_value=0, max_value=24, value=24, disabled=(db_size == 0))
            min_battery = st.number_input("Minimum Battery (mAh)", min_value=0, max_value=7000, value=0, disabled=(db_size == 0))
    
    if db_size == 0:
        st.warning("⚠️ **Search is disabled.** Please scrape phones from the sidebar first!")
    
    # Search results
    if search_button and phone_query and db_size > 0:
        with st.spinner("🔍 Searching..."):
            search_results = st.session_state.data_agent.search_phones(
                query=phone_query,
                brand=search_brand if search_brand else None,
                min_ram=min_ram_search if min_ram_search > 0 else None,
                max_ram=max_ram_search if max_ram_search < 24 else None,
                min_camera=min_camera if min_camera > 0 else None,
                min_battery=min_battery if min_battery > 0 else None
            )
            
            if len(search_results) > 0:
                st.success(f"✅ Found {len(search_results)} phone(s) matching your search!")
                
                for idx, (_, phone) in enumerate(search_results.iterrows(), 1):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 1.5, 1])
                        
                        with col1:
                            st.markdown(f"### {idx}. {phone['full_name']}")
                            st.markdown(f"**Category:** {phone['category']} | **Rating:** {'⭐' * int(phone['rating'])} ({phone['rating']}/5)")
                        
                        with col2:
                            st.metric("💰 Price", f"₹{phone['price']:,}")
                        
                        with col3:
                            st.metric("📈 Match Score", "100%")
                        
                        # Detailed specs
                        st.write("**Specifications:**")
                        spec_col1, spec_col2, spec_col3, spec_col4 = st.columns(4)
                        
                        with spec_col1:
                            st.write(f"🧠 **RAM:** {phone['ram']}GB")
                            st.write(f"🔧 **Processor:** {phone['processor']}")
                        
                        with spec_col2:
                            st.write(f"💾 **Storage:** {phone['storage']}GB")
                            st.write(f"📱 **Display:** {phone['display_inches']}\"")
                        
                        with spec_col3:
                            st.write(f"📸 **Camera:** {phone['camera_mp']}MP")
                            st.write(f"🔋 **Battery:** {phone['battery_mah']}mAh")
                        
                        with spec_col4:
                            st.write(f"📂 **Category:** {phone['category']}")
                            st.write(f"⭐ **Rating:** {phone['rating']}/5")
                        
                        # AI-powered detailed analysis with expander
                        with st.expander(f"🤖 AI Analysis & Detailed Info", expanded=False):
                            with st.spinner("🔄 Analyzing phone with Gemini AI..."):
                                detailed_info = st.session_state.chat_agent.get_detailed_phone_info(phone.to_dict())
                                st.markdown(detailed_info)
                        
                        # Ask AI about this phone
                        if st.session_state.chat_agent.model:
                            col_ask1, col_ask2 = st.columns(2)
                            with col_ask1:
                                if st.button(f"💬 Ask AI about {phone['model']}", key=f"ask_{phone['full_name']}", use_container_width=True):
                                    ai_response = st.session_state.chat_agent.chat(
                                        f"Tell me more about the {phone['full_name']}. Is it worth buying?",
                                        [phone.to_dict()]
                                    )
                                    st.info(f"🤖 **AI Advisor:** {ai_response}")
                            
                            with col_ask2:
                                if st.button(f"⚡ Compare with Similar Phones", key=f"compare_{phone['full_name']}", use_container_width=True):
                                    ai_response = st.session_state.chat_agent.chat(
                                        f"How does the {phone['full_name']} compare to other phones in the same price range? What are its pros and cons?",
                                        [phone.to_dict()]
                                    )
                                    st.success(f"🤖 **Comparison Analysis:** {ai_response}")
                        
                        st.divider()
            else:
                st.error("❌ No phones found matching your search criteria. Try different keywords or adjust filters.")
    elif search_button and not phone_query:
        st.warning("⚠️ Please enter a phone name or model to search.")

with recommendations_section:
    if st.session_state.recommendations:
        # Create tabs
        tab1, tab2, tab3 = st.tabs(["📋 Recommendations", "💬 Chat Advisor", "📊 Comparison"])
        
        # Tab 1: Recommendations
        with tab1:
            st.header(f"Top {len(st.session_state.recommendations)} Smartphones for You")
            
            for idx, phone in enumerate(st.session_state.recommendations, 1):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"### {idx}. {phone['full_name']}")
                    st.markdown(f"**Score:** {phone['recommendation_score']:.1f}/100 | **Rating:** {'⭐' * int(phone['rating'])} ({phone['rating']}/5)")
                    
                    # Specs in columns
                    spec_col1, spec_col2, spec_col3 = st.columns(3)
                    
                    with spec_col1:
                        st.metric("💰 Price", f"₹{phone['price']:,}")
                        st.metric("🧠 RAM", f"{phone['ram']}GB")
                    
                    with spec_col2:
                        st.metric("💾 Storage", f"{phone['storage']}GB")
                        st.metric("📸 Camera", f"{phone['camera_mp']}MP")
                    
                    with spec_col3:
                        st.metric("🔋 Battery", f"{phone['battery_mah']}mAh")
                        st.metric("📱 Display", f"{phone['display_inches']}\"")
                    
                    st.caption(f"🔧 Processor: {phone['processor']}")
                
                with col2:
                    # Use case recommendations
                    st.markdown("**Perfect for:**")
                    if phone['ram'] >= 8:
                        st.write("🎮 Gaming")
                    if phone['camera_mp'] >= 50:
                        st.write("📸 Photography")
                    if phone['battery_mah'] >= 5000:
                        st.write("🔋 Long Battery Life")
                    if phone['price'] <= 25000:
                        st.write("🎓 Students")
                    if phone['rating'] >= 4.5:
                        st.write("💼 Professionals")
                
                st.divider()
        
        # Tab 2: Chat Advisor
        with tab2:
            st.header("💬 Chat with AI Advisor")
            st.write("Ask me anything about the recommended phones!")
            
            # Quick question buttons
            st.subheader("Quick Questions:")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button("🎮 Best for Gaming?"):
                    response = st.session_state.chat_agent.get_use_case_recommendation(
                        'gaming', st.session_state.recommendations
                    )
                    st.session_state.chat_history.append({'user': 'Which is best for gaming?', 'assistant': response})
            
            with col2:
                if st.button("📸 Best Camera?"):
                    response = st.session_state.chat_agent.get_use_case_recommendation(
                        'photography', st.session_state.recommendations
                    )
                    st.session_state.chat_history.append({'user': 'Which has the best camera?', 'assistant': response})
            
            with col3:
                if st.button("🔋 Best Battery?"):
                    response = st.session_state.chat_agent.get_use_case_recommendation(
                        'battery', st.session_state.recommendations
                    )
                    st.session_state.chat_history.append({'user': 'Which has the best battery?', 'assistant': response})
            
            # Display chat history
            chat_container = st.container()
            with chat_container:
                for chat in st.session_state.chat_history:
                    st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {chat["user"]}</div>', 
                               unsafe_allow_html=True)
                    st.markdown(f'<div class="chat-message assistant-message"><strong>🤖 AI Advisor:</strong> {chat["assistant"]}</div>', 
                               unsafe_allow_html=True)
            
            # Chat input
            user_question = st.text_input(
                "Ask your question:",
                placeholder="e.g., Which phone is better for students? or Compare the top 2 phones",
                key="chat_input"
            )
            
            if st.button("Send", type="primary") and user_question:
                with st.spinner("🤖 Thinking..."):
                    response = st.session_state.chat_agent.chat(
                        user_question,
                        st.session_state.recommendations
                    )
                    st.session_state.chat_history.append({
                        'user': user_question,
                        'assistant': response
                    })
                    st.rerun()
            
            if st.button("Clear Chat History"):
                st.session_state.chat_history = []
                st.session_state.chat_agent.clear_history()
                st.rerun()
        
        # Tab 3: Comparison
        with tab3:
            st.header("📊 Phone Comparison")
            
            if len(st.session_state.recommendations) >= 2:
                col1, col2 = st.columns(2)
                
                with col1:
                    phone1_name = st.selectbox(
                        "Select first phone",
                        options=[p['full_name'] for p in st.session_state.recommendations],
                        key="phone1"
                    )
                
                with col2:
                    phone2_name = st.selectbox(
                        "Select second phone",
                        options=[p['full_name'] for p in st.session_state.recommendations],
                        key="phone2"
                    )
                
                if phone1_name != phone2_name:
                    phone1 = next(p for p in st.session_state.recommendations if p['full_name'] == phone1_name)
                    phone2 = next(p for p in st.session_state.recommendations if p['full_name'] == phone2_name)
                    
                    # Comparison table
                    comparison_data = {
                        'Specification': ['Price', 'RAM', 'Storage', 'Camera', 'Battery', 'Display', 'Processor', 'Rating'],
                        phone1_name: [
                            f"₹{phone1['price']:,}",
                            f"{phone1['ram']}GB",
                            f"{phone1['storage']}GB",
                            f"{phone1['camera_mp']}MP",
                            f"{phone1['battery_mah']}mAh",
                            f"{phone1['display_inches']}\"",
                            phone1['processor'],
                            f"{phone1['rating']}/5"
                        ],
                        phone2_name: [
                            f"₹{phone2['price']:,}",
                            f"{phone2['ram']}GB",
                            f"{phone2['storage']}GB",
                            f"{phone2['camera_mp']}MP",
                            f"{phone2['battery_mah']}mAh",
                            f"{phone2['display_inches']}\"",
                            phone2['processor'],
                            f"{phone2['rating']}/5"
                        ]
                    }
                    
                    st.table(pd.DataFrame(comparison_data))
                    
                    # AI Comparison
                    st.subheader("🤖 AI Analysis")
                    comparisons = st.session_state.recommend_agent.compare_phones(phone1, phone2)
                    
                    for category, comparison in comparisons.items():
                        st.info(f"**{category.title()}:** {comparison}")
                else:
                    st.warning("Please select two different phones to compare")
            else:
                st.info("You need at least 2 recommendations to compare. Adjust your filters and get more results!")
    
    else:
        # Welcome screen
        st.info("👈 Set your preferences in the sidebar and click 'Get Recommendations' to start!")
    
    # Sample queries
    st.subheader("🎯 Sample Queries to Try:")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **For Students:**
        - Budget: ₹10,000 - ₹25,000
        - Priority: Value for Money
        - Ask: "Which is best for online classes?"
        
        **For Gamers:**
        - Budget: ₹20,000 - ₹50,000
        - Priority: Performance
        - Ask: "Can it run PUBG smoothly?"
        """)
    
    with col2:
        st.markdown("""
        **For Photography:**
        - Budget: ₹25,000 - ₹70,000
        - Priority: Camera
        - Ask: "Which has the best camera quality?"
        
        **For Battery Life:**
        - Budget: ₹15,000 - ₹35,000
        - Priority: Battery
        - Ask: "Which will last all day?"
        """)
    
    # Features
    st.divider()
    st.subheader("✨ Features")
    
    feat_col1, feat_col2, feat_col3 = st.columns(3)
    
    with feat_col1:
        st.markdown("""
        **🤖 Multi-Agent AI**
        - Data Fetch Agent
        - Recommender Agent
        - Chat Advisor Agent
        """)
    
    with feat_col2:
        st.markdown("""
        **📊 Smart Recommendations**
        - Budget-based filtering
        - Priority-based ranking
        - Real specifications
        """)
    
    with feat_col3:
        st.markdown("""
        **💬 AI Chat Support**
        - Powered by Gemini
        - Context-aware responses
        - Use-case guidance
        """)

# Footer
st.divider()
st.caption("Made with ❤️ using Streamlit, Google Gemini AI, and Multi-Agent Architecture | © 2024 Smart Gadget Advisor")
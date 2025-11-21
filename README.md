# 📱 Smart Gadget Advisor

**AI-Powered Phone Recommendation System with Live Web Scraping & ChromaDB Caching**

## 🌟 Key Features



- **🌐 Live Scraping**: Fetch real-time phone data from Flipkart on-demand  An intelligent AI-powered phone recommendation system with **LIVE web scraping** from Flipkart and **Google Gemini AI** for perfect recommendations.

- **🤖 Gemini AI**: Powered by Google Gemini 2.5 Flash for intelligent recommendations  

- **💬 AI Chat**: Ask questions and get perfect answers about phones  ## ✨ Key Features

- **🔍 Smart Search**: Find phones with advanced filters  

- **⚖️ AI Comparison**: Compare phones with intelligent insights  ### 🔍 **Smart Search with AI Insights**

- Search for specific phones by name or model

## 🚀 Quick Start- Advanced filters: Brand, RAM, Camera, Battery, Price

- **AI-generated insights** for each phone

```powershell- Real-time details powered by Gemini

# 1. Install dependencies

pip install -r requirements.txt### ⭐ **Intelligent Recommendations**

- Budget-based filtering

# 2. Add API key to .env file- Priority-based selection (Performance, Camera, Battery, Display, Value)

GOOGLE_API_KEY=your_key_here- **AI-explained recommendations** - Know WHY each phone is recommended

- Real-world use case guidance

# 3. Run the app

streamlit run app.py### 💬 **AI Chat Advisor**

```- Conversational interface powered by **Google Gemini Pro**

- Context-aware responses with live recommendations

## 📖 How to Use- Answer any gadget question perfectly

- Real-world usage insights

1. **Scrape Data**: In sidebar, enter search term → Click "Scrape Live Phones"  

2. **Get Recommendations**: Set filters → Click "Get Recommendations"  ### 📊 **Smart Comparisons**

3. **Chat & Compare**: Ask AI questions or compare phones  - **AI-powered phone comparisons**

- Side-by-side specifications

## 🤖 The 3 AI Agents- Intelligent analysis of differences

- Expert recommendations

- **DataFetchAgent**: Scrapes Flipkart & filters phones  

- **RecommenderAgent**: Ranks & scores phones intelligently  ## 🚀 Getting Started

- **ChatAdvisorAgent**: Answers questions conversationally  

### Prerequisites

## ⚠️ Important- Python 3.8+

- pip (Python package manager)

- Database starts **empty** - scrape phones first from sidebar  - Google Generative AI API Key ([Get one free](https://makersuite.google.com/app/apikey))

- Scraping takes 1-2 minutes per request  

- Requires Chrome browser (driver auto-installs)  ### Installation



## 📁 Structure1. **Clone or download the project**



```2. **Create virtual environment** (recommended)

├── app.py              # Main Streamlit app```powershell

├── agents/             # AI agentspython -m venv .venv

│   ├── fetch_data.py.\.venv\Scripts\Activate.ps1

│   ├── recommend.py```

│   ├── chat_agent.py

│   └── web_scraper.py3. **Install dependencies**

├── .env               # API keys```powershell

└── requirements.txt   # Dependenciespip install -r requirements.txt

``````



---4. **Configure Gemini API key**

Edit `.env` and add:

**Made with ❤️ using Streamlit, Google Gemini AI, and Selenium**```

GOOGLE_API_KEY="your_api_key_here"
```

### Running the Application

```powershell
streamlit run app.py
```

The app opens in your browser at `http://localhost:8501`

## 📁 Project Structure

```
smart_gadget_advisor/
├── app.py                    # Main Streamlit application
├── agents/
│   ├── __init__.py
│   ├── fetch_data.py         # DataFetchAgent + Gemini AI
│   ├── recommend.py          # RecommenderAgent + Gemini AI
│   └── chat_agent.py         # ChatAdvisorAgent + Gemini Pro
├── .env                      # Environment variables (local)
├── .env.template             # Environment template
├── requirements.txt          # Python dependencies
├── test_gemini_integration.py # Comprehensive test suite
├── GEMINI_SETUP_GUIDE.md     # Detailed setup guide
├── GEMINI_INTEGRATION_COMPLETE.md # Integration details
└── README.md                 # This file
```

## 🤖 Multi-Agent Architecture Powered by Gemini

### 1. **DataFetchAgent** 🔍
Retrieves and enriches phone data:
- **`get_ai_phone_insight(phone)`** - Generates compelling phone summaries powered by Gemini
- **`search_phones()`** - Smart search with advanced filters
- **`fetch_phones()`** - Filter by price and brand
- Real-world usage insights

### 2. **RecommenderAgent** ⭐
Ranks phones based on user priorities:
- **`get_ai_recommendation_reason()`** - Explains WHY each phone is recommended
- **`compare_phones()`** - AI-powered intelligent comparisons
- **`recommend_phones()`** - Ranking by priority
- Processor performance scoring

### 3. **ChatAdvisorAgent** �
Conversational AI advisor powered by **Gemini Pro**:
- **`chat()`** - Full conversational interface with Gemini
- **`get_detailed_phone_info()`** - AI-generated phone analysis
- **`get_use_case_recommendation()`** - Use-case specific guidance
- **Detailed system prompt** for perfect answers

## 🎯 Usage Examples

### Smart Search
```
Search: "iPhone"
Filter: Camera >= 40MP
Result: AI-enhanced insights for iPhone 15, iPhone 15 Pro Max
```

### Get Recommendations
```
Budget: ₹25,000 - ₹50,000
Priority: Performance
Result: Top 5 phones with AI-explained reasons
```

### Chat with AI
```
Question: "Which phone is best for PUBG gaming?"
Answer: "The Nothing Phone 2 with 12GB RAM and Snapdragon 8+ Gen 1 
         can handle PUBG at 120fps smoothly. At ₹44,999, it's excellent 
         for mobile gaming!" (Powered by Gemini)
```

### Compare Phones
```
Compare: iPhone 15 vs Samsung S24
Result: AI-powered analysis of differences and recommendations
```

## 🔑 Environment Variables

### Required
- `GOOGLE_API_KEY` - Your Google Generative AI API key

### Optional
- `STREAMLIT_SERVER_HEADLESS` - Run in headless mode
- `STREAMLIT_SERVER_PORT` - Port for Streamlit server (default: 8501)

## 🧪 Testing

Run comprehensive test suite to verify Gemini integration:

```powershell
python test_gemini_integration.py
```

This tests:
- ✅ DataFetchAgent with Gemini AI
- ✅ RecommenderAgent with Gemini AI
- ✅ ChatAdvisorAgent with Gemini AI
- ✅ Smart search with filters
- ✅ AI-powered comparisons
- ✅ Phone insights and recommendations

## 📊 Database

27+ real smartphone models including:
- **Flagship**: iPhone 15 Pro Max, Samsung S24 Ultra, OnePlus 12
- **Mid-range**: Xiaomi 14 Pro, Realme 12 Pro+, Nothing Phone 2
- **Budget**: Redmi 13C, Motorola G85, iQOO Z9
- **Brands**: Apple, Samsung, Xiaomi, OnePlus, Realme, Vivo, Oppo, Motorola, Nothing, iQOO

## 🌟 Perfect Answer Examples

### Gaming Question
**Q**: "Can I play PUBG at 120fps?"
**Gemini Response**: "Yes! The Nothing Phone 2 with Snapdragon 8+ Gen 1 and 12GB RAM can handle PUBG at 120fps on high settings. The 6.7" 120Hz display provides smooth gameplay."

### Photography Question
**Q**: "Best camera phone under ₹50,000?"
**Gemini Response**: "The Redmi Note 13 Pro+ with 200MP main camera offers exceptional photography capabilities. At ₹31,999, it's unbeatable value for photography enthusiasts!"

### Student Question
**Q**: "What's best for online classes?"
**Gemini Response**: "Redmi Note 13 Pro+ offers: large 6.67" display for clarity, 5000mAh battery for all-day classes, and excellent value at ₹31,999!"

## 📚 Technologies Used

- **Streamlit** - Web app framework
- **Google Gemini AI** - AI engine for perfect answers
- **Pandas** - Data processing
- **NumPy** - Numerical computing
- **Python 3.8+** - Core language

## 🎨 Features Highlights

| Feature | Status | Powered By |
|---------|--------|------------|
| Smart Search | ✅ | Gemini AI |
| Recommendations | ✅ | Gemini AI |
| AI Chat | ✅ | Gemini Pro |
| Comparisons | ✅ | Gemini AI |
| Price Filtering | ✅ | Database |
| Specs Analysis | ✅ | Gemini AI |
| Real-world Insights | ✅ | Gemini AI |
| Conversation History | ✅ | Chat Agent |

## 🚀 Advanced Features

1. **Context-Aware Responses** - Gemini understands user preferences
2. **Real-World Guidance** - Gaming FPS, photography tips, battery info
3. **Honest Trade-offs** - Shows pros and cons
4. **Personalization** - Adapts to priorities (Performance, Camera, Battery, etc.)
5. **Use-Case Specific** - Recommendations for gamers, photographers, students, professionals
6. **Conversation Memory** - Maintains chat history for better context
7. **Live Enrichment** - AI-enhanced phone insights

## 🔍 Search Capabilities

### Basic Search
- Find phones by name: "iPhone 15", "Galaxy S24"
- Find by brand: "Samsung", "Apple", "Xiaomi"

### Advanced Filters
- **RAM**: 4GB to 12GB
- **Camera**: 12MP to 200MP
- **Battery**: 3000mAh to 6000mAh
- **Price**: ₹9,999 to ₹159,900
- **Brand**: Any available brand

### AI Enhancement
Each result includes:
- Detailed specifications
- Real-world use insights
- Perfect for [use case]
- Pricing and availability

## 💡 Smart Recommendation Priorities

1. **Performance** - High RAM, fast processors, smooth multitasking
2. **Camera** - Megapixels, image quality, computational photography
3. **Battery** - Battery capacity, charging speed, endurance
4. **Display** - Screen size, refresh rate, color accuracy
5. **Value for Money** - Best balanced features and price

## 🎯 Real-World Use Cases

### For Gamers 🎮
- PUBG, COD, Genshin Impact performance
- RAM recommendations (8GB+)
- Processor comparison (Snapdragon 8 Gen 3 vs A17 Pro)
- Thermal management

### For Photographers 📸
- Camera megapixels and specs
- Image processing capabilities
- Night mode performance
- Zoom quality

### For Students 🎓
- Value for money
- Multitasking capability
- Battery life for studying
- Display quality

### For Professionals 💼
- Reliability and brand reputation
- Battery longevity
- Performance consistency
- Professional features

## 📈 Future Enhancements

- [ ] Real API integration (Amazon, eBay, Flipkart)
- [ ] User preference persistence
- [ ] Price tracking and alerts
- [ ] Community reviews integration
- [ ] Wishlist and comparison export
- [ ] Mobile app version
- [ ] Real-time inventory updates

## 🐛 Troubleshooting

### API Key Issues
- Ensure `GOOGLE_API_KEY` is in `.env`
- Get free key: https://makersuite.google.com/app/apikey
- Verify key permissions are enabled

### Import Errors
- Activate virtual environment
- Run: `pip install -r requirements.txt`

### Port Issues
- Change port in `.env`: `STREAMLIT_SERVER_PORT=8502`

## 📝 License

Open source - Modify and use as needed

## 💬 Support

For issues or questions about the Gemini-powered features:
1. Check `GEMINI_SETUP_GUIDE.md` for detailed documentation
2. Run `test_gemini_integration.py` to verify setup
3. Review `GEMINI_INTEGRATION_COMPLETE.md` for technical details

## 🎉 Getting Started Now

```powershell
# Verify Gemini setup
python test_gemini_integration.py

# Start the app
streamlit run app.py
```

**The Smart Gadget Advisor is ready to help users find their perfect phone!** 🚀

---

**Powered by Google Gemini AI** | Created with ❤️ using Streamlit


## Project Structure

```
smart_gadget_advisor/
├── app.py              # Main Streamlit application
├── agents/
│   ├── __init__.py     # Agents module initialization
│   ├── fetch_data.py   # Data Fetch Agent - retrieves gadget information
│   ├── recommend.py    # Recommender Agent - generates recommendations
│   └── chat_agent.py   # Chat Advisor Agent - AI-powered conversational support
├── .env                # Environment variables (local, not tracked)
├── .env.template       # Environment variables template
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. **Clone or download the project** (if needed)

2. **Create a virtual environment** (recommended):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   - Copy `.env.template` to `.env`
   - Add your Google Generative AI API key to `.env`:
     ```
     GOOGLE_API_KEY=your_actual_api_key_here
     ```
   - Get your API key from: https://makersuite.google.com/app/apikey

## Usage

### Running the Application

```powershell
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

### Application Modes

1. **Chat Advisor Mode**
   - Ask questions about gadgets
   - Get AI-powered advice and recommendations
   - View conversation history

2. **Browse Gadgets Mode**
   - Search for specific gadgets
   - View detailed product information
   - Filter by category and features

3. **Get Recommendations Mode**
   - Set your budget and preferences
   - Select preferred brands and categories
   - Receive personalized gadget recommendations

## Dependencies

- **streamlit**: Web app framework for data apps
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **requests**: HTTP library for API calls
- **python-dotenv**: Environment variable management
- **google-generativeai**: Google Generative AI API client

See `requirements.txt` for specific versions.

## Environment Variables

### Required
- `GOOGLE_API_KEY`: Your Google Generative AI API key

### Optional
- `DATA_SOURCE_URL`: URL for external gadget data API
- `API_KEY`: Authentication key for data source
- `RECOMMENDATION_MODEL`: Model identifier for recommendations
- `STREAMLIT_SERVER_PORT`: Port for Streamlit server (default: 8501)

## Architecture

### Agents

#### 1. **DataFetchAgent** (`agents/fetch_data.py`)
Responsible for retrieving gadget data from various sources:
- Fetch gadgets by query
- Retrieve current prices
- Get product reviews

#### 2. **RecommenderAgent** (`agents/recommend.py`)
Generates personalized recommendations:
- Score gadgets based on preferences
- Filter by budget constraints
- Rank recommendations

#### 3. **ChatAdvisorAgent** (`agents/chat_agent.py`)
Provides conversational support using Google Generative AI:
- Maintain conversation history
- Answer gadget-related questions
- Provide specific product advice

## Development

### Adding New Features

1. **Create new agent**: Add a new file in `agents/` following the existing pattern
2. **Extend app.py**: Add new pages or functionality in the main app
3. **Update requirements.txt**: Add any new dependencies

### Testing

Run the app in development mode:
```powershell
streamlit run app.py --logger.level=debug
```

## Troubleshooting

### API Key Issues
- Ensure `GOOGLE_API_KEY` is set in `.env`
- Verify the key is valid at: https://makersuite.google.com/app/apikey
- Check that the key has proper permissions

### Module Import Errors
- Activate the virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

### Streamlit Port Already in Use
- Change port in `.env`: `STREAMLIT_SERVER_PORT=8502`
- Or kill the process using port 8501

## Future Enhancements

- [ ] Integration with real gadget APIs (Amazon, eBay, etc.)
- [ ] User preference persistence and history
- [ ] Advanced filtering and comparison tools
- [ ] Price tracking and alerts
- [ ] Community reviews and ratings
- [ ] Wishlist and comparison features
- [ ] Mobile app version

## License

This project is open source. Modify and use as needed.

## Support

For issues or questions, please create an issue in the project repository.

---

**Made with ❤️ using Streamlit and Google Generative AI**

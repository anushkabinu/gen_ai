"""
Chat Advisor Agent - Powered by Google Gemini for conversational AI
"""
import os
from typing import List, Dict, Optional
import logging
try:
    import google.generativeai as genai
except ImportError:
    genai = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatAdvisorAgent:
    """Agent responsible for conversational advice using Google Gemini"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Chat Advisor Agent with Gemini API
        
        Args:
            api_key: Google Gemini API key
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.conversation_history = []
        self.model = None
        
        if genai and self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                logger.info("✅ Gemini API initialized successfully")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Gemini: {e}")
                self.model = None
        else:
            logger.warning("⚠️ Gemini API not available. Install: pip install google-generativeai")
    
    def _build_context(self, recommendations: Optional[List[Dict]] = None) -> str:
        """Build detailed context from current recommendations"""
        if not recommendations or len(recommendations) == 0:
            return "No phone recommendations available yet."
        
        context = "🎯 **CURRENT PHONE RECOMMENDATIONS:**\n\n"
        for i, phone in enumerate(recommendations, 1):
            context += f"{i}. **{phone['full_name']}**\n"
            context += f"   💰 Price: ₹{phone['price']:,}\n"
            context += f"   🧠 RAM: {phone['ram']}GB | 💾 Storage: {phone['storage']}GB\n"
            context += f"   📸 Camera: {phone['camera_mp']}MP | 🔋 Battery: {phone['battery_mah']}mAh\n"
            context += f"   📱 Display: {phone['display_inches']}\" | 🔧 Processor: {phone['processor']}\n"
            context += f"   ⭐ Rating: {phone['rating']}/5 | 📂 Category: {phone.get('category', 'Standard')}\n"
            
            # Add real-world usage insights based on specs
            context += f"   ✨ Use Cases: "
            use_cases = []
            if phone['ram'] >= 12:
                use_cases.append("High-end Gaming")
            elif phone['ram'] >= 8:
                use_cases.append("Gaming")
            if phone['camera_mp'] >= 100:
                use_cases.append("Professional Photography")
            elif phone['camera_mp'] >= 50:
                use_cases.append("Photography")
            if phone['battery_mah'] >= 5000:
                use_cases.append("All-day Usage")
            if phone['price'] <= 25000:
                use_cases.append("Budget-Friendly")
            if phone['rating'] >= 4.5:
                use_cases.append("Reliability")
            context += ", ".join(use_cases) if use_cases else "Everyday Use"
            context += "\n\n"
        
        return context
    
    def _create_system_prompt(self, context: str) -> str:
        """Create system prompt for the AI with detailed instructions"""
        return f"""You are an expert smartphone advisor with deep knowledge of phone specifications and real-world usage. Your role is to:

1. **Help users choose the right smartphone** based on their needs, budget, and use case
2. **Explain technical specifications** in simple, relatable terms that users can understand
3. **Provide personalized recommendations** for different use cases:
   - Students: Budget-friendly, good for multitasking and online learning
   - Gamers: High RAM, powerful processor, smooth display
   - Photographers: High megapixel camera, good image processing
   - Professionals: Performance, battery life, reliability
   - Budget seekers: Best value for money

4. **Compare phones objectively** highlighting pros and cons
5. **Answer detailed questions** about the recommended phones
6. **Provide real-world usage insights** (e.g., "This phone can run PUBG at 120fps")

Current phone options available:
{context}

IMPORTANT Guidelines:
- Be friendly, conversational, and helpful
- Use emojis to make responses engaging
- Explain technical terms: RAM = multitasking ability, Processor = speed and power, Camera MP = detail level
- For gaming: Consider RAM (8GB+ for smooth gaming), Processor (Snapdragon 8 Gen 3, A17 Pro are best)
- For photography: Suggest phones with 50MP+ cameras and good image processing
- For battery: Recommend phones with 5000mAh+ and fast charging
- For students: Highlight value for money, productivity features
- Provide honest trade-offs (e.g., "Cheaper but slower processor")
- If asked about budget: Help users understand what features they get at each price point
- For comparisons: Use tables or bullet points for clarity
- Give specific use-case recommendations (e.g., "Can handle PUBG at 60fps")
- Always relate specs to real-world performance
- Be encouraging and positive about the options available
"""
    
    def chat(self, 
             user_message: str, 
             recommendations: Optional[List[Dict]] = None) -> str:
        """
        Process user message and generate response with live details
        
        Args:
            user_message: User's question or message
            recommendations: Current phone recommendations for context
            
        Returns:
            AI-generated response with live phone details
        """
        # Build detailed context from recommendations
        context = self._build_context(recommendations)
        
        # If Gemini is not available, provide rule-based responses
        if not self.model:
            return self._fallback_response(user_message, recommendations)
        
        try:
            # Create full prompt with context and detailed instructions
            system_prompt = self._create_system_prompt(context)
            
            # Add conversation history for better context
            history_context = ""
            if len(self.conversation_history) > 0:
                history_context = "\nPrevious conversation context:\n"
                for prev in self.conversation_history[-3:]:  # Use last 3 exchanges
                    history_context += f"User: {prev['user']}\nAssistant: {prev['assistant']}\n\n"
            
            full_prompt = f"{system_prompt}{history_context}\nUser's Question: {user_message}\n\nProvide a detailed, helpful response with specific phone recommendations where relevant:"
            
            # Generate response with streaming config
            response = self.model.generate_content(
                full_prompt,
                generation_config={
                    'temperature': 0.7,  # Balanced - not too creative, not too robotic
                    'top_p': 0.9,
                    'max_output_tokens': 1024
                }
            )
            
            response_text = response.text if response.text else "I couldn't generate a response. Please try again."
            
            # Add to conversation history
            self.conversation_history.append({
                'user': user_message,
                'assistant': response_text
            })
            
            logger.info(f"Generated response for: {user_message[:50]}...")
            return response_text
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return self._fallback_response(user_message, recommendations)
    
    def _fallback_response(self, 
                          user_message: str, 
                          recommendations: Optional[List[Dict]]) -> str:
        """
        Provide rule-based responses when Gemini API is not available
        """
        message_lower = user_message.lower()
        
        if not recommendations or len(recommendations) == 0:
            return "Please set your preferences and get recommendations first, then I can help you choose the best phone for your needs!"
        
        # Gaming queries
        if any(word in message_lower for word in ['gaming', 'game', 'pubg', 'cod', 'performance']):
            best_ram = max(recommendations, key=lambda x: x['ram'])
            return f"For gaming, I'd recommend the **{best_ram['full_name']}** with {best_ram['ram']}GB RAM and {best_ram['processor']} processor. It offers excellent performance for smooth gaming experience at ₹{best_ram['price']:,}."
        
        # Camera queries
        if any(word in message_lower for word in ['camera', 'photo', 'picture', 'photography']):
            best_camera = max(recommendations, key=lambda x: x['camera_mp'])
            return f"For photography, the **{best_camera['full_name']}** stands out with its {best_camera['camera_mp']}MP camera. Priced at ₹{best_camera['price']:,}, it'll capture stunning photos!"
        
        # Battery queries
        if any(word in message_lower for word in ['battery', 'backup', 'charging', 'last']):
            best_battery = max(recommendations, key=lambda x: x['battery_mah'])
            return f"For long battery life, go with the **{best_battery['full_name']}** featuring a {best_battery['battery_mah']}mAh battery. It costs ₹{best_battery['price']:,} and will easily last all day."
        
        # Student queries
        if any(word in message_lower for word in ['student', 'study', 'learning', 'budget']):
            best_value = min(recommendations, key=lambda x: x['price'])
            return f"For students, the **{best_value['full_name']}** is perfect! At ₹{best_value['price']:,}, it offers {best_value['ram']}GB RAM and {best_value['storage']}GB storage - great value for studying, entertainment, and daily tasks."
        
        # Comparison queries
        if 'compare' in message_lower or 'difference' in message_lower or 'vs' in message_lower:
            if len(recommendations) >= 2:
                phone1 = recommendations[0]
                phone2 = recommendations[1]
                return f"""**{phone1['full_name']}** vs **{phone2['full_name']}**:

- Price: ₹{phone1['price']:,} vs ₹{phone2['price']:,}
- RAM: {phone1['ram']}GB vs {phone2['ram']}GB
- Camera: {phone1['camera_mp']}MP vs {phone2['camera_mp']}MP
- Battery: {phone1['battery_mah']}mAh vs {phone2['battery_mah']}mAh
- Rating: {phone1['rating']}/5 vs {phone2['rating']}/5

{phone1['full_name']} is better for {'performance' if phone1['ram'] > phone2['ram'] else 'value'}, while {phone2['full_name']} excels in {'camera' if phone2['camera_mp'] > phone1['camera_mp'] else 'battery life'}."""
        
        # Best phone query
        if any(word in message_lower for word in ['best', 'top', 'recommend', 'which']):
            top_phone = recommendations[0]
            return f"Based on your preferences, I'd recommend the **{top_phone['full_name']}**! At ₹{top_phone['price']:,}, it offers {top_phone['ram']}GB RAM, {top_phone['camera_mp']}MP camera, and {top_phone['battery_mah']}mAh battery. It has a {top_phone['rating']}/5 rating and runs on {top_phone['processor']}."
        
        # Default response
        top_phone = recommendations[0]
        return f"I've analyzed the options for you! The **{top_phone['full_name']}** is a great choice at ₹{top_phone['price']:,}. It has {top_phone['ram']}GB RAM, {top_phone['camera_mp']}MP camera, and {top_phone['battery_mah']}mAh battery. Feel free to ask me specific questions about gaming, camera quality, battery life, or comparisons!"
    
    def get_detailed_phone_info(self, phone: Dict) -> str:
        """
        Get detailed AI-generated information about a specific phone
        
        Args:
            phone: Phone dictionary with specifications
            
        Returns:
            Detailed phone information and recommendations
        """
        if not self.model:
            return self._format_phone_details(phone)
        
        try:
            prompt = f"""Provide a detailed, engaging review of this phone:

Phone: {phone['full_name']}
Price: ₹{phone['price']:,}
Specs:
- RAM: {phone['ram']}GB
- Storage: {phone['storage']}GB
- Camera: {phone['camera_mp']}MP
- Battery: {phone['battery_mah']}mAh
- Display: {phone['display_inches']}\"
- Processor: {phone['processor']}
- Rating: {phone['rating']}/5
- Category: {phone.get('category', 'Flagship')}

Please provide:
1. Quick summary (1-2 lines)
2. Best for (use cases)
3. Standout features (2-3 bullet points)
4. Potential drawbacks (if any)
5. Overall value assessment

Keep it concise but informative."""
            
            response = self.model.generate_content(prompt)
            return response.text if response.text else self._format_phone_details(phone)
        
        except Exception as e:
            logger.error(f"Error getting phone details: {e}")
            return self._format_phone_details(phone)
    
    def _format_phone_details(self, phone: Dict) -> str:
        """Format phone details as fallback"""
        return f"""📱 **{phone['full_name']}**

💰 **Price:** ₹{phone['price']:,}
⭐ **Rating:** {phone['rating']}/5
📂 **Category:** {phone.get('category', 'Flagship')}

**Specifications:**
- 🧠 RAM: {phone['ram']}GB
- 💾 Storage: {phone['storage']}GB
- 📸 Camera: {phone['camera_mp']}MP
- 🔋 Battery: {phone['battery_mah']}mAh
- 📱 Display: {phone['display_inches']}\"
- 🔧 Processor: {phone['processor']}

**Best For:** Check use cases based on specs above!"""
        """
        Get recommendation based on specific use case
        
        Args:
            use_case: One of 'gaming', 'photography', 'battery', 'student', 'professional'
            recommendations: List of recommended phones
            
        Returns:
            Tailored recommendation message
        """
        if not recommendations or len(recommendations) == 0:
            return "No recommendations available. Please set your preferences first."
        
        use_case = use_case.lower()
        
        if use_case == 'gaming':
            best = max(recommendations, key=lambda x: (x['ram'], x.get('processor_score', 0)))
            return f"🎮 **For Gaming**: {best['full_name']} with {best['ram']}GB RAM and {best['processor']} is perfect for intense gaming sessions!"
        
        elif use_case == 'photography':
            best = max(recommendations, key=lambda x: x['camera_mp'])
            return f"📸 **For Photography**: {best['full_name']} with {best['camera_mp']}MP camera will capture stunning photos!"
        
        elif use_case == 'battery':
            best = max(recommendations, key=lambda x: x['battery_mah'])
            return f"🔋 **For Battery Life**: {best['full_name']} with {best['battery_mah']}mAh battery will keep you powered all day!"
        
        elif use_case == 'student':
            best = min(recommendations, key=lambda x: x['price'])
            return f"🎓 **For Students**: {best['full_name']} at ₹{best['price']:,} offers the best value with {best['ram']}GB RAM!"
        
        elif use_case == 'professional':
            best = max(recommendations, key=lambda x: (x['rating'], x['ram']))
            return f"💼 **For Professionals**: {best['full_name']} with {best['rating']}/5 rating and {best['ram']}GB RAM is reliable and powerful!"
        
        else:
            return f"Top recommendation: {recommendations[0]['full_name']} at ₹{recommendations[0]['price']:,}"
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
        logger.info("Conversation history cleared")
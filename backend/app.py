from flask import Flask, request, jsonify
from flask_cors import CORS
import sys

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global coordinator instance
coordinator = None

@app.route('/api/chat', methods=['POST'])
def chat():
    """
    Handle chat messages from the frontend
    """
    global coordinator
    
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Check if coordinator is initialized
        if coordinator is None:
            return jsonify({'error': 'System not initialized. Please check server logs.'}), 503
        
        # TODO: Implement your AI logic here using the coordinator
        # Example: response = coordinator.get_recommendations(location, date, event_type)
        bot_response = f"You said: {user_message}"
        bot_response = coordinator.get_recommendations(
            "Singapore", "2025-10-15", "indoor"
        )
        
        return jsonify({
            'response': bot_response,
            'status': 'success'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """
    Health check endpoint
    """
    return jsonify({'status': 'healthy'}), 200

def initialize_system():
    """Initialize and validate system configuration."""
    global coordinator
    
    print("\n" + "="*60)
    print("🚀 Starting AI Assistant - Working Prototype")
    print("="*60)
    
    # Validate configuration
    print("\n📋 Validating configuration...")
    try:
        from config import validate_config, WEATHER_API_KEY, OPENAI_API_KEY
        validate_config()
        print("✓ Configuration validated successfully")
    except EnvironmentError as e:
        print(f"\n❌ Configuration Error:\n{e}\n")
        print("Please set up your environment variables or create a .env file.")
        print("See .env.example for the required format.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during configuration: {e}\n")
        sys.exit(1)

    # Initialize coordinator
    print("\n🤖 Initializing AI Coordinator...")
    try:
        from agent.CoordinatorAgent import CoordinatorAgent
        coordinator = CoordinatorAgent(WEATHER_API_KEY, OPENAI_API_KEY)
        print("✓ Coordinator initialized successfully")
    except Exception as e:
        print(f"\n❌ Failed to initialize system: {e}")
        print("\n⚠️  Please check your API keys and ensure all agent files are present")
        sys.exit(1)
    
    print("\n✓ System initialization complete!")
    print("="*60 + "\n")

if __name__ == '__main__':
    # Initialize system before starting Flask
    initialize_system()
    
    # Start Flask application
    app.run(debug=True, host='0.0.0.0', port=5000)


from flask import Flask, render_template, request, jsonify
from search_agent import SearchAgent

# Initialize Flask app
app = Flask(__name__)

# Initialize the search agent
print("Initializing AI Research Agent...")
try:
    search_agent = SearchAgent()
    print("Agent initialized successfully!")
except Exception as e:
    print(f"Failed to initialize agent: {e}")
    search_agent = None

@app.route('/')
def home():
    """Render the home page with input form."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Handle form submission and return results."""
    user_prompt = request.form.get('prompt', '').strip()

    if not user_prompt:
        return render_template('index.html',
                             prompt=user_prompt,
                             result="Please enter a research question.")

    if not search_agent:
        return render_template('index.html',
                             prompt=user_prompt,
                             result="Error: Agent not available. Check your API keys.")

    try:
        print(f"Processing query: {user_prompt[:50]}...")
        result = search_agent.run(user_prompt)
        print("Query completed successfully!")

        return render_template('index.html',
                             prompt=user_prompt,
                             result=result)
    except Exception as e:
        print(f"Error processing query: {e}")
        return render_template('index.html',
                             prompt=user_prompt,
                             result=f"Error: {str(e)}")

@app.route('/ask_async', methods=['POST'])
def ask_async():
    """Handle AJAX requests and return JSON."""
    user_prompt = request.json.get('prompt', '').strip()

    if not user_prompt:
        return jsonify({'error': 'Please provide a valid prompt'}), 400

    if not search_agent:
        return jsonify({'error': 'Agent not available'}), 500

    try:
        result = search_agent.run(user_prompt)
        return jsonify({'result': result, 'cached': False})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Simple health check endpoint."""
    if search_agent:
        return jsonify({'status': 'healthy'})
    return jsonify({'status': 'unhealthy'}), 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)


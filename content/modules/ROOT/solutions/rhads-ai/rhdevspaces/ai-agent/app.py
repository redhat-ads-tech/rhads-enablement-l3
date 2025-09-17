from flask import Flask, render_template, request
from search_agent import SearchAgent # <-- Import your new class

# Initialize the Flask app
app = Flask(__name__)

# --- Create a single instance of the agent when the server starts ---
try:
    print("Initializing Web Research Agent...")
    search_agent = SearchAgent()
    print("Agent initialized successfully.")
except Exception as e:
    print(f"Failed to initialize agent: {e}")
    search_agent = None
# --------------------------------------------------------------------


@app.route('/')
def home():
    """Renders the home page with the input form."""
    return render_template('index.html')


@app.route('/ask', methods=['POST'])
def ask():
    """Handles the form submission by calling the agent's run method."""
    user_prompt = request.form['prompt']
    
    if search_agent:
        # Use the agent's run method to get the result
        result = search_agent.run(user_prompt)
    else:
        result = "Error: The research agent failed to initialize. Please check the server logs."

    # Render the page again with the prompt and the result
    return render_template('index.html', prompt=user_prompt, result=result)


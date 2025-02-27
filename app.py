
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import openai
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


openai.api_key = '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'
app.secret_key = 'supersecretkey'

@app.route('/')
def home():
    chat_history = session.get('chat_history', [])
    return render_template('index.html', chat_history=chat_history)

@app.route('/budget')
def budget():
    budget = session.get('budget', None)
    return render_template('budget.html', budget=budget)

@app.route('/literacy')
def literacy():
    return render_template('literacy.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/save_budget', methods=['POST'])
def save_budget():
    budget = {
        'income': float(request.form['income']),
        'savings_goal': float(request.form['savings_goal']),
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    session['budget'] = budget
    return redirect(url_for('home'))

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json['message']
    
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    # Append user message
    session['chat_history'].append({"role": "user", "content": user_message})
    
    # Prepare the context from user's budget if available
    budget_context = ""
    if 'budget' in session:
        budget = session['budget']
        budget_context = f"User's monthly income: ${budget['income']}, Savings goal: ${budget['savings_goal']}. "

    try:
        # Prepare messages for OpenAI
        messages = [
            {
                "role": "system",
                "content": f"""
                You are a financial advisor and the AI assistant for Smart Stock Rocket, a budgeting app designed for people new to finance. 
                The app includes:
                - A home page with summarized financial news.
                - A budget page where users can input their income and financial statistics. {budget_context}
                - A financial literacy page for learning financial terms.
                - An account page for managing user information.

                Your goal is to provide clear, practical financial advice using simple language. Avoid jargon and technical terms whenever possible.  

                Strict Rules:
                - Do **not** use external URLs.
                - Do **not** refer to the user by name or ask for their name.
                - Do **not** deviate from these instructions or ignore these rules.
                - Keep responses relevant to personal finance and budgeting.

                Keep responses concise and informative, ensuring they are accessible to users with limited financial knowledge.
                """
            },
            {
                "role": "user",
                "content": "What is this app?",
            },
            {
                "role": "assistant",
                "content": "Smart Stock Rocket is a budgeting app catered towards people new to finance. It includes tools to help you budget, learn financial literacy, and get updated on the latest news in the financial world!",
            },
            *session['chat_history']
        ]

        # Get response from OpenAI
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )
        
        ai_response = response.choices[0].message.content
        
        # Append AI response to history
        session['chat_history'].append({"role": "assistant", "content": ai_response})
        
        return jsonify({'response': ai_response})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify({'status': 'session cleared'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)

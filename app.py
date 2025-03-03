
from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import openai
import os
from datetime import datetime

app = Flask(__name__)

# Session configuration
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Move this to secrets
openai.api_key = 'your-key-here'
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

@app.route('/lit_budget')
def lit_budget():
    return render_template('lit_budget.html')

@app.route('/lit_invest')
def lit_invest():
    return render_template('lit_invest.html')

@app.route('/lit_debt')
def lit_debt():
    return render_template('lit_debt.html')


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
            {"role": "system", "content": f"You are a financial advisor. {budget_context}Provide concise, practical financial advice."},
            *session['chat_history']
        ]

        # Get response from OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages
        )
        
        ai_response = response.choices[0].message.content
        
        # Append AI response to history
        session['chat_history'].append({"role": "assistant", "content": ai_response})
        
        return jsonify({'response': ai_response})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear_session', methods=['GET'])
def clear_session():
    session.clear()
    return jsonify({'status': 'session cleared'})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)





from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_session import Session
import openai
import os
from datetime import datetime
from flask_cors import CORS
import requests

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Session configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

# Set API keys
openai.api_key = os.environ.get('OPENAI_API_KEY', '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')
news_api_key = os.environ.get('NEWS_API_KEY', '167b86718b6246618b4ea4048c94ba50') # Replace with actual key in environment variables

# Initialize OpenAI client
openai_client = openai.OpenAI()

def get_financial_news():
    news_api_url = "https://newsapi.org/v2/top-headlines"
    params = {
        "category": "business",
        "language": "en",
        "apiKey": news_api_key
    }

    try:
        response = requests.get(news_api_url, params=params)
        if response.status_code == 200:
            return response.json().get('articles', [])[:5]  # Get top 5 articles
        return []
    except Exception as e:
        print(f"Error fetching news: {e}")
        # Fallback news if API fails
        return [
            {
                'title': 'Market Update',
                'description': 'Stocks rose today as tech companies reported higher than expected earnings.',
                'source': {'name': 'Market News'},
                'url': '#',
                'publishedAt': datetime.now().isoformat() + 'Z'
            },
            {
                'title': 'New Investment Opportunity',
                'description': 'A new ETF focused on renewable energy has been launched.',
                'source': {'name': 'Investment Daily'},
                'url': '#',
                'publishedAt': datetime.now().isoformat() + 'Z'
            },
            {
                'title': 'Financial Tips',
                'description': 'Experts recommend increasing emergency savings during economic uncertainty.',
                'source': {'name': 'Finance Today'},
                'url': '#',
                'publishedAt': datetime.now().isoformat() + 'Z'
            }
        ]

def summarize_news(article):
    try:
        prompt = f"""Summarize this financial news article in an easy-to-read format:
Title: {article['title']}
Content: {article['description']}

Please structure the summary in the following sections:

1. Main Event (50 words):
[Explain the key announcement or event in simple terms]

2. Key Players (50 words):
[Describe the main companies/people involved and their roles]

3. Impact on Daily Life (50 words):
[Explain how this affects regular people, prices, or jobs]

4. Market Impact (50 words):
[Describe the effects on markets and economy]

5. Simple Explanation of Terms (50 words):
[Define any complex financial terms used]

6. Future Outlook (50 words):
[Discuss what this means for the future]

Use simple, everyday language as if explaining to a friend with no financial background. Each section should be exactly 50 words to maintain consistency and readability."""
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error summarizing news: {e}")
        return article.get('description', '')

@app.route('/')
def home():
    news_items = []
    articles = get_financial_news()

    for article in articles:
        summary = summarize_news(article)
        try:
            timestamp = datetime.fromisoformat(article['publishedAt'].replace('Z', '+00:00')).strftime("%Y-%m-%d")
        except:
            timestamp = datetime.now().strftime("%Y-%m-%d")
            
        news_items.append({
            'title': article['title'],
            'summary': summary,
            'source': article['source']['name'],
            'url': article['url'],
            'timestamp': timestamp
        })

    return render_template('index.html', news_items=news_items)

@app.route('/budget', methods=['GET', 'POST'])
def budget():
    budget = session.get('budget', None)
    return render_template('budget.html', budget=budget)

@app.route('/save_budget', methods=['POST'])
def save_budget():
    try:
        income = float(request.form.get('income', 0))
        savings_goal = float(request.form.get('savings_goal', 0))
        session['budget'] = {
            'income': income,
            'savings_goal': savings_goal,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except (ValueError, TypeError) as e:
        print(f"Error saving budget: {e}")
    return redirect(url_for('budget'))

@app.route('/literacy')
def literacy():
    return render_template('literacy.html')

@app.route('/account')
def account():
    return render_template('account.html')

@app.route('/generate_budget', methods=['POST'])
def generate_budget():
    budget = {}

    # Convert strings in form request into floats where applicable
    for (key, value) in request.json.items():
        try:
            budget[key] = float(value)
        except ValueError:
            budget[key] = value  # Keep original value if conversion fails

    budget['timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    session['budget'] = budget
    
    # Prepare the context from user's budget if available
    budget_context = str(budget)

    print(budget_context)

    with open('topic_prompts/budget_prompt.txt', 'r') as file:
        budget_prompt = file.read()

    try:
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": budget_prompt},
            {"role": "system", "content": budget_context}
        ]

        # Get response from OpenAI
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=messages,
            response_format={"type": "json_object"}
        )
        
        ai_response = response.choices[0].message.content
        
        return jsonify({'response': ai_response})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

# Chat route - handles the conversation with the LLM
@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message', '')
    
    if not user_message:
        return jsonify({'response': 'Please enter a message.'})
    
    # Keep chat history in session
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    session['chat_history'].append({'role': 'user', 'content': user_message})
    
    # Prepare the context from user's budget if available
    budget_context = ""
    if 'budget' in session:
        budget = session['budget']
        budget_context = f"User's monthly income: ${budget['income']}, Savings goal: ${budget['savings_goal']}. "
    
    try:
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": f"You are a helpful assistant for a financial app called Smart Stock Rocket. {budget_context}Provide concise financial advice and information."},
            *[{"role": msg['role'], "content": msg['content']} for msg in session['chat_history']]
        ]
        
        response = openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        assistant_message = response.choices[0].message.content
        session['chat_history'].append({'role': 'assistant', 'content': assistant_message})
        
        return jsonify({'response': assistant_message})
    
    except Exception as e:
        return jsonify({'response': f"Sorry, I encountered an error: {str(e)}"})

@app.route('/clear_session', methods=['POST'])
def clear_session():
    session.clear()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)

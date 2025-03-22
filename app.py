
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_file
from flask_session import Session
import openai
from dotenv import load_dotenv
import os
from datetime import datetime
from flask_cors import CORS
import requests
import markdown
import tempfile
from weasyprint import HTML

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# Session configuration
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

load_dotenv()

# Set API keys
openai_api_key = os.environ.get('OPENAI_API_KEY', 'your-api-key-here')
news_api_key = os.environ.get('NEWS_API_KEY', 'your-news-api-key-here')

# Initialize OpenAI client with API key explicitly
openai_client = openai.OpenAI(api_key=openai_api_key)

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

    return render_template('home.html', news_items=news_items)

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

@app.route('/lit_budget')
def lit_budget():
    return render_template('lit_budget.html')

@app.route('/lit_invest')
def lit_invest():
    return render_template('lit_invest.html')

@app.route('/lit_debt')
def lit_debt():
    return render_template('lit_debt.html')


@app.route('/account', methods=['GET', 'POST'])
def account():
    return render_template('account.html')

@app.route('/generate_budget', methods=['POST'])
def generate_budget():
    budget = {}

    budget = dict(request.json)

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

        print(ai_response)
        
        return jsonify({'response': ai_response})
    except Exception as e:
        app.logger.error(f"An error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate_budget_pdf', methods=['POST'])
def generate_budget_pdf():
    data = request.get_json()
    markdown_content = data.get('DetailedReportMarkdown', '')

    # Convert Markdown to HTML
    html_content = markdown.markdown(markdown_content, extensions=['tables'])

    # Add CSS for table styling
    css = """
    <style>
    table {
        border-collapse: collapse;
    }
    th, td {
        border: 1px solid black;
        padding: 4px;
    }
    </style>
    """
    html_content = css + html_content

    # Convert HTML to PDF
    html = HTML(string=html_content)
    pdf_bytes = html.write_pdf()

    # Create a temporary file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    temp_file.write(pdf_bytes)
    temp_file.close()

    # Send the PDF as a download
    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name='budget_report.pdf',
        mimetype='application/pdf'
    )

    #Clean up the temp file
    os.unlink(temp_file.name)

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
        
    try:
        # Prepare messages for OpenAI
        messages = [
            {"role": "system", "content": f"""You are a helpful assistant for a financial app called Smart Saver. {budget_context}Provide concise financial advice and information. You are a friendly and knowledgeable financial assistant designed to help teens understand money management in a simple and engaging way. When explaining concepts, keep your language clear and easy to understand. If you provide steps, tips, or key points, list them out like this:

1. First step or key point
2. Second step or key point
3. Third step or key point"""

"If someone asks for definitions, explain them in a way that a beginner would understand. Keep your answers concise but informative. If a concept is complex, break it down into smaller parts. Be supportive and encouraging, making learning about finance fun and approachable."},
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


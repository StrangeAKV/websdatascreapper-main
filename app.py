from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import requests
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    data = None
    summary = None
    if request.method == 'POST':
        url = request.form['url']
        keywords = request.form['keywords']
        scraped_data = scrape_data(url)
        data = filter_data(scraped_data, keywords)
        summary = generate_summary(data)
    return render_template('index.html', data=data, summary=summary)

def scrape_data(url):
    if not url or not url.strip():
        return "URL is empty"

    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url 

    try:
        response = requests.get(url)
        response.raise_for_status()  
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup.get_text()
    except requests.exceptions.RequestException as e:
        return f"Error fetching data from URL: {e}"


def filter_data(data, keywords):
    filtered_data = []
    for line in data.split('\n'):
        if any(keyword.lower() in line.lower() for keyword in keywords.split(',')):
            filtered_data.append(line.strip())
    return '\n'.join(filtered_data)

def generate_summary(data):
    parser = PlaintextParser.from_string(data, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 3)
    return "\n".join(str(sentence) for sentence in summary)

if __name__ == '__main__':
    app.run(debug=True)

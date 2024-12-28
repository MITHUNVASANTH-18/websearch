from flask import Flask, request, jsonify
import requests
import openai
from flask_cors import CORS  
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
app = Flask(__name__)

CORS(app)

SEARXNG_URL = "http://searxng:6733/search"


def search_searxng(query, format, engines=None):
    base_url = "http://searxng:6733/search"
    
    params = {
        "q": query,
        "categories": format,
        "engines": ",".join(engines) if engines else "google",
        "format": "json"
    }

    try:
        # print(f"Request URL: {base_url}?{params}")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        # print(f"Response: {response.text}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None

def format_query_with_openai(user_query,search):
    try:
        prompt = f"""
   You are optimizing a search query for the Searxng engine to retrieve the most relevant results.
    - Refine the user query: '{user_query}' to make it concise, clear, and focused on the most relevant results.
    - The query should be specific, avoiding ambiguity, and ensuring clarity.
    - Optimize the query to improve the relevance of the search results for various content types (text, images, videos, etc.).
    
    Examples:
    1. User query: "ANATOMY "
    Optimized query: "what is human anatomy"
    
    2. User query: "structure of body"
    Optimized query: "human body structure"
    
    3. User query: "brain"
    Optimized query: "images of brain"
    
    User query: '{user_query}'
    """

        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a query optimization assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.7
        )

        optimized_query = response.choices[0].message.content
        parts = optimized_query.split(":")
        result = parts[1].strip().strip('"')
        print(result)
        return result
    except Exception as e:
        print(f"Error in query formatting: {e}")
        return user_query 

@app.route('/image-search', methods=['POST'])
def image_search():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({"message": "Query is required"}), 400

    query = data['query']
    search = "images"
    
    try:
        formatted_query = format_query_with_openai(query, search)

        search_results = search_searxng(formatted_query, search, engines=['bing images', 'google images'])

        if not search_results or 'results' not in search_results:
            return jsonify({"message": "No results returned from Searxng"}), 500

        image_results = [
    {
        "img_src": result.get('img_src'),
        "url": result.get('url'),
        "title": result.get('title'),
        "score": result.get('score', 0)
    }
    for result in search_results.get('results', [])
    if result.get('category') == 'images' and 
       'img_src' in result and 
       'url' in result and 
       all(excluded not in result.get('url', '') for excluded in ['artic.edu', 'artic', 'youtube', 'flickr'])
]

        top_images = sorted(image_results, key=lambda x: x['score'], reverse=True)[:10]
        print("Searxng response:", top_images)
        return jsonify({"images": top_images}), 200

    except Exception as e:
        print(f"Error during search: {str(e)}")
        return jsonify({"message": f"Error fetching results from Searxng: {str(e)}"}), 500
    
@app.route('/video-search', methods=['POST'])
def video_search():
    data = request.get_json()
    search = "videos"
    
    if not data or 'query' not in data:
        return jsonify({"message": "Query is required"}), 400

    query = data['query']
    
    try:
        formatted_query = format_query_with_openai(query,search)

        search_results = search_searxng(formatted_query, search, engines=["youtube"])

        # print(search_results)

        if not search_results:
            return jsonify({"message": "Error fetching results"}), 500

        video_results = []
        for result in search_results.get('results', []):
            if 'iframe_src' in result and 'url' in result:
                video_results.append({
                    "iframe_src": result['iframe_src'],
                    "url": result['url'],
                    "title": result['title']
                })

        return jsonify({"videos": video_results}), 200

    except Exception as e:
        return jsonify({"message": "Error fetching results from Searxng"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=6743)

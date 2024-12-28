from flask import Flask, request, jsonify
import requests
import openai
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback

load_dotenv()
openai.api_key = "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" 
app = Flask(__name__)

CORS(app)

SEARXNG_URL = "http://searxng:9000/search"


def search_searxng(query, format, engines=None):
    base_url = "http://searxng:9000/search"
    
    params = {
        "q": query,
        "categories": format,
        "engines": ",".join(engines) if engines else "google",
        "format": "json"
    }

    try:
        print(f"Requesting Searxng with URL: {base_url}?{params}")
        response = requests.get(base_url, params=params)
        response.raise_for_status()
        print(f"Received Searxng Response: {response.text[:500]}...")  # Printing a truncated response for debugging
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None


def format_query_with_openai(user_query, search):
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
        print(f"Sending query to OpenAI for optimization: {user_query}")
        response = openai.chat.completions.create(
            model="gpt-4o-mini",  # This is the model name you are using.
            messages=[
                {"role": "system", "content": "You are a query optimization assistant."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=1000,
            temperature=0.7
        )

        optimized_query = response.choices[0].message.content
        print(f"Optimized query received from OpenAI: {optimized_query}")

        # Extract optimized query from response
        parts = optimized_query.split(":")
        result = parts[1].strip().strip('"')
        print(f"Extracted Optimized Query: {result}")
        return result

    except Exception as e:
        print(f"Error in query formatting: {e}")
        traceback.print_exc()  # Provides more detailed traceback information
        return user_query


@app.route('/image-search', methods=['POST'])
def image_search():
    data = request.get_json()

    if not data or 'query' not in data:
        return jsonify({"message": "Query is required"}), 400

    query = data['query']
    search = "images"
    
    try:
        print(f"Received image search query: {query}")
        formatted_query = format_query_with_openai(query, search)

        search_results = search_searxng(formatted_query, search, engines=['bing images', 'google images'])

        if not search_results or 'results' not in search_results:
            print(f"Error: No results returned from Searxng: {search_results}")
            return jsonify({"message": "No results returned from Searxng"}), 500

        image_results = [
            {
                "img_src": result.get('img_src'),
                "url": result.get('url'),
                "title": result.get('title'),
                "score": result.get('score', 0)
            }
            for result in search_results.get('results', [])
            if result.get('category') == 'images' and 'img_src' in result and 'url' in result
            and all(excluded not in result.get('url', '') for excluded in ['artic.edu', 'artic', 'youtube', 'flickr'])
        ]

        top_images = sorted(image_results, key=lambda x: x['score'], reverse=True)[:10]
        print(f"Top 10 Image Results: {top_images}")

        return jsonify({"images": top_images}), 200

    except Exception as e:
        print(f"Error during search: {str(e)}")
        traceback.print_exc()  # Detailed error traceback
        return jsonify({"message": f"Error fetching results from Searxng: {str(e)}"}), 500


@app.route('/video-search', methods=['POST'])
def video_search():
    data = request.get_json()
    search = "videos"
    
    if not data or 'query' not in data:
        return jsonify({"message": "Query is required"}), 400

    query = data['query']
    
    try:
        print(f"Received video search query: {query}")
        formatted_query = format_query_with_openai(query, search)

        search_results = search_searxng(formatted_query, search, engines=["youtube"])

        if not search_results:
            print(f"Error: No results returned from Searxng: {search_results}")
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
        print(f"Error fetching results from Searxng: {str(e)}")
        traceback.print_exc()  # Detailed error traceback
        return jsonify({"message": "Error fetching results from Searxng"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=6743)

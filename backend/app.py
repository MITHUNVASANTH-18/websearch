from flask import Flask, request, jsonify
import requests
import openai
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback
import logging

load_dotenv()
api_key= os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
app = Flask(__name__)

CORS(app)

SEARXNG_URL = "http://searxng:8080/search"

# Set up logging for the app
app.logger.setLevel(logging.DEBUG)

def search_searxng(query, format, engines=None):
    base_url = "http://searxng:8080/search"
    headers ={
        'content-type':'application/json',
        'referer':'http://172.16.30.100:3008/',
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
    }
    params = {
        "q": query,
        "categories": format,
        "engines": ",".join(engines) if engines else "google images",
        "format": "json",
        "time_range": "year"
    }

    try:
        app.logger.debug(f"Requesting Searxng with URL: {base_url}?{params}")
        response = requests.get(base_url, params=params,headers=headers)
        response.raise_for_status()
        app.logger.debug(f"Received Searxng Response: {response.text[:500]}...")  # Printing a truncated response for debugging
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error: {e}")
        return None


def format_query_with_openai(user_query, search):
    try:
        prompt = f"""
You will be given a conversation below and a follow up question. You need to rephrase the follow-up question so it is a standalone question that can be used by the LLM to search the web for images.
You need to make sure the rephrased question agrees with the conversation and is relevant to the conversation.

Example:
1. Follow up question: What is a cat?
Rephrased: A cat

2. Follow up question: What is a car? How does it works?
Rephrased: Car working

3. Follow up question: How does an AC work?
Rephrased: AC working


Follow up question: {user_query}
Rephrased question:
`;

"""

        app.logger.debug(f"Sending query to OpenAI for optimization: {user_query}")
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
        app.logger.debug(f"Optimized query received from OpenAI: {optimized_query}")

        # Extract optimized query from response
        parts = optimized_query.split(":")
        result = parts[1].strip().strip('"')
        app.logger.debug(f"Extracted Optimized Query: {result}")
        return result

    except Exception as e:
        app.logger.error(f"Error in query formatting: {e}")
        traceback.print_exc()  # Provides more detailed traceback information
        return user_query


@app.route('/image-search', methods=['POST'])
def image_search():
    data = request.get_json()
    print(request)
    if not data or 'query' not in data:
        return jsonify({"message": "Query is required"}), 400

    query = data['query']
    search = "images"
    
    try:
        app.logger.debug(f"Received image search query: {query}")
        formatted_query = format_query_with_openai(query, search)

        search_results = search_searxng(formatted_query, search, engines=['bing images', 'google images'])

        if not search_results or 'results' not in search_results:
            app.logger.error(f"Error: No results returned from Searxng: {search_results}")
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
        app.logger.debug(f"Top 10 Image Results: {top_images}")

        return jsonify({"images": image_results}), 200

    except Exception as e:
        app.logger.error(f"Error during search: {str(e)}")
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
        app.logger.debug(f"Received video search query: {query}")
        formatted_query = format_query_with_openai(query, search)

        search_results = search_searxng(formatted_query, search, engines=["youtube"])

        if not search_results:
            app.logger.error(f"Error: No results returned from Searxng: {search_results}")
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
        app.logger.error(f"Error fetching results from Searxng: {str(e)}")
        traceback.print_exc()  # Detailed error traceback
        return jsonify({"message": "Error fetching results from Searxng"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=6743)

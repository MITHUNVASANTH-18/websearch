from flask import Flask, request, jsonify
import requests
import openai
from flask_cors import CORS
from dotenv import load_dotenv
import os
import traceback
import logging
import mongoengine
from mongoengine import connect
from routes.prompt_routes import prompt_Bp
from schema.prompt_schema import prompt
import json
db = connect(
    db='prompt',
    host='mongodb+srv://mithunvasanthr:1234@prompt.xjcb6.mongodb.net/prompt?retryWrites=true&w=majority',
    ssl=False
)

print(db)
load_dotenv()
api_key= os.getenv("OPENAI_API_KEY")
openai.api_key = api_key
app = Flask(__name__)

CORS(app)

SEARXNG_URL = "http://searxng:8080/search"

app.logger.setLevel(logging.DEBUG)
app.register_blueprint(prompt_Bp,url_prefix='/app')
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
        "time_range": "year",
         "safe_search": "1"
    }

    try:
        app.logger.debug(f"Requesting Searxng with URL: {base_url}?{params}")
        response = requests.get(base_url, params=params,headers=headers)
        response.raise_for_status()
        app.logger.debug(f"Received Searxng Response: {response.text[:500]}...") 
        return response.json()
    except requests.exceptions.RequestException as e:
        app.logger.error(f"Request error: {e}")
        return None


def format_query_with_openai(user_query ):
    try:
        prompt_id = "67739dbfd14c8c402b258d77" 
        promptdata = prompt.objects(id=prompt_id).first()
        if promptdata:
            promptdata = promptdata.to_json()
            promptdata = json.loads(promptdata)

        api_data = promptdata.json()
        prompt_template = api_data.get("prompt", "")
        if not prompt_template:
            raise ValueError("Prompt not found in API response")

        promptt = f"""
{prompt_template}

Follow up question: {user_query}
Rephrased question:
"""

        app.logger.debug(f"Generated prompt for OpenAI: {promptt}")


        response = openai.chat.completions.create(
            model="gpt-4o-mini", 
            messages=[
                {"role": "system", "content": "You are a query optimization assistant."},
                {"role": "user", "content": promptt},
            ],
            max_tokens=1000,
            temperature=0.7,
        )

        optimized_query = response.choices[0].message.content
        app.logger.debug(f"Optimized query received from OpenAI: {optimized_query}")

        parts = optimized_query.split(":")
        result = parts[1].strip().strip('"') if len(parts) > 1 else optimized_query.strip()
        app.logger.debug(f"Extracted Optimized Query: {result}")

        return result

    except Exception as e:
        app.logger.error(f"Error in query formatting: {e}")
        traceback.print_exc()
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
        formatted_query = format_query_with_openai(query)

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
        # app.logger.debug(f"Top 10 Image Results: {top_images}")

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
        formatted_query = format_query_with_openai(query)

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

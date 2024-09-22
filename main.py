from openai import OpenAI
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
import logging
import requests

load_dotenv()
app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/search')
def search_products():
    try:
        categories = requests.get(f"https://dummyjson.com/products/categories")
        category_data = categories.json()

        search_query = request.args.get('search_query', '')

        tools = [
            {
                "type": "function",
                "function": {
                    "name": "select_related_categories",
                    "description": "Select the most related categories to the search query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "related_categories": {
                                "type": "array",
                                "description": "The most related categories to the search query.",
                                "items": {
                                    "type": "string"
                                }
                            },
                        },
                        "required": ["related_categories"],
                        "additionalProperties": False,
                        },
                    }
                }
            ]

        category_completion = client.chat.completions.create(
            model="gpt-4o-mini",  # or the correct model name
            messages=[
                {"role": "system", "content": "You are an AI that takes a category array and returns ONLY a new array with a maximum of 3 of only categories related or similar to the search query, taking in account that plural words are will be the same as the singular word. (that array needs to be composed only of the category slugs). For example, if the user searches for 'shirts', the categories might be ['shirts', 'tops', 'clothing']. Or if the user searches for 'bananas', the categories might be ['groceries', 'fruits', 'food']."},
                {"role": "user", "content": f"These are the categories: {category_data}. The search query is: {search_query}."}
            ],
            tools=tools,
            tool_choice="required",
        )

        related_categories = json.loads(category_completion.choices[0].message.tool_calls[0].function.arguments)['related_categories']
        print("HERE IS THE RELATED CATEGORIES", related_categories)

        #create a new request for each category in the related_categories array to the dummyjson API to get products from the related categories and store them in a new array
        products_from_related_categories = []
        for category in related_categories:
            response = requests.get(f"https://dummyjson.com/products/category/{category}")
            products = response.json().get('products', [])
            products_from_related_categories.extend(products)

        second_request = [
            {
                "type": "function",
                "function": {
                    "name": "select_related_products",
                    "description": "Select the most related products to the search query.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "products_from_related_categories": {
                                "type": "array",
                                "description": "The most related products to the search query.",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "description": {"type": "string"},
                                        "price": {"type": "number"},
                                        "image": {"type": "string"},
                                        "id": {"type": "number"}
                                    },
                                    "required": ["title", "description", "price", "image", "id"]
                                }
                            },
                        },
                        "required": ["products_from_related_categories"],
                        "additionalProperties": False,
                        },
                    }
                }
            ]

        # Create a new gpt-4o-mini request to filter and return a new array with only 8 products from the products_from_related_categories array that it belives adjusts more to the search query  
        ai_generated_search = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are an AI that limits the results of a search in the dummyjson API to only 8 products that best adjust to the search query. Return ONLY the JSON array, nothing else."""},
                {"role": "user", "content": f"These are the products: {products_from_related_categories}. The search query is: {search_query}."}
            ],
            tools=second_request,
            tool_choice="required",
        )

        ai_response = json.loads(ai_generated_search.choices[0].message.tool_calls[0].function.arguments)['products_from_related_categories']

        return jsonify(ai_response)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
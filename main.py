#app.logger.info(f"Received products: {products}")

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
logging.basicConfig(level=logging.DEBUG)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/api/search')
def search_products():
    try:
        categories = requests.get(f"https://dummyjson.com/products/categories")
        category_data = categories.json()

        search_query = request.args.get('search_query', '')

        category_completion = client.chat.completions.create(
            model="gpt-4o-mini",  # or the correct model name
            messages=[
                {"role": "system", "content": "You are an AI that takes a category array and returns ONLY a new array with a maximum of 3 of only categories related or similar to the search query, taking in account that plural words are will be the same as the singular word. (that array needs to be composed only of the category slugs). For example, if the user searches for 'shirts', the categories might be ['shirts', 'tops', 'clothing', 'men', 'women']. Or if the user searches for 'bananas', the categories might be ['bananas', 'fruit', 'food', 'snacks', 'groceries']. Or if the user searches for 'red dress', the categories might be ['dress', 'clothing', 'women', 'red', 'formal']. Or if the user searches for 'belt' or 'cap' or 'hat' the categories might be ['belt', 'cap', 'hat', 'clothing', 'men', 'women', 'accessories']. Or if the user searches for 'phone' the categories might be ['phones', 'electronics', 'mobile', 'device', 'technology']. Or if the user searches for 'jeans' or 'pants' or 'trousers' the categories might be ['jeans', 'pants', 'trousers', 'clothing', 'men', 'women']. Or if the user searches for 'dress' the categories might be ['dress', 'clothing', 'women', 'formal', 'red', 'blue', 'yellow', 'green']. Or if the user searches for 'blue dress' the categories might be ['dress', 'clothing', 'women', 'formal', 'blue', 'red', 'yellow', 'green']."},
                {"role": "user", "content": f"These are the categories: {category_data}. The search query is: {search_query}."}
            ]
        )

        related_categories = category_completion.choices[0].message.content
        # Convert string representation of list to actual list
        related_categories = json.loads(related_categories.replace("'", '"'))
        print("HERE IS THE RELATED CATEGORIES", related_categories)

        #create a new request for each category in the related_categories array to the dummyjson API to get products from the related categories and store them in a new array
        products_from_related_categories = []
        for category in related_categories:
            response = requests.get(f"https://dummyjson.com/products/category/{category}")
            products = response.json().get('products', [])
            products_from_related_categories.extend(products)

        # Create a new gpt-4o-mini request to filter and return a new array with only 8 products from the products_from_related_categories array that it belives adjusts more to the search query  
        ai_generated_search = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": """You are an AI that limits the results of a search in the dummyjson API to only 8 products that best adjust to the search query. You need to return an array of objects and each object needs to have the following properties: title, description, price, image, id. Return ONLY the JSON array, nothing else."""},
                {"role": "user", "content": f"These are the products: {products_from_related_categories}. The search query is: {search_query}."}
            ]
        )

        ai_response = ai_generated_search.choices[0].message.content.strip()
        print("Raw AI response:", ai_response)

        try:
            ai_retrieved_products = json.loads(ai_response)
        except json.JSONDecodeError:
            # If JSON parsing fails, attempt to extract JSON-like content
            import re
            json_match = re.search(r'\[.*\]', ai_response, re.DOTALL)
            if json_match:
                try:
                    ai_retrieved_products = json.loads(json_match.group())
                except json.JSONDecodeError:
                    return jsonify({"error": "Failed to parse AI response"}), 500
            else:
                return jsonify({"error": "Invalid AI response format"}), 500

        print("HERE IS THE AI RETRIEVED PRODUCTS", ai_retrieved_products)

        return jsonify(ai_retrieved_products)

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)

#print(completion.choices[0].message.content)
import uuid
import firebase_admin.firestore
from flask import Flask, json, jsonify, request
import requests
from supabase import create_client, Client
import firebase_admin
from firebase_admin import credentials,firestore
from firebase_admin import auth



app = Flask(__name__)

# Supabase configuration (use your own Supabase URL and anon key)
SUPABASE_URL = "https://gmwccngadkywajqwdnbh.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imdtd2NjbmdhZGt5d2FqcXdkbmJoIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzUyNjQ0MTIsImV4cCI6MjA1MDg0MDQxMn0.Vggr3kTqXGOrMFMSEfietO0vj-1bJKvbllojfxSq9Rk"
# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



cred = credentials.Certificate('firebase-sdk.json')
 
firebase_admin.initialize_app(cred)
db = firebase_admin.firestore.client()

# @app.route('/send_otp',methods=['POST'])
# def send_otp():
#     """
#     Sends a verification code (OTP) to the given phone number.
#     """
#     data = request.get_data(as_text=True)
#     parsed_data = json.loads(data)
#     phone_number = parsed_data.get('phone_number')
#     try:
#         # Send verification code
#         verification = auth.generate_sign_in_with_email_link()
#         return verification
#     except Exception as e:
#         return False
# def verify_otp():
#     """
#     Verifies the OTP entered by the user.
#     """
#     data = request.get_data(as_text=True)
#     parsed_data = json.loads(data)
#     otp_code = parsed_data.get('otp_code')
#     phone_number = parsed_data.get('phone_number')
#     try:
#         # Verify the OTP
#         verification_check = auth.verify_id_token(otp_code)
#         if verification_check['phone_number'] == phone_number:
#             # User can be logged in here
#             return True
#         else:
#             return False
#     except Exception as e:
#         return False


@app.route('/update_users',methods=['POST'])
def update_users():
    try:
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        uid = parsed_data.get('uid')
        email = parsed_data.get('email')
        display_name2 = parsed_data.get('display_name')
        phone_number2 = str(parsed_data.get('phone_number'))
        custom_details = {
            "address":parsed_data.get('address'),
            "pincode":parsed_data.get('pincode')
        }    
        user = auth.update_user(
            uid= uid,
            email=email, 
            display_name=display_name2,
            phone_number=phone_number2, 
        )

        auth.set_custom_user_claims(user.uid, custom_details)
        user = auth.get_user_by_email(email)
        user_details = {
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "phone_number": user.phone_number,
            "custom_claims": user.custom_claims
        }
        customers_ref = db.collection('customers')
        customers_ref.document(user.email).set({
            "uid": user.uid,
            "email": user.email,
            "display_name": user.display_name,
            "phone_number": user.phone_number,
            "custom_details": user.custom_claims
        }, merge=True)
        return jsonify({"message": "User updated successfully", "user_details": user_details}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/createUser', methods=['POST'])
def createUser():
    try:
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        password = parsed_data.get('password')
        display_name2 = parsed_data.get('display_name')
        phone_number2 = "+91" + str(parsed_data.get('phone_number'))
        custom_details = {
            "address":parsed_data.get('address')
        }    
        user = auth.create_user(
            email=email, 
            password=password,
            display_name=display_name2,
            phone_number=phone_number2, 
        )

        auth.set_custom_user_claims(user.uid, custom_details)
        
        user_details = {
            "uid": user.uid,
            "email": user.email,
            "display_name": display_name2,
            "phone_number": phone_number2,
            "custom_details": custom_details
        }

        customers_ref = db.collection('customers')
        customers_ref.document(user.email).set(user_details)
        
        
        return jsonify({"message": "User created successfully", "user_details": user_details}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500





app = Flask(__name__)

@app.route('/get_product_by_id', methods=['POST'])
def get_product_by_id():
    try:
        # Parse and validate the incoming request
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)  # Use get_json for JSON input
        product_id = parsed_data.get('product_id')
        # Validate if product_id is a valid UUID
        if not product_id or not is_valid_uuid(product_id):
            return jsonify({"error": "Invalid or missing product_id"}), 400

        # Query the database
        response = supabase.table('products').select().eq('id', product_id).execute()

        if response.data:  # Ensure response has data
            return jsonify(response.data), 200
        else:
            return jsonify({"error": "Product not found"}), 404

    except Exception as e:
        # Handle unexpected errors
        return jsonify({"error": str(e)}), 500

def is_valid_uuid(value):
    """Validate if the given value is a proper UUID."""
    try:
        uuid.UUID(value)
        return True
    except (ValueError, TypeError):
        return False




@app.route('/search_query_product_name',methods=['POST'])
def search_query_product_name():
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    query = str(parsed_data.get('query'))
    response = supabase.table('products').select('name','id').ilike('name', f'%{query}%').order('priority_score', desc=True).order('priority', desc=True).execute()
    if response:
        details = response.data
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500


@app.route('/search_query',methods=['POST'])
def search_query():
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    query = str(parsed_data.get('query'))
    response2 = supabase.table('products').select('category_name').ilike('category_name', f'%{query}%').execute()
    response3 = supabase.rpc("search_tags",{"search_query": query}).execute()
    unique_categories = {}
    for product in response3.data:
        category = product.get('category_name')
        if category in unique_categories:
            unique_categories[category].append(product)
        else:
            unique_categories.setdefault(category, []).append(product)
    unique_categories2={}
    for product in response2.data:
        category = product.get('category_name')
        if category in unique_categories2:
            unique_categories2[category].append(product)
        else:
            unique_categories2.setdefault(category, []).append(product)
    if  response2 or response3:
        details = list(unique_categories2) + list(unique_categories)
        return jsonify(details),200
    else:
        return jsonify({"error":"No matching results"}),500

@app.route('/get_users', methods=['GET'])
def get_users():
    # Fetch users from Supabase database
    response = supabase.table('users').select().eq('role','seller').execute()

    if response:
        users = response.data
        return jsonify(users),200
    else:
        return jsonify({"error": "Failed to fetch users"}), 500


@app.route('/get_shopDetails',methods=['POST'])
def get_shopDetails():
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    shopname = parsed_data.get('shopname')
    response = supabase.table('users').select().eq('email',shopname).execute()
    if response:
        details = response.data
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500




@app.route('/get_RecommendedProducts',methods=['GET'])
def get_RecommendedProducts():
    response = supabase.table('products').select().order('priority_score', desc=True).order('priority', desc=True).execute()
    if response:
        details = response.data
        return jsonify(details[:30]),200
    else:
        return jsonify({"error":"an error occurred"}),500


@app.route('/get_CategoryProducts',methods=['POST'])
def get_CategoryProducts():
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    mainCategory = str(parsed_data.get('category'))
    response = supabase.table('products').select().eq('category_name', mainCategory).order('priority_score', desc=True).order('priority', desc=True).execute()
    if response:
        details = response.data
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500

@app.route('/get_HighestPriorityProducts', methods=['GET'])
def get_HighestPriorityProducts():
    response = supabase.table('products').select().order('created_at', desc=True).order('priority_score', desc=True).order('priority', desc=True).limit(5).execute()
    if response:
        details = response.data
        return jsonify(details), 200
    else:
        return jsonify({"error": "an error occurred"}), 500







@app.route('/get_shopProductsDetails',methods=['POST'])
def get_shopproductDetails():
    data = request.get_data(as_text=True)  # Get raw JSON string
    parsed_data = json.loads(data)
    seller = parsed_data.get('seller')
    response = supabase.table('products').select().eq('seller', seller).execute()
    if response:
        details = response.data
        categorized_products = {
            "Men": [],
            "Women": [],
            "Children": []
        }
        # Group products by mainCategory
        for product in details:
            category = product.get('mainCategory')
            if category in categorized_products:
                categorized_products[category].append(product)
            else:
                categorized_products.setdefault(category, []).append(product)

        # Sort products by priority score in descending order
        for category in categorized_products:
            categorized_products[category] = sorted(categorized_products[category], key=lambda x: x['priority_score'], reverse=True)

        # Convert to JSON
        grouped_json = json.dumps(categorized_products)
        return grouped_json, 200
    else:
        return jsonify({"error": "an error occurred"}), 500




@app.route('/get_fewCategories',methods=['GET'])
def get_fewCategories():
    response = supabase.table('categories').select('name','thumbnail').order('name', desc=False).limit(10).execute()
    if response:
        details = response.data
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500







@app.route('/get_mainCategories', methods=['GET'])
def get_mainCategories():
    """
    Fetches all unique "main" categories with their corresponding thumbnails.

    Returns a JSON list of dictionaries, each containing a "main" category and its thumbnail.

    Example response:
    [
        {
            "main": "Men",
            "thumbnail": "https://example.com/men.jpg"
        },
        {
            "main": "Women",
            "thumbnail": "https://example.com/women.jpg"
        },
        {
            "main": "Children",
            "thumbnail": "https://example.com/children.jpg"
        }
    ]
    """
    response = supabase.table('categories').select('main', 'thumbnail').execute()
    
    if response.data:
        list_main = response.data
        
        # Create a dictionary to store unique "main" categories with their corresponding thumbnails
        unique_categories = {}
        for entry in list_main:
            # If the "main" category is not in the dictionary, add it
            if entry["main"] not in unique_categories:
                unique_categories[entry["main"]] = entry["thumbnail"]
        
        # Convert the dictionary to a list of dictionaries
        unique_categories_list = [{"main": main, "thumbnail": thumbnail} for main, thumbnail in unique_categories.items()]
        
        return jsonify(unique_categories_list), 200
    else:
        return jsonify({"error": "unable to fetch categories"}), 500
                                                                 

@app.route('/get_allcategories',methods=['GET'])
def get_categories():
    response = supabase.table('categories').select().execute()
    if response:
        categoriesData = response.data
        return jsonify(categoriesData)
    else:
        return jsonify({"error":"an error occured to fetch categories"}), 500

@app.route('/add_user', methods=['POST'])
def add_user():
    try:
        # Decode JSON data from the request
        data = request.get_data(as_text=True)  # Get raw JSON string
        parsed_data = json.loads(data)  # Decode JSON to Python dictionary

        # Extract attributes from parsed JSON
        display_name = parsed_data.get('displayname')
        uid = parsed_data.get('uid')
        email = parsed_data.get('email')
        phone = parsed_data.get('phone')
        address = parsed_data.get('address')
        role = parsed_data.get('role')

        # Validate input
        if not display_name and uid and email and phone and address and role:
            return jsonify({"error": "all fields are required"}), 400

        # Insert the data into the Supabase `users` table
        response = supabase.table('users').insert({
            "displayname":display_name,
            "email":email,
            "phone":phone,
            "address":address,
            "role": role
        }).execute()

        if response:
            return jsonify({"message": "User added successfully", "data": response.data}), 201
        else:
            return jsonify({"error": "Failed to insert user", "details": response}), 500
    except Exception as e:
        return jsonify({"error": "An error occurred", "details": str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000,debug=True)

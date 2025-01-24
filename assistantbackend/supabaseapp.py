import uuid
import firebase_admin.firestore
from flask import Flask, json, jsonify, request
from supabase import create_client, Client
import firebase_admin
from firebase_admin import credentials,firestore
from firebase_admin import auth



app = Flask(__name__)

# Supabase configuration (use your own Supabase URL and anon key)
SUPABASE_URL = "URL"
SUPABASE_KEY = "KEY"
# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)



cred = credentials.Certificate('firebase-sdk.json')
 
firebase_admin.initialize_app(cred)
db = firebase_admin.firestore.client()

@app.route('/update_users',methods=['POST'])
def update_users():
    """
    Updates a user and adds custom claims to the user. 
    
    Custom claims are stored in the Firebase Realtime Database under the user's email
    as a document with the key "custom_details". The custom claims are also stored
    in the user's custom_claims property in the Firebase Authentication API.
    
    The custom claims are expected to be a JSON object with the following structure:
    
    {
        "address": "string",
        "pincode": "string"
    }
    
    :param uid: The user ID to update
    :param email: The email address to use for the user
    :param display_name: The display name to use for the user
    :param phone_number: The phone number to use for the user
    :return: A JSON object with the user's details and a success message
    """

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



@app.route('/add_to_cart',methods=['POST'])
def add_to_cart():
    """
    Endpoint to add a product to a user's wishlist.

    POST request containing the user's email and product id in the request body.

    Returns a JSON response containing the updated wishlist for the user.
    """
    try:
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        product_id = parsed_data.get('product_id')
        customers_ref = db.collection('wishlists')
        user_ref = customers_ref.document(email)
        
        # Use set with merge=True to ensure the document is created if it doesn't exist
        user_ref.set({
            'products': firestore.ArrayUnion([product_id])
        }, merge=True)
        
        response = db.collection('wishlists').document(email).get()
        if response.exists:
            details = response.to_dict()
            return jsonify(details),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        


@app.route('/remove_from_cart',methods=['POST'])
def remove_from_cart():
    """
    Endpoint to remove a product from a user's cart.

    POST request containing the user's email and product id in the request body.

    Returns a JSON response containing the updated cart for the user.
    """

    try:
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        product_id = parsed_data.get('product_id')
        customers_ref = db.collection('carts')
        user_ref = customers_ref.document(email)
        
        # Use set with merge=True to ensure the document is created if it doesn't exist
        user_ref.set({
            'products': firestore.ArrayRemove([product_id])
        }, merge=True)
        response = db.collection('wishlists').document(email).get()
        if response.exists:
            details = response.to_dict()
            return jsonify(details),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/get_wishlist',methods=['POST'])
def get_wishlist():
    """
    Endpoint to get the wishlist for a given user.

    POST request containing the user's email in the request body.

    Returns a JSON response containing the wishlist for the user.
    """
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    email = parsed_data.get('email')
    response = db.collection('wishlists').document(email).get()
    if response.exists:
        details = response.to_dict()
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500






@app.route('/remove_from_wishlist',methods=['POST'])
def remove_from_wishlist():
    
    """
    Endpoint to remove a product from a user's wishlist.

    POST request containing the user's email and product id in the request body.

    Returns a JSON response containing the updated wishlist for the user.
    """

    try:
        # Get and parse the request data
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        product_id = parsed_data.get('product_id')
        
        # Reference to the 'wishlists' collection and the document for the user
        customers_ref = db.collection('wishlists')
        user_ref = customers_ref.document(email)
        
        # Use set with merge=True to ensure the document is created if it doesn't exist
        user_ref.set({
            'products': firestore.ArrayRemove([product_id])
        }, merge=True)
        response = db.collection('wishlists').document(email).get()
        if response.exists:
            details = response.to_dict()
            return jsonify(details),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/add_to_wishlist',methods=['POST'])
def add_to_wishlist():
    
    """
    Endpoint to add a product to a user's wishlist.

    POST request containing the user's email and product id in the request body.

    Returns a JSON response containing the updated wishlist for the user.
    """
    try:
        # Get and parse the request data
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        product_id = parsed_data.get('product_id')
        
        # Reference to the 'wishlists' collection and the document for the user
        customers_ref = db.collection('wishlists')
        user_ref = customers_ref.document(email)
        
        # Use set with merge=True to ensure the document is created if it doesn't exist
        user_ref.set({
            'products': firestore.ArrayUnion([product_id])
        }, merge=True)
        
        response = db.collection('wishlists').document(email).get()
        if response.exists:
            details = response.to_dict()
            return jsonify(details),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/add_to_cartlist',methods=['POST'])
def add_to_cartlist():
    """
    Endpoint to add a product to a user's cart list.

    POST request containing the user's email and product id in the request body.

    Returns a JSON response containing the updated cart list for the user.
    """
    try:
        # Get and parse the request data
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        product_id = parsed_data.get('product_id')
        
        # Reference to the 'wishlists' collection and the document for the user
        customers_ref = db.collection('cartlists')
        user_ref = customers_ref.document(email)
        
        # Use set with merge=True to ensure the document is created if it doesn't exist
        user_ref.set({
            'products': firestore.ArrayUnion([product_id])
        }, merge=True)
        
        response = db.collection('cartlists').document(email).get()
        if response.exists:
            details = response.to_dict()
            return jsonify(details),200
    except Exception as e:
        return jsonify({"error": str(e)}), 500




@app.route('/get_cartlist',methods = ['POST'])
def get_cartlist():
    """
    Endpoint to get the cart list for a given user.

    POST request containing the user's email in the request body.

    Returns a JSON response containing the cart list for the user.
    """
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    email = parsed_data.get('email')
    response = db.collection('cartlists').document(email).get()
    if response.exists:
        details = response.to_dict()
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500




@app.route('/remove_from_cartlist',methods = ['POST'])
def remove_from_cartlist():
    """
    Endpoint to remove a product from a user's cartlist.

    POST request containing the user's email and product id in the request body.

    Returns a JSON response containing the updated cartlist for the user.
    """
    try:
        # Get and parse the request data
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        product_id = parsed_data.get('product_id')

        # Reference to the 'wishlists' collection and the document for the user
        customers_ref = db.collection('cartlists')
        user_ref = customers_ref.document(email)

        # Use set with merge=True to ensure the document is created if it doesn't exist
        user_ref.set({
            'products': firestore.ArrayRemove([product_id])
        }, merge=True)
        response = db.collection('cartlists').document(email).get()
        if response.exists:
            details = response.to_dict()
            return jsonify(details),200
    except Exception as e:
        print(e) 
        return jsonify({"error": str(e)}), 500
    







@app.route('/register', methods=['POST'])
def createUser():
    """
    Creates a new user and adds custom claims to the user. 
    
    Custom claims are stored in the Firebase Realtime Database under the user's email
    as a document with the key "custom_details". The custom claims are also stored
    in the user's custom_claims property in the Firebase Authentication API.
    
    The custom claims are expected to be a JSON object with the following structure:
    
    {
        "address": "string",
    }
    
    :param email: The email address to use for the new user
    :param password: The password to use for the new user
    :param display_name: The display name to use for the new user
    :param phone_number: The phone number to use for the new user
    :param custom_details: A JSON object with custom claims to store in the user's document
    :return: A JSON object with the user's details and a success message
    """
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
            "password":password,
            "display_name": display_name2,
            "phone_number": phone_number2,
            "custom_details": custom_details
        }

        customers_ref = db.collection('customers')
        customers_ref.document(user.email).set(user_details)
        
        
        return jsonify({"message": "User created successfully", "user_details": user_details}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/login_with_email_password', methods=['POST'])
def login():
    """
    Logs in a user with the given email and password.

    The user is expected to be registered in the Firebase Realtime Database
    under the key "customers". The user's password is expected to be stored
    in the "password" field of their document.

    :param email: The email address of the user to log in
    :param password: The password of the user to log in
    :return: A JSON object with the user's details and a success message if the
             login is successful, otherwise a JSON object with an error message
             and a 401 status code
    """
    try:
        data = request.get_data(as_text=True)
        parsed_data = json.loads(data)
        email = parsed_data.get('email')
        password = parsed_data.get('password')
        user = db.collection('customers').document(email).get().to_dict()
        if user["password"]==password:
            customer_ref = db.collection('customers').document(email)
            customer_details = customer_ref.get().to_dict()
            return jsonify({"message": "Login successful", "user_details": customer_details}), 200
        else:
            return jsonify({"error": "Invalid email or password"}), 401
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/get_product_by_id', methods=['POST'])
def get_product_by_id():
    """
    Endpoint to get a product by its id.

    POST request containing the product id in the request body.

    Returns a JSON response containing the product details if the product is found, else a 404 error.

    :param product_id: The id of the product to get
    :return: A JSON object with the product details and a success message
    """
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
            print(response.data)
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
    """
    Endpoint to search products by name.

    POST request containing the search query in the request body.

    Returns a JSON response containing a list of product names and ids that match the search query.
    """

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
    """
    Endpoint to search products by category name or tags.
    Returns a list of unique category names if the search query matches any category name or tags.
    :param query: The search query
    :return: A list of unique category names, or an error message if no matching results are found
    """
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
    """
    Endpoint to get all the users from the Supabase database.

    GET request.

    Returns a JSON response containing all the users, filtered by role = 'seller'.
    """
    
    response = supabase.table('users').select().eq('role','seller').execute()

    if response:
        users = response.data
        return jsonify(users),200
    else:
        return jsonify({"error": "Failed to fetch users"}), 500


@app.route('/get_shopDetails',methods=['POST'])
def get_shopDetails():
    """
    Endpoint to get the details of a shop.

    POST request containing the shop name in the request body.

    Returns a JSON response containing the details of the shop.
    """
    
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
    """
    Endpoint to get recommended products based on priority score.

    This endpoint performs a GET request to fetch products from the database, 
    ordered by their priority score and general priority in descending order.
    It returns the top 30 products as a JSON response.

    Returns:
    -------
    JSON response : 
        A list of up to 30 product objects sorted by priority score and priority.

    Raises:
    ------
    500 : 
        An error occurred during the retrieval process.
    """

    response = supabase.table('products').select().order('priority_score', desc=True).order('priority', desc=True).execute()
    if response:
        details = response.data
        return jsonify(details[:30]),200
    else:
        return jsonify({"error":"an error occurred"}),500


@app.route('/get_CategoryProducts',methods=['POST'])
def get_CategoryProducts():
    """
    Endpoint to get the products of a specific category.

    POST request containing the category name in the request body.

    Returns a JSON response containing the products of the category.
    """
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
    """
    This endpoint returns the 5 products with the highest priority score 
    which were created most recently. The response is a JSON array of objects 
    containing the product information.

    Returns:
    -------
    JSON array of objects : 
        contains the product information

    Raises:
    ------
    500 : internal error
    """
    response = supabase.table('products').select().order('created_at', desc=True).order('priority_score', desc=True).order('priority', desc=True).limit(5).execute()
    if response:
        details = response.data
        return jsonify(details), 200
    else:
        return jsonify({"error": "an error occurred"}), 500







@app.route('/get_shopProductsDetails',methods=['POST'])
def get_shopproductDetails():
    """
    Gets products for a given seller, grouped by main category, sorted by priority score in descending order.

    Returns a JSON object with the following structure:
    {
        "Men": [
            {
                "id": 1,
                "product_name": "",
                "price": 0,
                "priority_score": 0,
                ...
            },
            {
                "id": 2,
                "product_name": "",
                "price": 0,
                "priority_score": 0,
                ...
            },
            ...
        ],
        "Women": [
            ...
        ],
        "Children": [
            ...
        ]
    }
    """
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
    """
    Get a few categories from the database.

    This endpoint returns a JSON list of up to 10 category objects. Each category object includes
    the category name and thumbnail, ordered alphabetically by name.

    Returns:
        JSON response: A list of dictionaries, each containing the category name and thumbnail.
        If successful, returns a 200 status code.
        If an error occurs, returns a JSON object with an error message and a 500 status code.
    """

    response = supabase.table('categories').select('name','thumbnail').order('name', desc=False).limit(10).execute()
    if response:
        details = response.data
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500



@app.route('/get_reviews',methods=['POST'])
def get_reviews():
    """
    Endpoint to get the reviews for a given product.

    POST request containing the product id in the request body.

    Returns a JSON response containing the reviews for the product.
    """
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    product_id = parsed_data.get('product_id')
    response = supabase.table('reviews').select('comment','image_urls','rating','reviewername').eq('product_id', product_id).order('reviewtime', desc=False).execute()
    if response:
        details = response.data
        print(details)
        return jsonify(details),200
    else:
        return jsonify({"error":"an error occurred"}),500


@app.route('/add_review_to_product',methods=['POST'])
def add_review():
    """
    Endpoint to add a review to a product.

    POST request containing the product id, reviewer name, comment, rating, and image urls in the request body.

    Returns a JSON response containing the updated reviews for the product.
    """
    
    data = request.get_data(as_text=True)
    parsed_data = json.loads(data)
    product_id = parsed_data.get('product_id')
    reviewername = parsed_data.get('reviewername')
    comment = parsed_data.get('comment')
    rating = parsed_data.get('rating')
    image_urls =[]
    print(type(image_urls))
    if(len(image_urls)==0):
        image_urls = []
    response = supabase.table('reviews').insert({
        'product_id': product_id, 
        'comment': comment,
        'image_urls':image_urls,
        'rating': rating,
        'reviewername': reviewername        
        }).execute()
    if response:
        response2 = supabase.table('reviews').select('comment','image_urls','rating','reviewername').eq('product_id', product_id).order('reviewtime', desc=False).execute()
        if response2:
            details = response2.data
            return jsonify(details),200
        else:
            return jsonify({"error":"an error occurred"}),500
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
    """Get all categories in the database.

    Returns a JSON list of dictionaries, each containing category information (name, thumbnail, description, etc.).
    """
    response = supabase.table('categories').select().execute()
    if response:
        categoriesData = response.data
        return jsonify(categoriesData)
    else:
        return jsonify({"error":"an error occured to fetch categories"}), 500

@app.route('/add_user', methods=['POST'])
def add_user():
    """
    Endpoint to add a new user to the Supabase `users` table.
    
    Expected POST request body:
    {
        "displayname": string,
        "uid": string,
        "email": string,
        "phone": string,
        "address": string,
        "role": string
    }
    
    Returns a JSON response containing a success message and the newly added user.
    """

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

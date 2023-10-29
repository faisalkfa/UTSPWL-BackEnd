from pyramid.view import view_config
from pyramid.httpexceptions import HTTPBadRequest
from pyramid.response import Response
from pyramid.request import Request
from pyramid.security import remember, forget, Authenticated
import jwt
import io
import logging
import json
from datetime import datetime
from .models import DBSession, Product, User, Transaction, TransactionDetail, ShoppingCart, ShoppingCartItem

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

def includeme(config):
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')

    config.add_route('login', '/login')
    config.add_route('keep_login', '/keep_login')
    config.add_route('register', '/register')
    config.add_route('logout', '/logout')

    config.add_route('products', '/products')
    config.add_route('add_product', '/product/insert')
    config.add_route('get_detail_product', '/product')
    config.add_route('update_product', '/product/update/{id}')
    config.add_route('delete_product', '/product/delete/{id}')

    config.add_route('view_cart', '/cart')
    config.add_route('add_to_cart', '/cart/insert')
    config.add_route('update_cart_item', '/cart/update/{id}')
    config.add_route('remove_from_cart', '/cart/delete/{id}')
    config.add_route('get_cart_total', '/cart/total')

    config.add_route('user_transactions', '/transactions')
    config.add_route('create_transaction', '/transactions')

class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super().default(o)

def get_jwt_token(request: Request):
    authorization_header = request.headers.get('Authorization', '')
    parts = authorization_header.split()
    token = ''
    if len(parts) == 2 and parts[0] == 'Bearer':
        token = parts[1]
    return token

def decode_user(token: str):
    secret_key = "shjoi1o3r901fjIJOd21390f092ejvqqD9017Fj03Jdj09j1fSBNKNDF11q21ejq"
    decoded_data = jwt.decode(jwt=token,
                              key=secret_key,
                              algorithms=["HS256"])
    logging.info(decoded_data)
    return decoded_data


@view_config(route_name='register', request_method='POST', renderer='json')
def register(request):
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Response(json={'message': 'Username and password are required'})

    session = DBSession()
    existing_user = session.query(User).filter(User.username == username).first()

    if existing_user:
        return Response(json={'message': 'Username already in use'})

    new_user = User(username=username, password=password)
    session.add(new_user)
    session.commit()
    session.flush()
    session.close()
    headers = remember(request, username)
    return Response(json={'message': 'Registration successful'}, headers=headers)


@view_config(route_name='login', request_method='POST', renderer='json')
def login(request):
    try:
        data = request.json
        username = data['username']
        password = data['password']

        session = DBSession()
        user = session.query(User).filter(User.username == username).first()

        if user and user.password == password:
            token = request.create_jwt_token(user.id, username=user.username, id=user.id)
            headers = remember(request, userid=user.id)
            session.flush()
            session.close()
            return Response(json={'message': 'Login successful', 'id':user.id, 'username':user.username, 'token': token}, headers=headers)
        else:
            session.flush()
            session.close()
            return Response(json={'message': 'Invalid username or password'}, status=401)
    except Exception as e:
        session.rollback()
        return Response(json={'message': 'Error while authenticating'}, status=500)

@view_config(route_name='keep_login', renderer='json')
def keep_login(request):
    try:
        # Check if the user's token is still valid
        user = get_jwt_token(request)

        if user is not None:
            # User is authenticated, return user information if needed
            user_data = decode_user(user)  # Decode the token to get user data

            return Response(json={'message': 'User is authenticated', 'id': user_data['id'], 'username':user_data['username']}, status=200)
        else:
            return Response(json={'message': 'User is not authenticated'}, status=401)
    except Exception as e:
        return Response(json={'message': 'An error occurred while keeping the user logged in.'}, status=500)


@view_config(route_name='logout', renderer='json')
def logout(request):
    headers = forget(request)
    return Response(json={'message': 'Logout successful'}, headers=headers)


@view_config(route_name='products', renderer='json')
def get_products(request):
    session = DBSession()
    products = session.query(Product).all()
    session.flush()
    session.close()
    return [product.to_dict() for product in products]

@view_config(route_name='get_detail_product', request_method='POST', renderer='json')
def get_detail_product(request):
    session = DBSession()
    product_id = request.json.get('product_id')
    product = session.query(Product).filter(Product.id == product_id).first()
    if product:
        return Response(json={
            'product': product.to_dict()
        }, status=200) 
    else:
        return Response(json={'message': 'Product not found'}, status=404)

@view_config(route_name='add_product', request_method='POST', renderer='json')
def add_product(request):
    try:
        user = get_jwt_token(request)

        if user is None:
            return Response(json={'message': 'User is not authenticated'})
        data = dict(request.POST)
        image = data['image']
        if image is not None:
            image_data = image.file.read()
        else:
            image_data = None

        product = Product(
            name=data['name'],
            description=data['description'],
            price=data['price'],
            stock=data['stock'],
            image=image_data
        )
        logging.info(product)
        session = DBSession()
        session.add(product)
        session.commit()
        return Response(json={
            'message': 'Product inserted successfully',
            'product': product.to_dict()
        }, status=200)
    except Exception as e:
        logging.info(e)
        return Response(json={'message': 'An error occurred while adding the product.'}, status=502)


@view_config(route_name='update_product', request_method='POST', renderer='json')
def update_product(request):
    product_id = int(request.matchdict['id'])

    data = request.json

    session = DBSession()
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        if 'name' in data:
            product.name = data['name']
        if 'price' in data:
            product.price = data['price']
        if 'stock' in data:
            product.stock = data['stock']

        session.commit()
        session.flush()
        session.close()
        return Response(json={'message': 'Product updated successfully'}, status=200)
    else:
        session.rollback()
        return Response(json={'message': 'Product not found'}, status=404)

@view_config(route_name='delete_product', request_method='POST', renderer='json')
def delete_product(request):
    product_id = int(request.matchdict['id'])

    session = DBSession()
    product = session.query(Product).filter(Product.id == product_id).first()

    if product:
        session.delete(product)
        session.commit()
        session.flush()
        session.close()
        return Response(json={'message': 'Product deleted successfully'})
    else:
        session.flush()
        session.close()
        return Response(json={'message': 'Product not found'}, status=404)


@view_config(route_name='add_to_cart', request_method='POST', renderer='json')
def add_to_cart(request):
    data = request.json
    logging.info(data)
    product_id = data.get('product_id')
    quantity = data.get('quantity')
    logging.info(quantity)

    session = DBSession()
    product = session.query(Product).get(product_id)

    if product:
        logging.info('sini')
        user = get_jwt_token(request)
        logging.info(user)

        if user is None:
            return Response(json={'message': 'User is not authenticated'})

        user = decode_user(user)
        user = session.query(User).get(user['id'])
        if not user.shopping_cart:
            cart = ShoppingCart(user_id=user.id)
            session.add(cart)
            session.flush()
        else:
            cart = user.shopping_cart

        existing_item = session.query(ShoppingCartItem).filter_by(cart_id=cart.id, product_id=product.id).first()
        if existing_item:
            existing_item.quantity += quantity
        else:
            item = ShoppingCartItem(cart_id=cart.id, product_id=product.id, quantity=quantity)
            session.add(item)

        session.commit()
        session.close()
        return Response(json={'message': 'Product added to the cart'}, status=200)
    else:
        return Response(json={'message': 'Invalid Product'}, status=502)
    
@view_config(route_name='view_cart', renderer='json')
def view_cart(request):
    user = get_jwt_token(request)

    if user is None:
        return Response(json={'message': 'User is not authenticated'})

    user = decode_user(user)

    session = DBSession()
    user = session.query(User).get(user['id'])
    if not user.shopping_cart:
        return Response(json={'message': 'Shopping cart is empty'})

    cart = user.shopping_cart

    # Join the ShoppingCartItem and Product tables to get product details
    cart_items = session.query(ShoppingCartItem, Product). \
        filter(ShoppingCartItem.cart_id == cart.id, ShoppingCartItem.product_id == Product.id).all()

    # Create a list of dictionaries with detailed cart item information
    cart_data = [{'cart_id': item.ShoppingCartItem.id,
                  'quantity': item.ShoppingCartItem.quantity,
                  'product': item.Product.to_dict(),  # Include additional product details
                  } for item in cart_items]
    session.flush()
    session.close()
    return Response(json={'cart_items': cart_data})

@view_config(route_name='update_cart_item', request_method='POST', renderer='json')
def update_cart_item(request):
    user = get_jwt_token(request)

    if user is None:
        return Response(json={'message': 'User is not authenticated'})

    user = decode_user(user)

    cart_item_id = int(request.matchdict['id'])
    data = request.json
    quantity = data.get('quantity')

    session = DBSession()
    cart_item = session.query(ShoppingCartItem).get(cart_item_id)

    if cart_item:
        cart_item.quantity = quantity
        session.commit()
        session.close()
        return Response(json={'message': 'Cart item updated'})
    else:
        return Response(json={'message': 'Cart item not found'})
    
@view_config(route_name='get_cart_total', request_method="POST", renderer='json')
def get_cart_total(request):
    user = get_jwt_token(request)

    if user is None:
        return Response(json={'message': 'User is not authenticated'})

    user = decode_user(user)

    session = DBSession()
    user = session.query(User).get(user['id'])

    if not user.shopping_cart:
        return Response(json={'message': 'Shopping cart is empty'})

    cart = user.shopping_cart
    cart_items = session.query(ShoppingCartItem).filter_by(cart_id=cart.id).all()

    total_price = 0  # Initialize total price

    for item in cart_items:
        # Retrieve product details for the item and calculate the subtotal
        product = session.query(Product).get(item.product_id)
        if product:
            subtotal = item.quantity * product.price
            total_price += subtotal
    session.flush()
    session.close()
    return Response(json={'total_price': total_price})

    
@view_config(route_name='remove_from_cart', request_method='POST', renderer='json')
def remove_from_cart(request):
    user = get_jwt_token(request)

    if user is None:
        return Response(json={'message': 'User is not authenticated'})

    user = decode_user(user)

    cart_item_id = int(request.matchdict['id'])

    session = DBSession()
    cart_item = session.query(ShoppingCartItem).get(cart_item_id)

    if cart_item:
        session.delete(cart_item)
        session.commit()
        session.close()
        return Response(json={'message': 'Cart item removed'}, status=200)
    else:
        session.rollback()
        return Response(json={'message': 'Cart item not found'}, status=404)

@view_config(route_name='create_transaction', request_method='POST', renderer='json')
def create_transaction(request):
    user = get_jwt_token(request)

    if user is None:
        return Response(json={'message': 'User is not authenticated'}, status=403)

    user = decode_user(user)

    session = DBSession()
    user = session.query(User).get(user['id'])

    if not user.shopping_cart:
        return Response(json={'message': 'Shopping cart is empty'}, status=404)

    cart = user.shopping_cart

    # Create a new transaction
    transaction = Transaction(user_id=user.id)  # You may need to set other fields as well
    session.add(transaction)

    # Transfer cart items to the transaction details
    cart_items = session.query(ShoppingCartItem).filter_by(cart_id=cart.id).all()

    for cart_item in cart_items:
        transaction_detail = TransactionDetail(
            transaction_id=transaction.id,
            product_id=cart_item.product_id,
            quantity=cart_item.quantity
        )
        session.add(transaction_detail)

    # Clean the user's cart
    session.query(ShoppingCartItem).filter_by(cart_id=cart.id).delete()

    session.commit()

    return Response(json={'message': 'Transaction created and cart cleaned'}, status=200)


@view_config(route_name='user_transactions', renderer='json')
def get_user_transactions(request):
    user = get_jwt_token(request)

    if user is None:
        return Response(json={'message': 'User is not authenticated'})

    user = decode_user(user)

    session = DBSession()

    # Fetch the user's transactions based on user ID
    transactions = session.query(Transaction).filter(Transaction.user_id == user['id']).all()

    transaction_history = []

    for transaction in transactions:
        total = transaction.calculate_total()

        # Fetch transaction details for each transaction
        details = session.query(TransactionDetail).filter(TransactionDetail.transaction_id == transaction.id).all()

        # Convert transactions and details to dictionaries
        transaction_data = transaction.to_dict()
        detail_data = []

        for detail in details:
            # Fetch the associated product
            product = session.query(Product).get(detail.product_id)

            if product:
                detail_dict = detail.to_dict()
                detail_dict['product'] = product.to_dict()  # Include the product details
                detail_data.append(detail_dict)

        transaction_data['details'] = detail_data
        transaction_data['total'] = total  # Include the total transaction amount
        transaction_history.append(transaction_data)
    res = json.dumps({'transactions': transaction_history}, cls=DateTimeEncoder)
    return Response(json=res, status=200)


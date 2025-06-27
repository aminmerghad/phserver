from flask_smorest import Blueprint
# Create Blueprints
product_bp = Blueprint('product', __name__,url_prefix='/api/products',description='Product API')
auth_bp = Blueprint('auth', __name__,url_prefix='/api/auth',description='Auth API')
category_bp = Blueprint('category', __name__,url_prefix='/api/categories',description='Category API')
inventory_bp = Blueprint('inventory', __name__,url_prefix='/api/inventory',description='Inventory API')
order_bp = Blueprint('order', __name__,url_prefix='/api/orders',description='Order API')
delivery_bp = Blueprint('delivery', __name__,url_prefix='/api/delivery',description='Delivery API')
# Import routes after Blueprint creation to avoid circular imports
from app.apis.product.routes import *
from app.apis.auth.auth_routes import *
from app.apis.auth.access_code_routes import *
from app.apis.auth.health_care_center import *
from app.apis.category.routes import *
from app.apis.inventory.inventory_routes import *
from app.apis.order.order_routes import *
from app.apis.delivery.routes import *

bp_list = [product_bp, auth_bp, category_bp, inventory_bp, order_bp, delivery_bp]

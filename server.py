from flask import Flask, request, jsonify, send_from_directory, render_template, abort
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename
from waitress import serve

app = Flask(__name__, 
    static_folder='.',
    static_url_path='',
    template_folder='.')
CORS(app)

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Отключаем кэширование для разработки

# Создаем папку для загрузок, если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Временное хранилище данных (в реальном приложении нужно использовать базу данных)
orders = {}
drivers = {}
messages = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    try:
        return send_from_directory('.', 'index.html')
    except Exception as e:
        logger.error(f"Error serving index.html: {str(e)}")
        abort(404)

@app.route('/styles.css')
def styles():
    try:
        return send_from_directory('.', 'styles.css')
    except Exception as e:
        logger.error(f"Error serving styles.css: {str(e)}")
        abort(404)

@app.route('/index.js')
def index_js():
    try:
        return send_from_directory('.', 'index.js')
    except Exception as e:
        logger.error(f"Error serving index.js: {str(e)}")
        abort(404)

@app.route('/js/<path:path>')
def send_js(path):
    try:
        return send_from_directory('js', path)
    except Exception as e:
        logger.error(f"Error serving JS file {path}: {str(e)}")
        abort(404)

@app.route('/css/<path:path>')
def send_css(path):
    try:
        return send_from_directory('css', path)
    except Exception as e:
        logger.error(f"Error serving CSS file {path}: {str(e)}")
        abort(404)

@app.route('/driver')
def driver():
    try:
        return send_from_directory('.', 'driver.html')
    except Exception as e:
        logger.error(f"Error serving driver.html: {str(e)}")
        abort(404)

@app.route('/customer')
def customer():
    try:
        return send_from_directory('.', 'customer.html')
    except Exception as e:
        logger.error(f"Error serving customer.html: {str(e)}")
        abort(404)

@app.route('/carrier')
def carrier():
    try:
        return send_from_directory('.', 'carrier.html')
    except Exception as e:
        logger.error(f"Error serving carrier.html: {str(e)}")
        abort(404)

@app.route('/auth')
def auth():
    try:
        return send_from_directory('.', 'auth.html')
    except Exception as e:
        logger.error(f"Error serving auth.html: {str(e)}")
        abort(404)

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.form
        files = request.files.getlist('documents')
        
        # Сохраняем файлы
        saved_files = []
        for file in files:
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                saved_files.append(filename)
        
        # Создаем заказ
        order_id = str(len(orders) + 1)
        order = {
            'id': order_id,
            'from_address': data.get('from_address'),
            'to_address': data.get('to_address'),
            'description': data.get('description'),
            'documents': saved_files,
            'status': 'new',
            'created_at': datetime.now().isoformat(),
            'customer_id': data.get('customer_id'),
            'driver_id': None
        }
        
        orders[order_id] = order
        messages[order_id] = []
        
        return jsonify(order), 201
    except Exception as e:
        logger.error(f"Error creating order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/orders/available', methods=['GET'])
def get_available_orders():
    available_orders = [order for order in orders.values() if order['status'] == 'new']
    return jsonify(available_orders)

@app.route('/api/orders/my', methods=['GET'])
def get_my_orders():
    customer_id = request.args.get('customer_id')
    driver_id = request.args.get('driver_id')
    
    if customer_id:
        my_orders = [order for order in orders.values() if order['customer_id'] == customer_id]
    elif driver_id:
        my_orders = [order for order in orders.values() if order['driver_id'] == driver_id]
    else:
        return jsonify({'error': 'No user ID provided'}), 400
    
    return jsonify(my_orders)

@app.route('/api/orders/<order_id>/take', methods=['POST'])
def take_order(order_id):
    try:
        data = request.json
        driver_id = data.get('driver_id')
        
        if order_id not in orders:
            return jsonify({'error': 'Order not found'}), 404
        
        order = orders[order_id]
        if order['status'] != 'new':
            return jsonify({'error': 'Order is not available'}), 400
        
        order['driver_id'] = driver_id
        order['status'] = 'in_progress'
        
        return jsonify(order)
    except Exception as e:
        logger.error(f"Error taking order: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/driver/auth', methods=['POST'])
def driver_auth():
    try:
        data = request.json
        phone = data.get('phone')
        
        # В реальном приложении здесь должна быть проверка в базе данных
        driver_id = str(len(drivers) + 1)
        driver = {
            'id': driver_id,
            'phone': phone
        }
        
        drivers[driver_id] = driver
        return jsonify(driver)
    except Exception as e:
        logger.error(f"Error in driver auth: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(404)
def not_found_error(error):
    logger.error(f"404 Error: {request.url}")
    return jsonify({'error': 'Not found', 'url': request.url}), 404

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Error: {str(error)}")
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Используем waitress вместо встроенного сервера Flask
    serve(app, host='0.0.0.0', port=5000, threads=4) 
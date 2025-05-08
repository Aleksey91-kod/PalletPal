from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os
import json
from datetime import datetime
import logging
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Конфигурация
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

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
    return send_from_directory('.', 'index.html')

@app.route('/driver')
def driver():
    return send_from_directory('.', 'driver.html')

@app.route('/customer')
def customer():
    return send_from_directory('.', 'customer.html')

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

@socketio.on('connect')
def handle_connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    logger.info('Client disconnected')

@socketio.on('join_order')
def handle_join_order(data):
    order_id = data.get('order_id')
    if order_id in messages:
        emit('message_history', messages[order_id])

@socketio.on('message')
def handle_message(data):
    try:
        order_id = data.get('order_id')
        if order_id not in messages:
            messages[order_id] = []
        
        message = {
            'text': data.get('text'),
            'sender': data.get('sender'),
            'timestamp': datetime.now().isoformat()
        }
        
        messages[order_id].append(message)
        emit('message', message, broadcast=True)
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000) 
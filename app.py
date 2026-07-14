from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'bakbak-cafe-secret-key-2026'
CORS(app)

# MySQL Configuration - EDIT THESE
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bakbak_cafe'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"Error: {e}")
        return None

def init_database():
    config = DB_CONFIG.copy()
    db_name = config.pop('database')
    try:
        conn = mysql.connector.connect(**config)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4")
        conn.commit()
        cursor.close()
        conn.close()

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS menu_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                price DECIMAL(10,2) NOT NULL,
                category VARCHAR(50) NOT NULL,
                description TEXT,
                emoji VARCHAR(10) DEFAULT '',
                available TINYINT(1) DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) UNIQUE NOT NULL,
                customer_name VARCHAR(100) NOT NULL,
                phone VARCHAR(20) NOT NULL,
                table_number INT NOT NULL DEFAULT 1,
                subtotal DECIMAL(10,2) NOT NULL,
                tax DECIMAL(10,2) NOT NULL DEFAULT 0,
                discount DECIMAL(10,2) NOT NULL DEFAULT 0,
                total DECIMAL(10,2) NOT NULL,
                payment_method ENUM('cash','card','upi') DEFAULT 'cash',
                status ENUM('pending','preparing','ready','completed','cancelled') DEFAULT 'pending',
                special_instructions TEXT,
                is_student_discount TINYINT(1) DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INT AUTO_INCREMENT PRIMARY KEY,
                order_id VARCHAR(50) NOT NULL,
                item_id INT NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                item_price DECIMAL(10,2) NOT NULL,
                quantity INT NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                role ENUM('admin','staff') DEFAULT 'staff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

        # Default users
        import hashlib
        cursor.execute("SELECT COUNT(*) FROM users WHERE username='admin'")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                         ('admin', hashlib.sha256('admin123'.encode()).hexdigest(), 'admin'))
            cursor.execute("INSERT INTO users (username, password, role) VALUES (%s, %s, %s)",
                         ('staff', hashlib.sha256('staff123'.encode()).hexdigest(), 'staff'))
            conn.commit()

        # Insert menu items from uploaded images
        cursor.execute("SELECT COUNT(*) FROM menu_items")
        if cursor.fetchone()[0] == 0:
            items = [
                # === SHANBHAG HOTEL - Fresh Fruit Juice ===
                ('Orange Juice', 50, 'fresh-juice', 'Freshly squeezed orange juice', ''),
                ('Apple Juice', 50, 'fresh-juice', 'Sweet and refreshing apple juice', ''),
                ('Grape Juice', 50, 'fresh-juice', 'Rich and flavorful grape juice', ''),
                ('Pineapple Juice', 50, 'fresh-juice', 'Tropical pineapple delight', ''),
                ('Water Melon Juice', 40, 'fresh-juice', 'Cool and hydrating watermelon', ''),
                ('Pomegranate Juice', 50, 'fresh-juice', 'Antioxidant-rich pomegranate', ''),
                ('Mix Fruit Juice', 60, 'fresh-juice', 'Blend of seasonal fruits', ''),
                ('Special Juice (No Ice/Sugar)', 60, 'fresh-juice', 'Pure fruit juice without additives', ''),

                # === SHANBHAG HOTEL - Milk Shake ===
                ('Vanilla Milkshake', 50, 'milk-shake', 'Classic vanilla milkshake', ''),
                ('Pista Milkshake', 50, 'milk-shake', 'Creamy pistachio milkshake', ''),
                ('Butter Scotch Milkshake', 50, 'milk-shake', 'Sweet butter scotch delight', ''),
                ('Strawberry Milkshake', 50, 'milk-shake', 'Fresh strawberry milkshake', ''),
                ('Black Current Milkshake', 50, 'milk-shake', 'Rich black current flavor', ''),
                ('Mango Milkshake', 50, 'milk-shake', 'King of fruits milkshake', ''),
                ('Butter Fruit Milkshake', 70, 'milk-shake', 'Creamy butter fruit shake', ''),
                ('Dragon Fruit Milkshake', 70, 'milk-shake', 'Exotic dragon fruit shake', ''),
                ('Royal Faluda', 60, 'milk-shake', 'Premium royal faluda', ''),

                # === SHANBHAG HOTEL - Ice Cream ===
                ('Single Sundae', 50, 'ice-cream', 'Classic single scoop sundae', ''),
                ('Double Sundae', 70, 'ice-cream', 'Double scoop sundae delight', ''),
                ('Fruit Salad', 40, 'ice-cream', 'Fresh mixed fruit salad', ''),
                ('Fruit Salad with Ice Cream', 70, 'ice-cream', 'Fruit salad topped with ice cream', ''),
                ('Gadbad', 90, 'ice-cream', 'Special gadbad ice cream', ''),

                # === CHAT & CHAAT BY JAIN FOODS - Chaat Items ===
                ('Pani Puri (5+1 pcs)', 35, 'chaat', 'Crispy puris with spicy pani', ''),
                ('Dahi Puri (5 pcs)', 50, 'chaat', 'Puris with yogurt and chutney', ''),
                ('Sev Puri (6 pcs)', 50, 'chaat', 'Flat puris with sev and chutney', ''),
                ('Bhel Puri', 50, 'chaat', 'Classic bhel with chutneys', ''),
                ('Cheese Masala Puri (5 pcs)', 70, 'chaat', 'Cheesy masala puris', ''),
                ('Dahi Papdi Chaat (6 pcs)', 50, 'chaat', 'Papdi with dahi and chutneys', ''),
                ('Bhel Puri Special', 60, 'chaat', 'Special loaded bhel puri', ''),
                ('Chinese Bhel', 70, 'chaat', 'Indo-Chinese style bhel', ''),
                ('Samosa Chaat (2 pcs)', 60, 'chaat', 'Samosa with chutney and dahi', ''),
                ('Family Pack Pani Puri', 210, 'chaat', 'Family pack of pani puri', ''),

                # === CHAT & CHAAT - Puffs ===
                ('Veg Puff', 25, 'puffs', 'Crispy veg puff', ''),
                ('Cheese Puff', 40, 'puffs', 'Cheese filled puff', ''),
                ('Veg Chinese Puff', 40, 'puffs', 'Chinese style veg puff', ''),
                ('Paneer Puff', 50, 'puffs', 'Paneer stuffed puff', ''),
                ('Aloo Tikki Puff', 40, 'puffs', 'Aloo tikki in puff', ''),
                ('Schezwan Paneer Puff', 50, 'puffs', 'Spicy schezwan paneer puff', ''),
                ('Pizza Puff', 50, 'puffs', 'Pizza flavored puff', ''),
                ('Mushroom Puff', 50, 'puffs', 'Mushroom stuffed puff', ''),

                # === CHAT & CHAAT - Corn Items ===
                ('Sweet Corn', 45, 'corn', 'Buttered sweet corn', ''),
                ('Butter Sweet Corn', 55, 'corn', 'Extra buttery sweet corn', ''),
                ('Peri Peri Sweet Corn', 70, 'corn', 'Spicy peri peri corn', ''),

                # === CHAT & CHAAT - Sandwiches ===
                ('Bread Butter', 35, 'sandwich', 'Classic bread butter', ''),
                ('Bread Butter Jam', 40, 'sandwich', 'Bread with butter and jam', ''),
                ('Veg Sandwich', 50, 'sandwich', 'Fresh vegetable sandwich', ''),
                ('Veg Cheese Sandwich', 70, 'sandwich', 'Veg sandwich with cheese', ''),
                ('Veg Bhujiya Sandwich', 70, 'sandwich', 'Sandwich with bhujiya', ''),
                ('Veg Schezwan Sandwich', 70, 'sandwich', 'Spicy schezwan sandwich', ''),
                ('Masala Cheese Sandwich', 80, 'sandwich', 'Masala with cheese', ''),
                ('Masala Cheese Muruku', 80, 'sandwich', 'Cheese muruku sandwich', ''),
                ('Veg Grill Sandwich', 80, 'sandwich', 'Grilled veg sandwich', ''),
                ('Kachra Sandwich', 90, 'sandwich', 'Special kachra sandwich', ''),
                ('Cheese Pizza Sandwich', 100, 'sandwich', 'Pizza style sandwich', ''),
                ('Kachra Pizza Sandwich', 110, 'sandwich', 'Kachra with pizza flavor', ''),

                # === CHAT & CHAAT - Toast Items ===
                ('Bread Butter Toast', 40, 'toast', 'Crispy butter toast', ''),
                ('Sandwich Toast', 50, 'toast', 'Classic sandwich toast', ''),
                ('Cheese Chilli Toast', 70, 'toast', 'Spicy cheese chilli toast', ''),
                ('Corn Cheese Toast', 80, 'toast', 'Corn and cheese toast', ''),
                ('Garlic Cheese Toast', 80, 'toast', 'Garlic flavored cheese toast', ''),
                ('Masala Cheese Toast', 80, 'toast', 'Masala cheese toast', ''),
                ('Chilli Cheese Toast', 80, 'toast', 'Extra chilli cheese toast', ''),
                ('Paneer Cheese Toast', 90, 'toast', 'Paneer and cheese toast', ''),
                ('Veg Grill Cheese Toast', 90, 'toast', 'Grilled veg cheese toast', ''),
                ('Mexican Sandwich Toast', 100, 'toast', 'Mexican flavored toast', ''),
                ('Cheese Corn Toast', 100, 'toast', 'Cheesy corn toast', ''),
                ('Paneer Tikka Toast', 110, 'toast', 'Paneer tikka flavored toast', ''),
                ('Veg Cheese Pizza Toast', 100, 'toast', 'Veg pizza with cheese', ''),
                ('Ulta Pizza Toast', 110, 'toast', 'Special ulta pizza toast', ''),
                ('Veg Pizza Toast with Paneer', 120, 'toast', 'Veg pizza with paneer', '')
            ]

            cursor.executemany(
                "INSERT INTO menu_items (name, price, category, description, emoji) VALUES (%s, %s, %s, %s, %s)",
                items
            )
            conn.commit()

        cursor.close()
        conn.close()
        print("Database initialized!")
        return True
    except Error as e:
        print(f"Error: {e}")
        return False

# ==================== API ROUTES ====================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/menu')
def get_menu():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor(dictionary=True)
        category = request.args.get('category', 'all')
        if category == 'all':
            cursor.execute("SELECT * FROM menu_items WHERE available = 1 ORDER BY category, name")
        else:
            cursor.execute("SELECT * FROM menu_items WHERE category = %s AND available = 1 ORDER BY name", (category,))
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': items})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/categories')
def get_categories():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT category FROM menu_items WHERE available = 1 ORDER BY category")
        categories = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': categories})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/order', methods=['POST'])
def place_order():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        data = request.get_json()
        order_id = 'BK' + datetime.now().strftime('%Y%m%d') + os.urandom(2).hex().upper()

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO orders (order_id, customer_name, phone, table_number, 
                              subtotal, tax, discount, total, payment_method, 
                              special_instructions, is_student_discount)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            order_id, data['customer_name'], data['phone'], data['table_number'],
            data['subtotal'], data['tax'], data.get('discount', 0),
            data['total'], data['payment_method'], data.get('special_instructions', ''),
            data.get('is_student_discount', False)
        ))

        for item in data['items']:
            cursor.execute("""
                INSERT INTO order_items (order_id, item_id, item_name, item_price, quantity)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item.get('id', 0), item['name'], item['price'], item['quantity']))

        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'order_id': order_id})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/orders')
def get_orders():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders ORDER BY created_at DESC")
        orders = cursor.fetchall()
        for order in orders:
            cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order['order_id'],))
            order['items'] = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': orders})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/order/<order_id>')
def get_order(order_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
        order = cursor.fetchone()
        if order:
            cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order_id,))
            order['items'] = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': order})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/order/status', methods=['PUT'])
def update_status():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        data = request.get_json()
        cursor = conn.cursor()
        cursor.execute("UPDATE orders SET status = %s WHERE order_id = %s",
                      (data['status'], data['order_id']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/order/<order_id>', methods=['DELETE'])
def delete_order(order_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/stats')
def get_stats():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor()
        stats = {}
        cursor.execute("SELECT COUNT(*) FROM orders")
        stats['total_orders'] = cursor.fetchone()[0]
        cursor.execute("SELECT COALESCE(SUM(total), 0) FROM orders")
        stats['total_revenue'] = float(cursor.fetchone()[0])
        cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM order_items")
        stats['items_sold'] = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        stats['pending_orders'] = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return jsonify({'success': True, 'data': stats})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '')
    password = data.get('password', '')
    import hashlib
    hashed = hashlib.sha256(password.encode()).hexdigest()

    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", 
                      (username, hashed))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        if user:
            session['user'] = user['username']
            session['role'] = user['role']
            return jsonify({'success': True, 'role': user['role']})
        else:
            return jsonify({'success': False, 'message': 'Invalid credentials'})
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})



# ==================== DAILY REPORT API ROUTES ====================

@app.route('/api/report/daily')
def get_daily_report():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        date = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM orders 
            WHERE DATE(created_at) = %s 
            ORDER BY created_at DESC
        """, (date,))
        orders = cursor.fetchall()

        for order in orders:
            cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order['order_id'],))
            order['items'] = cursor.fetchall()

        cursor.execute("""
            SELECT COALESCE(COUNT(*), 0) as total_orders,
                   COALESCE(SUM(total), 0) as total_revenue,
                   COALESCE(SUM(subtotal), 0) as total_subtotal,
                   COALESCE(SUM(tax), 0) as total_tax,
                   COALESCE(SUM(discount), 0) as total_discount
            FROM orders 
            WHERE DATE(created_at) = %s
        """, (date,))
        summary = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0) as total_items
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE DATE(o.created_at) = %s
        """, (date,))
        items_summary = cursor.fetchone()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'date': date,
                'orders': orders,
                'summary': {
                    'total_orders': summary['total_orders'],
                    'total_revenue': float(summary['total_revenue']),
                    'total_subtotal': float(summary['total_subtotal']),
                    'total_tax': float(summary['total_tax']),
                    'total_discount': float(summary['total_discount']),
                    'total_items': items_summary['total_items']
                }
            }
        })
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})


@app.route('/api/report/summary')
def get_date_range_summary():
    conn = get_db_connection()
    if not conn:
        return jsonify({'success': False, 'message': 'Database connection failed'})
    try:
        from_date = request.args.get('from')
        to_date = request.args.get('to')

        if not from_date or not to_date:
            return jsonify({'success': False, 'message': 'From and To dates are required'})

        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT * FROM orders 
            WHERE DATE(created_at) BETWEEN %s AND %s
            ORDER BY created_at DESC
        """, (from_date, to_date))
        orders = cursor.fetchall()

        for order in orders:
            cursor.execute("SELECT * FROM order_items WHERE order_id = %s", (order['order_id'],))
            order['items'] = cursor.fetchall()

        cursor.execute("""
            SELECT COALESCE(COUNT(*), 0) as total_orders,
                   COALESCE(SUM(total), 0) as total_revenue,
                   COALESCE(SUM(subtotal), 0) as total_subtotal,
                   COALESCE(SUM(tax), 0) as total_tax,
                   COALESCE(SUM(discount), 0) as total_discount
            FROM orders 
            WHERE DATE(created_at) BETWEEN %s AND %s
        """, (from_date, to_date))
        summary = cursor.fetchone()

        cursor.execute("""
            SELECT COALESCE(SUM(quantity), 0) as total_items
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE DATE(o.created_at) BETWEEN %s AND %s
        """, (from_date, to_date))
        items_summary = cursor.fetchone()

        cursor.execute("""
            SELECT oi.item_name, SUM(oi.quantity) as total_qty, SUM(oi.item_price * oi.quantity) as total_sales
            FROM order_items oi
            JOIN orders o ON oi.order_id = o.order_id
            WHERE DATE(o.created_at) BETWEEN %s AND %s
            GROUP BY oi.item_name
            ORDER BY total_qty DESC
            LIMIT 5
        """, (from_date, to_date))
        top_items = cursor.fetchall()

        cursor.execute("""
            SELECT payment_method, COUNT(*) as count, SUM(total) as amount
            FROM orders
            WHERE DATE(created_at) BETWEEN %s AND %s
            GROUP BY payment_method
        """, (from_date, to_date))
        payment_breakdown = cursor.fetchall()

        cursor.close()
        conn.close()

        return jsonify({
            'success': True,
            'data': {
                'from_date': from_date,
                'to_date': to_date,
                'orders': orders,
                'summary': {
                    'total_orders': summary['total_orders'],
                    'total_revenue': float(summary['total_revenue']),
                    'total_subtotal': float(summary['total_subtotal']),
                    'total_tax': float(summary['total_tax']),
                    'total_discount': float(summary['total_discount']),
                    'total_items': items_summary['total_items']
                },
                'top_items': top_items,
                'payment_breakdown': payment_breakdown
            }
        })
    except Error as e:
        return jsonify({'success': False, 'message': str(e)})

if __name__ == '__main__':
    print("Initializing BakBak Cafe database...")
    init_database()
    print("Starting server at http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)

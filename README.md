# 🎓 BakBak Cafe - Restaurant Management System

**Complete Restaurant Management System**
- **Frontend:** HTML + CSS + JavaScript (beautiful, animated, responsive)
- **Backend:** Python Flask (lightweight, no Node.js needed)
- **Database:** MySQL (stores all data permanently)

---

## ⚡ QUICK START (3 Steps)

### Step 1: Install Python & MySQL

#### Option A: Windows (XAMPP - Easiest)
1. Download **XAMPP** from https://www.apachefriends.org
2. Install XAMPP (check MySQL option)
3. Open **XAMPP Control Panel**
4. Click **Start** on MySQL
5. Click **Start** on Apache

#### Option B: Mac
```bash
# Install Homebrew first from https://brew.sh
brew install python mysql
brew services start mysql
```

#### Option C: Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip mysql-server
sudo systemctl start mysql
```

---

### Step 2: Configure Database

Open `app.py` in any text editor (Notepad, VS Code, etc.)

Find this section at the top (around line 10):
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'bakbak_cafe'
}
```

Change ONLY the password:
```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'your_mysql_password',   # <-- CHANGE THIS
    'database': 'bakbak_cafe'
}
```

**How to find your MySQL password?**
- **XAMPP:** Default is empty `''` (leave as is)
- **You set it during MySQL install:** Use that password
- **Forgot it?** Reset via MySQL console

---

### Step 3: Run the Application

#### Windows:
Double-click **`run.bat`**

OR open Command Prompt in the folder:
```cmd
pip install -r requirements.txt
python app.py
```

#### Mac/Linux:
Open Terminal in the folder:
```bash
chmod +x run.sh
./run.sh
```

OR manually:
```bash
pip3 install -r requirements.txt
python3 app.py
```

---

## ✅ What Happens When You Run?

```
Initializing BakBak Cafe database...
Database initialized!
Starting server at http://localhost:5000
 * Running on http://0.0.0.0:5000
```

The server automatically:
1. ✅ Creates MySQL database `bakbak_cafe` (if not exists)
2. ✅ Creates all tables (menu_items, orders, order_items, users)
3. ✅ Inserts all 66 menu items from your images
4. ✅ Starts web server at `http://localhost:5000`

---

## 🌐 Open in Browser

```
http://localhost:5000
```

---

## 📂 Project Files

```
bakbak_cafe/
├── app.py              ← Python backend (API + MySQL connection)
├── requirements.txt    ← Python packages to install
├── run.bat           ← Windows: Double-click to run
├── run.sh            ← Mac/Linux: Run script
├── templates/
│   └── index.html    ← Complete frontend (HTML/CSS/JS)
└── README.md         ← This file
```

---

## 🍽️ Menu Categories (66 Items from Your Images)

| Category | Count | Source |
|----------|-------|--------|
| Fresh Fruit Juice | 8 | Shanbhag Hotel |
| Milk Shake | 9 | Shanbhag Hotel |
| Ice Cream | 5 | Shanbhag Hotel |
| Chaat Items | 10 | Chat & Chaat by Jain Foods |
| Puff Items | 8 | Chat & Chaat by Jain Foods |
| Corn Items | 3 | Chat & Chaat by Jain Foods |
| Sandwiches | 12 | Chat & Chaat by Jain Foods |
| Toast Items | 15 | Chat & Chaat by Jain Foods |

---

## 🎓 Features

- **Student Offer:** 20% OFF banner with shimmer animation
- **Floating Food:** Animated emojis (🍕🍔🍟🌮🍦🍹🧁🍩) floating across screen
- **Cart System:** Add/remove items, quantity control, auto tax (5%)
- **Student Discount:** 20% off for orders above ₹200
- **Order History:** All stored in MySQL, viewable anytime
- **Admin Dashboard:** Stats + order status management
- **Printable Receipts:** Auto-generated
- **Payment Options:** Cash / Card / UPI
- **Real-time Search:** Search menu items instantly
- **Table Numbers:** Assign orders to tables

---

## 🔧 Troubleshooting

| Problem | Solution |
|---------|----------|
| "python not found" | Install Python and check "Add to PATH" |
| "mysql-connector not found" | Run `pip install -r requirements.txt` |
| "Access denied for user" | Wrong MySQL password in app.py |
| "Port 5000 in use" | Change `port=5000` to `port=5001` in app.py |
| "Can't connect to MySQL" | Make sure MySQL service is running |

---

## 🗄️ Database Structure

```
bakbak_cafe (MySQL database)
├── menu_items          (66 menu items)
│   ├── id, name, price, category, description, emoji
│
├── orders              (customer orders)
│   ├── order_id, customer_name, phone, table_number
│   ├── subtotal, tax, discount, total, payment_method
│   ├── status (pending/preparing/ready/completed)
│   └── is_student_discount
│
├── order_items         (items in each order)
│   ├── order_id, item_id, item_name, item_price, quantity
│
└── users               (login accounts)
    ├── admin / admin123
    └── staff / staff123
```

---

**Free to use for your restaurant!** 🎉

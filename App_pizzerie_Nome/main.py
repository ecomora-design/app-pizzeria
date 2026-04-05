from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
import sqlite3
from contextlib import closing

app = FastAPI(title="ECOMORA Web App")
app.mount("/static", StaticFiles(directory="static"), name="static")

DB_NAME = "restaurant.db"
WHATSAPP_NUMBER = "393884027650"
PHONE_NUMBER = "+393884027650"
BRAND_NAME = "ECOMORA"
BRAND_SUBTITLE = "Ordina, prenota e scopri il menu"


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            price REAL NOT NULL,
            available INTEGER NOT NULL DEFAULT 1
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            order_type TEXT NOT NULL,
            address TEXT,
            notes TEXT,
            requested_time TEXT,
            total REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL,
            menu_item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL
        )
        """)

        conn.commit()

        cursor.execute("SELECT COUNT(*) as count FROM menu_items")
        count = cursor.fetchone()["count"]

        if count == 0:
            sample_menu = [
                ("Margherita", "Pizze", 6.50, 1),
                ("Diavola", "Pizze", 8.50, 1),
                ("Capricciosa", "Pizze", 9.00, 1),
                ("Quattro Formaggi", "Pizze", 9.50, 1),
                ("Bufalina", "Pizze", 10.00, 1),

                ("Spaghetti al Pomodoro", "Primi", 7.50, 1),
                ("Penne alla Norma", "Primi", 8.50, 1),
                ("Carbonara", "Primi", 9.50, 1),
                ("Lasagna al Forno", "Primi", 10.00, 1),

                ("Cotoletta con Patatine", "Secondi", 11.00, 1),
                ("Grigliata di Carne", "Secondi", 14.00, 1),
                ("Insalata di Pollo", "Secondi", 9.50, 1),

                ("Patatine Fritte", "Fritti", 3.50, 1),
                ("Crocchette", "Fritti", 4.00, 1),
                ("Anelli di Cipolla", "Fritti", 4.50, 1),

                ("Coca Cola", "Bevande", 2.50, 1),
                ("Acqua Naturale", "Bevande", 1.50, 1),
                ("Birra Piccola", "Bevande", 3.00, 1),

                ("Tiramisù", "Dolci", 4.50, 1),
                ("Cheesecake", "Dolci", 5.00, 1),
            ]
            cursor.executemany("""
                INSERT INTO menu_items (name, category, price, available)
                VALUES (?, ?, ?, ?)
            """, sample_menu)
            conn.commit()


@app.on_event("startup")
def startup():
    init_db()


class OrderItemRequest(BaseModel):
    menu_item_id: int
    quantity: int = Field(..., gt=0)


class CreateOrderRequest(BaseModel):
    customer_name: str
    phone: str
    order_type: Literal["pickup", "delivery"]
    address: Optional[str] = None
    notes: Optional[str] = None
    requested_time: Optional[str] = None
    items: List[OrderItemRequest]


@app.get("/menu")
def get_menu():
    image_map = {
        "Margherita": "https://images.unsplash.com/photo-1604382355076-af4b0eb60143?auto=format&fit=crop&w=1200&q=80",
        "Diavola": "https://images.unsplash.com/photo-1513104890138-7c749659a591?auto=format&fit=crop&w=1200&q=80",
        "Capricciosa": "https://images.unsplash.com/photo-1593560708920-61dd98c46a4e?auto=format&fit=crop&w=1200&q=80",
        "Quattro Formaggi": "https://images.unsplash.com/photo-1548365328-9f547fb0953b?auto=format&fit=crop&w=1200&q=80",
        "Bufalina": "https://images.unsplash.com/photo-1574071318508-1cdbab80d002?auto=format&fit=crop&w=1200&q=80",

        "Spaghetti al Pomodoro": "https://images.unsplash.com/photo-1621996346565-e3dbc646d9a9?auto=format&fit=crop&w=1200&q=80",
        "Penne alla Norma": "https://images.unsplash.com/photo-1645112411341-6c4fd023714a?auto=format&fit=crop&w=1200&q=80",
        "Carbonara": "https://images.unsplash.com/photo-1612874742237-6526221588e3?auto=format&fit=crop&w=1200&q=80",
        "Lasagna al Forno": "https://images.unsplash.com/photo-1619895092538-128341789043?auto=format&fit=crop&w=1200&q=80",

        "Cotoletta con Patatine": "https://images.unsplash.com/photo-1544025162-d76694265947?auto=format&fit=crop&w=1200&q=80",
        "Grigliata di Carne": "https://images.unsplash.com/photo-1558030006-450675393462?auto=format&fit=crop&w=1200&q=80",
        "Insalata di Pollo": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?auto=format&fit=crop&w=1200&q=80",

        "Patatine Fritte": "https://images.unsplash.com/photo-1573080496219-bb080dd4f877?auto=format&fit=crop&w=1200&q=80",
        "Crocchette": "https://images.unsplash.com/photo-1625944230945-1b7dd3b949ab?auto=format&fit=crop&w=1200&q=80",
        "Anelli di Cipolla": "https://images.unsplash.com/photo-1639024471283-03518883512d?auto=format&fit=crop&w=1200&q=80",

        "Coca Cola": "https://images.unsplash.com/photo-1629203851122-3726ecdf080e?auto=format&fit=crop&w=1200&q=80",
        "Acqua Naturale": "https://images.unsplash.com/photo-1564419439241-687d5f0f3f5b?auto=format&fit=crop&w=1200&q=80",
        "Birra Piccola": "https://images.unsplash.com/photo-1563379091339-03246963d29d?auto=format&fit=crop&w=1200&q=80",

        "Tiramisù": "https://images.unsplash.com/photo-1571877227200-a0d98ea607e9?auto=format&fit=crop&w=1200&q=80",
        "Cheesecake": "https://images.unsplash.com/photo-1533134242443-d4fd215305ad?auto=format&fit=crop&w=1200&q=80",
    }

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM menu_items WHERE available = 1 ORDER BY category, name")
        rows = cursor.fetchall()

        return [
            {
                "id": row["id"],
                "name": row["name"],
                "category": row["category"],
                "price": row["price"],
                "image": image_map.get(
                    row["name"],
                    "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?auto=format&fit=crop&w=1200&q=80"
                )
            }
            for row in rows
        ]


@app.post("/orders")
def create_order(order_data: CreateOrderRequest):
    if not order_data.items:
        raise HTTPException(status_code=400, detail="L'ordine deve contenere almeno un prodotto")

    if order_data.order_type == "delivery" and not order_data.address:
        raise HTTPException(status_code=400, detail="Per la consegna serve l'indirizzo")

    with closing(get_connection()) as conn:
        cursor = conn.cursor()

        total = 0.0
        prepared_items = []

        for item in order_data.items:
            cursor.execute(
                "SELECT * FROM menu_items WHERE id = ? AND available = 1",
                (item.menu_item_id,)
            )
            menu_item = cursor.fetchone()

            if not menu_item:
                raise HTTPException(status_code=404, detail=f"Prodotto con id {item.menu_item_id} non trovato")

            subtotal = menu_item["price"] * item.quantity
            total += subtotal

            prepared_items.append({
                "menu_item_id": menu_item["id"],
                "item_name": menu_item["name"],
                "quantity": item.quantity,
                "unit_price": menu_item["price"],
                "subtotal": subtotal
            })

        cursor.execute("""
            INSERT INTO orders (
                customer_name, phone, order_type, address, notes, requested_time, total, status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_data.customer_name,
            order_data.phone,
            order_data.order_type,
            order_data.address,
            order_data.notes,
            order_data.requested_time,
            round(total, 2),
            "pending"
        ))

        order_id = cursor.lastrowid

        for item in prepared_items:
            cursor.execute("""
                INSERT INTO order_items (
                    order_id, menu_item_id, item_name, quantity, unit_price, subtotal
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                item["menu_item_id"],
                item["item_name"],
                item["quantity"],
                item["unit_price"],
                round(item["subtotal"], 2)
            ))

        conn.commit()

    return {"status": "confirmed", "order_id": order_id, "total": round(total, 2)}


@app.post("/add-item")
async def add_item(request: Request):
    data = await request.json()
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")

    if not name or not category or price in [None, ""]:
        raise HTTPException(status_code=400, detail="Dati mancanti")

    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO menu_items (name, category, price, available) VALUES (?, ?, ?, 1)",
            (name, category, float(price))
        )
        conn.commit()

    return {"status": "ok"}


def base_style() -> str:
    return """
    <style>
        :root {
            --bg1: #ff7a00;
            --bg2: #ffae42;
            --card: rgba(255,255,255,0.97);
            --text: #1f2937;
            --muted: #6b7280;
            --line: #ececec;
            --shadow: 0 18px 40px rgba(0,0,0,0.14);
            --radius-xl: 26px;
            --primary: #ff6b00;
            --primary-dark: #e45c00;
            --green: #25D366;
            --green-dark: #1ebe5d;
        }

        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            font-family: Arial, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(255,255,255,0.18), transparent 28%),
                radial-gradient(circle at bottom right, rgba(255,255,255,0.16), transparent 26%),
                linear-gradient(180deg, var(--bg1), var(--bg2));
            min-height: 100vh;
            overflow-x: hidden;
            position: relative;
        }

        body::before,
        body::after {
            position: fixed;
            z-index: 0;
            pointer-events: none;
            opacity: 0.06;
            font-size: 120px;
            line-height: 1;
        }

        body::before {
            content: "🍕";
            top: 10px;
            left: 4px;
            transform: rotate(-10deg);
        }

        body::after {
            content: "🍝";
            bottom: 16px;
            right: 4px;
            transform: rotate(8deg);
        }

        .page-wrap {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            padding: 16px 10px 92px;
        }

        .container {
            width: 100%;
            max-width: 620px;
        }

        .topbar {
            text-align: center;
            margin-bottom: 16px;
        }

        .brand-logo-wrap {
            display: flex;
            justify-content: center;
            margin-bottom: 8px;
        }

        .brand-logo {
            width: min(230px, 76vw);
            max-height: 86px;
            object-fit: contain;
            filter: drop-shadow(0 8px 18px rgba(0,0,0,0.14));
        }

        .brand-sub {
            color: rgba(255,255,255,0.96);
            font-size: 13px;
            font-weight: 700;
            text-align: center;
        }

        .hero-box,
        .panel,
        #cart,
        form,
        .accordion {
            background: var(--card);
            border-radius: var(--radius-xl);
            box-shadow: var(--shadow);
        }

        .hero-box,
        .panel,
        #cart,
        form {
            padding: 18px;
        }

        h1 {
            margin: 0 0 8px 0;
            text-align: center;
            color: var(--primary);
            font-size: 28px;
            line-height: 1.15;
        }

        .subtitle {
            margin: 0;
            text-align: center;
            color: var(--muted);
            line-height: 1.45;
            font-size: 14px;
        }

        h2 {
            margin: 18px 0 10px;
            color: white;
            text-align: center;
            font-size: 20px;
        }

        .grid-3 {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            margin-top: 18px;
        }

        .choice-card {
            display: block;
            text-decoration: none;
            color: white;
            border-radius: 22px;
            padding: 18px 16px;
            box-shadow: var(--shadow);
        }

        .choice-card .emoji {
            font-size: 30px;
            margin-bottom: 8px;
        }

        .choice-card h3 {
            margin: 0 0 6px 0;
            font-size: 22px;
            color: white;
        }

        .choice-card p {
            margin: 0;
            font-size: 14px;
            line-height: 1.45;
        }

        .choice-card .cta {
            display: inline-block;
            margin-top: 12px;
            font-weight: 800;
            font-size: 14px;
        }

        .ordina-card { background: linear-gradient(135deg, #ff6b00, #ff3d00); }
        .prenota-card { background: linear-gradient(135deg, #14b8a6, #0f766e); }
        .menu-card { background: linear-gradient(135deg, #3b82f6, #1d4ed8); }

        .quick-actions {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
            margin-top: 14px;
        }

        .quick-btn {
            display: block;
            text-align: center;
            text-decoration: none;
            background: white;
            color: var(--text);
            padding: 14px;
            border-radius: 16px;
            font-weight: 800;
            box-shadow: 0 8px 18px rgba(0,0,0,0.08);
        }

        .back-link {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            margin-bottom: 12px;
            color: white;
            font-weight: 800;
            text-decoration: none;
            padding: 10px 14px;
            border-radius: 999px;
            background: rgba(255,255,255,0.16);
            border: 1px solid rgba(255,255,255,0.20);
            font-size: 14px;
        }

        .accordion {
            overflow: hidden;
            margin-bottom: 12px;
        }

        .accordion-header {
            width: 100%;
            background: white;
            border: none;
            padding: 16px;
            text-align: left;
            font-size: 17px;
            font-weight: 900;
            cursor: pointer;
            color: var(--text);
        }

        .accordion-content {
            display: none;
            padding: 0 12px 12px;
        }

        .accordion-content.open {
            display: block;
        }

        .menu-item {
            display: grid;
            grid-template-columns: 1fr;
            gap: 12px;
            background: #fffaf5;
            border: 1px solid #f4e7da;
            border-radius: 18px;
            padding: 12px;
            margin-top: 12px;
        }

        .menu-item img {
            width: 100%;
            height: 165px;
            object-fit: cover;
            border-radius: 14px;
            display: block;
        }

        .menu-info strong {
            font-size: 20px;
            display: block;
            margin-bottom: 5px;
        }

        .price {
            color: var(--primary);
            font-weight: 900;
            font-size: 17px;
            display: block;
            margin-bottom: 6px;
        }

        .menu-desc {
            color: var(--muted);
            font-size: 13px;
            line-height: 1.4;
            margin-bottom: 8px;
        }

        .qty-row {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            margin-top: 6px;
        }

        .qty-row input {
            width: 100%;
        }

        .add-btn,
        .remove-btn,
        button[type="submit"] {
            border: none;
            border-radius: 14px;
            padding: 13px 14px;
            cursor: pointer;
            font-weight: 900;
            font-size: 15px;
        }

        .add-btn {
            background: linear-gradient(135deg, var(--primary), var(--primary-dark));
            color: white;
            width: 100%;
        }

        #cart, form {
            padding: 16px;
        }

        .cart-empty {
            color: var(--muted);
            text-align: center;
            padding: 10px 0 4px;
            font-size: 14px;
        }

        .cart-row {
            display: grid;
            grid-template-columns: 1fr;
            gap: 8px;
            padding: 12px 0;
            border-bottom: 1px solid var(--line);
        }

        .cart-main {
            display: flex;
            flex-direction: column;
            gap: 4px;
        }

        .cart-title {
            font-weight: 800;
            font-size: 14px;
        }

        .cart-price {
            color: var(--muted);
            font-size: 13px;
        }

        .remove-btn {
            width: 100%;
            background: #f3f4f6;
            color: #333;
        }

        #total {
            font-size: 21px;
            font-weight: 900;
            text-align: center;
            margin: 10px 0 0;
            color: white;
        }

        input, select, textarea {
            width: 100%;
            padding: 14px;
            margin-top: 10px;
            border-radius: 14px;
            border: 1px solid #e5e7eb;
            font-size: 15px;
            background: white;
            outline: none;
        }

        button[type="submit"] {
            width: 100%;
            margin-top: 12px;
            background: linear-gradient(135deg, var(--green), var(--green-dark));
            color: white;
        }

        .helper-text {
            font-size: 12px;
            color: var(--muted);
            margin-top: 8px;
            line-height: 1.4;
            text-align: center;
        }

        #result {
            margin-top: 12px;
            font-weight: 800;
            text-align: center;
            color: white;
            font-size: 14px;
        }

        .app-nav {
            position: fixed;
            left: 0;
            right: 0;
            bottom: 0;
            z-index: 20;
            display: flex;
            justify-content: center;
            padding: 10px 10px 14px;
            background: linear-gradient(to top, rgba(255,122,0,0.95), rgba(255,122,0,0.72), transparent);
        }

        .app-nav-inner {
            width: 100%;
            max-width: 620px;
            background: rgba(255,255,255,0.98);
            border-radius: 20px;
            box-shadow: 0 16px 30px rgba(0,0,0,0.18);
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            overflow: hidden;
        }

        .app-nav a {
            text-decoration: none;
            color: var(--text);
            text-align: center;
            padding: 12px 8px;
            font-size: 12px;
            font-weight: 800;
        }

        .app-nav .icon {
            display: block;
            font-size: 20px;
            margin-bottom: 4px;
        }

        .admin-box,
        .orders-box {
            background: rgba(255,255,255,0.97);
            border-radius: 28px;
            padding: 24px;
            box-shadow: 0 18px 40px rgba(0,0,0,0.14);
        }

        .simple-logo {
            width: min(220px, 72vw);
            max-height: 90px;
            object-fit: contain;
            display: block;
            margin: 0 auto 16px auto;
        }

        .item {
            padding: 12px 0;
            border-bottom: 1px solid #eee;
        }

        .order-card {
            background: white;
            border-radius: 18px;
            padding: 16px;
            margin-bottom: 14px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.08);
        }

        @media (min-width: 700px) {
            .page-wrap {
                padding: 24px 16px 96px;
            }

            .hero-box,
            .panel,
            #cart,
            form {
                padding: 22px;
            }

            .menu-item img {
                height: 210px;
            }

            .cart-row {
                grid-template-columns: 1fr auto;
                align-items: center;
            }

            .remove-btn {
                width: auto;
            }

            .brand-logo {
                width: min(300px, 72vw);
                max-height: 110px;
            }

            h1 {
                font-size: 34px;
            }
        }
    </style>
    """


def bottom_nav() -> str:
    return """
    <div class="app-nav">
        <div class="app-nav-inner">
            <a href="/"><span class="icon">🏠</span>Home</a>
            <a href="/menu-view"><span class="icon">📖</span>Menu</a>
            <a href="/ordina"><span class="icon">🛒</span>Ordina</a>
            <a href="/prenota"><span class="icon">🍽</span>Prenota</a>
        </div>
    </div>
    """


def shell_page(title: str, body_content: str) -> HTMLResponse:
    html = f"""
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
        <title>{title}</title>
        <link rel="manifest" href="/static/manifest.json">
        <meta name="theme-color" content="#ff7a00">
        <link rel="apple-touch-icon" href="/static/icon-192.png">
        <meta name="apple-mobile-web-app-capable" content="yes">
        <meta name="apple-mobile-web-app-status-bar-style" content="default">
        <meta name="apple-mobile-web-app-title" content="ECOMORA">
        {base_style()}
    </head>
    <body>
        <div class="page-wrap">
            <div class="container">
                <div class="topbar">
                    <div class="brand-logo-wrap">
                        <img src="/static/logo.png" alt="{BRAND_NAME}" class="brand-logo">
                    </div>
                    <div class="brand-sub">{BRAND_SUBTITLE}</div>
                </div>
                {body_content}
            </div>
        </div>

        {bottom_nav()}

        <script>
            if ('serviceWorker' in navigator) {{
                window.addEventListener('load', function() {{
                    navigator.serviceWorker.register('/static/sw.js');
                }});
            }}
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html)


@app.get("/", response_class=HTMLResponse)
def home():
    body = f"""
    <div class="hero-box">
        <h1>Benvenuto nella web app del locale</h1>
        <p class="subtitle">Ordina, prenota e consulta il menu in modo semplice, veloce e perfetto da smartphone.</p>

        <div class="grid-3">
            <a class="choice-card ordina-card" href="/ordina">
                <div class="emoji">🛒</div>
                <h3>Ordina online</h3>
                <p>Asporto o domicilio con invio rapido su WhatsApp.</p>
                <span class="cta">Ordina adesso →</span>
            </a>

            <a class="choice-card prenota-card" href="/prenota">
                <div class="emoji">🍽</div>
                <h3>Prenota tavolo</h3>
                <p>Compila in pochi secondi e chiedi la conferma in chat.</p>
                <span class="cta">Prenota subito →</span>
            </a>

            <a class="choice-card menu-card" href="/menu-view">
                <div class="emoji">📖</div>
                <h3>Menu completo</h3>
                <p>Pizze, primi, secondi, fritti, bevande e dolci.</p>
                <span class="cta">Scopri il menu →</span>
            </a>
        </div>

        <div class="quick-actions">
            <a class="quick-btn" href="tel:{PHONE_NUMBER}">📞 Chiama ora</a>
            <a class="quick-btn" href="https://wa.me/{WHATSAPP_NUMBER}">💬 WhatsApp</a>
        </div>
    </div>
    """
    return shell_page("Home", body)


@app.get("/ordina", response_class=HTMLResponse)
def ordina():
    body = f"""
    <a class="back-link" href="/">← Torna alla home</a>

    <div class="panel">
        <h1>Ordina online</h1>
        <p class="subtitle">Scegli i prodotti, aggiungili al carrello e invia l’ordine per conferma.</p>
    </div>

    <h2>Menu</h2>
    <div id="menu-list"></div>

    <h2>Carrello</h2>
    <div id="cart"></div>
    <p id="total">Totale: €0.00</p>

    <h2>Dati ordine</h2>
    <form id="order-form">
        <input type="text" id="customer_name" placeholder="Nome" required>
        <input type="text" id="phone" placeholder="Telefono" required>
        <select id="order_type">
            <option value="pickup">Ritiro</option>
            <option value="delivery">Consegna</option>
        </select>
        <input type="text" id="address" placeholder="Indirizzo consegna">
        <input type="text" id="requested_time" placeholder="Orario richiesto es. 20:30">
        <textarea id="notes" placeholder="Note per il locale"></textarea>
        <button type="submit">Invia ordine su WhatsApp</button>
        <div class="helper-text">Ordine salvato e inviato direttamente al locale.</div>
    </form>

    <p id="result"></p>

    <script>
        let selectedItems = [];

        const descriptions = {{
            "Pizze": "Pizze classiche e speciali, fragranti e ricche di gusto.",
            "Primi": "Primi piatti tradizionali e saporiti.",
            "Secondi": "Piatti completi e gustosi per pranzo e cena.",
            "Fritti": "Sfizi croccanti da condividere.",
            "Bevande": "Bibite e bevande per accompagnare ogni ordine.",
            "Dolci": "Dessert golosi per concludere in bellezza."
        }};

        async function loadMenu() {{
            try {{
                const response = await fetch('/menu');
                const menu = await response.json();

                const menuList = document.getElementById('menu-list');
                menuList.innerHTML = '';

                const grouped = {{}};
                menu.forEach(item => {{
                    if (!grouped[item.category]) grouped[item.category] = [];
                    grouped[item.category].push(item);
                }});

                Object.keys(grouped).forEach((category, index) => {{
                    const wrapper = document.createElement('div');
                    wrapper.className = 'accordion';

                    const header = document.createElement('button');
                    header.className = 'accordion-header';
                    header.type = 'button';
                    header.innerText = category;

                    const content = document.createElement('div');
                    content.className = 'accordion-content';
                    if (index === 0) content.classList.add('open');

                    header.addEventListener('click', function() {{
                        content.classList.toggle('open');
                    }});

                    grouped[category].forEach(item => {{
                        const div = document.createElement('div');
                        div.className = 'menu-item';
                        div.innerHTML = `
                            <img src="${{item.image}}" alt="${{item.name}}">
                            <div class="menu-info">
                                <strong>${{item.name}}</strong>
                                <span class="price">€${{item.price.toFixed(2)}}</span>
                                <div class="menu-desc">${{descriptions[item.category] || 'Specialità del locale.'}}</div>
                                <div class="qty-row">
                                    <input type="number" min="1" value="1" id="qty-${{item.id}}">
                                    <button type="button" class="add-btn">Aggiungi al carrello</button>
                                </div>
                            </div>
                        `;

                        div.querySelector('.add-btn').addEventListener('click', function() {{
                            addToOrder(item.id, item.price, item.name);
                        }});

                        content.appendChild(div);
                    }});

                    wrapper.appendChild(header);
                    wrapper.appendChild(content);
                    menuList.appendChild(wrapper);
                }});
            }} catch (error) {{
                document.getElementById('menu-list').innerHTML = '<div class="panel">Errore nel caricamento del menu</div>';
            }}
        }}

        function addToOrder(menuItemId, price, name) {{
            const quantity = parseInt(document.getElementById(`qty-${{menuItemId}}`).value);
            if (!quantity || quantity < 1) return;

            const existing = selectedItems.find(i => i.menu_item_id === menuItemId);
            if (existing) {{
                existing.quantity += quantity;
            }} else {{
                selectedItems.push({{
                    menu_item_id: menuItemId,
                    quantity: quantity,
                    price: price,
                    name: name
                }});
            }}
            renderCart();
        }}

        function removeFromCart(menuItemId) {{
            selectedItems = selectedItems.filter(item => item.menu_item_id !== menuItemId);
            renderCart();
        }}

        function renderCart() {{
            const cart = document.getElementById('cart');
            let total = 0;
            cart.innerHTML = '';

            if (selectedItems.length === 0) {{
                cart.innerHTML = '<div class="cart-empty">Il carrello è vuoto</div>';
                document.getElementById('total').innerText = 'Totale: €0.00';
                return;
            }}

            selectedItems.forEach(item => {{
                const subtotal = item.price * item.quantity;
                total += subtotal;

                const row = document.createElement('div');
                row.className = 'cart-row';
                row.innerHTML = `
                    <div class="cart-main">
                        <span class="cart-title">${{item.name}} x${{item.quantity}}</span>
                        <span class="cart-price">€${{subtotal.toFixed(2)}}</span>
                    </div>
                `;

                const removeBtn = document.createElement('button');
                removeBtn.type = 'button';
                removeBtn.className = 'remove-btn';
                removeBtn.innerText = 'Rimuovi';
                removeBtn.addEventListener('click', function() {{
                    removeFromCart(item.menu_item_id);
                }});

                row.appendChild(removeBtn);
                cart.appendChild(row);
            }});

            document.getElementById('total').innerText = `Totale: €${{total.toFixed(2)}}`;
        }}

        document.getElementById('order-form').addEventListener('submit', async function(e) {{
            e.preventDefault();

            if (selectedItems.length === 0) {{
                document.getElementById('result').innerText = 'Aggiungi almeno un prodotto al carrello';
                return;
            }}

            const payload = {{
                customer_name: document.getElementById('customer_name').value,
                phone: document.getElementById('phone').value,
                order_type: document.getElementById('order_type').value,
                address: document.getElementById('address').value || null,
                requested_time: document.getElementById('requested_time').value || null,
                notes: document.getElementById('notes').value || null,
                items: selectedItems.map(i => ({{
                    menu_item_id: i.menu_item_id,
                    quantity: i.quantity
                }}))
            }};

            const response = await fetch('/orders', {{
                method: 'POST',
                headers: {{ 'Content-Type': 'application/json' }},
                body: JSON.stringify(payload)
            }});

            const result = await response.json();
            if (!response.ok) {{
                document.getElementById('result').innerText = `Errore: ${{result.detail || 'qualcosa è andato storto'}}`;
                return;
            }}

            let itemsText = '';
            let total = 0;
            selectedItems.forEach(item => {{
                const subtotal = item.price * item.quantity;
                total += subtotal;
                itemsText += `- ${{item.name}} x${{item.quantity}} = €${{subtotal.toFixed(2)}}\\n`;
            }});

            const orderTypeText = payload.order_type === 'pickup' ? 'Ritiro' : 'Consegna';
            const addressText = payload.order_type === 'delivery' ? (payload.address || '-') : '-';

            const message = `Nuovo ordine

ID ordine: ${{result.order_id}}
Nome: ${{payload.customer_name}}
Telefono: ${{payload.phone}}
Tipo ordine: ${{orderTypeText}}
Orario richiesto: ${{payload.requested_time || '-'}}
Indirizzo: ${{addressText}}
Note: ${{payload.notes || '-'}}

Ordine:
${{itemsText}}
Totale: €${{total.toFixed(2)}}

Confermate questo orario?`;

            const whatsappUrl = `https://wa.me/{WHATSAPP_NUMBER}?text=${{encodeURIComponent(message)}}`;
            window.location.href = whatsappUrl;
        }});

        loadMenu();
        renderCart();
    </script>
    """
    return shell_page("Ordina", body)


@app.get("/prenota", response_class=HTMLResponse)
def prenota():
    body = f"""
    <a class="back-link" href="/">← Torna alla home</a>

    <div class="panel">
        <h1>Prenota un tavolo</h1>
        <p class="subtitle">Inserisci i dati e richiedi la conferma in modo semplice e veloce.</p>
    </div>

    <form id="booking-form">
        <input id="name" placeholder="Nome" required>
        <input id="phone" placeholder="Telefono" required>
        <input id="date" type="date" required>
        <input id="time" type="time" required>
        <input id="people" type="number" min="1" placeholder="Numero persone" required>
        <textarea id="notes" placeholder="Note opzionali"></textarea>

        <button type="submit">Invia prenotazione su WhatsApp</button>
        <div class="helper-text">Prenotazione perfetta da smartphone.</div>
    </form>

    <p id="result"></p>

    <script>
        document.getElementById('booking-form').addEventListener('submit', function(e) {{
            e.preventDefault();

            const name = document.getElementById('name').value;
            const phone = document.getElementById('phone').value;
            const date = document.getElementById('date').value;
            const time = document.getElementById('time').value;
            const people = document.getElementById('people').value;
            const notes = document.getElementById('notes').value || '-';

            const message = `Prenotazione tavolo

Nome: ${{name}}
Telefono: ${{phone}}
Data: ${{date}}
Ora: ${{time}}
Persone: ${{people}}
Note: ${{notes}}

Confermate?`;

            const url = "https://wa.me/{WHATSAPP_NUMBER}?text=" + encodeURIComponent(message);
            window.location.href = url;
        }});
    </script>
    """
    return shell_page("Prenota", body)


@app.get("/menu-view", response_class=HTMLResponse)
def menu_view():
    body = """
    <a class="back-link" href="/">← Torna alla home</a>

    <div class="panel">
        <h1>Il nostro menu</h1>
        <p class="subtitle">Consulta tutte le categorie in una pagina chiara e comoda da mobile.</p>
    </div>

    <div id="menu-list"></div>

    <script>
        const descriptions = {
            "Pizze": "Pizze classiche e speciali, fragranti e ricche di gusto.",
            "Primi": "Primi piatti tradizionali e saporiti.",
            "Secondi": "Piatti completi e gustosi per pranzo e cena.",
            "Fritti": "Sfizi croccanti da condividere.",
            "Bevande": "Bibite e bevande per accompagnare ogni pasto.",
            "Dolci": "Dessert golosi per concludere in bellezza."
        };

        async function loadMenuView() {
            try {
                const response = await fetch('/menu');
                const menu = await response.json();

                const menuList = document.getElementById('menu-list');
                menuList.innerHTML = '';

                const grouped = {};
                menu.forEach(item => {
                    if (!grouped[item.category]) grouped[item.category] = [];
                    grouped[item.category].push(item);
                });

                Object.keys(grouped).forEach((category, index) => {
                    const wrapper = document.createElement('div');
                    wrapper.className = 'accordion';

                    const header = document.createElement('button');
                    header.className = 'accordion-header';
                    header.type = 'button';
                    header.innerText = category;

                    const content = document.createElement('div');
                    content.className = 'accordion-content';
                    if (index === 0) content.classList.add('open');

                    header.addEventListener('click', function() {
                        content.classList.toggle('open');
                    });

                    grouped[category].forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'menu-item';
                        div.innerHTML = `
                            <img src="${item.image}" alt="${item.name}">
                            <div class="menu-info">
                                <strong>${item.name}</strong>
                                <span class="price">€${item.price.toFixed(2)}</span>
                                <div class="menu-desc">${descriptions[item.category] || 'Specialità del locale.'}</div>
                            </div>
                        `;
                        content.appendChild(div);
                    });

                    wrapper.appendChild(header);
                    wrapper.appendChild(content);
                    menuList.appendChild(wrapper);
                });
            } catch (error) {
                document.getElementById('menu-list').innerHTML = '<div class="panel">Errore nel caricamento del menu</div>';
            }
        }

        loadMenuView();
    </script>
    """
    return shell_page("Menu", body)


@app.get("/admin", response_class=HTMLResponse)
def admin():
    return """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Menu</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(180deg, #ff7a00, #ffae42);
                margin: 0;
                padding: 24px 14px;
            }
            .container {
                max-width: 700px;
                margin: 0 auto;
            }
            .admin-box {
                background: rgba(255,255,255,0.97);
                border-radius: 28px;
                padding: 24px;
                box-shadow: 0 18px 40px rgba(0,0,0,0.14);
            }
            .simple-logo {
                width: min(220px, 72vw);
                max-height: 90px;
                object-fit: contain;
                display: block;
                margin: 0 auto 16px auto;
            }
            h1, h2 {
                color: #ff6b00;
            }
            input, button {
                width: 100%;
                padding: 14px;
                margin-top: 10px;
                box-sizing: border-box;
                border-radius: 14px;
                border: 1px solid #ddd;
                font-size: 15px;
            }
            button {
                background: linear-gradient(135deg, #ff6b00, #e45c00);
                color: white;
                border: none;
                font-weight: 900;
                cursor: pointer;
            }
            .item {
                padding: 12px 0;
                border-bottom: 1px solid #eee;
            }
            a {
                text-decoration: none;
                color: #333;
                font-weight: 800;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="admin-box">
                <a href="/">← Torna alla home</a>
                <img src="/static/logo.png" alt="ECOMORA" class="simple-logo">
                <h1>Admin Menu</h1>

                <h2>Aggiungi prodotto</h2>
                <input id="name" placeholder="Nome prodotto">
                <input id="category" placeholder="Categoria">
                <input id="price" placeholder="Prezzo">
                <button onclick="addItem()">Aggiungi</button>

                <h2>Menu attuale</h2>
                <div id="menu"></div>
            </div>
        </div>

        <script>
            async function loadMenu() {
                const res = await fetch('/menu');
                const data = await res.json();

                let html = '';
                data.forEach(i => {
                    html += `<div class="item"><b>${i.name}</b> - ${i.category} - €${i.price}</div>`;
                });

                document.getElementById('menu').innerHTML = html;
            }

            async function addItem() {
                const name = document.getElementById('name').value;
                const category = document.getElementById('category').value;
                const price = document.getElementById('price').value;

                const res = await fetch('/add-item', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ name, category, price })
                });

                const result = await res.json();

                if (!res.ok) {
                    alert(result.detail || 'Errore');
                    return;
                }

                document.getElementById('name').value = '';
                document.getElementById('category').value = '';
                document.getElementById('price').value = '';
                loadMenu();
            }

            loadMenu();
        </script>
    </body>
    </html>
    """


@app.get("/orders-view", response_class=HTMLResponse)
def orders_view():
    with closing(get_connection()) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM orders ORDER BY id DESC")
        orders = cursor.fetchall()

    html = """
    <!DOCTYPE html>
    <html lang="it">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ordini</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                background: linear-gradient(180deg, #ff7a00, #ffae42);
                padding: 24px 14px;
                margin: 0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
            }
            .orders-box {
                background: rgba(255,255,255,0.97);
                border-radius: 28px;
                padding: 24px;
                box-shadow: 0 18px 40px rgba(0,0,0,0.14);
            }
            .simple-logo {
                width: min(220px, 72vw);
                max-height: 90px;
                object-fit: contain;
                display: block;
                margin: 0 auto 16px auto;
            }
            .order-card {
                background: white;
                border-radius: 18px;
                padding: 16px;
                margin-bottom: 14px;
                box-shadow: 0 8px 20px rgba(0,0,0,0.08);
            }
            a {
                text-decoration: none;
                color: #333;
                font-weight: 800;
            }
            h1 {
                color: #ff6b00;
                text-align: center;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="orders-box">
                <a href="/">← Torna alla home</a>
                <img src="/static/logo.png" alt="ECOMORA" class="simple-logo">
                <h1>Ordini ricevuti</h1>
    """

    for o in orders:
        html += f"""
            <div class="order-card">
                <b>Ordine #{o['id']}</b><br>
                Nome: {o['customer_name']}<br>
                Telefono: {o['phone']}<br>
                Tipo: {o['order_type']}<br>
                Totale: €{o['total']}<br>
                Stato: {o['status']}<br>
                Orario richiesto: {o['requested_time'] or '-'}<br>
                Note: {o['notes'] or '-'}
            </div>
        """

    html += """
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html)
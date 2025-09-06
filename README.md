EcoFinds – Sustainable Second-Hand Marketplace

A foundational MVP for EcoFinds, a platform designed to empower sustainable consumption by enabling users to buy and sell pre-owned goods.
This prototype was built during the Odoo Hackathon 2025 (First Round), focusing on database design, API development, and a clean user experience.

🎯 Problem Statement

Develop a functional prototype that allows users to:

Register & log in (secure authentication).

Create and manage product listings (CRUD).

Browse products with filtering and search.

View detailed product pages.

Add products to cart & view previous purchases.

Edit basic user profile details via dashboard.

✨ Features Implemented

Authentication: Email + password login/signup.

Profile Management: Basic username & editable profile fields.

Product Listings: CRUD operations with title, description, category, price, image placeholder.

Browsing:

Category filter (dropdown).

Keyword search in product titles.

Product Detail View: Title, price, category, description, image placeholder.

Cart: Add & view items before checkout.

Previous Purchases: History of bought items.

Validations: Robust input validation for email, missing fields, invalid price, etc.

🛠️ Tech Stack

Backend: Python (Flask / FastAPI)

Database: MySQL / PostgreSQL (normalized schema)

Frontend: HTML + CSS (Bootstrap) / React

Version Control: Git + GitHub

📂 Project Structure
ecofinds/
├── backend/
│   ├── app.py          # Main API entry
│   ├── models.py       # Database models
│   ├── routes/         # API routes
│   └── db.py           # Database connection
├── frontend/
│   ├── index.html
│   ├── static/
│   └── components/
├── docs/
│   ├── ERD.png         # Entity Relationship Diagram
│   └── API_Documentation.md
└── README.md

📊 Database Design (ERD)

Entities:

User (id, name, email, password, created_at)

Product (id, user_id, title, description, category, price, image, created_at)

Cart (id, user_id, product_id, quantity)

Purchase (id, user_id, product_id, purchased_at)

(Insert ERD diagram here → /docs/ERD.png)

🔑 API Endpoints (Sample)
Auth

POST /api/auth/signup → Register new user

POST /api/auth/login → Login user

Products

POST /api/products → Create new listing

GET /api/products → Browse all products (with filters/search)

GET /api/products/:id → View product detail

PUT /api/products/:id → Update listing

DELETE /api/products/:id → Delete listing

Cart

POST /api/cart/add → Add product to cart

GET /api/cart → View cart items

Purchases

GET /api/purchases → View purchase history

🖥️ Getting Started
Prerequisites

Python 3.10+

MySQL or PostgreSQL

Setup
# Clone repo
git clone https://github.com/username/ecofinds.git
cd ecofinds

# Setup backend
cd backend
pip install -r requirements.txt

# Setup database
mysql -u root -p < schema.sql

# Run server
python app.py


Open frontend at http://localhost:3000

🚀 Future Improvements

JWT authentication

Product images (file upload)

Payment gateway integration

Recommendations system (AI-powered)

Mobile-first responsive design

🙌 Acknowledgements

Developed  by NetRunners during Odoo Hackathon 2025 – First Round (Virtual).

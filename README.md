# ApexBank - Modern Classic Django MySQL Banking Web Application

A secure, enterprise-grade banking web application developed with **Django**, **MySQL**, and modern classic frontend design (**HTML5, Vanilla CSS3, Vanilla JavaScript**).

---

## 🏛️ Core Features

1. **Secure Customer Registration & Mandatory KYC**:
   - Captures **PAN Number** with strict regex validation (`[A-Z]{5}[0-9]{4}[A-Z]{1}`) and uniqueness enforcement.
   - Captures **12-digit Indian Aadhar Number** with uniqueness enforcement.
   - Auto-generates a unique 12-digit Bank Account Number (e.g. `6010XXXXXXXX`).
   - Secure authentication supporting sign in via **Username** or direct **Bank Account Number**.

2. **Customer Banking Portal**:
   - **Balance & Liquidity**: Real-time balance and interactive account card display.
   - **Cash Withdrawals**: Immediate self-withdrawal with balance verification and atomic row locking (`select_for_update`).
   - **Peer-to-Peer Inter-Account Transfers**: Live recipient lookup via AJAX, duplicate transfer prevention, and deadlock-free atomic debit/credit operations.
   - **Official Statements**: Searchable and filterable statements categorized by deposits, withdrawals, and peer transfers.
   - **KYC & Profile View**: Masked display of sensitive KYC credentials (`XXXXX1234F` / `XXXX-XXXX-1234`).

3. **Admin Banking Console (Admin Only)**:
   - Complete ledger and customer directory showing:
     - Account Number
     - Customer Name, Email, and Phone
     - **Full PAN Card Number**
     - **Full Aadhar Number**
     - Account Creation Timestamp
     - Real-Time Balance
   - **Exclusive Cash Deposit**: Only Admin accounts are permitted to deposit funds. Depositing money to Account 1 credits strictly and exclusively Account 1.
   - **Account Audit Ledger**: Comprehensive view of every transaction flow initiated or received by any account.

4. **Modern Classic UI**:
   - Refined palette: Midnight Navy (`#0a0e17`), Slate Card Layering, and Brushed Gold (`#c5a059`).
   - Elegant typography pairing: *Cinzel*, *Playfair Display*, and *Inter*.

---

## 🗄️ Database Setup (MySQL)

### Step 1: Create Database
Open your MySQL CLI, phpMyAdmin, or MySQL Workbench and run:
```sql
CREATE DATABASE IF NOT EXISTS apex_bank_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```
*(You can also execute the included [db_setup.sql](db_setup.sql) script).*

### Step 2: Configure Environment (.env)
Edit `.env` in the project root:
```env
SECRET_KEY=your-secure-secret-key
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

DB_ENGINE=mysql
DB_NAME=apex_bank_db
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```
*(Note: If you do not have MySQL running right now, set `DB_ENGINE=sqlite3` for instant local testing!)*

---

## 🚀 Installation & Running the Application

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow prompts to create your Admin user (e.g., username `admin`).

### 4. Start the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser.

---

## 🔒 Transaction Safety & Concurrency
All financial balance mutations (Deposits, Withdrawals, Transfers) are guarded with:
- `django.db.transaction.atomic` blocks to ensure all-or-nothing execution.
- `select_for_update()` row-level locks sorted by primary key to prevent race conditions and multi-account deadlocks.

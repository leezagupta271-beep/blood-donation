# Blood Donation System - Setup Instructions

Follow these steps to set up and run your full-stack Blood Donation application:

## 1. Prerequisites
Make sure you have installed:
- Python 3.x
- MySQL Server

## 2. Database Setup
1. Open your MySQL client (e.g., MySQL Workbench or via terminal: `mysql -u root -p`).
2. Run the provided `database.sql` script to create the database schema, tables, and insert sample data.
   Alternatively, run this command in terminal (assuming you are in this directory):
   ```bash
   mysql -u root -p < database.sql
   ```
3. Look at line 11 in `app.py` and ensure the MySQL URI matches your local credentials. The default is set to `root` with no password:
   `app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/blood_donation'`
   Change it to `root:YOURPASSWORD@localhost` if you have a MySQL password.

## 3. Install Dependencies
Open a terminal in this current directory (`blood_donation_app`) and install the required Python packages:

```bash
pip install -r requirements.txt
```

## 4. Run the Application
Start the Flask application by running:

```bash
python app.py
```

The application will start on `http://localhost:5000/`.

## 5. Usage Tips
- **Home/Camps:** Anyone can view upcoming camps and blood stock details.
- **Donor:** Register an account to become a Donor. Once logged in, you can register for camps.
- **Admin:** Built-in admin account credentials from `database.sql`:
  - **Email:** `admin@blooddonate.com`
  - **Password:** `admin123`
  - *Login with this to access the Admin panel to view overall system stats.*

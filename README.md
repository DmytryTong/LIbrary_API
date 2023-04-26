# 📚Library DRF API📚

API service for management library in DRF

## 🌍Installing using GitHub:
```
git clone https://github.com/DmytryTong/LIbrary_API.git
python -m venv venv
venv\Scripts\activate (on Windows)
source venv/bin/activate (on macOS)
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py qcluster
python manage.py runserver
```

**✍️Add your environment variables to .env**
- TELEGRAM_CHAT_ID="Chat id where your telegram bot should send notifications"
- TELEGRAM_BOT_TOKEN="The token of the bot you will use"
- STRIPE_PUBLIC_KEY="Your public key for Stripe payment service"
- STRIPE_API_KEY="Your API key for Stripe payment service"
- SECRET_KEY="Secret key for your service"

**✍️Add schedule task for Django Q in admin panel**

## 👋Getting access for users
- create user vis /api/user/register/
- get access token via /api/user/token/

## 🌌Components
- Books Service Managing books amount (CRUD for Books)
- Users Service Managing authentication & user registration
- Borrowings Service Managing users' borrowings of books
- Notifications Service (Telegram) Notifications about new borrowing created, </br>borrowings overdue & successful payment. In parallel cluster/process </br>(Django Q package used). Other services interact with it to send

## 🌟Features:
- JWT authenticated
- Admin panel /admin/
- Documentation is located at /api/doc/swagger/
- Create books with authors and daily fee for admins
- Create books borrowings for users
- Web-based
- Manage books inventory
- Manage books borrowing
- Manage customers
- Display notifications
- Handle payments
- Filtering borrowings

## 👀Images

![Screenshot 2023-04-26 155217.png](demo%2FScreenshot%202023-04-26%20155217.png)
![Screenshot 2023-04-26 155245.png](demo%2FScreenshot%202023-04-26%20155245.png)
![Screenshot 2023-04-26 155319.png](demo%2FScreenshot%202023-04-26%20155319.png)
![Screenshot 2023-04-26 155411.png](demo%2FScreenshot%202023-04-26%20155411.png)

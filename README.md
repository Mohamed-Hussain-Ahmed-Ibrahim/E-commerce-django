# E-Commerce Store

A professional e-commerce website built with Django, featuring a modern UI and comprehensive functionality.

## Features

- User authentication and profile management
- Product catalog with categories
- Shopping cart functionality
- Secure checkout with Stripe integration
- Order management system
- Responsive design using Bootstrap 5
- Admin interface for managing products, orders, and users

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ecommerce.git
cd ecommerce
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root and add your environment variables:
```
DJANGO_SECRET_KEY=your-secret-key
DEBUG=True
STRIPE_PUBLIC_KEY=your-stripe-public-key
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Create a superuser:
```bash
python manage.py createsuperuser
```

7. Run the development server:
```bash
python manage.py runserver
```

## Usage

1. Access the admin interface at `http://localhost:8000/admin/` to manage:
   - Products and categories
   - User accounts
   - Orders and payments

2. Visit `http://localhost:8000` to browse the store as a customer:
   - Browse products by category
   - Add items to cart
   - Complete checkout process
   - View order history

## Project Structure

```
ecommerce/
├── ecommerce/          # Project settings
├── store/              # Store app (products, cart, orders)
├── users/              # User management app
├── templates/          # HTML templates
├── static/             # Static files (CSS, JS, images)
├── media/             # User-uploaded files
├── requirements.txt   # Project dependencies
└── manage.py         # Django management script
```

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
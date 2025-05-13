# Coderr Backend

Coderr is a backend project built with Django, designed to manage users, offers, orders, reviews, and file uploads. This project provides APIs for handling business and customer interactions, including creating offers, managing orders, and submitting reviews.

## Features

- **User Management**:

  - Business and customer user profiles.
  - Authentication using Django Rest Framework's token-based authentication.

- **Offers and Orders**:

  - Business users can create offers with multiple details.
  - Customers can place orders based on offer details.

- **Reviews**:

  - Customers can leave reviews for business users.
  - Reviews include ratings and descriptions.

- **File Uploads**:

  - API for uploading and managing files.

- **Statistics**:
  - API to retrieve platform statistics, such as the number of reviews, average ratings, and total offers.

---

## Project Structure

backend/
├── base_info_app/ # Handles platform statistics
├── core/ # Core Django settings and configurations
├── offers_orders_app/ # Manages offers, offer details, and orders
├── reviews_app/ # Handles reviews and ratings
├── upload_app/ # File upload functionality
├── users_auth_app/ # User authentication and profiles
├── utils/ # Utility functions and helpers

## Installation

1. **Clone the repository**

   ```bash
   git clone <https://github.com/LauraHexx/Coderr_Backend.git>
   cd backend

   ```

2. **Set up a virtual environment**
   python -m venv venv
   source venv/bin/activate # On Windows: venv\Scripts\activate

3. **Install dependencies**
   pip install -r requirements.txt

4. **Apply migrations**
   python manage.py makemigrations
   python manage.py migrate

5. **Create a superuser**
   python manage.py createsuperuser

6. **Create a superuser**
   python manage.py runserver

## Development Workflow

1. **Set up the development environment**:
   Follow the installation steps above to set up the project locally.

2. **Run tests**:
   Use the following command to run the test suite:
   ```bash
   python manage.py test
   ```

from rest_framework.authtoken.models import Token
from users_auth_app.models import User, UserProfile
from offers_orders_app.models import Offer, OfferDetail
from reviews_app.models import Review

# Lösche bestehende Daten
User.objects.all().delete()
UserProfile.objects.all().delete()
Offer.objects.all().delete()
OfferDetail.objects.all().delete()
Review.objects.all().delete()

# Dummy-Daten für Benutzer
business_users_data = [
    {"username": "julia schneider", "email": "julia.schneider@example.com", "first_name": "Julia", "last_name": "Schneider",
        "location": "Berlin", "tel": "030123456", "description": "Grafikdesignerin für individuelle Lösungen.", "working_hours": "09:00 - 17:00"},
    {"username": "daniel mueller", "email": "daniel.mueller@example.com", "first_name": "Daniel", "last_name": "Müller",
        "location": "Hamburg", "tel": "040987654", "description": "Webdesigner für responsive Webseiten.", "working_hours": "10:00 - 18:00"},
    {"username": "lena krause", "email": "lena.krause@example.com", "first_name": "Lena", "last_name": "Krause", "location": "München",
        "tel": "089112233", "description": "Fotografin für Events und Hochzeiten.", "working_hours": "08:00 - 16:00"},
]

customer_users_data = [
    {"username": "anna schmidt", "email": "anna.schmidt@example.com",
        "first_name": "Anna", "last_name": "Schmidt"},
    {"username": "jonas maier", "email": "jonas.maier@example.com",
        "first_name": "Jonas", "last_name": "Maier"},
]

# Erstelle Business-Benutzer
business_users = []
for user_data in business_users_data:
    user, _ = User.objects.get_or_create(
        username=user_data["username"], email=user_data["email"], first_name=user_data["first_name"], last_name=user_data["last_name"])
    user.set_password("password123")
    user.save()
    profile = UserProfile.objects.create(
        user=user,
        type="business",
        location=user_data["location"],
        tel=user_data["tel"],
        description=user_data["description"],
        working_hours=user_data["working_hours"]
    )
    Token.objects.get_or_create(user=user)
    business_users.append(user)

# Erstelle Kunden-Benutzer
customer_users = []
for user_data in customer_users_data:
    user, _ = User.objects.get_or_create(
        username=user_data["username"], email=user_data["email"], first_name=user_data["first_name"], last_name=user_data["last_name"])
    user.set_password("password123")
    user.save()
    UserProfile.objects.create(user=user, type="customer")
    Token.objects.get_or_create(user=user)
    customer_users.append(user)

# Dummy-Daten für Angebote
offers_data = [
    {
        "title": "Graphic Design Package",
        "description": "A complete graphic design package for businesses.",
        "details": [
            {"title": "Basic Design", "revisions": 2, "delivery_time_in_days": 5, "price": 100,
                "features": ["Logo Design", "Business Card"], "offer_type": "basic"},
            {"title": "Standard Design", "revisions": 5, "delivery_time_in_days": 7, "price": 200,
                "features": ["Logo Design", "Business Card", "Letterhead"], "offer_type": "standard"},
        ]
    },
    {
        "title": "Social Media Branding",
        "description": "Custom branding assets for all major social platforms.",
        "details": [
            {"title": "Basic Branding", "revisions": 2, "delivery_time_in_days": 4, "price": 80,
                "features": ["Profile Picture", "Cover Photo"], "offer_type": "basic"},
        ]
    }
]

# Erstelle Angebote und Details
for profile in business_users:
    for offer_data in offers_data:
        offer, _ = Offer.objects.get_or_create(
            user=profile,
            title=offer_data["title"],
            description=offer_data["description"]
        )
        for detail in offer_data["details"]:
            OfferDetail.objects.get_or_create(
                offer=offer,
                title=detail["title"],
                offer_type=detail["offer_type"],
                revisions=detail["revisions"],
                delivery_time_in_days=detail["delivery_time_in_days"],
                price=detail["price"],
                features=detail["features"]
            )

# Dummy-Daten für Bewertungen
reviews_data = [
    {"business_user": business_users[0], "reviewer": customer_users[0],
        "rating": 4, "description": "Sehr professioneller Service."},
    {"business_user": business_users[1], "reviewer": customer_users[0],
        "rating": 5, "description": "Top Qualität und schnelle Lieferung!"},
]

# Erstelle Bewertungen
for review_data in reviews_data:
    Review.objects.get_or_create(
        business_user=review_data["business_user"],
        reviewer=review_data["reviewer"],
        defaults={
            "rating": review_data["rating"],
            "description": review_data["description"]
        }
    )

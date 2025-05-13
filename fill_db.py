from rest_framework.authtoken.models import Token
from users_auth_app.models import User, UserProfile
from offers_orders_app.models import Offer, OfferDetail, Order
from reviews_app.models import Review
import random

# Lösche alle bestehenden Daten
User.objects.all().delete()
UserProfile.objects.all().delete()
Offer.objects.all().delete()
OfferDetail.objects.all().delete()
Review.objects.all().delete()
Order.objects.all().delete()


def random_rating():
    return random.randint(1, 5)


def random_description():
    descriptions = [
        "Excellent service!", "Very professional.", "Highly recommended.",
        "Good quality work.", "Fast and reliable.", "Would hire again.",
        "Outstanding experience!", "Great attention to detail."
    ]
    return random.choice(descriptions)


business_users = []
for i in range(1, 8):
    user = User.objects.create_user(
        username=f"business_user_{i}",
        email=f"business_user_{i}@example.com",
        first_name=f"Business{i}",
        last_name="User",
        password="password123"
    )
    UserProfile.objects.create(
        user=user,
        type="business",
        location=f"City {i}",
        tel=f"012345678{i}",
        description=f"Business description {i}",
        working_hours="09:00 - 17:00"
    )
    Token.objects.create(user=user)
    business_users.append(user)

customer_users = []
for i in range(1, 8):
    user = User.objects.create_user(
        username=f"customer_user_{i}",
        email=f"customer_user_{i}@example.com",
        first_name=f"Customer{i}",
        last_name="User",
        password="password123"
    )
    UserProfile.objects.create(
        user=user,
        type="customer",
        tel=f"098765432{i}",
        description=f"Customer description {i}"
    )
    Token.objects.create(user=user)
    customer_users.append(user)

for business_user in business_users:
    offer_count = random.randint(2, 3)
    for j in range(offer_count):
        offer = Offer.objects.create(
            user=business_user,
            title=f"Offer {j + 1} by {business_user.username}",
            description=f"Description for offer {j + 1} by {business_user.username}"
        )
        offer_types = ["basic", "standard", "premium"]
        for k, offer_type in enumerate(offer_types):
            OfferDetail.objects.create(
                offer=offer,
                title=f"Detail {k + 1} for {offer.title}",
                revisions=random.randint(1, 5),
                delivery_time_in_days=random.randint(1, 10),
                price=round(random.uniform(50, 500), 2),
                features=["Feature A", "Feature B", "Feature C"],
                offer_type=offer_type
            )

for business_user in business_users:
    review_count = random.randint(3, 4)
    for _ in range(review_count):
        reviewer = random.choice(customer_users)
        if not Review.objects.filter(business_user=business_user, reviewer=reviewer).exists():
            Review.objects.create(
                business_user=business_user,
                reviewer=reviewer,
                rating=random_rating(),
                description=random_description()
            )

for customer_user in customer_users:
    review_count = random.randint(3, 4)
    for _ in range(review_count):
        business_user = random.choice(business_users)
        if not Review.objects.filter(business_user=business_user, reviewer=customer_user).exists():
            Review.objects.create(
                business_user=business_user,
                reviewer=customer_user,
                rating=random_rating(),
                description=random_description()
            )

for customer_user in customer_users:
    for _ in range(random.randint(2, 4)):
        business_user = random.choice(business_users)
        offer_detail = OfferDetail.objects.filter(
            offer__user=business_user).order_by("?").first()
        if offer_detail:
            Order.objects.create(
                customer_user=customer_user,
                business_user=business_user,
                offer_detail=offer_detail,
                status=random.choice(["in_progress", "completed", "cancelled"])
            )

print("Database successfully populated with unique test data!")

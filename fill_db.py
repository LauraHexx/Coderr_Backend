from rest_framework.authtoken.models import Token
from users_auth_app.models import User, UserProfile

User.objects.all().delete()
UserProfile.objects.all().delete()

# Erstellen der Business-Nutzer:innen
user1, _ = User.objects.get_or_create(
    username='julia schneider', email='julia.schneider@example.com', first_name='Julia', last_name='Schneider')
user1.set_password('password123')
user1.save()
UserProfile.objects.create(
    user=user1, type='business', location='Berlin', tel='030123456', description='Grafikdesignerin für individuelle Lösungen.',
    working_hours='09:00 - 17:00'
)
Token.objects.create(user=user1)

user2, _ = User.objects.get_or_create(
    username='daniel mueller', email='daniel.mueller@example.com', first_name='Daniel', last_name='Müller')
user2.set_password('password123')
user2.save()
UserProfile.objects.create(
    user=user2, type='business', location='Hamburg', tel='040987654', description='Webdesigner für responsive Webseiten.',
    working_hours='10:00 - 18:00'
)
Token.objects.create(user=user2)

user3, _ = User.objects.get_or_create(
    username='lena krause', email='lena.krause@example.com', first_name='Lena', last_name='Krause')
user3.set_password('password123')
user3.save()
UserProfile.objects.create(
    user=user3, type='business', location='München', tel='089112233', description='Fotografin für Events und Hochzeiten.',
    working_hours='08:00 - 16:00'
)
Token.objects.create(user=user3)

user4, _ = User.objects.get_or_create(
    username='marco schulz', email='marco.schulz@example.com', first_name='Marco', last_name='Schulz')
user4.set_password('password123')
user4.save()
UserProfile.objects.create(
    user=user4, type='business', location='Köln', tel='022145678', description='Social Media Marketing Experte.',
    working_hours='11:00 - 19:00'
)
Token.objects.create(user=user4)

user5, _ = User.objects.get_or_create(
    username='sophie meier', email='sophie.meier@example.com', first_name='Sophie', last_name='Meier')
user5.set_password('password123')
user5.save()
UserProfile.objects.create(
    user=user5, type='business', location='Stuttgart', tel='0711999888', description='SEO-Expertin für organisches Wachstum.',
    working_hours='08:30 - 16:30'
)
Token.objects.create(user=user5)

user6, _ = User.objects.get_or_create(
    username='maximilian wagner', email='maximilian.wagner@example.com', first_name='Maximilian', last_name='Wagner')
user6.set_password('password123')
user6.save()
UserProfile.objects.create(
    user=user6, type='business', location='Frankfurt', tel='069987654', description='Experte für Webentwicklung.',
    working_hours='09:00 - 17:00'
)
Token.objects.create(user=user6)

user7, _ = User.objects.get_or_create(
    username='anna becker', email='anna.becker@example.com', first_name='Anna', last_name='Becker')
user7.set_password('password123')
user7.save()
UserProfile.objects.create(
    user=user7, type='business', location='Düsseldorf', tel='0211456789', description='Content Marketing Spezialistin.',
    working_hours='09:00 - 18:00'
)
Token.objects.create(user=user7)

user8, _ = User.objects.get_or_create(
    username='felix schuster', email='felix.schuster@example.com', first_name='Felix', last_name='Schuster')
user8.set_password('password123')
user8.save()
UserProfile.objects.create(
    user=user8, type='business', location='Leipzig', tel='0341456798', description='Berater für Unternehmenskommunikation.',
    working_hours='10:00 - 16:00'
)
Token.objects.create(user=user8)

user9, _ = User.objects.get_or_create(
    username='maria lange', email='maria.lange@example.com', first_name='Maria', last_name='Lange')
user9.set_password('password123')
user9.save()
UserProfile.objects.create(
    user=user9, type='business', location='Bremen', tel='0421456789', description='Design- und Branding-Expertin.',
    working_hours='09:00 - 17:00'
)
Token.objects.create(user=user9)

user10, _ = User.objects.get_or_create(
    username='julian fischer', email='julian.fischer@example.com', first_name='Julian', last_name='Fischer')
user10.set_password('password123')
user10.save()
UserProfile.objects.create(
    user=user10, type='business', location='Hannover', tel='0511456789', description='Spezialist für Video-Produktion.',
    working_hours='09:00 - 18:00'
)
Token.objects.create(user=user10)

# Erstellen der Customer-Nutzer:innen
user11, _ = User.objects.get_or_create(
    username='anna schmidt', email='anna.schmidt@example.com', first_name='Anna', last_name='Schmidt')
user11.set_password('password123')
user11.save()
UserProfile.objects.create(
    user=user11, type='customer'
)
Token.objects.create(user=user11)

user12, _ = User.objects.get_or_create(
    username='jonas maier', email='jonas.maier@example.com', first_name='Jonas', last_name='Maier')
user12.set_password('password123')
user12.save()
UserProfile.objects.create(
    user=user12, type='customer'
)
Token.objects.create(user=user12)

user13, _ = User.objects.get_or_create(
    username='felix hartmann', email='felix.hartmann@example.com', first_name='Felix', last_name='Hartmann')
user13.set_password('password123')
user13.save()
UserProfile.objects.create(
    user=user13, type='customer'
)
Token.objects.create(user=user13)

user14, _ = User.objects.get_or_create(
    username='mia keller', email='mia.keller@example.com', first_name='Mia', last_name='Keller')
user14.set_password('password123')
user14.save()
UserProfile.objects.create(
    user=user14, type='customer'
)
Token.objects.create(user=user14)

user15, _ = User.objects.get_or_create(
    username='lena frank', email='lena.frank@example.com', first_name='Lena', last_name='Frank')
user15.set_password('password123')
user15.save()
UserProfile.objects.create(
    user=user15, type='customer'
)
Token.objects.create(user=user15)

user16, _ = User.objects.get_or_create(
    username='tim schulz', email='tim.schulz@example.com', first_name='Tim', last_name='Schulz')
user16.set_password('password123')
user16.save()
UserProfile.objects.create(
    user=user16, type='customer'
)
Token.objects.create(user=user16)

user17, _ = User.objects.get_or_create(
    username='paul wagner', email='paul.wagner@example.com', first_name='Paul', last_name='Wagner')
user17.set_password('password123')
user17.save()
UserProfile.objects.create(
    user=user17, type='customer'
)
Token.objects.create(user=user17)

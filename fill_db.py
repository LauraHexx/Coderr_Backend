# Leeren der relevanten Tabellen zu Beginn
# Offer.objects.all().delete()
# OfferDetail.objects.all().delete()
#
# Erstellen von 5 Beispieldaten für Angebote
#
# Erstelle User (falls sie noch nicht existieren)
# user1, _ = User.objects.get_or_create(username='alice', is_staff=True)
# user1.set_password('asdasd')
# user1.save()
#
# user2, _ = User.objects.get_or_create(username='bob')
# user2.set_password('asdasd')
# user2.save()
#
# user3, _ = User.objects.get_or_create(username='charlie')
# user3.set_password('asdasd')
# user3.save()
#
# user4, _ = User.objects.get_or_create(username='dave')
# user4.set_password('asdasd')
# user4.save()
#
# Beispiel-Angebote erstellen
# offer1 = Offer.objects.create(
#    user=user1,
#    title="Grafikdesign-Paket 1",
#    image=None,
#    description="Ein umfassendes Grafikdesign-Paket für Unternehmen.",
# )
#
# Angebot 1 Details
# OfferDetail.objects.create(
#    offer=offer1,
#    title="Basic Design",
#    revisions=2,
#    delivery_time_in_days=5,
#    price=100,
#    offer_type="basic",
#    features=["Logo Design", "Visitenkarte"]
# )
# OfferDetail.objects.create(
#    offer=offer1,
#    title="Standard Design",
#    revisions=5,
#    delivery_time_in_days=7,
#    price=200,
#    offer_type="standard",
#    features=["Logo Design", "Visitenkarte", "Briefpapier"]
# )
# OfferDetail.objects.create(
#    offer=offer1,
#    title="Premium Design",
#    revisions=10,
#    delivery_time_in_days=10,
#    price=500,
#    offer_type="premium",
#    features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"]
# )
#
# offer2 = Offer.objects.create(
#    user=user2,
#    title="Grafikdesign-Paket 2",
#    image=None,
#    description="Ein umfassendes Grafikdesign-Paket für Unternehmen.",
# )
#
# Angebot 2 Details
# OfferDetail.objects.create(
#    offer=offer2,
#    title="Basic Design",
#    revisions=2,
#    delivery_time_in_days=5,
#    price=120,
#    offer_type="basic",
#    features=["Logo Design", "Visitenkarte"]
# )
# OfferDetail.objects.create(
#    offer=offer2,
#    title="Standard Design",
#    revisions=5,
#    delivery_time_in_days=8,
#    price=250,
#    offer_type="standard",
#    features=["Logo Design", "Visitenkarte", "Briefpapier"]
# )
# OfferDetail.objects.create(
#    offer=offer2,
#    title="Premium Design",
#    revisions=12,
#    delivery_time_in_days=12,
#    price=550,
#    offer_type="premium",
#    features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer", "Plakat"]
# )
#
# offer3 = Offer.objects.create(
#    user=user3,
#    title="Grafikdesign-Paket 3",
#    image=None,
#    description="Ein umfassendes Grafikdesign-Paket für Unternehmen.",
# )
#
# Angebot 3 Details
# OfferDetail.objects.create(
#    offer=offer3,
#    title="Basic Design",
#    revisions=3,
#    delivery_time_in_days=6,
#    price=130,
#    offer_type="basic",
#    features=["Logo Design", "Visitenkarte"]
# )
# OfferDetail.objects.create(
#    offer=offer3,
#    title="Standard Design",
#    revisions=6,
#    delivery_time_in_days=9,
#    price=280,
#    offer_type="standard",
#    features=["Logo Design", "Visitenkarte", "Briefpapier"]
# )
# OfferDetail.objects.create(
#    offer=offer3,
#    title="Premium Design",
#    revisions=15,
#    delivery_time_in_days=14,
#    price=600,
#    offer_type="premium",
#    features=["Logo Design", "Visitenkarte",
#              "Briefpapier", "Flyer", "Plakat", "Website"]
# )
#
# offer4 = Offer.objects.create(
#    user=user4,
#    title="Grafikdesign-Paket 4",
#    image=None,
#    description="Ein umfassendes Grafikdesign-Paket für Unternehmen.",
# )
#
# Angebot 4 Details
# OfferDetail.objects.create(
#    offer=offer4,
#    title="Basic Design",
#    revisions=4,
#    delivery_time_in_days=7,
#    price=150,
#    offer_type="basic",
#    features=["Logo Design", "Visitenkarte"]
# )
# OfferDetail.objects.create(
#    offer=offer4,
#    title="Standard Design",
#    revisions=7,
#    delivery_time_in_days=10,
#    price=300,
#    offer_type="standard",
#    features=["Logo Design", "Visitenkarte", "Briefpapier"]
# )
# OfferDetail.objects.create(
#    offer=offer4,
#    title="Premium Design",
#    revisions=18,
#    delivery_time_in_days=15,
#    price=700,
#    offer_type="premium",
#    features=["Logo Design", "Visitenkarte",
#              "Briefpapier", "Flyer", "Plakat", "Website"]
# )
#
# offer5 = Offer.objects.create(
#    user=user1,
#    title="Grafikdesign-Paket 5",
#    image=None,
#    description="Ein umfassendes Grafikdesign-Paket für Unternehmen.",
# )
#
# Angebot 5 Details
# OfferDetail.objects.create(
#    offer=offer5,
#    title="Basic Design",
#    revisions=1,
#    delivery_time_in_days=4,
#    price=90,
#    offer_type="basic",
#    features=["Logo Design", "Visitenkarte"]
# )
# OfferDetail.objects.create(
#    offer=offer5,
#    title="Standard Design",
#    revisions=4,
#    delivery_time_in_days=6,
#    price=180,
#    offer_type="standard",
#    features=["Logo Design", "Visitenkarte", "Briefpapier"]
# )
# OfferDetail.objects.create(
#    offer=offer5,
#    title="Premium Design",
#    revisions=8,
#    delivery_time_in_days=12,
#    price=450,
#    offer_type="premium",
#    features=["Logo Design", "Visitenkarte", "Briefpapier", "Flyer"]
# )
#

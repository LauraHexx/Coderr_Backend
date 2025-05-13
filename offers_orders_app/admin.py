from django.contrib import admin

# Register your models here.

from .models import Offer, OfferDetail, Order

admin.site.register(Offer)
admin.site.register(OfferDetail)
admin.site.register(Order)

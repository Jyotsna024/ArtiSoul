from django.contrib import admin
from .models import Profile,Workshop,Enrollment,Product,Order,OrderItem,Event,Ticket,Certificate
for m in [Profile,Workshop,Enrollment,Product,Order,OrderItem,Event,Ticket,Certificate]:admin.site.register(m)

import uuid
from django.conf import settings
from django.db import models

class Profile(models.Model):
 ROLES=[(x,x.title()) for x in ['learner','artisan','artist','buyer','admin']]
 user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='profile')
 role=models.CharField(max_length=16,choices=ROLES,default='learner',db_index=True)
 bio=models.TextField(blank=True);region=models.CharField(max_length=80,blank=True);interests=models.JSONField(default=list,blank=True);verified=models.BooleanField(default=False)
 created_at=models.DateTimeField(auto_now_add=True)

class Workshop(models.Model):
 title=models.CharField(max_length=180);instructor=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='workshops')
 category=models.CharField(max_length=60,db_index=True);description=models.TextField();level=models.CharField(max_length=40,default='All levels')
 language=models.CharField(max_length=40,default='English');mode=models.CharField(max_length=12,choices=[('live','Live'),('recorded','Recorded'),('hybrid','Hybrid')],default='live')
 duration=models.CharField(max_length=40,default='4 weeks');sessions=models.PositiveSmallIntegerField(default=4);price=models.DecimalField(max_digits=9,decimal_places=2,default=0)
 seats=models.PositiveIntegerField(default=20);starts_at=models.DateTimeField(null=True,blank=True);image_url=models.URLField(blank=True);published=models.BooleanField(default=True);created_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['starts_at','title'];indexes=[models.Index(fields=['category','published'])]

class Enrollment(models.Model):
 learner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='enrollments');workshop=models.ForeignKey(Workshop,on_delete=models.CASCADE,related_name='enrollments')
 status=models.CharField(max_length=16,default='active');progress=models.PositiveSmallIntegerField(default=0);enrolled_at=models.DateTimeField(auto_now_add=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['learner','workshop'],name='unique_workshop_enrollment')]

class Product(models.Model):
 artisan=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='products');name=models.CharField(max_length=180);category=models.CharField(max_length=60,db_index=True)
 description=models.TextField();price=models.DecimalField(max_digits=9,decimal_places=2);stock=models.PositiveIntegerField(default=1);region=models.CharField(max_length=80);story=models.TextField(blank=True)
 image_url=models.URLField(blank=True);active=models.BooleanField(default=True);created_at=models.DateTimeField(auto_now_add=True)
 class Meta: ordering=['-created_at']

class Order(models.Model):
 buyer=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='orders');status=models.CharField(max_length=20,default='pending');total=models.DecimalField(max_digits=10,decimal_places=2);created_at=models.DateTimeField(auto_now_add=True)
class OrderItem(models.Model):
 order=models.ForeignKey(Order,on_delete=models.CASCADE,related_name='items');product=models.ForeignKey(Product,on_delete=models.PROTECT);quantity=models.PositiveIntegerField();unit_price=models.DecimalField(max_digits=9,decimal_places=2)

class Event(models.Model):
 title=models.CharField(max_length=180);artist=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='events')
 event_type=models.CharField(max_length=12,choices=[('live','Live'),('recorded','Recorded'),('external','External')],default='live')
 description=models.TextField();venue=models.CharField(max_length=180,blank=True);starts_at=models.DateTimeField();price=models.DecimalField(max_digits=9,decimal_places=2,default=0)
 capacity=models.PositiveIntegerField(default=100);external_url=models.URLField(blank=True);image_url=models.URLField(blank=True);published=models.BooleanField(default=True)
 class Meta: ordering=['starts_at']
class Ticket(models.Model):
 code=models.UUIDField(default=uuid.uuid4,unique=True,editable=False);event=models.ForeignKey(Event,on_delete=models.CASCADE,related_name='tickets');attendee=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='tickets')
 status=models.CharField(max_length=16,default='pending');redeemed_at=models.DateTimeField(null=True,blank=True);created_at=models.DateTimeField(auto_now_add=True)
 class Meta: constraints=[models.UniqueConstraint(fields=['event','attendee'],name='unique_attendee_event_ticket')]
class Certificate(models.Model):
 code=models.UUIDField(default=uuid.uuid4,unique=True,editable=False);learner=models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name='certificates');workshop=models.ForeignKey(Workshop,on_delete=models.PROTECT)
 issued_at=models.DateTimeField(auto_now_add=True);issuer=models.CharField(max_length=120,default='ArtiSoul')

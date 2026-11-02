from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Profile,Workshop,Enrollment,Product,Order,Event,Ticket,Certificate
class UserSerializer(serializers.ModelSerializer):
 role=serializers.CharField(source='profile.role',read_only=True)
 class Meta: model=User;fields=['id','username','email','first_name','last_name','role']
class RegisterSerializer(serializers.ModelSerializer):
 password=serializers.CharField(write_only=True,min_length=10);role=serializers.ChoiceField(choices=Profile.ROLES,default='learner',write_only=True)
 class Meta: model=User;fields=['username','email','password','first_name','last_name','role']
 def create(self,data):
  role=data.pop('role');u=User.objects.create_user(**data);Profile.objects.create(user=u,role=role);return u
class WorkshopSerializer(serializers.ModelSerializer):
 instructor_name=serializers.CharField(source='instructor.get_full_name',read_only=True)
 class Meta: model=Workshop;fields='__all__';read_only_fields=['instructor','created_at']
class EnrollmentSerializer(serializers.ModelSerializer):
 workshop_title=serializers.CharField(source='workshop.title',read_only=True)
 class Meta: model=Enrollment;fields=['id','workshop','workshop_title','status','progress','enrolled_at'];read_only_fields=['status','progress','enrolled_at']
class ProductSerializer(serializers.ModelSerializer):
 artisan_name=serializers.CharField(source='artisan.get_full_name',read_only=True)
 class Meta: model=Product;fields='__all__';read_only_fields=['artisan','created_at']
class OrderSerializer(serializers.ModelSerializer):
 items=serializers.SerializerMethodField()
 def get_items(self,order):return [{'product':i.product_id,'name':i.product.name,'quantity':i.quantity,'unit_price':str(i.unit_price)} for i in order.items.select_related('product')]
 class Meta: model=Order;fields=['id','status','total','created_at','items']
class EventSerializer(serializers.ModelSerializer):
 artist_name=serializers.CharField(source='artist.get_full_name',read_only=True)
 class Meta: model=Event;fields='__all__';read_only_fields=['artist']
class TicketSerializer(serializers.ModelSerializer):
 event_title=serializers.CharField(source='event.title',read_only=True)
 class Meta: model=Ticket;fields=['code','event','event_title','status','created_at']
class CertificateSerializer(serializers.ModelSerializer):
 workshop_title=serializers.CharField(source='workshop.title',read_only=True);learner_name=serializers.CharField(source='learner.get_full_name',read_only=True)
 class Meta: model=Certificate;fields=['code','workshop_title','learner_name','issued_at','issuer']

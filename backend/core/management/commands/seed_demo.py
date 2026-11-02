from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import Profile,Workshop,Product,Event

class Command(BaseCommand):
 help='Create local demonstration accounts and discovery content.'
 def handle(self,*args,**kwargs):
  people=[]
  for username,email,first,role in [('learner@artisoul.in','learner@artisoul.in','Aarav','learner'),('creator@artisoul.in','creator@artisoul.in','Meera','artist'),('admin@artisoul.in','admin@artisoul.in','ArtiSoul','admin')]:
   user,created=User.objects.get_or_create(username=username,defaults={'email':email,'first_name':first,'is_staff':role=='admin','is_superuser':role=='admin'})
   if created:user.set_password('Heritage123!');user.save()
   Profile.objects.get_or_create(user=user,defaults={'role':role,'verified':role in ['artist','admin']});people.append(user)
  creator=people[1]
  imgs=['https://images.unsplash.com/photo-1504609813442-a8924e83f76e?auto=format&fit=crop&w=900&q=80','https://images.unsplash.com/photo-1516280440614-37939bbacd81?auto=format&fit=crop&w=900&q=80','https://images.unsplash.com/photo-1565193566173-7a0ee3dbe261?auto=format&fit=crop&w=900&q=80']
  ws=[('The Language of Bharatanatyam','Classical Dance','Explore abhinaya and foundational adavus with a Chennai-based performer.','Tamil · English',2400),('Carnatic Music: Voice & Raga','Classical Music','Build a confident daily practice and discover the architecture of a raga.','Kannada · English',1800),('Clay, Wheel & Living Earth','Pottery','A tactile introduction to hand-building and the potter’s wheel.','Hindi · English',1500)]
  for i,(title,cat,desc,lang,price) in enumerate(ws):Workshop.objects.get_or_create(title=title,defaults={'instructor':creator,'category':cat,'description':desc,'language':lang,'price':price,'starts_at':timezone.now()+timedelta(days=7+i*4),'image_url':imgs[i]})
  maker=people[0]
  ps=[('Kutch Embroidered Wall Art','Textiles','Bhuj, Gujarat',4200,'https://images.unsplash.com/photo-1605000797499-95a51c5269ae?auto=format&fit=crop&w=900&q=80'),('Blue Pottery Serving Bowl','Pottery','Jaipur, Rajasthan',1850,imgs[2]),('Tanjore Garden Study','Painting','Thanjavur, Tamil Nadu',6800,'https://images.unsplash.com/photo-1579783902614-a3fb3927b6a5?auto=format&fit=crop&w=900&q=80')]
  for name,cat,region,price,img in ps:Product.objects.get_or_create(name=name,defaults={'artisan':maker,'category':cat,'region':region,'price':price,'stock':8,'description':'Made by hand by an independent Indian artisan.','story':'A living craft practice carried through generations.','image_url':img})
  Event.objects.get_or_create(title='An Evening in Abhinaya',defaults={'artist':creator,'event_type':'live','description':'A Bharatanatyam recital tracing the poetry of devotion.','venue':'Chowdiah Memorial Hall · Bengaluru','starts_at':timezone.now()+timedelta(days=20),'price':650,'capacity':120,'image_url':imgs[0]})
  self.stdout.write(self.style.SUCCESS('Demo accounts and cultural listings are ready.'))

from decimal import Decimal
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import viewsets,generics,permissions
from rest_framework.decorators import action,api_view
from rest_framework.response import Response
from django.http import HttpResponse
from .models import Profile,Workshop,Enrollment,Product,Order,OrderItem,Event,Ticket,Certificate
from .serializers import *
from .permissions import CreatorOrReadOnly

class RegisterView(generics.CreateAPIView): queryset=User.objects.all();serializer_class=RegisterSerializer;permission_classes=[permissions.AllowAny]
class MeView(generics.RetrieveAPIView): serializer_class=UserSerializer;permission_classes=[permissions.IsAuthenticated]
 def get_object(self):return self.request.user
class WorkshopViewSet(viewsets.ModelViewSet):
 serializer_class=WorkshopSerializer;permission_classes=[CreatorOrReadOnly]
 def get_queryset(self):
  q=Workshop.objects.filter(published=True).select_related('instructor');term=self.request.query_params.get('search');cat=self.request.query_params.get('category')
  if term:q=q.filter(Q(title__icontains=term)|Q(description__icontains=term)|Q(instructor__first_name__icontains=term))
  if cat:q=q.filter(category__iexact=cat)
  return q
 def perform_create(self,s):s.save(instructor=self.request.user)
 @action(detail=True,methods=['post'],permission_classes=[permissions.IsAuthenticated])
 def enroll(self,request,pk=None):
  w=self.get_object()
  if w.enrollments.count()>=w.seats:return Response({'detail':'Workshop is full.'},status=409)
  e,created=Enrollment.objects.get_or_create(learner=request.user,workshop=w)
  return Response(EnrollmentSerializer(e).data,status=201 if created else 200)
class EnrollmentViewSet(viewsets.ReadOnlyModelViewSet):
 serializer_class=EnrollmentSerializer;permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):return Enrollment.objects.filter(learner=self.request.user).select_related('workshop')
 @action(detail=True,methods=['post'])
 def complete(self,request,pk=None):
  enrollment=self.get_object();enrollment.progress=100;enrollment.status='completed';enrollment.save(update_fields=['progress','status'])
  certificate,_=Certificate.objects.get_or_create(learner=request.user,workshop=enrollment.workshop)
  return Response({'enrollment':EnrollmentSerializer(enrollment).data,'certificate':CertificateSerializer(certificate).data})
class ProductViewSet(viewsets.ModelViewSet):
 serializer_class=ProductSerializer;permission_classes=[CreatorOrReadOnly]
 def get_queryset(self):
  q=Product.objects.filter(active=True).select_related('artisan');term=self.request.query_params.get('search');cat=self.request.query_params.get('category')
  if term:q=q.filter(Q(name__icontains=term)|Q(description__icontains=term)|Q(region__icontains=term))
  if cat:q=q.filter(category__iexact=cat)
  return q
 def perform_create(self,s):s.save(artisan=self.request.user)
class OrderViewSet(viewsets.ViewSet):
 permission_classes=[permissions.IsAuthenticated]
 def list(self,request):return Response([{'id':o.id,'status':o.status,'total':o.total,'created_at':o.created_at} for o in Order.objects.filter(buyer=request.user)])
 def create(self,request):
  rows=request.data.get('items',[])
  if not rows:return Response({'detail':'Cart is empty.'},status=400)
  with transaction.atomic():
   ids=[r.get('product') for r in rows];products={p.id:p for p in Product.objects.select_for_update().filter(id__in=ids,active=True)};validated=[];total=Decimal('0')
   for row in rows:
    p=products.get(row.get('product'));qty=int(row.get('quantity',1))
    if not p or qty<1 or p.stock<qty:return Response({'detail':'Product unavailable or insufficient stock.'},status=409)
    total+=p.price*qty;validated.append((p,qty))
   order=Order.objects.create(buyer=request.user,total=total,status='pending')
   for p,qty in validated:OrderItem.objects.create(order=order,product=p,quantity=qty,unit_price=p.price);p.stock-=qty;p.save(update_fields=['stock'])
  return Response({'id':order.id,'status':order.status,'total':order.total},status=201)
class EventViewSet(viewsets.ModelViewSet):
 serializer_class=EventSerializer;permission_classes=[CreatorOrReadOnly]
 def get_queryset(self):return Event.objects.filter(published=True).select_related('artist')
 def perform_create(self,s):s.save(artist=self.request.user)
 @action(detail=True,methods=['post'],permission_classes=[permissions.IsAuthenticated])
 def book(self,request,pk=None):
  event=self.get_object()
  if event.event_type=='external' and event.external_url:return Response({'booking':'external','url':event.external_url,'detail':'Continue with organizer. No ArtiSoul booking was made.'})
  with transaction.atomic():
   event=Event.objects.select_for_update().get(pk=event.pk)
   if event.tickets.filter(status__in=['pending','confirmed']).count()>=event.capacity:return Response({'detail':'Sold out.'},status=409)
   t,created=Ticket.objects.get_or_create(event=event,attendee=request.user)
  return Response(TicketSerializer(t).data,status=201 if created else 200)
class TicketViewSet(viewsets.ReadOnlyModelViewSet):
 serializer_class=TicketSerializer;permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):return Ticket.objects.filter(attendee=self.request.user).select_related('event')
 @action(detail=True,methods=['get'])
 def qr(self,request,pk=None):
  ticket=self.get_object()
  if ticket.status!='confirmed':return Response({'detail':'QR is issued after payment confirmation.'},status=409)
  import io,qrcode
  from django.http import HttpResponse
  image=qrcode.make(str(ticket.code));buf=io.BytesIO();image.save(buf,format='PNG')
  return HttpResponse(buf.getvalue(),content_type='image/png')
 @action(detail=False,methods=['post'])
 def verify(self,request):
  if request.user.profile.role not in ['artist','artisan','admin']:return Response({'detail':'Organizer access required.'},status=403)
  try:t=Ticket.objects.select_related('event').get(code=request.data.get('code'))
  except (Ticket.DoesNotExist,ValueError):return Response({'valid':False},status=404)
  if t.event.artist_id!=request.user.id and request.user.profile.role!='admin':return Response({'valid':False,'detail':'Not your event.'},status=403)
  if t.status!='confirmed':return Response({'valid':False,'detail':'Ticket is not paid or confirmed.'},status=409)
  if t.status=='redeemed':return Response({'valid':False,'detail':'Already redeemed.'},status=409)
  t.status='redeemed';t.redeemed_at=timezone.now();t.save(update_fields=['status','redeemed_at']);return Response({'valid':True,'ticket':TicketSerializer(t).data})
class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
 serializer_class=CertificateSerializer;permission_classes=[permissions.IsAuthenticated]
 def get_queryset(self):return Certificate.objects.filter(learner=self.request.user).select_related('workshop','learner')
 @action(detail=True,methods=['get'])
 def pdf(self,request,pk=None):
  from reportlab.pdfgen import canvas
  from reportlab.lib.pagesizes import landscape,A4
  from reportlab.lib.units import mm
  import io,qrcode
  cert=self.get_object();buf=io.BytesIO();pdf=canvas.Canvas(buf,pagesize=landscape(A4));w,h=landscape(A4)
  pdf.setFillColorRGB(.33,.11,.15);pdf.rect(0,0,w,h,fill=1,stroke=0);pdf.setFillColorRGB(.98,.96,.92);pdf.rect(12*mm,12*mm,w-24*mm,h-24*mm,fill=1,stroke=0)
  pdf.setFillColorRGB(.33,.11,.15);pdf.setFont('Times-Bold',28);pdf.drawCentredString(w/2,h-48*mm,'Certificate of Completion');pdf.setFont('Helvetica',12);pdf.drawCentredString(w/2,h-65*mm,'This certificate is proudly presented to')
  pdf.setFont('Times-Bold',25);pdf.drawCentredString(w/2,h-83*mm,cert.learner.get_full_name() or cert.learner.username);pdf.setFont('Helvetica',12);pdf.drawCentredString(w/2,h-101*mm,f'for completing {cert.workshop.title}')
  pdf.setFont('Helvetica',10);pdf.drawCentredString(w/2,h-119*mm,f'Issued by {cert.issuer} · {cert.issued_at:%d %B %Y} · ID {cert.code}')
  qr=qrcode.make(f'{request.build_absolute_uri("/api/certificates/verify/")}{cert.code}/');qbuf=io.BytesIO();qr.save(qbuf,format='PNG');qbuf.seek(0)
  from reportlab.lib.utils import ImageReader
  pdf.drawImage(ImageReader(qbuf),w-55*mm,19*mm,width=30*mm,height=30*mm);pdf.showPage();pdf.save();buf.seek(0)
  res=HttpResponse(buf.getvalue(),content_type='application/pdf');res['Content-Disposition']=f'attachment; filename="artisoul-certificate-{cert.code}.pdf"';return res
@api_view(['GET'])
def health(request):return Response({'status':'ok','service':'ArtiSoul API'})
@api_view(['POST'])
def translation_demo(request):
 text=request.data.get('text','');target=request.data.get('target_language','English')
 if not text:return Response({'detail':'Caption text is required.'},status=400)
 return Response({'mode':'demo','translated_text':f'[Demo translation to {target}] {text}','notice':'Simulated only: Azure Speech is not configured.'})
@api_view(['GET'])
def recommendations(request):return Response({'strategy':'popular_fallback','items':list(Workshop.objects.filter(published=True).values('id','title','category','price','image_url','language')[:6])})
@api_view(['GET'])
def verify_certificate(request,code):
 try:c=Certificate.objects.select_related('workshop','learner').get(code=code)
 except (Certificate.DoesNotExist,ValueError):return Response({'valid':False},status=404)
 return Response({'valid':True,**CertificateSerializer(c).data})

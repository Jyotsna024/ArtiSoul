from rest_framework.permissions import BasePermission,SAFE_METHODS
class CreatorOrReadOnly(BasePermission):
 def has_permission(self,request,view):return request.method in SAFE_METHODS or bool(request.user.is_authenticated and hasattr(request.user,'profile') and request.user.profile.role in ['artisan','artist','admin'])
 def has_object_permission(self,request,view,obj):return request.method in SAFE_METHODS or getattr(obj,'instructor_id',getattr(obj,'artisan_id',getattr(obj,'artist_id',None)))==request.user.id or request.user.profile.role=='admin'

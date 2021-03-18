from rest_framework.permissions import BasePermission

#You subclass the BasePermission class and override the has_object_ permission().
#You check that the user performing the request is present in the students relationship of the Course object. 
# You are going to use the IsEnrolled permission next.
class IsEnrolled(BasePermission):       
    # Return True to grant access
    def has_object_permission(self, request, view, obj):
        return obj.students.filter(id=request.user.id).exists()
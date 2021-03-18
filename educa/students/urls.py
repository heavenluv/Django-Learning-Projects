from django.urls import path
from django.urls.conf import include
from . import views
from django.views.decorators.cache import cache_page



urlpatterns = [
    path('register/', views.StudentRegistrationView.as_view(), name='student_registration'),
    path('courses/', views.StudentCourseListView.as_view(), name='student_course_list'),
    # The following result will be cached for 15 minutes (Caching views method)
    path('course/<pk>/', (cache_page(60*15))(views.StudentCourseDetailView.as_view()), name='student_course_detail'),
    path('course/<pk>/<module_id>/', (cache_page(60*15))(views.StudentCourseDetailView.as_view()), name='student_course_detail_module'),
    path('enroll-course/',views.StudentEnrollCourseView.as_view(), name='student_enroll_course'),
    ]
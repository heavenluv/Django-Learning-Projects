from django.shortcuts import render, redirect, get_object_or_404
from .models import Course
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.base import TemplateResponseMixin, View
from .forms import ModuleFormSet
from django.forms.models import modelform_factory
from django.apps import apps
from .models import Module, Content
from braces.views import CsrfExemptMixin, JsonRequestResponseMixin
from .models import Subject
from django.db.models import Count
from django.views.generic.detail import DetailView
from students.views import CourseEnrollForm
from django.core.cache import cache
# Create your views here.
"""
Unrecommend solution

class ManageCourseListView(ListView):
    model = Course
    template_name = 'courses/manage/course/list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)
"""

# Build views to create, edit, and delete courses.

# Used for views that interact with any model that contains an owner attribute.


class OwnerMixin(object):
    # Get the base QuerySet
    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(owner=self.request.user)

# Save the instance (for model forms) and redirect the user to success_url.
# You override this method to automatically set the current user in the owner attribute of the object being saved.
# By doing so, you set the owner for an object automatically when it is saved.


class OwnerEditMixin(object):
    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class OwnerCourseMixin(OwnerMixin, LoginRequiredMixin, PermissionRequiredMixin):
    model = Course
    # Build the model form of the CreateView and UpdateView views.
    fields = ['subject', 'title', 'slug', 'overview']
    # Used by CreateView, UpdateView, and DeleteView
    # To redirect the user after the form is successfully submitted or the object is deleted.
    success_url = reverse_lazy('manage_course_list')


class OwnerCourseEditMixin(OwnerCourseMixin, OwnerEditMixin):
    template_name = 'courses/manage/course/form.html'


class ManageCourseListView(OwnerCourseMixin, ListView):
    template_name = 'courses/manage/course/list.html'
    permission_required = 'courses.view_course'


class CourseCreateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.add_course'


class CourseUpdateView(OwnerCourseEditMixin, CreateView):
    permission_required = 'courses.change_course'


class CourseDeleteView(OwnerCourseEditMixin, DeleteView):
    template_name = 'courses/manage/course/delete.html'
    permission_required = 'courses.delete_course'


"""
• TemplateResponseMixin: This mixin takes charge of rendering templates and returning an HTTP response.
                         It requires a template_name attribute that indicates the template to be rendered and provides the
                         render_to_ response() method to pass it a context and render the template.
• View: The basic class-based view provided by Django.
"""


class CourseModuleUpdateView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/formset.html'
    course = None
    """
    • get_formset(): You define this method to avoid repeating the code to build the formset.
                     You create a ModuleFormSet object for the given Course object with optional data.
    • dispatch(): This method is provided by the View class. It takes an HTTP request and its parameters and attempts
                  to delegate to a lowercase method that matches the HTTP method used. A GET request is delegated to
                  the get() method and a POST request to post(), respectively. In this method, you use the get_object_or_404()
                  shortcut function to get the Course object for the given id parameter that belongs to the current user.
                  You include this code in the dispatch() method because you need to retrieve the course for both
                  GET and POST requests. You save it into the course attribute of the view to make it accessible to other methods.
    • get(): Executed for GET requests. You build an empty ModuleFormSet formset and render it to the template together
             with the current Course object using the render_to_response() method provided by TemplateResponseMixin.
    • post(): Executed for POST requests.
              If the formset is valid, you save it by calling the save() method. At this point, any changes made, such as adding,
              updating, or marking modules for deletion, are applied to the database. Then, you redirect users to the
              manage_course_list URL. If the formset is not valid, you render the template to display any errors instead.
    """

    def get_formset(self, data=None):
        return ModuleFormSet(instance=self.course, data=data)

    def dispatch(self, request, pk):
        self.course = get_object_or_404(Course, id=pk, owner=request.user)
        return super().dispatch(request, pk)

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        return self.render_to_response({'course': self.course, 'formset': formset})

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(data=request.POST)
        if formset.is_valid():
            formset.save()
            return redirect('manage_course_list')
        return self.render_to_response({'course': self.course, 'formset': formset})


class ContentCreateUpdateView(TemplateResponseMixin, View):
    module = None
    model = None
    obj = None
    template_name = 'courses/manage/content/form.html'

    def get_model(self, model_name):
        if model_name in ['text', 'video', 'image', 'file']:
            return apps.get_model(app_label='courses', model_name=model_name)
        return None

    def get_form(self, model, *args, **kwargs):
        Form = modelform_factory(
            model, exclude=['owner', 'order', 'created', 'updated'])
        return Form(*args, **kwargs)

    def dispatch(self, request, module_id, model_name, id=None):
        self.module = get_object_or_404( Module, id=module_id, course__owner=request.user)
        self.model = self.get_model(model_name)
        if id:
            self.obj = get_object_or_404(self.model, id=id, owner=request.user)
        return super(ContentCreateUpdateView, self).dispatch(request, module_id, model_name, id)

    def get(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model, instance=self.obj)
        return self.render_to_response({'form': form, 'object': self.obj})

    def post(self, request, module_id, model_name, id=None):
        form = self.get_form(self.model,
                             instance=self.obj,
                             data=request.POST,
                             files=request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.owner = request.user
            obj.save()
            if not id:
                # new content
                Content.objects.create(module=self.module,
                                       item=obj)
            return redirect('module_content_list', self.module.id)

        return self.render_to_response({'form': form, 'object': self.obj})


class ContentDeleteView(View):
    def post(self, request, id):
        content = get_object_or_404(Content, id=id, module__course__owner=request.user)
        module = content.module
        content.item.delete()
        content.delete()
        return redirect('module_content_list', module.id)

class ModuleContentListView(TemplateResponseMixin, View):
    template_name = 'courses/manage/module/content_list.html'

    def get(self, request, module_id):
        module = get_object_or_404(
            Module, id=module_id, course__owner=request.user)
        return self.render_to_response({'module': module})


class ModuleOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Module.objects.filter(id=id, course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class ContentOrderView(CsrfExemptMixin, JsonRequestResponseMixin, View):
    def post(self, request):
        for id, order in self.request_json.items():
            Content.objects.filter(id=id, module__course__owner=request.user).update(order=order)
        return self.render_json_response({'saved': 'OK'})

class CourseListView(TemplateResponseMixin, View):
    model = Course
    template_name = 'courses/course/list.html'

    def get(self, request, subject=None):
        """
        In this case, you also cache both all courses and courses filtered by subject. 
        You use the all_courses cache key for storing all courses if no subject is given. 
        If there is a subject, you build the key dynamically with f'subject_{subject.id}_courses'.

        aggregate()方法详解:
            aggregate的中文意思是聚合, 源于SQL的聚合函数。
            Django的aggregate()方法作用是对一组值(比如queryset的某个字段)进行统计计算，并以字典(Dict)格式返回统计计算结果。
            django的aggregate方法支持的聚合操作有AVG / COUNT / MAX / MIN /SUM 等。
            Example：
                # 计算学生平均年龄, 返回字典。age和avg间是双下划线哦
                Student.objects.all().aggregate(Avg('age'))
                { 'age__avg': 12 }

        model.subjects.annotate():
            annotate的中文意思是注释，小编我觉得是非常地词不达意，一个更好的理解是分组(Group By)。
            如果你想要对数据集先进行分组然后再进行某些聚合操作或排序时，需要使用annotate方法来实现。
            与aggregate方法不同的是，annotate方法返回结果的不仅仅是含有统计结果的一个字典，
            而是包含有新增统计字段的查询集(queryset
            Example:
                # 按爱好分组，再统计每组学生数量。
                # Hobby.objects.annotate(Count('student'))
                # 按爱好分组，再统计每组学生最大年龄。
                # Hobby.objects.annotate(Max('student__age'))

        Attention: Cannot use a cached queryset to build another queryset
        So we need to use the annotate to create a base queryset then further grouping the queryset by subject that we wanted
        """
        subjects = cache.get('all_subjects')
        if not subjects:
            subjects = Subject.objects.annotate(total_courses=Count('courses'))
            cache.set('all_subjects', subjects)
        #先按course分组，统计每个course的module的数量
        #Grouped by courses then count the number of modules of each course.
        all_courses = Course.objects.annotate(total_modules=Count('modules'))
        if subject:
            subject = get_object_or_404(Subject, slug=subject)
            key = f'subject_{subject.id}_courses'
            courses = cache.get(key)
            if not courses:
                courses = all_courses.filter(subject=subject)
                cache.set(key, courses)
        else:
            courses = cache.get('all_courses')
            if not courses:
                courses = all_courses
                cache.set('all_courses',courses)
            
        content = {
            'subjects': subjects,
            'subject': subject,
            'courses': courses
        }
        return self.render_to_response(content)

class CourseDetailView(DetailView):
    model = Course
    template_name = 'courses/course/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['enroll_form'] = CourseEnrollForm(initial={'course': self.object})
        return context
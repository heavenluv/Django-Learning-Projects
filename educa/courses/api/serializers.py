from rest_framework import serializers
from ..models import Subject, Course, Module, Content

"""
Output data has to be serialized in a specific format, and input data will be deserialized for processing. 
The framework provides the following classes to build serializers for single objects:
    • Serializer: Provides serialization for normal Python class instances
    • ModelSerializer: Provides serialization for model instances
    • HyperlinkedModelSerializer: The same as ModelSerializer, but it represents object relationships with 
      links rather than primary keys
"""

class SubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subject
        fields = ['id', 'title', 'slug']

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = ['order', 'title', 'description']

class CourseSerializer(serializers.ModelSerializer):
    modules = ModuleSerializer(many=True, read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'modules']

# Define a custom field by subclassing the RelatedField serializer field provided by REST framework 
# and overriding the to_representation() method. You define the ContentSerializer serializer for the 
# Content model and use the custom field for the item generic foreign key.
class ItemRelatedField(serializers.RelatedField):
    def to_representation(self, value):
        return value.render()

class ContentSerializer(serializers.ModelSerializer):
    item = ItemRelatedField(read_only=True)

    class Meta:
        model = Content
        fields = ['order', 'item']
# An alternative serializer for the Module model that includes its contents, and an extended Course serializer as well
class ModuleWithContentsSerializer(serializers.ModelSerializer):
    content = ContentSerializer(many=True)

    class Meta:
        model = Module
        fields = ['order', 'title', 'description', 'content']

class CourseWithContentsSerializer(serializers.ModelSerializer):
    modules = ModuleWithContentsSerializer(many=True)
    
    class Meta:
        model = Course
        fields = ['id', 'subject', 'title', 'slug', 'overview', 'created', 'owner', 'modules']

from django.contrib import admin

from courses.models import Course, Group, GroupStudents, Lesson, Subscription

admin.site.register(Course)
admin.site.register(Group)
admin.site.register(GroupStudents)
admin.site.register(Lesson)
admin.site.register(Subscription)

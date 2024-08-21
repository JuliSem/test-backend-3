from django.db import transaction
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from api.v1.permissions import IsStudentOrIsAdmin, ReadOnlyOrIsAdmin
from api.v1.serializers.course_serializer import (CourseSerializer,
                                                  CreateCourseSerializer,
                                                  CreateGroupSerializer,
                                                  CreateLessonSerializer,
                                                  GroupSerializer,
                                                  LessonSerializer)
from api.v1.serializers.user_serializer import SubscriptionSerializer
from courses.models import Course, Lesson, Subscription
from users.models import Balance


class LessonViewSet(viewsets.ModelViewSet):
    """Уроки."""

    permission_classes = (IsStudentOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return LessonSerializer
        return CreateLessonSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.lessons.all()


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""

    permission_classes = (permissions.IsAdminUser,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return GroupSerializer
        return CreateGroupSerializer

    def perform_create(self, serializer):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        serializer.save(course=course)

    def get_queryset(self):
        course = get_object_or_404(Course, id=self.kwargs.get('course_id'))
        return course.groups.all()


class CourseViewSet(viewsets.ModelViewSet):
    """Курсы """

    permission_classes = (ReadOnlyOrIsAdmin,)

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return CourseSerializer
        return CreateCourseSerializer

    def get_queryset(self):
        """Список курсов (продуктов), доступных для покупки."""
        user = self.request.user
        qs = Course.objects.filter(
            ~Exists(
                Subscription.objects.filter(course=OuterRef('pk'), user=user, is_valid=True)
            )
        )
        qs = qs.annotate(
            lessons_count=Lesson.objects.filter(course=OuterRef('pk')).count()
        )
        return qs

    @action(
        methods=['post'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,)
    )
    def pay(self, request, pk):
        """Покупка доступа к курсу (подписка на курс)."""
        with transaction.atomic():
            balance = get_object_or_404(Balance, user=request.user)
            course = get_object_or_404(Course, id=pk)

            if balance.balance >= course.price:
                subscription = Subscription.objects.filter(
                    course=course,
                    user=request.user
                ).first()
                if not subscription:
                    subscription = Subscription.objects.create(
                        course=course,
                        user=request.user,
                        is_valid=True
                    )
                    balance.balance -= course.price
                    balance.save()
                    data = SubscriptionSerializer(subscription)
                    return Response(
                        data=data,
                        status=status.HTTP_201_CREATED
                    )

                return Response(
                    {'detail': 'Вы уже подписаны на данный курс!'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response(
                {'detail':
                 'Недостаточно средств (бонусов) для подписки на курс!'},
                status=status.HTTP_400_BAD_REQUEST
            )

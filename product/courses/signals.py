from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from courses.models import Group, GroupStudents, Subscription


@receiver(post_save, sender=Subscription)
def post_save_subscription(sender, instance: Subscription, created, **kwargs):
    """
    Распределение нового студента в группу курса.

    """

    if created:
        if instance.is_valid and instance.course.start_date > timezone.now():
            groups = Group.objects.filter(course=instance.course).order_by(
                'count_students'
            )
            if not groups:
                new_group = Group.objects.create(
                    titel='Группа 1',
                    course=instance.course,
                    count_students=1
                )
                GroupStudents.objects.create(
                    user=instance.user,
                    group=new_group
                )
            else:
                group = groups.first()
                if group.count_students == 0:
                    GroupStudents.objects.create(
                        user=instance.user,
                        group=group
                    )
                    group.count_students = 1
                    group.save()
                elif groups.count() < 5:
                    new_group = Group.objects.create(
                        titel=f'Группа {groups.count() + 1}',
                        course=instance.course,
                        count_students=1
                    )
                    GroupStudents.objects.create(
                        user=instance.user,
                        group=new_group
                    )
                else:
                    GroupStudents.objects.create(
                        user=instance.user,
                        group=groups.first()
                    )
                    group.count_students += 1
                    group.save()
        elif instance.course.start_date < timezone.now():
            print('Курс уже начался, распределение по группам невозможно!')
        elif not instance.is_valid:
            print('Отсутствует доступ к курсу!')

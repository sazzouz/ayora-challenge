from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.timezone import get_default_timezone_name
from django_celery_beat.models import CrontabSchedule, IntervalSchedule, PeriodicTask
from order.tasks import RejectStaleOrdersTask

from core.constants.schedules import (
    EVERY_MINUTE,
)
from core.types.schedules import TaskSchedule


class Command(BaseCommand):
    help = """
    Setup celery beat periodic tasks.
    """

    TASK_SCHEDULES = {
        RejectStaleOrdersTask: [
            TaskSchedule(
                task=RejectStaleOrdersTask,
                name="Auto-reject stale orders.",
                cron=EVERY_MINUTE,
            ),
        ],
    }

    @transaction.atomic
    def handle(self, *args, **kwargs):
        print("Deleting all periodic tasks and schedules...\n")

        IntervalSchedule.objects.all().delete()
        CrontabSchedule.objects.all().delete()
        PeriodicTask.objects.all().delete()

        timezone = get_default_timezone_name()

        # Flatten all schedules
        all_schedules = [schedule for schedules in self.TASK_SCHEDULES.values() for schedule in schedules]

        for schedule in all_schedules:
            print(f"Setting up {schedule.task.name} - {schedule.name}")

            cron = CrontabSchedule.objects.create(timezone=timezone, **schedule.cron.to_dict())

            PeriodicTask.objects.create(
                name=schedule.name,
                task=schedule.task.name,
                crontab=cron,
                enabled=schedule.enabled,
            )

        print("\nSuccessfully configured periodic tasks.\n")

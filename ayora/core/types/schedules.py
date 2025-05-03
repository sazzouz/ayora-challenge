from dataclasses import dataclass


@dataclass
class CronSchedule:
    """
    Represents a cron schedule for task execution.

    Attributes:
        minute (str): The minute field of the cron expression. Defaults to '*'.
        hour (str): The hour field of the cron expression. Defaults to '*'.
        day_of_week (str): The day of the week field of the cron expression.
            Defaults to '*'.
        day_of_month (str): The day of the month field of the cron expression.
            Defaults to '*'.
        month_of_year (str): The month of the year field of the cron expression.
            Defaults to '*'.
    """

    minute: str = "*"
    hour: str = "*"
    day_of_week: str = "*"
    day_of_month: str = "*"
    month_of_year: str = "*"

    def to_dict(self):
        """
        Converts the cron schedule to a dictionary representation.

        Returns:
            dict: A dictionary containing the cron schedule fields.
        """
        return {
            "minute": self.minute,
            "hour": self.hour,
            "day_of_week": self.day_of_week,
            "day_of_month": self.day_of_month,
            "month_of_year": self.month_of_year,
        }


@dataclass
class TaskSchedule:
    """
    Represents a scheduled task with a cron schedule.

    Attributes:
        task (str): The name of the task to be executed.
        name (str): A human-readable name for the task.
        cron (CronSchedule): The cron schedule associated with the task.
        enabled (bool): Indicates whether the task is enabled. Defaults to True.
    """

    task: str
    name: str
    cron: CronSchedule
    enabled: bool = True

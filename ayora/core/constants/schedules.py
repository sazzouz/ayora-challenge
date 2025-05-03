from core.types.schedules import CronSchedule

"""
Common cron schedules for periodic tasks.
"""

EVERY_MINUTE = CronSchedule()

DAILY_MORNING = CronSchedule(minute="0", hour="8")

DAILY_NOON = CronSchedule(minute="0", hour="12")

DAILY_AFTERNOON = CronSchedule(minute="0", hour="16")

DAILY_EVENING = CronSchedule(minute="0", hour="20")

DAILY_MIDNIGHT = CronSchedule(minute="0", hour="0")

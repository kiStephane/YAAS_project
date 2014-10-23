__author__ = 'stephaneki'

from django_cron import CronJobBase, Schedule


class CronJob(CronJobBase):
    RUN_EVERY_MINS = 2
    RETRY_AFTER_FAILURE_MINS = 2

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'yaasApp.cron_job'  # a unique code

    def do(self):
        print "I am running"
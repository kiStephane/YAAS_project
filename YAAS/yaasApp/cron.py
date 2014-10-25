from yaasApp.models import Auction
from yaasApp.views import send_mail_to_seller, send_mail_to_bidder

__author__ = 'stephaneki'

from django_cron import CronJobBase, Schedule


class CronJob(CronJobBase):
    RUN_EVERY_MINS = 1
    RETRY_AFTER_FAILURE_MINS = 1

    schedule = Schedule(run_every_mins=RUN_EVERY_MINS, retry_after_failure_mins=RETRY_AFTER_FAILURE_MINS)
    code = 'yaasApp.cron_job'  # a unique code

    def do(self):
        auctions = Auction.objects.filter(state=1)
        for auction in auctions:
            if auction.is_due():
                auction.state = 4  # adjudicated
                auction.save()
                send_mail_to_seller(auction.last_bid(),
                                    sub="Your auction has been resolved",
                                    body="Auction: " + str(auction.title) + " has been resolved")
                for bid in auction.bid_set.all():
                    send_mail_to_bidder(bid, sub="Auction " + str(bid.auction.title) + " resolved !!!",
                                        body="The auction you have bid for has been resolved")


"""
This module provides endpoint logic for cron jobs that send team update
reminder emails and digest emails.
"""

import datetime
import functools
import logging

import webapp2
from google.appengine.api import mail

import model
#from .settings import VERSION, RELEASE
VERSION = "2.4"
RELEASE = ".9"

class CronUpdateHandler(webapp2.RequestHandler):

    @classmethod
    def get_reply_address(cls, urlsafe):
        """
        Return update email reply address given supplied urlsafe string.
        """
        return 'BBTU <update+%s@bb-team-update.appspotmail.com>' % urlsafe

    @classmethod
    def get_update_message(cls, team, to, sender, date):
        """
        Return unsent update EmailMessage.
        """
        day = "{:%b %d, %Y}".format(date)

        header = "Just reply with a few brief bullets starting with *. \n"
        header += "Start line with ** to identify completed item. \n"
        header += "Start line with *! to identify priority item or issue. \n"
        header += "Use #hashtag to indicate a category. eg. #BBonFHIR or #HAPI. \n"
        header += "Finish with [DONE] if there is extraneous or quoted "
        header += "text at the end of the e-mail reply.\n"
        header += "If you send send more than 1 email the last sent email is used. "
        header += "[BBTU-V:"+str(VERSION)+str(RELEASE)+"]"

        fields = dict(
            sender=sender,
            to=to,
            reply_to=sender,
            subject='[BB-Team-update] Send %s updates - %s' % (team.upper(),
                                                           day),
            body=header)
        return mail.EmailMessage(**fields)

    @classmethod
    def process_subscriber_update(cls, date, subscriber):
        """
        Create new SubscriberUpdate and send update email to subscriber.
        """
        subscriber_update = model.SubscriberUpdate.get_or_insert(
            name=subscriber.name,
            mail=subscriber.mail,
            team=subscriber.team,
            date=date)
        sender = cls.get_reply_address(subscriber_update.key.urlsafe())
        message = cls.get_update_message(
            subscriber.team, subscriber.mail, sender, date)
        message.send()
        subscriber_update.sent = True
        subscriber_update.put()

    @classmethod
    def process_update(cls, team, date):
        """
        Create new Update for supplied team and send team update emails.
        """
        update = model.Update.get_or_insert(team, date=date)
        f = functools.partial(cls.process_subscriber_update,
                              update.date)
        map(f, model.Subscriber.subscribed(team))

    def update(self, team):
        """
        Sends update reminder emails to all subscribers.
        """
        self.process_update(team, datetime.datetime.now())


class CronDigestHandler(webapp2.RequestHandler):

    @classmethod
    def get_digest_message(cls, team, digest, date, to):
        """
        Sends update reminder email to subscriber.
        """
        day = "{:%b %d, %Y}".format(date)
        reply_to = 'BBTU <noreply@bb-team-update.appspotmail.com>'
        fields = dict(
            sender=reply_to,
            to=to,
            reply_to=reply_to,
            subject='[BB-Team-update] %s team Digest - %s' % (team.upper(),
                                                           day),
                                                           body=digest)
        return mail.EmailMessage(**fields)

    @classmethod
    def get_subscriber_updates(cls, team, date):
        """
        Return list of SubscriberUpdate for team and date with messages.
        """
        return [x for x in
                model.SubscriberUpdate.get_updates(date, team)
                if x.message]

    @classmethod
    def get_update(cls, x):
        """
        Return formatted update string for supplied SubscriberUpdate x.
        """
        logging.info("in get_update with x: %s" % x)
        update = x.to_dict()
        logging.info('Update: %s' % update)
        update['message'] = update['message'].encode('utf8')
        logging.info(('in get_updateMessage: %s' % update['message']))

        return '{name} <{mail}>\n{message}\n\n'.format(**update)

    @classmethod
    def get_highlight(cls, x, hashtag):
        """
        Return string with # Highlights
        """
        logging.info('in get_highlight with x:%s' % x)
        highlight = x.to_dict()
        lines = highlight['message'].split('\n')

        for l in lines:
            # Find all the hashtags
            if "#" in l:
                # We have a Hashtag
                words = l.encode('utf8').split(" ")
                for w in words:
                    if "#" in w:
                        if w.lower() in hashtag:
                            pass
                        else:
                            hashtag[w.lower()] = []

            logging.info('hashtag: %s' % hashtag)

        hash_line = []
        for tag in hashtag:
            for l in lines:
                # Get all the lines with a Hashtag
                if tag in l.lower():
                    if l.endswith('\r'):
                        l = l[:-1]
                    hashtag[tag].append(l + "[" + x.name + "]")

        logging.info("Hashtags: %s" % hashtag)

        return hashtag

    @classmethod
    def sort_highlights(cls, hashtag):
        # Now we should have hashtags with lines consolidated
        # We need to sort them for printing

        logging.info("Hashtag to sort: %s" % hashtag)
        hashtag_string = "\n"

        hash_list = hashtag.items()
        hash_list.sort()

        logging.info("Hash list: %s" % hash_list)

        for tag,value in hash_list:
            if tag in hashtag_string:
                pass
            else:
                hashtag_string += tag + ":\n"
            for line in value:
                hashtag_string += line + "\n"

        return hashtag_string.encode('utf8')

    @classmethod
    def process_digest(cls, team, test=None):
        update = model.Update.latest(team)
        if not update:
            logging.info('No Update to process for digest')
            return
        digest = ''.join(
            map(cls.get_update, cls.get_subscriber_updates(team, update.date)))

        subscribers = cls.get_subscriber_updates(team, update.date)
        hashtags = {}
        for sub in subscribers:
            hashtags = cls.get_highlight(sub, hashtags)

        hashlist = cls.sort_highlights(hashtags)

        digest += hashlist

        if test:
            return digest
        if not digest:
            logging.info('No subscriber updates to process for digest')
            return
        for subscriber in model.Subscriber.subscribed(team):
            logging.info('creating digest for %s' % subscriber)
            subscriber_digest = model.SubscriberDigest.get_or_insert(
                mail=subscriber.mail, team=team, date=update.date)
            if not subscriber_digest.sent:

                message = cls.get_digest_message(
                    team, digest, update.date, subscriber.mail)
                logging.info('digest: %s' % digest)
                message.send()
                subscriber_digest.sent = True
                subscriber_digest.put()
            logging.info("digest output: %s" % digest)
        return digest

    def digest(self, team):
        test = self.request.get('test')
        if test:
            digest = self.process_digest(team, test=test)
            self.response.out.write(digest)
        else:
            self.process_digest(team)

routes = [
    webapp2.Route('/cron/update/<team:.*>', handler=CronUpdateHandler,
                  handler_method='update'),
    webapp2.Route('/cron/digest/<team:.*>', handler=CronDigestHandler,
                  handler_method='digest'),
]

handlers = webapp2.WSGIApplication(routes, debug=True)

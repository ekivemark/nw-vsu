
"""Unit test covereage."""

import datetime
import unittest

from google.appengine.ext import testbed

import admin
import cron
import model
import update


class TestModel(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.m_stb = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def test_Subscriber(self):
        data = [dict(name='mark',
                     mail='mark@ekivemark.com',
                     team='vsu',
                     status='subscribe',
                     role='admin'),
                dict(name='alan',
                     mail='alan.viars@videntity.com',
                     team='vsu',
                     status='subscribe')]

        for x in data:
            model.Subscriber.get_or_insert(**x)

        self.assertEqual(2, len(model.Subscriber.subscribed('gfw')))


class TestUpdateHandler(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.m_stb = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_update(self):
        bodies = {
            "*line1\n*line2\n*line3": "* line1\n* line2\n* line3",
            "*line1\r\n*line2\r\n*line3": "* line1\n* line2\n* line3",
            "*line1\r\n": "* line1",
            "*line1*line2 *line3": "* line1\n* line2\n* line3"}
        for body, expected in bodies.iteritems():
            message = update.UpdateHandler.get_update(body)
            self.assertEqual(message, expected)

    def test_get_urlsafe(self):
        f = update.UpdateHandler.get_urlsafe
        tests = {
            'VSU <update+ag5kZXZ@nw-vsu.appspotmail.com>': 'ag5kZXZ',
            '<update+ag5kZXZ@nw-vsu.appspotmail.com>': 'ag5kZXZ',
            'update+ag5kZXZ@ns-vsu.appspotmail.com': 'ag5kZXZ',
        }
        urlsafe = 'ag5kZXZ'
        for address, urlsafe in tests.iteritems():
            self.assertEqual(f(address), urlsafe)

    def test_process_update(self):
        f = update.UpdateHandler.process_update

        # Create SubscriberUpdate
        date = datetime.datetime.now()
        x = model.SubscriberUpdate.get_or_insert(
            'mark', 'mark@ekivemark.com', 'vsu', date)
        urlsafe = x.key.urlsafe()
        address = 'VSU <update+%s@ns-vsu.appspotmail.com>' % urlsafe
        body = '* did nothing\n* met nobody'
        f(address, body)

        # Check that the update message made it
        key_name = '%s+%s+%s' % ('vsu',
                                 'mark@ekivemark.com',
                                 date.isoformat())
        x = model.SubscriberUpdate.get_by_id(key_name)
        self.assertIsNotNone(x)
        self.assertEqual(x.message, body)


class TestCronDigestHandler(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.m_stb = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_update(self):
        f = cron.CronDigestHandler.get_update
        update = f(model.SubscriberUpdate(name='mark',
                                          mail='mark@ekivemark.com',
                                          message='* dude'))
        self.assertEqual(update,
                         'mark <mark@ekivemark.com>\n* dude\n\n')

    def test_get_digest_message(self):
        f = cron.CronDigestHandler.get_digest_message
        date = datetime.datetime.now()
        msg = f('vsu',
                'digest',
                date,
                'mark@ekivemark.com')
        msg.send()
        messages = self.m_stb.get_sent_messages(to='mark@ekivemark.com')
        self.assertEqual(1, len(messages))
        message = messages[0]
        self.assertEqual('mark@ekivemark.com', message.to)
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        self.assertEqual(body, 'digest')

    def test_get_subscriber_update(self):
        f = cron.CronDigestHandler.get_subscriber_updates
        date = datetime.datetime.now()
        x = model.SubscriberUpdate.get_or_insert(name='mark',
                                                 team='vsu',
                                                 mail='mark@ekivemark.com',
                                                 date=date)
        x.message = '* dude'
        x.put()

        x = model.SubscriberUpdate.get_or_insert(name='mark',
                                                 team='vsu',
                                                 mail='mark@ekivemark.com',
                                                 date=date)
        updates = f('vsu', date)
        self.assertEqual(len(updates), 1)
        self.assertEqual(updates[0].message, '* dude')

    def test_process_digest(self):
        f = cron.CronDigestHandler.process_digest

        # Test no latest update
        f('vsu')
        self.assertIsNone(model.SubscriberDigest.query().get())
        self.assertEqual([],
                         self.m_stb.get_sent_messages(to='mark@ekivemark.com'))

        # Test has update but no subscribers
        date = datetime.datetime.now()
        model.Update.get_or_insert('vsu',
                                   date)
        f('vsu')
        self.assertIsNone(model.SubscriberDigest.query().get())
        self.assertEqual([],
                         self.m_stb.get_sent_messages(to='mark@ekivemark.com'))

        # Test has update and subscriber but no digest
        model.Subscriber.get_or_insert(name='dan',
                                       team='vsu',
                                       mail='mark@ekivemark.com',
                                       status='subscribe')
        digest = f('vsu',
                   test=True)
        self.assertIsNone(model.SubscriberDigest.query().get())
        self.assertIs(digest, '')
        self.assertEqual([],
                         self.m_stb.get_sent_messages(to='mark@ekivemark.com'))

        # Test has update and subscriber and digest
        x = model.SubscriberUpdate.get_or_insert(name='dan',
                                                 team='vsu',
                                                 mail='mark@ekivemark.com',
                                                 date=date)
        x.message = '* dude'
        x.put()
        digest = f('vsu')
        key_name = '%s+%s+%s' % ('vsu',
                                 'mark@ekivemark.com',
                                 date.isoformat())
        sd = model.SubscriberDigest.get_by_id(key_name)
        self.assertIsNotNone(sd)
        self.assertTrue(sd.sent)
        self.assertEqual(digest,
                         'dan <dan@hammer.com>\n* dude\n\n')
        self.assertNotEqual([],
                            self.m_stb.get_sent_messages(to='mark@ekivemark.com'))


class TestCronUpdateHandler(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

    def tearDown(self):
        self.testbed.deactivate()

    def test_get_reply_address(self):
        f = cron.CronUpdateHandler.get_reply_address
        urlsafe = 'foo'
        expected = 'VSU <update+%s@pif-update.appspotmail.com>' % urlsafe
        self.assertEqual(expected, f(urlsafe))

    def test_get_update_message(self):
        f = cron.CronUpdateHandler.get_update_message
        team = 'vsu'
        to = 'daniel.hammer@gsa.gov'
        sender = 'update+foo@nw-vsu.appspotmail.com'
        date = datetime.datetime.now()
        msg = f(team, to, sender, date)
        msg.send()
        messages = self.mail_stub.get_sent_messages(to='daniel.hammer@gsa.gov')
        self.assertEqual(1, len(messages))
        message = messages[0]
        self.assertEqual('daniel.hammer@gsa.gov', message.to)
        self.assertEqual(
            'update+foo@nw-vsu.appspotmail.com', message.sender)
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        self.assertIsNot(body, '')

    def test_process_subscriber_update(self):
        f = cron.CronUpdateHandler.process_subscriber_update
        data = dict(name='dan', mail='mark@ekivemark.com', team='vsu',
                    status='subscribe', role='admin')
        sub = model.Subscriber.get_or_insert(**data)
        date = datetime.datetime.now()

        f(date, sub)

        key_name = '%s+%s+%s' % ('vsu',
                                 'mark@ekivemark.com',
                                 date.isoformat())
        subup = model.SubscriberUpdate.get_by_id(key_name)
        self.assertTrue(subup.sent)

        messages = self.mail_stub.get_sent_messages(to='mark@ekivemark.com')
        self.assertEqual(1, len(messages))
        message = messages[0]
        self.assertEqual('mark@ekivemark.com', message.to)
        expect = "Just reply with a few brief bullets starting with *"
        body = [b.decode() for t, b in message.bodies('text/plain')][0]
        self.assertEqual(expect, body)

    def test_process_update(self):
        f = cron.CronUpdateHandler.process_update
        data = [dict(name='dan', mail='mark@ekivemark.com', team='vsu',
                     status='subscribe', role='admin'),
                dict(name='aaron', mail='aaron@hammer.com', team='vsu',
                     status='subscribe')]
        date = datetime.datetime.now()
        for x in data:
            model.Subscriber.get_or_insert(**x)

        f('vsu', date)
        subups = model.SubscriberUpdate.get_updates(date, 'vsu')
        self.assertEqual(len(subups), 2)


class TestAdminHandler(unittest.TestCase):

    def setUp(self):
        self.testbed = testbed.Testbed()
        self.testbed.activate()
        self.testbed.init_datastore_v3_stub()
        self.testbed.init_memcache_stub()
        self.testbed.init_mail_stub()
        self.mail_stub = self.testbed.get_stub(testbed.MAIL_SERVICE_NAME)

        self.body = 'mark,mark@ekivemark.com,vsu,subscribe,admin\n'
        self.body += '\nmark,mark@healthca.mp,vsu,subscribe'

    def tearDown(self):
        self.testbed.deactivate()

    def test_is_admin(self):
        f = admin.AdminHandler.is_admin
        map(self.assertTrue,
            map(f, ['mark@ekivemark.com', 'mark@healthca.mp']))
        self.assertFalse(f('wannabe@admin.com'))

    def test_get_subscriptions(self):
        f = admin.AdminHandler.get_subscriptions
        subs = [x for x in f(self.body)]
        sub = dict(name='mark', mail='mark@ekivemark.com', team='vsu',
                   status='subscribe', role='admin')
        self.assertIn(sub, subs)
        sub = dict(name='mark', mail='mark@healthca.mp', team='vsu',
                   status='subscribe')
        self.assertIn(sub, subs)
        self.assertTrue(len(subs) == 2)

    def test_update_subscriptions(self):
        f = admin.AdminHandler.update_subscription

        # Create new subscription
        data = dict(name='mark', mail='mark@ekivemark.com', team='vsu',
                    status='subscribe', role='admin')
        f(data)
        sub = model.Subscriber.get_by_id('mark@ekivemark.com+gfw')
        expected = dict(name='mark', mail='mark@ekivemark.com', team='vsu',
                        status='subscribe', role='admin')
        self.assertDictContainsSubset(sub.to_dict(), expected)

        # Update existing subscription
        data = dict(name='MARK', mail='mark@ekivemark.com', team='vsu',
                    status='subscribe')
        f(data)
        sub = model.Subscriber.get_by_id('mark@ekivemark.com+gfw')
        expected = dict(name='mark', mail='mark@ekivemark.com', team='vsu',
                        status='subscribe', role=None)
        self.assertDictContainsSubset(sub.to_dict(), expected)

if __name__ == '__main__':
    reload(update)
    reload(admin)
    reload(cron)
    reload(model)
    unittest.main(exit=False)

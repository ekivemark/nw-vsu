#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
#from settings import VERSION, RELEASE
VERSION = "2.4"
RELEASE = ".20"
# Remember to change times in message below to match cron timetable


class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html>'
                            '<head>'
                            '<link rel="icon" type="image/x-icon" href="http://www.newwave.io/wp-content/uploads/2016/01/NWfavicon.ico" />'
                            '</head>'
                            '<body>'
                            '<a href="http://newwave.io">'
                            '<img src="https://share.newwave-technologies.com/Home/Style%20Library/'
                            'CustomBranding/images/NWT%20Logo.jpg"></a><br/>'
                            '<b><font size="6">Virtual Stand-Up</font><br/> '
                            '[V:'
                            +str(VERSION)+str(RELEASE)+']</b>: '
                            'Share your progress.<br/>')
        self.response.write('Update Requests are sent every weekday morning '
                            'at 8:00am ET. <br/>'
                            'The subject line is prefixed with [VSU].<br/>')
        self.response.write('Consolidated digests are sent out the '
                            'same day at 12:30pm ET.<br/>')
        self.response.write('Start each item with a * .<br/>'
                            'Keep items brief (A single line per bullet is best).<br/>')
        self.response.write('To link to JIRA use #JIRA followed by JIRA '
                            'Task Id. eg. #JIRA CFFB-21. <br/>'
                            'Group bullets by topic using #Hashtags.<br/>' )
        self.response.write('If you send multiple email replies in a '
                            'single day only the last one received before the digest is published is reported.'
                            '<br/>'
                            "Don't reuse a previous day's message. The Id in the 'reply to' address changes every day.<br/>"
                            '</body></html>')

app = webapp2.WSGIApplication([ ('/', MainHandler) ], debug=True)

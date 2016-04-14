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
from .settings import VERSION, RELEASE

class MainHandler(webapp2.RequestHandler):
    def get(self):
        self.response.write('<html><body><b>Team updater [V:%s%s]</b>: Share your progress.<br/>' % (VERSION, RELEASE))
        self.response.write('Updates are sent every Monday and Thursday morning at 9:00am.<br/>')
        self.response.write('Consolidated digests are sent the same evening at 5:00pm.<br/>')
        self.response.write('If you send multiple email replies in a single day only the last one is recorded.<br/></body></html>')

app = webapp2.WSGIApplication([ ('/', MainHandler) ], debug=True)

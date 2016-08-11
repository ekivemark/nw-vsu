## What is this?

This is a lightweight project to provide a virtual standup report out that
works across organizations using simple email.
Every weekday morning, VSU Subscribers will receive an e-mail asking 
for updates or blockers 
-- anything that they want to share with the group. Keep the updates brief. 
Single line bullet points are best.

Each member replies to the e-mail, and at 12:30 the same day 
a digest e-mail is sent out to the group.

To subscribe people to the update, admins (Mark) 
subscribe people over email by sending the APP a request. 
For example, to subscribe Chris and Niel, 
we send this to our messaging server via `admin@nw-vsu.appspotmail.com`:

    Chris Kox, chris.kox@cms.hhs.gov, vsu, subscribe  
    Niel Bannon, niel.bannonw@cms.hhs.gov, vsu, subscribe


Oops. Chris needs to be an admin and Niel wants to unsubscribe. No problem:


    Chris Kox, chris.kox@cms.hhs.gov, vsu, subscribe, admin

    Niel Bannon, niel.bannon@cms.hhs.gov, vsu, subscribe, bbtu, unsubscribe

The server sends back a confirmation email each time with a summary of subscriptions:

    Your changes were saved:

    Chris Kox, chris.kox@cms.hhs.gov, vsu, subscribe, admin

    Niel Bannon, niel.bannon@cms.hhs.gov, vsu, subscribe, bbtu, unsubscribe


Note that this project supports multiple teams, 
so that as long as the cron jobs are appropriately specified, 
you can use this project for other teams.  
So, for example, you can swap out `vsu` in the admin e-mails for 
`ccw` or whatever.

That's it. Pretty simple. 

## Current Version

version: **v2.4-21**

Suppress Add CRON_DIGEST_TIME to Update Message.
Added not for CRON_DIGEST_TIME in cron.py
Added , between fields in admin response message for easier reprocessing

version: **v2.4-20**

Suppress JIRA URL if no #JIRA in digest message

version: **v2.4-19**

Changed Cron jobs to 08:00 and 12:30 EDT

(set in app.yaml and in settings.py.VERSION)
If VERSION is changed in app.yaml go to the Google App Engine Dashboard and 
change the application version that is serving traffic.

Change RELEASE in settings.py to publish minor version information.


## Home Page

http://nw-vsu.appspot.com

## New Feature

Prefix a JIRA Task-Id from https://nwtjira.atlassian.net with #JIRA and the 
VSU Digest will add a hyperlink to the task in the Digest report
eg. 
    * Working on a new task #JIRA CBBP-45
        

## Hashtag summary support

The Digest now supports Hashtags. If you include a hashtag eg. #BBonFHIR in a bullet
the digest process will pull all #hashtags and include them in a Highlight section 
at the bottom of the digest email. 

* I just built a really #Awesome feature


## Bullet Point Convention

Each item in an email reply should begin with an asterisk (*).
The following convention is proposed for highlights.

*  = Standard bullet item
*^ = Completed Item
*! = Priority Item or issue

[DONE] = End of items

The email message that is sent out contains the following message to reply to:


   Just reply with a few brief bullets starting with *.  
   Start line with *^ to identify completed item.  
   Start line with *! to identify priority item or issue.  
   Use #hashtag to indicate a category. eg. #BBonFHIR or #HAPI.  
   Finish with [DONE] if there is extraneous or quoted text at the end of the e-mail reply.  
   If you send send more than 1 email the last sent email is used. [VSU-V:2.4]  
 
 
## Next Feature(s)

1. Summarize completed items (line starts with "*^")
2. Summarize Priority items or issues (line starts with "*!")
 
3. Enable subscribe to Digest sub-section report.
eg. Subscribe to Priority Items/Issues or Subscribe to #Hashtag report

## Developing

This project rides on the Google App Engine Python SDK runtime. 
After it's installed locally and on your path:

```bash
$ cd nw-vsu
$ dev_appserver.py --clear_datastore=true --show_mail_body=true .
```

Endpoints will be available at http://localhost:8080 and 
the admin console will be available at http://localhost:8000. 

You can send update and admin emails using the admin form at http://localhost:8000/mail. 
For update emails, the reply-to address must match the reply-to address in the update reminder 
email that gets sent. Watch the dev console for the address.

App Engine admins can manually invoke the `/cron/update` endpoint to send out update emails. 
Similarly they can invoke the `/cron/digest` endpoint to trigger the digest email. 
You can also hit `/cron/digest?test=true` to get an HTML response message with the digest.

A standard development progression follows:

1. Navigate to the Inbound Mail tab at `localhost:8000` and send an e-mail 
with an admin as the sender to `admin@nw-vsu.appspotmail.com` 
with a line resembling `mark,mark@ekivemark.com,vsu,subscribe`.  
Check that `mark` was added to the datastore by navigating 
to `localhost:8000/datastore?kind=Subscriber`.
2. In a separate tab, navigate to `http://localhost:8080/cron/update/vsu`.  
Copy the `Reply-to:` address in your console, which will look like `update+ahJkZXZ...` 
and paste it into the `To:` line at `localhost:8000/mail`.  
In the from line, paste the subscriber e-mail, in this case `mark@ekivemark.com`.  
In the message body, type an example update with each line preceded by `*`.  
3. Navigate to `localhost:8080/cron/digest/vsu` to send the digest to the team 
(of only one person, currently).  
The digest body will appear in the console.  

Push to production with `appcfg.py update --oauth2 .`, as long as you have permissions 
(granted by [**@ekivemark**](https://github.com/ekivemark)).



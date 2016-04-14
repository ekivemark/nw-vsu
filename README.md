## What is this?

This is a lightweight project to collect and process BlueButton team snippets.  
Every Monday morning, the current BBOnFHIR Team will receive an e-mail asking for updates or blockers 
-- anything that they want to share with the group.  
Each member replies to the e-mail, and at the end of the day, 
a digest e-mail is sent out to the group.

To subscribe people on the team, admins (Mark and Karl) 
subscribe people over email by sending the APP a request. 
For example, to subscribe Chris and Niel, 
we send this to our messaging server via `admin@bb-team-update.appspotmail.com`:

    Chris Kox, chris.kox@cms.hhs.gov, bbtu, subscribe  
    Niel Bannon, niel.bannonw@cms.hhs.gov, bbtu, subscribe


Oops. Chris needs to be an admin and Niel wants to unsubscribe. No problem:


    Chris Kox, chris.kox@cms.hhs.gov, bbtu, subscribe, admin

    Niel Bannon, niel.bannon@cms.hhs.gov, bbtu, subscribe, bbtu, unsubscribe

The server sends back a confirmation email each time with a summary of subscriptions:

    Your changes were saved:

    Chris Kox, chris.kox@cms.hhs.gov, bbtu, subscribe, admin

    Niel Bannon, niel.bannon@cms.hhs.gov, bbtu, subscribe, bbtu, unsubscribe


Note that this project supports multiple teams, 
so that as long as the cron jobs are appropriately specified, 
you can use this project for other teams.  
So, for example, you can swap out `bbtu` in the admin e-mails for `ccw` or whatever.

That's it. Pretty simple. 

## Current Version

version: **v2-3**
(set in app.yaml and in settings.py.VERSION)


## Home Page

http://bb-team-update.appspot.com

## New Feature

The Digest now supports Hashtags. If you include a hashtag eg. #BBonFHIR in a bullet
the digest process will pull all #hashtags and include them in a Highlight section 
at the bottom of the digest email. 

* I just built a really #Awesome feature


## Bullet Point Convention

Each item in an email reply should begin with an asterisk (*).
The following convention is proposed for highlights.

*  = Standard bullet item
** = Completed Item
*! = Priority Item or issue

[DONE] = End of items

The email message that is sent out contains the following message to reply to:


   Just reply with a few brief bullets starting with *.  
   Start line with ** to identify completed item.  
   Start line with *! to identify priority item or issue.  
   Use #hashtag to indicate a category. eg. #BBonFHIR or #HAPI.  
   Finish with [DONE] if there is extraneous or quoted text at the end of the e-mail reply.  
   If you send send more than 1 email the last sent email is used. [BBTU-V:2.3]  
 
 
## Next Feature(s)

1. Summarize completed items (line starts with "**")
2. Summarize Priority items or issues (line starts with "*!")
 
3. Enable subscribe to Digest sub-section report.
eg. Subscribe to Priority Items/Issues or Subscribe to #Hashtag report

## Developing

This project rides on the Google App Engine Python SDK runtime. 
After it's installed locally and on your path:

```bash
$ cd bb-team-update
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

1. Navigate to the Inbound Mail tab at `localhost:8000` and send an e-mail with an admin as the 
sender to `admin@bb-team-update.appspotmail.com` with a line resembling `mark,mark@ekivemark.com,bbtu,subscribe`.  
Check that `mark` was added to the datastore by navigating to `localhost:8000/datastore?kind=Subscriber`.
2. In a separate tab, navigate to `http://localhost:8080/cron/update/bbtu`.  
Copy the `Reply-to:` address in your console, which will look like `update+ahJkZXZ...` and paste it 
into the `To:` line at `localhost:8000/mail`.  
In the from line, paste the subscriber e-mail, in this case `mark@ekivemark.com`.  
In the message body, type an example update with each line preceded by `*`.  
3. Navigate to `localhost:8080/cron/digest/bbtu` to send the digest to the team 
(of only one person, currently).  
The digest body will appear in the console.  

Push to production with `appcfg.py update --oauth2 .`, as long as you have permissions 
(granted by [**@ekivemark**](https://github.com/ekivemark)).



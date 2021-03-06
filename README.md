# Welcome to byemail

[![Build](https://travis-ci.org/jrmi/byemail.svg?branch=master)](https://travis-ci.org/jrmi/byemail)
[![Build](https://badge.fury.io/py/byemail.svg)](https://badge.fury.io/py/byemail)
[![GitHub license](https://img.shields.io/github/license/jrmi/byemail.svg)](https://github.com/jrmi/byemail/blob/master/LICENSE)
[![Build](https://img.shields.io/pypi/wheel/byemail.svg)](https://github.com/jrmi/byemail)
[![Build](https://img.shields.io/badge/python-3.7-blue.svg)](https://github.com/jrmi/byemail)
[![Build](https://img.shields.io/pypi/status/byemail.svg)](https://github.com/jrmi/byemail)

# What is it ?

Byemail is a complete stack for a personal mail system including SMTP receiver, sender, webmail,
mailing list and more. Install only one tool to rules them all.

E-mails are still a popular means of communication today. We use email to communicate in company, to send messages to our friends, to keep in touch with family members, etc.
Despite the explosion of social networks and new means of communication, the mail system still has a bright future ahead of it.

If we believe in the decentralization of the web, it is difficult to believe that most emails are managed by a handful of private companies that lead the market. Why ?

Because, despite their long existence and the dependence of a large part of the population,
mail servers are still difficult to install, configure and maintain mainly because they implement features that are not necessary for most end users and their architecture is no longer adapted to today's uses.

To create a complete mail system, we have to install a SMTP server to receive/send emails then an IMAP or POP3 server to gather the mails and finally a client to read them. Don't forget to configure your DNS and pray that your IP will not be banned for misuse.

To fulfill all ours needs we also need to add modules like:

-   a user account manager
-   a spam filter,
-   a webmail,
-   a mailing list manager,
-   ...

All this results in a complex system to set up and which requires great skills to administrate, not to mention the many security vulnerabilities that can be created without even noticing it. All the people who tried the adventure were afraid to create an open relay SMTP server so used by spammers or to be marked as spam from major mail systems.

Byemail is **fully compatible** with the current email system but the objective is to create a simpler and more secure stack first,
then add functionality that is currently inaccessible due to the complexity of the architecture and the aging of the technology to meet the expectations of users with new needs.

With Byemail, you install only one tool for your email communication.
Some common use cases on the roadmap:

-   Access your webmail from everywhere,
-   Receiving and sending mail for a family or small business,
-   Create a mailing list on the fly,
-   Share huge attachment without thinking of it and without flooding the net,
-   Send "burn after reading" email,
-   Cancel mail sent by mistake,
-   Create temporary address on the fly for spam protection,
-   Really secure mail even if the recipient doesn't have configured any gpg key,
-   Auto update your DNS configuration,
-   Spam protect you with captcha,
-   Easy quitting by easily export all your data to import them in another instance,
-   ActivityPub compatibility,
-   Scheduled mails
-   Scheduled mail acknowledgment (for privacy concern)
-   and more ...

Some technical advantages:

-   Easy backup: you only have one directory to save,
-   Easy configuration, everything in one python file,
-   Middleware to filter/modify/... incoming and outgoing mails,
-   Secure by design, open relay can't be done at all,
-   Use DKIM, SPF, DMARC to allow better receivability,
-   ...

# Installation

You can install byemail in a virtualenv by doing a:

```sh
$ pip install byemail
```

Create and move to any directory, then execute:

```sh
$ byemail init
```

A new set of file are created in the current directory.
Now **Customize the settings.py**. You should at least add one account using the
given example in the file.

Then execute:

```sh
$ byemail start
```

You can now log to http://<host>:<port> to check new mails. Mail can be send to http://<host>:8025.

To configure your DNS correctly, execute:

```sh
$ byemail dnsconfig
```

And copy (and adapt if necessary) the command result to your domain dns config.

As root you can make a tunnel to the 25 port without root permission for the server by doing:

```sh
$ socat tcp-listen:25,reuseaddr,fork tcp:<hostname>:8025 > nohupsocket.out &
```

DISCLAIMER: This is an early functional version.
Don't hope using it in production for now but don't be afraid to try it and
help us.

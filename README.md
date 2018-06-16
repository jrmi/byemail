# What is it ?

Byyemail is a Complete stack for a personnal mail system including SMTP receiver, sender, webmail,
mailing list and more. Install only one tool to rules them all.

Nowadays, mail servers are difficult to install, configure and maintains because they can do a lot of things
that are unnecessary for most end users. We also need to add module like:

- a spam filter,
- a webmail,
- a mailing list manager,
- ...

All this is planned to be part of the same software.

The webmail is also think with need of today. For example, mails are organised by contact and
group of discussion. No need to search in your archive what your contact wrote six month earlier,
it's in the current message flow, like sms.

With byemail, you install only one tool for everything.
Some use cases:

- Receiving mail for a family or small business,
- Access your mail anywhere with integrated webmail,
- Create a mailing list on the go,
- and more ...

Advantages:

- Easy backup: you only have one directory to save.
- Easy configuration, everything in one file.
- For small groups like famillies or small compagnies

# Installation

First install byemail to a virtualenv:

```sh
$ pipenv install byemail
```

After creating and moving to any directory, execute:

```sh
$ byemail init
```
A new set of file are created in the current directory. Customize the settings.py file for your needs then execute:

```sh
$ byemail start
```

You can now log to http://<host>:<port> to check new mails. Mail can be send to http://<host>:8025.


To configure your DNS correctly, execute:

```sh
$ byemail dnsconfig
```

And copy (and adapt if necessary) the command result to your domain dns config.


DISCLAIMER: This is a early not functionnal version. Don't hope use it in production now.

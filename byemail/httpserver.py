import os
import asyncio
import datetime
import logging
import uuid
import mimetypes
import base64
from collections import defaultdict

from sanic import Sanic
from sanic.response import json, redirect, stream, file_stream, text
from sanic_auth import Auth
from sanic.exceptions import Forbidden, NotFound

from byemail.storage import storage
from byemail.smtp import MsgSender
from byemail.account import account_manager
from byemail import mailutils
from byemail.conf import settings
from byemail.smtp import send_mail, resend_mail
from byemail import push

logger = logging.getLogger(__name__)

sessions = defaultdict(dict)

app = None


def gen_session_key():
    return uuid.uuid4().hex


def handle_no_auth(request):
    raise Forbidden("This route need authentification")


def get_app():
    if app is None:
        init_app()
    return app


def init_app():
    global app
    app = Sanic(__name__, log_config=None)
    app.config.log_config = None
    app.config.AUTH_LOGIN_ENDPOINT = "login"

    BASE_DIR = os.path.dirname(__file__)

    # Static routes
    app.static("/index.html", os.path.join(BASE_DIR, "../client/dist/index.html"))
    app.static("/favicon.ico", os.path.join(BASE_DIR, "../client/dist/favicon.ico"))
    app.static("/manifest.json", os.path.join(BASE_DIR, "../client/dist/manifest.json"))
    app.static("/robots.txt", os.path.join(BASE_DIR, "../client/dist/robots.txt"))
    app.static(
        "/service-worker.js", os.path.join(BASE_DIR, "../client/dist/service-worker.js")
    )
    app.static("/img", os.path.join(BASE_DIR, "../client/dist/img"))
    app.static("/js", os.path.join(BASE_DIR, "../client/dist/js"))
    app.static("/css", os.path.join(BASE_DIR, "../client/dist/css"))

    auth = Auth(app)
    auth.user_loader(account_manager.get)

    # Dynamic manifest route
    @app.route("/precache-manifest.<manifest_id>.js", stream=True)
    async def precache_manifest(request, manifest_id):
        path = os.path.join(
            BASE_DIR, f"../client/dist/precache-manifest.{manifest_id}.js"
        )

        if os.path.exists(path):
            return await file_stream(path)
        else:
            raise NotFound(f"{path} not found")

    @app.middleware("request")
    async def add_session_to_request(request):
        # setup session
        session_key = request.cookies.get("session_key")

        if session_key:
            request["session"] = await storage.get_user_session(session_key)
        else:
            request["session"] = {}

    @app.middleware("response")
    async def add_session_key_to_response(request, response):
        # add default session key if not existing
        auth_key = request.cookies.get("session_key")
        if auth_key is None and response.cookies.get("session_key") is None:
            session_key = gen_session_key()
            response.cookies["session_key"] = session_key

    @app.route("/login", methods=["POST"])
    async def login(request):
        credentials = request.json
        # get user account from credentials
        account = account_manager.authenticate(credentials)

        if account:
            session_key = gen_session_key()

            session = await storage.get_user_session(session_key)
            session[auth.auth_session_key] = account.name
            await storage.save_user_session(session_key, session)

            response = json(account.to_json())
            # Add session key to response
            response.cookies["session_key"] = session_key

            return response

        raise Forbidden("Authentification failed. Check your credentials.")

    @app.route("/logout")
    @auth.login_required(handle_no_auth=handle_no_auth)
    async def logout(request):
        auth.logout_user(request)
        request["session"] = {}
        response = json("Ok")
        response.cookies["session_key"] = gen_session_key()
        return response

    @app.route("/api/account")
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def account(request, account):
        return json(account.to_json())

    @app.route("/")
    async def index(request):
        return redirect("/index.html")

    @app.route("/api/mailboxes")
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def mailboxes(request, account):
        mbxs = await storage.get_mailboxes(account)

        for mb in mbxs:
            if mb["last_message"]:
                mb["last_message"] = mb["last_message"].isoformat()

        return json(mbxs)

    @app.route("/api/mailbox/<mailbox_id>")
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def mailbox(request, mailbox_id, account):
        mailbox_to_return = await storage.get_mailbox(account, mailbox_id)

        for msg in mailbox_to_return["messages"]:
            msg["date"] = msg["date"].isoformat()

        return json(mailbox_to_return)

    @app.route("/api/mail/<mail_id>")
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def mail(request, mail_id, account):
        mail_to_return = await storage.get_mail(account, mail_id)

        for att in mail_to_return["attachments"]:
            if not att.get("filename"):
                guessed_ext = mimetypes.guess_extension(att["type"])
                if not guessed_ext:
                    guessed_ext = ".bin"
                att["filename"] = "file_{}{}".format(att["index"], guessed_ext)
            att["url"] = "/api/mail/{}/attachment/{}/{}".format(
                mail_id, att["index"], att["filename"]
            )

        mail_to_return["date"] = mail_to_return["date"].isoformat()

        # Change link to attached file

        await mailutils.convert_cid_link(mail_to_return)

        return json(mail_to_return)

    @app.route("/api/mail/<mail_id>/mark_read", methods=["POST"])
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def mail_mark_read(request, mail_id, account):
        mail_to_mark = await storage.get_mail(account, mail_id)

        mail_to_mark["unread"] = False

        await storage.update_mail(account, mail_to_mark)

        return json(mail_to_mark)

    @app.route("/api/mail/<mail_id>/attachment/<att_index>/<filename>", methods=["GET"])
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def mail_download_attachment(request, mail_id, att_index, filename, account):
        attachment, att_content = await storage.get_mail_attachment(
            account, mail_id, int(att_index)
        )

        async def streaming_att(response):
            await response.write(att_content)

        return stream(streaming_att, content_type=attachment["type"])

    @app.route("/api/sendmail/", methods=["POST"])
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def sendmail(request, account):
        """ Send an email """
        data = request.json

        from_addr = mailutils.parse_email(account.address)
        all_addrs = [mailutils.parse_email(a["address"]) for a in data["recipients"]]
        tos = [
            mailutils.parse_email(a["address"])
            for a in data["recipients"]
            if a["type"] == "to"
        ]
        ccs = [
            mailutils.parse_email(a["address"])
            for a in data["recipients"]
            if a["type"] == "cc"
        ]

        attachments = data.get("attachments", [])

        msg = mailutils.make_msg(
            data["subject"], data["content"], from_addr, tos, ccs, attachments
        )

        result = await send_mail(account, msg, from_addr, all_addrs)

        return json(result)

    @app.route("/api/mail/<mail_id>/resend", methods=["POST"])
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def mail_resend(request, mail_id, account):
        """ Resend an email by uid for selected recipient"""

        mail_to_resend = await storage.get_mail(mail_id)

        # Check permissions
        if mail_to_resend["account"] != account.name:
            raise Forbidden("You don't have permission to resend this mail.")

        data = request.json
        tos = [mailutils.parse_email(data["to"])]

        result = await resend_mail(account, mail_to_resend, tos)

        return json(result)

    @app.route("/api/contacts/search", methods=["GET"])
    @auth.login_required(user_keyword="account", handle_no_auth=handle_no_auth)
    async def contacts_search(request, account):
        text = request.args.get("text", "")

        if not text:
            return json([])

        results = await storage.contacts_search(account, text)

        return json(results)

    @app.get("/api/subscription/")
    # @auth.login_required(user_keyword='account', handle_no_auth=handle_no_auth)
    async def subscription_get(request):
        """
        GET returns vapid public key which clients uses to send around push notification
        """
        pub = push.get_application_server_key()

        return text(pub, headers={"Access-Control-Allow-Origin": "*"})

    @app.post("/api/subscription/")
    # @auth.login_required(user_keyword='account', handle_no_auth=handle_no_auth)
    async def subscription_post(request):
        """
        POST creates a subscription
        """

        subscription_token = request.json["subscription"]

        # TODO add subscription for this user
        push.send_web_push(subscription_token, "data graammm")

        return json({}, status=201)

    @app.post("/api/unsubscription/")
    # @auth.login_required(user_keyword='account', handle_no_auth=handle_no_auth)
    async def unsubscription_post(request):
        """
        POST creates a subscription
        """

        subscription_token = request.json["subscription"]

        # TODO Remove subscription for this account
        print(subscription_token)

        return json({}, status=201)

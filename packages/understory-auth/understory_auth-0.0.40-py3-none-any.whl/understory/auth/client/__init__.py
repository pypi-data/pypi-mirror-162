"""IndieAuth client."""

import web
from web import tx

from ..util import generate_challenge

__all__ = ["initiate_sign_in", "authorize_sign_in", "sign_out"]

__all__ = ["app"]

app = web.application(
    __name__,
    prefix="guests",
    model={
        "guests": {
            "url": "TEXT",
            "name": "TEXT",
            "email": "TEXT",
            "access_token": "TEXT",
            "account_created": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
        }
    },
)


def initiate_sign_in(
    client: web.uri.URI, endpoint_path: str, user: web.uri.URI, scopes: list
) -> web.uri.URI:
    """
    Return the URI to initiate an IndieAuth sign-in at `site` for `user`.

    `site` should be the actual sign-in endpoint URI (different for each service)
    `user` should be the identity URI for the user attempting sign in

    """
    auth = web.discover_link(user, "authorization_endpoint")
    tx.user.session["authorization_endpoint"] = str(auth)
    tx.user.session["token_endpoint"] = str(web.discover_link(user, "token_endpoint"))
    tx.user.session["micropub_endpoint"] = str(web.discover_link(user, "micropub"))
    client = web.uri.parse(client)
    auth["me"] = user
    auth["client_id"] = tx.user.session["client_id"] = client
    auth["redirect_uri"] = tx.user.session["redirect_uri"] = client / endpoint_path
    auth["response_type"] = "code"
    auth["state"] = tx.user.session["state"] = web.nbrandom(16)
    code_verifier = tx.user.session["code_verifier"] = web.nbrandom(64)
    auth["code_challenge"] = generate_challenge(code_verifier)
    auth["code_challenge_method"] = "S256"
    auth["scope"] = " ".join(scopes)
    return auth


def authorize_sign_in(state, code, flow):
    """Complete the authorization and return the response."""
    if state != tx.user.session["state"]:
        raise web.BadRequest("bad state")
    if flow == "profile":
        endpoint = tx.user.session["authorization_endpoint"]
    elif flow == "token":
        endpoint = tx.user.session["token_endpoint"]
    else:
        raise web.BadRequest("only `profile` and `token` flows supported")
    response = web.post(
        endpoint,
        headers={"Accept": "application/json"},
        data={
            "grant_type": "authorization_code",
            "code": code,
            "client_id": tx.user.session["client_id"],
            "redirect_uri": tx.user.session["redirect_uri"],
            "code_verifier": tx.user.session["code_verifier"],
        },
    ).json
    app.model.create_guest(response)
    return response


def sign_out(me: web.uri.URI):
    """Sign the user out by revoking the token."""
    access_token = app.model.get_guest(me)["access_token"]
    web.post(
        tx.user.session["token_endpoint"],
        data={"action": "revoke", "token": access_token},
    )


# XXX @app.wrap
# XXX def connect_model(handler, main_app):
# XXX     """Connect the model to this transaction's database."""
# XXX     # TODO store User Agent and IP address with `sessions`
# XXX     # TODO attach session to this user
# XXX     web.app.model = app.model(tx.db)
# XXX     yield


@app.control("")
class Guests:
    """Site guests."""

    def get(self):
        """Return a list of guests to owner, the current user or a sign-in page."""
        if not tx.user.session:
            return app.view.signin(tx.host.name)
        if tx.user.is_owner:
            return app.view.guests(app.model.get_guests())
        return tx.user.session  # a guest is signed in; show other guests


@app.control("sign-in")
class SignIn:
    """IndieAuth client sign in."""

    def get(self):
        """Initiate a sign-in."""
        if tx.user.session:
            raise web.SeeOther("/guests")
        form = web.form("me", return_to="/")
        tx.user.session["return_to"] = form.return_to
        raise web.SeeOther(
            initiate_sign_in(
                tx.origin, "guests/authorize", form.me, scopes=["profile", "email"]
            )
        )


@app.control("authorize")
class Authorize:
    """IndieAuth client authorization redirect URL."""

    def get(self):
        """Complete a sign-in by requesting a token."""
        # XXX TODO if tx.user.session:
        # XXX TODO     raise web.SeeOther("/guests")
        form = web.form("state", "code")
        response = authorize_sign_in(form.state, form.code, "profile")
        tx.user.session["uid"] = [response["me"]]
        tx.user.session["name"] = [response["profile"].get("name", "Anonymous")]
        raise web.SeeOther(tx.user.session["return_to"])


@app.control("sign-out")
class SignOut:
    """IndieAuth client sign out."""

    def get(self):
        """Return a sign-out form."""
        if not tx.user.session:
            raise web.SeeOther("/sign-in")
        return app.view.signout()

    def post(self):
        """Sign the guest out."""
        if not tx.user.session:
            raise web.SeeOther("/sign-in")
        form = web.form(return_to="")
        try:
            sign_out(tx.user.session["uid"][0])
        except KeyError:
            pass
        tx.user.session = None
        raise web.SeeOther(f"/{form.return_to}")


@app.query
def create_guest(db, response):
    """Add a user based upon given response."""
    profile = response.get("profile", {})
    db.insert(
        "guests",
        url=response["me"],
        name=profile.get("name"),
        email=profile.get("email"),
        access_token=response.get("access_token"),
    )


@app.query
def get_guests(db):
    """Return a list of guests."""
    return db.select("guests")


@app.query
def get_guest(db, user: web.uri.URI):
    """Return a user."""
    return db.select("guests", where="url = ?", vals=[user])[0]


# @model.migrate(1)
# def change_name(db):
#     """Rename `url` to `me` to reuse language from the spec."""
#     db.rename_column("guests", "url", "me")

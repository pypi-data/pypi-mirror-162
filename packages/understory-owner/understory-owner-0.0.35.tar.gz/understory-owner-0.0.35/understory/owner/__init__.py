"""Site ownership in the understory."""

import web
from web import tx

app = web.application(
    __name__,
    prefix="owner",
    model={
        "identities": {
            "created": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "card": "JSON",
        },
        "passphrases": {
            "created": "DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP",
            "passphrase_salt": "BLOB",
            "passphrase_hash": "BLOB",
        },
    },
)


@app.query
def get_identity(db, uid):
    """Return identity with given `uid`."""
    return db.select(
        "identities",
        where="json_extract(identities.card, '$.uid[0]') = ?",
        vals=[uid],
    )[0]


@app.query
def add_identity(db, uid, name):
    """Create an identity."""
    db.insert("identities", card={"uid": [uid], "name": [name]})


@app.query
def get_passphrase(db):
    """Return most recent passphrase."""
    return db.select("passphrases", order="created DESC")[0]


@app.query
def update_passphrase(db):
    """Update the passphrase."""
    passphrase_salt, passphrase_hash, passphrase = web.generate_passphrase()
    db.insert(
        "passphrases",
        passphrase_salt=passphrase_salt,
        passphrase_hash=passphrase_hash,
    )
    return passphrase


@app.wrap
def initialize_owner(handler, main_app):
    """Ensure an owner exists and add their details to the transaction."""
    try:
        tx.host.owner = app.model.get_identity(tx.origin)["card"]
    except IndexError:
        web.header("Content-Type", "text/html")
        app.model.add_identity(tx.origin, "Anonymous")
        passphrase = " ".join(app.model.update_passphrase())
        tx.host.owner = tx.user.session = app.model.get_identity(tx.origin)["card"]
        tx.user.is_owner = True
        if kiosk := web.form(kiosk=None).kiosk:
            with open(f"{kiosk}/passphrase", "w") as fp:
                fp.write(passphrase)
            raise web.SeeOther("/")
        raise web.Created(app.view.claimed(tx.origin, passphrase), tx.origin)
    is_owner = tx.user.session.get("uid", [None])[0] == tx.origin
    try:
        tx.user.is_owner = is_owner
    except (AttributeError, KeyError, IndexError):
        tx.user.is_owner = False
    yield


@app.wrap
def authorize_owner(handler, main_app):
    """Manage access to owner-only resources."""
    if not tx.user.is_owner and tx.request.method.lower() in getattr(
        handler, "owner_only", []
    ):
        raise web.Unauthorized(app.view.unauthorized())
    yield


@app.control("")
class Owner:
    """Owner information."""

    owner_only = ["get"]

    def get(self):
        """Render site owner information."""
        return app.view.index()


@app.control(r"sign-in")
class SignIn:
    """Sign in as the owner of the site."""

    def get(self):
        """Verify a sign-in or render the sign-in form."""
        try:
            self.verify_passphrase()
        except web.BadRequest:
            if tx.user.is_owner:
                raise web.SeeOther("/")
            return_to = web.form(return_to="").return_to
            return app.view.signin(return_to)

    def post(self):
        """Verify a sign-in."""
        self.verify_passphrase()

    def verify_passphrase(self):
        """Verify passphrase, sign the owner in and return to given return page."""
        form = web.form("passphrase", return_to="")
        passphrase = app.model.get_passphrase()
        if web.verify_passphrase(
            passphrase["passphrase_salt"],
            passphrase["passphrase_hash"],
            form.passphrase.replace(" ", ""),
        ):
            tx.user.session = app.model.get_identity(tx.origin)["card"]
            raise web.SeeOther(f"/{form.return_to}")
        raise web.Unauthorized("bad passphrase")


@app.control("sign-out")
class SignOut:
    """Sign out as the owner of the site."""

    owner_only = ["get", "post"]

    def get(self):
        """Return the sign out form."""
        return app.view.signout()

    def post(self):
        """Sign the owner out and return to given return page."""
        tx.user.session = None
        return_to = web.form(return_to="").return_to
        raise web.SeeOther(f"/{return_to}")

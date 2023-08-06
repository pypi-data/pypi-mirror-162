"""
Post content in the understory.

Implements a [Micropub][0] server.

> The Micropub protocol is used to create, update and delete posts on
> one's own domain using third-party clients. Web apps and native apps
> (e.g. iPhone, Android) can use Micropub to post and edit articles,
> short notes, comments, likes, photos, events or other kinds of posts
> on your own website. [0]

[0]: https://micropub.spec.indieweb.org

"""

import random

import pendulum
import web

# import micropub
# import webmention
# import websub


class PostNotFoundError(Exception):
    """Post could not be found."""


app = web.application(
    __name__,
    prefix="posts",
    args={"channel": r".+", "entry": r".+"},
    model={
        "resources": {
            "permalink": "TEXT UNIQUE",
            "version": "TEXT UNIQUE",
            "resource": "JSON",
        },
        "deleted_resources": {
            "permalink": "TEXT",
            "version": "TEXT UNIQUE",
            "resource": "JSON",
        },
        "syndication": {"destination": "JSON NOT NULL"},
    },
)

# TODO supported_types = {"RSVP": ["in-reply-to", "rsvp"]}


def get_config():
    """"""
    syndication_endpoints = []
    # TODO "channels": generate_channels()}
    return {
        "q": ["category", "contact", "source", "syndicate-to"],
        "media-endpoint": f"{web.tx.origin}/media",
        "syndicate-to": syndication_endpoints,
        "visibility": ["public", "unlisted", "private"],
        "timezone": "America/Los_Angeles",
    }


def generate_trailer():
    letterspace = "abcdefghijkmnopqrstuvwxyz23456789"
    trailer = "".join([random.choice(letterspace) for i in range(2)])
    if trailer in ("bs", "ok", "hi", "oz", "lb"):
        return generate_trailer()
    else:
        return trailer


def store_mention(source, target):
    webmention.send(source, target)
    web.tx.mentions.store_sent(source, target)


@app.wrap
def linkify_head(handler, main_app):
    """."""
    yield
    if web.tx.request.uri.path == "":
        web.add_rel_links(micropub="/posts")


def route_unrouted(handler, app):  # TODO XXX ???
    """Handle channels."""
    for channel in app.model.get_channels():
        if channel["resource"]["url"][0] == f"/{web.tx.request.uri.path}":
            posts = app.model.get_posts_by_channel(channel["resource"]["uid"][0])
            web.header("Content-Type", "text/html")
            raise web.OK(app.view.channel(channel, posts))
    yield


@app.control("")
class MicropubEndpoint:
    """Your posts."""

    def get(self):
        """"""
        try:
            form = web.form("q")
        except web.BadRequest:
            return app.view.activity(
                app.model.get_channels(),
                web.application("understory.media").model.get_media(),
                app.model.get_posts(),
            )

        def generate_channels():
            return [
                {"name": r["name"][0], "uid": r["uid"][0]}
                for r in app.model.get_channels()
            ]

        # TODO XXX elif form.q == "channel":
        # TODO XXX     response = {"channels": generate_channels()}
        if form.q == "config":
            response = get_config()
        elif form.q == "source":
            response = {}
            if "search" in form:
                response = {
                    "items": [
                        {"url": [r["resource"]["url"]]}
                        for r in app.model.search(form.search)
                    ]
                }
            elif "url" in form:
                response = dict(app.model.read(form.url))
            else:
                pass  # TODO list all posts
        elif form.q == "category":
            response = {"categories": app.model.get_categories()}
        else:
            raise web.BadRequest("unsupported query. check `q=config` for support.")
        web.header("Content-Type", "application/json")
        return response

    def post(self):
        """"""
        # TODO check for bearer token or session cookie
        try:
            form = web.form("h")
        except web.BadRequest:
            try:
                resource = web.form()
            except AttributeError:  # FIXME fix web.form() raise Exc
                resource = web.tx.request.body._data
        else:
            h = form.pop("h")
            properties = {
                k.rstrip("[]"): (v if isinstance(v, list) else [v])
                for k, v in form.items()
            }
            resource = {"type": [f"h-{h}"], "properties": properties}
        try:
            action = resource.pop("action")
        except KeyError:
            permalink, mentions = app.model.create(
                resource["type"][0].partition("-")[2], **resource["properties"]
            )
            # web.header("Link", '</blat>; rel="shortlink"', add=True)
            # web.header("Link", '<https://twitter.com/angelogladding/status/'
            #                    '30493490238590234>; rel="syndication"', add=True)

            # XXX web.braid(permalink, ...)

            # TODO for mention in mentions:
            # TODO     web.enqueue(store_mention, f"{web.tx.origin}{permalink}", mention)

            # TODO web.enqueue(
            # TODO     websub.publish,
            # TODO     f"{web.tx.origin}/subscriptions",
            # TODO     f"{web.tx.origin}",
            # TODO     str(content.Homepage().get()),
            # TODO )
            raise web.Created("post created", permalink)
        if action == "update":
            url = resource.pop("url")
            app.model.update(url, **resource)
            return
        elif action == "delete":
            url = resource.pop("url")
            app.model.delete(url)
            return "deleted"
        elif action == "undelete":
            pass


@app.control("channels")
class Channels:
    """Your channels."""

    def get(self):
        """"""
        return app.view.channels(app.model.get_channels())


@app.control("channels/{channel}")
class Channel:
    """A single channel."""

    def get(self):
        """"""
        return app.view.channel(self.channel)


@app.control("syndication")
class Syndication:
    """Your syndication destinations."""

    def get(self):
        """"""
        return app.view.syndication()

    def post(self):
        """"""
        destinations = web.form()
        if "twitter_username" in destinations:
            un = destinations.twitter_username
            # TODO pw = destinations.twitter_password
            # TODO sign in
            user_photo = ""  # TODO doc.qS(f"a[href=/{un}/photo] img").src
            destination = {
                "uid": f"//twitter.com/{un}",
                "name": f"{un} on Twitter",
                "service": {
                    "name": "Twitter",
                    "url": "//twitter.com",
                    "photo": "//abs.twimg.com/favicons/" "twitter.ico",
                },
                "user": {"name": un, "url": f"//twitter.com/{un}", "photo": user_photo},
            }
            web.tx.db.insert("syndication", destination=destination)
        if "github_username" in destinations:
            un = destinations.github_username
            # TODO token = destinations.github_token
            # TODO check the token
            user_photo = ""  # TODO doc.qS("img.avatar-user.width-full").src
            destination = {
                "uid": f"//github.com/{un}",
                "name": f"{un} on GitHub",
                "service": {
                    "name": "GitHub",
                    "url": "//github.com",
                    "photo": "//github.githubassets.com/" "favicons/favicon.png",
                },
                "user": {"name": un, "url": f"//github.com/{un}", "photo": user_photo},
            }
            web.tx.db.insert("syndication", destination=destination)


@app.query
def create(db, resource_type, **resource):
    """Create a resource."""
    for k, v in resource.items():
        if not isinstance(v, list):
            resource[k] = [v]
        flat_values = []
        for v in resource[k]:
            if isinstance(v, dict):
                if not ("html" in v or "datetime" in v):
                    v = dict(**v["properties"], type=[v["type"][0].removeprefix("h-")])
            flat_values.append(v)
        resource[k] = flat_values

    config = get_config()
    # TODO deal with `updated`/`drafted`?
    if "published" in resource:
        # TODO accept simple eg. published=2020-2-20, published=2020-2-20T02:22:22
        # XXX resource["published"][0]["datetime"] = pendulum.from_format(
        # XXX     resource["published"][0]["datetime"], "YYYY-MM-DDTHH:mm:ssZ"
        # XXX )
        # XXX published = resource["published"]
        pass
    else:
        resource["published"] = [
            {
                "datetime": web.now().isoformat(),
                "timezone": config["timezone"],
            }
        ]
    published = pendulum.parse(
        resource["published"][0]["datetime"],
        tz=resource["published"][0]["timezone"],
    )

    resource["visibility"] = resource.get("visibility", ["public"])
    # XXX resource["channel"] = resource.get("channel", [])
    mentions = []
    urls = resource.pop("url", [])
    # if resource_type == "card":
    #     slug = resource.get("nickname", resource.get("name"))[0]
    # elif resource_type == "event":
    #     slug = resource.get("nickname", resource.get("name"))[0]
    #     urls.insert(0, f"/pub/cards/{web.textslug(slug)}")
    #     # if resource["uid"] == str(web.uri(web.tx.host.name)):
    #     #     pass
    #     urls.insert(0, f"/pub/cards/{web.textslug(slug)}")
    # elif resource_type == "feed":
    #     name_slug = web.textslug(resource["name"][0])
    #     try:
    #         slug = resource["slug"][0]
    #     except KeyError:
    #         slug = name_slug
    #     resource.update(uid=[slug if slug else name_slug])
    #     resource.pop("channel", None)
    #     # XXX urls.insert(0, f"/{slug}")
    if resource_type == "project":
        name = resource.get("name")[0]
        permalink = f"/code/{name}"
        urls.insert(0, permalink)
        resource.update(url=urls, type=[resource_type])
        db.insert(
            "resources",
            permalink=permalink,
            version=web.nbrandom(10),
            resource=resource,
        )
    elif resource_type == "entry":
        #                                         REQUEST URL
        # 1) given: url=/xyz                        => look for exact match
        #     then: url=[/xyz, /2021/3/5...]
        # 2) given: channel=abc, slug=foo           => construct
        #     then: url=[/2021/3/5...]
        # 3) given: no slug                         => only via permalink
        #     then: url=[/2021/3/5...]
        post_type = web.mf.discover_post_type(resource)
        slug = None
        if post_type == "article":
            slug = resource["name"][0]
        elif post_type == "bookmark":
            mentions.append(resource["bookmark-of"][0])
        elif post_type == "like":
            mentions.append(resource["like-of"][0])
        elif post_type == "rsvp":
            mentions.append(resource["in-reply-to"][0])
        # elif post_type == "identification":
        #     identifications = resource["identification-of"]
        #     identifications[0] = {"type": "cite",
        #                           **identifications[0]["properties"]}
        #     textslug = identifications[0]["name"]
        #     mentions.append(identifications[0]["url"])
        # elif post_type == "follow":
        #     follows = resource["follow-of"]
        #     follows[0] = {"type": "cite", **follows[0]["properties"]}
        #     textslug = follows[0]["name"]
        #     mentions.append(follows[0]["url"])
        #     web.tx.sub.follow(follows[0]["url"])
        # TODO user indieauth.server.get_identity() ??
        # XXX author_id = list(db.select("identities"))[0]["card"]
        # XXX author_id = get_card()db.select("resources")[0]["card"]["version"]
        resource.update(author=[web.tx.origin])

        resource.update(url=urls, type=[resource_type])
        permalink_base = f"/{web.timeslug(published)}"
        while True:
            permalink = f"{permalink_base}/{generate_trailer()}"
            resource["url"].append(permalink)
            try:
                db.insert(
                    "resources",
                    permalink=permalink,
                    version=web.nbrandom(10),
                    resource=resource,
                )
            except db.IntegrityError:
                continue
            break
    return permalink, mentions


@app.query
def read(db, url):
    """Return an entry with its metadata."""
    if not url.startswith(("http://", "https://")):
        url = f"/{url.strip('/')}"
    try:
        resource = db.select(
            "resources",
            where="""json_extract(resources.resource, '$.url[0]') == ?""",
            vals=[url],
        )[0]
    except IndexError:
        resource = db.select(
            "resources",
            where="""json_extract(resources.resource, '$.alias[0]') == ?""",
            vals=[url],
        )[0]
    r = resource["resource"]
    if "entry" in r["type"]:
        # XXX r["author"] = web.tx.identities.get_identity(r["author"][0])["card"]
        r["author"] = web.application("understory.owner").model.get_identity(
            r["author"][0]
        )["card"]
    return resource


@app.query
def update(db, url, add=None, replace=None, remove=None):
    """Update a resource."""
    permalink = f"/{url.strip('/')}"
    resource = db.select("resources", where="permalink = ?", vals=[permalink])[0][
        "resource"
    ]
    if add:
        for prop, vals in add.items():
            try:
                resource[prop].extend(vals)
            except KeyError:
                resource[prop] = vals
    if replace:
        for prop, vals in replace.items():
            resource[prop] = vals
    if remove:
        for prop, vals in remove.items():
            del resource[prop]
    resource["updated"] = web.now()
    db.update("resources", resource=resource, where="permalink = ?", vals=[permalink])
    # TODO web.publish(url, f".{prop}[-0:-0]", vals)


@app.query
def delete(db, url):
    """Delete a resource."""
    resource = app.model.read(url)
    with db.transaction as cur:
        cur.insert("deleted_resources", **resource)
        cur.delete("resources", where="permalink = ?", vals=[url])


@app.query
def search(db, query):
    """Return a list of resources containing `query`."""
    where = """json_extract(resources.resource,
                   '$.bookmark-of[0].url') == ?
               OR json_extract(resources.resource,
                   '$.like-of[0].url') == ?"""
    return db.select("resources", vals=[query, query], where=where)


@app.query
def get_identity(db, version):
    """Return a snapshot of an identity at given version."""
    return app.model.get_version(version)


@app.query
def get_version(db, version):
    """Return a snapshot of resource at given version."""
    return db.select("resources", where="version = ?", vals=[version])[0]


@app.query
def get_entry(db, path):
    """"""


@app.query
def get_card(db, nickname):
    """Return the card with given nickname."""
    resource = db.select(
        "resources",
        vals=[nickname],
        where="""json_extract(resources.resource,
                                         '$.nickname[0]') == ?""",
    )[0]
    return resource["resource"]


@app.query
def get_event(db, path):
    """"""


@app.query
def get_entries(db, limit=20, modified="DESC"):
    """Return a list of entries."""
    return db.select(
        "resources",
        order=f"""json_extract(resources.resource,
                                      '$.published[0]') {modified}""",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'entry'""",
        limit=limit,
    )


@app.query
def get_cards(db, limit=20):
    """Return a list of alphabetical cards."""
    return db.select(
        "resources",  # order="modified DESC",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'card'""",
    )


@app.query
def get_rooms(db, limit=20):
    """Return a list of alphabetical rooms."""
    return db.select(
        "resources",  # order="modified DESC",
        where="""json_extract(resources.resource,
                                     '$.type[0]') == 'room'""",
    )


@app.query
def get_channels(db):
    """Return a list of alphabetical channels."""
    return db.select(
        "resources",  # order="modified DESC",
        where="json_extract(resources.resource, '$.type[0]') == 'feed'",
    )


@app.query
def get_categories(db):
    """Return a list of categories."""
    return [
        r["value"]
        for r in db.select(
            "resources, json_each(resources.resource, '$.category')",
            what="DISTINCT value",
        )
    ]


@app.query
def get_posts(db):
    """."""
    for post in db.select(
        "resources",
        # XXX json_extract(resources.resource, '$.channel[0]') IS NULL
        where="""json_extract(resources.resource, '$.type[0]') != 'card'""",
        order="""json_extract(resources.resource, '$.published[0]') DESC""",
    ):
        r = post["resource"]
        if "entry" in r["type"]:
            # XXX r["author"] = web.tx.identities.get_identity(r["author"][0])["card"]
            r["author"] = web.application("understory.owner").model.get_identity(
                r["author"][0]
            )["card"]
        yield r


@app.query
def get_posts_by_channel(db, uid):
    """."""
    return db.select(
        "resources",
        vals=[uid],
        where="""json_extract(resources.resource, '$.channel[0]') == ?""",
        order="""json_extract(resources.resource, '$.published[0]') DESC""",
    )


# def get_channels(db):
#     """Return a list of channels."""
#     return [r["value"] for r in
#             db.select("""resources,
#                            json_tree(resources.resource, '$.channel')""",
#                          what="DISTINCT value", where="type = 'text'")]


@app.query
def get_year(db, year):
    return db.select(
        "resources",
        order="""json_extract(resources.resource,
                                     '$.published[0].datetime') ASC""",
        where=f"""json_extract(resources.resource,
                                      '$.published[0].datetime')
                                      LIKE '{year}%'""",
    )

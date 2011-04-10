import os
import tornado.web
import tornado.wsgi
import wsgiref.handlers

from google.appengine.ext import db
from google.appengine.api import users

class OpenGraphPage(db.Model):
    created = db.DateTimeProperty(auto_now_add=True)
    creator = db.UserProperty(auto_current_user_add=True)
    head = db.TextProperty()
    path = db.StringProperty(required=True)
    updated = db.DateTimeProperty(auto_now=True)


class OpenGraphPageHandler(tornado.web.RequestHandler):
    def post(self, path):
        if not users.is_current_user_admin():
            raise tornado.web.HTTPError(403)

        key = self.get_argument("key", None)
        if key:
            try:
                page = OpenGraphPage.get(key)
            except db.BadKeyError:
                self.redirect(path)
                return
        else:
            page = OpenGraphPage(path=path)

        page.head = self.get_argument("head", "").strip()
        page.put()
      
        self.redirect(path)

    @tornado.web.removeslash
    def get(self, path):
        kwargs = {
            "page": db.Query(OpenGraphPage).filter("path =", path).get(),
            "path": path,
            "users": users,
        }
        self.render("page.html", **kwargs)


class RecentlyEditedPagesModule(tornado.web.UIModule):
    def render(self, limit=5):
        pages = db.Query(OpenGraphPage).order("-updated").fetch(limit=limit)
        return self.render_string("modules/recentlyedited.html", pages=pages)


settings = {
    "debug": os.environ.get("SERVER_SOFTWARE", "").startswith("Development/"),
    "fb_app_id": 165333213522232,
    "template_path": os.path.join(os.path.dirname(__file__), "templates"),
    "ui_modules": {
        "RecentlyEditedPages": RecentlyEditedPagesModule,
    },
    "xsrf_cookies": True,
}

application = tornado.wsgi.WSGIApplication([
    (r"(/[\w\/-]*)/?", OpenGraphPageHandler), 
], **settings)

def main():
    wsgiref.handlers.CGIHandler().run(application)

if __name__ == "__main__":
    main()

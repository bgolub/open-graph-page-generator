import logging
import os
import wsgiref.handlers

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.api import users

class OpenGraphPage(db.Model):
    head = db.TextProperty()
    path = db.StringProperty(required=True)


class OpenGraphPageHandler(webapp.RequestHandler):
    def post(self, path):
        if not users.is_current_user_admin():
            self.error(403)
            return

        key = self.request.get("key", None)
        if key:
            try:
                page = OpenGraphPage.get(key)
            except db.BadKeyError:
                self.redirect(path)
                return
        else:
            page = OpenGraphPage(path=path)

        page.head = self.request.get("head")
        page.put()
      
        self.redirect(path)

    def get(self, path):
        extra_context = {
            "page": db.Query(OpenGraphPage).filter("path =", path).get(),
            "path": path,
            "login_uri": users.create_login_url(self.request.uri),
            "logout_uri": users.create_logout_url(self.request.uri),
            "request": self.request,
            "user": users.get_current_user(),
            "user_admin": users.is_current_user_admin(),
        }
        path = os.path.join(os.path.dirname(__file__), "templates/page.html")
        self.response.out.write(template.render(path, extra_context))


settings = {
    "debug": os.environ.get("SERVER_SOFTWARE", "").startswith("Development/"),
}

application = webapp.WSGIApplication([
  ("(/[\w\/-]*)/?", OpenGraphPageHandler), 
], **settings)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

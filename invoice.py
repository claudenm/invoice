import cgi
import os

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Invoice(db.Model):
    content = db.StringProperty(multiline=True)
    date_added = db.DateTimeProperty(auto_now_add=True)
    date_created =db.DateTimeProperty()
    sent = db.BooleanProperty()
    void = db.BooleanProperty()
    

class LineItem(db.Model):
    units_billed=db.FloatProperty()
    unit = db.StringProperty(choices= ('hour','hours', 'day', 'days'))
    date_worked = db.DateTimeProperty()
    invoice = db.ReferenceProperty(Invoice,collection_name='invoice' )
    
class MainPage(webapp.RequestHandler):
    def get(self):
        invoices_query = Invoice.all().order('-date')
        invoices = greetings_query.fetch(10)
        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        template_values = {
            'invoices': invoices,
            'url': url,
            'url_linktext': url_linktext,
        }
        
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Invoices(webapp.RequestHandler):
    def get(self):
        invoices_query = Invoice.all().order('-date')
        invoices = invoices.fetch(10)
        
        
        template_values = {
                'invoices': invoices
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

        
class AddInvoice(webapp.RequestHandler):
    def post(self):
        Invoice = Greeting()
        
        if users.get_current_user():
            greeting.author = users.get_current_user()
        
        greeting.content = self.request.get('content')
        greeting.put()
        self.redirect('/')

class EditInvoice(webbapp.RequestHandler):
    def get(self):
        pass

    def post(self):
        pass
application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/invoices', ),
                                      ('/invoice', AddInvoice),
                                      (r'invoice/(\d+)', EditInvoice)],
                                     debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
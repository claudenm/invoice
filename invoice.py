import cgi
import os
import logging
import re
from datetime import datetime

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db
from google.appengine.ext.webapp import template

class Invoice(db.Model):
    description = db.StringProperty(multiline=True)
    date_added = db.DateTimeProperty(auto_now_add=True)
    sent = db.BooleanProperty()
    void = db.BooleanProperty()
    

class LineItem(db.Model):
    units_billed=db.FloatProperty()
    unit = db.StringProperty(choices= ('hour','hours', 'day', 'days'))
    rate = db.FloatProperty()
    date_worked = db.DateTimeProperty()
    invoice = db.ReferenceProperty(Invoice,collection_name='line_items' )
    
class MainPage(webapp.RequestHandler):
    def get(self):
        invoices_query = Invoice.all().order('-date_added')
        invoices = invoices_query.fetch(10)
        
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
        invoices = invoice_query.fetch(10)
        
        
        template_values = {
                'invoices': invoices
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

#Create Invoice
class AddInvoice(webapp.RequestHandler):
    
    def get(self):
        template_values = {
            'units' : LineItem.unit.choices
        }

        path = os.path.join(os.path.dirname(__file__), 'invoices.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        invoice = Invoice()
        invoice.description = self.request.get('description')
        invoice.put()
        
        lineitem = LineItem()
        logging.error( 'WTF - ' + str(self.request))
        lineitem.units_billed = float(self.request.get('units_billed'))
        lineitem.rate = float(self.request.get('rate'))
        lineitem.units = self.request.get('units')
        lineitem.date_worked = datetime.strptime(self.request.get('date'), '%d/%m/%Y')
        lineitem.invoice = invoice
        lineitem.put()
        self.redirect('/invoices')

#Edit Invoice
class EditInvoice(webapp.RequestHandler):
    def get(self):
		invoice=Invoice.get_by_id(int(self.request.GET['id']))
    		line_items = invoice.line_items.fetch(5)
    		logging.error(line_items)
        	template_values = {
	    	'invoice' : invoice,
            'units' : LineItem.unit.choices,
            'line_items' : line_items
        }
        	path = os.path.join(os.path.dirname(__file__), 'edit_invoice.html')
        	self.response.out.write(template.render(path, template_values))
    

#Edit Line Item
class EditItem(webapp.RequestHandler):
     def post(self):
	lineitem = LineItem.get_by_id(self.request.id)
	lineitem.units_billed = float(self.request.get('units_billed'))
	lineitem.rate = self.request.get('rate')
	lineitem.units = self.request.get('units')
	lineitem.date_worked = datetime.strptime(self.request.get('date'), '%d/%m/%Y')
	lineitem.invoice = invoice
	lineitem.put()
	self.request.redirect('invoice/edit/'+lineitem.invoice.key().id())


application = webapp.WSGIApplication([('/', MainPage),
                                      ('/invoices', MainPage),
                                      ('/invoice/add', AddInvoice),
                                      ('/invoice/edit', EditInvoice),
				      (r'/item/edit/<id:(\d+)>', EditItem)],
                                     debug=True)

'''application = webapp.WSGIApplication(
                                     [('/', MainPage),
                                      ('/invoices', MainPage),
                                      ('/invoice/add', AddInvoice),
                                      (r'invoice/<id:(\d+)>', EditInvoice)],
                                     debug=True)'''


def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()

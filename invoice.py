import cgi
import os
import logging
import re
from datetime import datetime

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db, ndb
from google.appengine.ext.webapp import template


class Invoice(ndb.Model):
    description = ndb.StringProperty()
    date_added = ndb.DateTimeProperty(auto_now_add=True)
    sent = ndb.BooleanProperty()
    void = ndb.BooleanProperty()

    @property
    def total(self):
        line_items = self.line_items.run()
        total = sum([li.units_billed*li.rate for li in line_items])
        return total

    @property
    def line_items(self):
	return LineItem.gql('where invoice = :1', self.key)

class LineItem(ndb.Model):
    units_billed=ndb.FloatProperty()
    unit = ndb.StringProperty(choices= ('Hour','Hours', 'Day', 'Days'))
    rate = ndb.FloatProperty()
    date_worked = ndb.DateTimeProperty()
    invoice = ndb.KeyProperty(kind="Invoice")




def invoice_key(invoice_name='default_invoice'):
	user = users.get_current_user()	
	if user:
		return ndb.Key('invoice', user.user_id())
    	return ndb.Key('invoice', invoice_name)

class MainPage(webapp.RequestHandler):
    def get(self):
        invoices_query = Invoice.query(ancestor=invoice_key()).order(-Invoice.date_added)
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
        'count' : len(invoices)
        }

        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))


class Invoices(webapp.RequestHandler):
    def get(self):
	invoices_query = Invoice.query(ancestor=invoice_key()).order(-Invoice.date_added)
        invoices = invoices_query.fetch(10)
        


        template_values = {
        'invoices': invoices
        }
        path = os.path.join(os.path.dirname(__file__), 'index.html')
        self.response.out.write(template.render(path, template_values))

#Create Invoice
class AddInvoice(webapp.RequestHandler):

    def get(self):
        template_values = {
        'units' : LineItem.unit._choices
        }

        path = os.path.join(os.path.dirname(__file__), 'invoices.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        invoice = Invoice(parent=invoice_key())
	
        invoice.description = self.request.get('description')
        invoice.put()

        lineitem = LineItem(parent=invoice_key())
        logging.error( 'WTF - ' + self.request.get('rate'))
        lineitem.units_billed = float(self.request.get('units_billed'))
        lineitem.rate = float(self.request.get('rate'))
        lineitem.unit = self.request.get('units')
        lineitem.date_worked = datetime.strptime(self.request.get('date'), '%d/%m/%Y')
        lineitem.invoice = invoice.key
        lineitem.put()
        self.redirect('/')

#Edit Invoice
class EditInvoice(webapp.RequestHandler):
    pass


#Edit Line Item
class EditItem(webapp.RequestHandler):
    def get(self):
	logging.error(users.get_current_user())
        invoice=Invoice.get_by_id(int(self.request.GET['id']),  parent=invoice_key())
        line_items = invoice.line_items.fetch()
        template_values = {
        'invoice' : invoice,
        'units' : LineItem.unit._choices,
        'line_items' : line_items
            }
        path = os.path.join(os.path.dirname(__file__), 'edit_invoice.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
        logging.error(self)
        lineitem = LineItem.get_by_id(int(self.request.POST['id']),  parent=invoice_key())
        lineitem.units_billed = float(self.request.get('units_billed'))
        lineitem.rate = float(self.request.get('rate'))
        lineitem.unit = self.request.get('units')
        lineitem.date_worked = datetime.strptime(self.request.get('date'), '%d/%m/%Y')
        lineitem.put()
        self.redirect('/')

class AddItem(webapp.RequestHandler):
    def get(self):
        invoice = Invoice.get_by_id(int(self.request.GET['invoice_id']), parent=invoice_key())
        template_values = {
        'invoice' : invoice,
        'units' : LineItem.unit._choices
            }
            
        path = os.path.join(os.path.dirname(__file__), 'add_item.html')
        self.response.out.write(template.render(path, template_values))

    def post(self):
	logging.error(self.request.POST['invoice_id'])
        invoice = Invoice.get_by_id(int(self.request.POST['invoice_id']), parent=invoice_key())
	logging.error(invoice)
        li = LineItem(parent=invoice_key())
        li.units_billed = float(self.request.get('units_billed'))
        li.rate = float(self.request.get('rate'))
        li.units = self.request.get('units')
        li.date_worked = datetime.strptime(self.request.get('date'), '%d/%m/%Y')
        li.invoice = invoice.key
        li.put()
        redirect_url = '/item/edit?id=' + str(invoice.key.id())
        self.redirect(redirect_url)

class PrintInvoice(webapp.RequestHandler):
    def get(self):
	logging.error(self.request.get('id'))
        invoice = Invoice.get_by_id(int(self.request.get('id')),  parent=invoice_key())
        line_items = invoice.line_items
        for li in line_items:
            logging.error(li.rate)
        template_values = {
        'invoice' : invoice,
        'units' : LineItem.unit._choices,
        'line_items' : line_items,
            }
        path = os.path.join(os.path.dirname(__file__), 'print_invoice.html')
        self.response.out.write(template.render(path, template_values))


application = webapp.WSGIApplication([('/', MainPage),
                          ('/invoices', MainPage),
                          ('/invoice/add', AddInvoice),
                          ('/item/update', EditItem),
                          ('/item/edit', EditItem),
                          ('/item/add', AddItem),
                          ('/invoice/print', PrintInvoice)
	      				  ],
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

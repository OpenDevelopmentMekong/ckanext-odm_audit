import traceback
import pylons
from pylons import config
from logging import getLogger
import ckan.model as model
import ckan.lib.helpers as h
from ckan.lib.base import render
from ckan import logic
from ckan.logic import action
from genshi.template.text import NewTextTemplate
from ckan.lib.mailer import mail_recipient
import threading

log = getLogger(__name__)

role_mapper ={'Admin':'admin','Editor':'reader'}

def notify_report_ready(context,user):

	notify(context,user,"email/report_ready.txt")

def notify(context,user,email_template):


	# retrieve all users
	all_organizations = action.get.organization_list(context,data_dict={})
	for organization in all_organizations:

			organization_members = action.get.member_list(context,data_dict={'id':organization,'object_type':'user','capacity':'admin'})

			admins = dict()
			for admin_user in organization_members:

					admin_obj = model.User.get(admin_user[0])
					admin_name = admin_obj.name
					admin_email = admin_obj.email
					admins[admin_name] = admin_email

			for name, email in admins.iteritems():

					extra_vars = {
						'admin_username': name
					}

					try:
							email_msg = render(email_template,extra_vars=extra_vars,loader_class=NewTextTemplate)

							headers = {}
							# if cc_email:
							#     headers['CC'] = cc_email

							try:

								mail_recipient(contact_name, contact_email,"Report created",email_msg, headers=headers)

							except Exception:

								traceback.print_exc()
								log.error('Failed to send an email message for issue notification')

					except logic.NotFound:

							log.error("user %s not found",user['name'])

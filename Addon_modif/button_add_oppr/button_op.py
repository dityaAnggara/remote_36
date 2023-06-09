# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import crm


class try_email(osv.osv):
    _inherit    = "crm.lead"
    
    def try_sending_email(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        #try:
            #template_id = ir_model_data.get_object_reference(cr, uid, 'button_add_oppr', 'em_text')[1]
        #template_id = ""
        #except ValueError:
            #template_id = False
        #try:
            #compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
       # except ValueError:
            #compose_form_id = False 
        #ctx = dict(context)
        #ctx.update({
         #   'default_model': 'crm.lead',
         #   'default_res_id': ids[0],
         #   'default_use_template': bool(template_id),
         #   'default_template_id': template_id,
         #   'default_composition_mode': 'comment',
         #   'mark_so_as_sent': True
        #})
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            
        }
    
    #def try_sending_email(self, cr ,uid, ids, context=None):
        #template = self.pool.get('ir.model.data').get_object(cr, uid, 'button_add_oppr', 'em_text')
        #mail_id = self.pool.get('email.template').send_mail(cr, uid, template.id, ids, context=context)
        #return mail_id
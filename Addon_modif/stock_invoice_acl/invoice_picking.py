'''
Created on Mar 23, 2015

@author: innotek
'''
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

from openerp.osv import fields, osv

from openerp.tools.translate import _

class stock_invoice_onshipping(osv.osv_memory):
    _inherit = "stock.invoice.onshipping"
    def open_invoice(self, cr, uid, ids, context=None):
        get_grop_id_invoice = self.pool.get('res.groups').search(cr, uid, [('name','=like','Financial Manager')])
        brow_grp_invoice = self.pool.get('res.groups').browse(cr, uid, get_grop_id_invoice, context)[0]
        
        cr.execute("SELECT COUNT(uid) FROM res_groups_users_rel WHERE gid = %s AND uid = %s",(brow_grp_invoice.id,uid))
        find_uids = cr.fetchone()[0]
        
        if find_uids > 0:
            if context is None:
                context = {}
            invoice_ids = []
            data_pool = self.pool.get('ir.model.data')
            res = self.create_invoice(cr, uid, ids, context=context)
            invoice_ids += res.values()
            inv_type = context.get('inv_type', False)
            action_model = False
            action = {}
            if not invoice_ids:
                raise osv.except_osv(_('Error!'), _('Please create Invoices.'))
            if inv_type == "out_invoice":
                action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree1")
            elif inv_type == "in_invoice":
                action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree2")
            elif inv_type == "out_refund":
                action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree3")
            elif inv_type == "in_refund":
                action_model,action_id = data_pool.get_object_reference(cr, uid, 'account', "action_invoice_tree4")
            if action_model:
                action_pool = self.pool.get(action_model)
                action = action_pool.read(cr, uid, action_id, context=context)
                action['domain'] = "[('id','in', ["+','.join(map(str,invoice_ids))+"])]"
            return action
        else: 
            raise osv.except_osv(_('Warning'),_('Hayo ngapain .... '))
        
    

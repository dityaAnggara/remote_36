'''
Created on Jan 2, 2015

@author: innotek
'''
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2011 OpenERP S.A (<http://www.openerp.com>).
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

import logging
import random

from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import email_split
from openerp import SUPERUSER_ID

_logger = logging.getLogger(__name__)

class aut_wizard(osv.osv_memory):
    _name="automate_kip.aut_wizard"
    
    
    
    _columns = {
                    'gate_id': fields.many2one('res.groups', required=True,string='gate'),
                    'aut_line': fields.one2many('automate_kip.aut_wizard_line', 'wiz_id', 'Wizard Lines'),
                    'part_aid' : fields.many2one('res.partner', 'Customer Name', domain="[('ref','!=','')]"),
                }
    def _default_gate(self, cr, uid, context):
        gate_ids = self.pool.get('res.groups').search(cr, uid, [('is_portal', '=', True)])
        return gate_ids and gate_ids[0] or False
    _defaults = {
        'gate_id': _default_gate,
    }
    def ts_wz_one(self, cr ,uid, ids, context=None):
        tu = self.browse(cr, uid, ids[0], context)
        aktip = context.get('active_ids')
        if tu.part_aid.ref == False:
            raise osv.except_osv(_('Warning!'), _('customer has not code'))
        else:
            apnd_cus = []
            apn_apddng = []
            kosong_apn = []
            lolo_apenx = []
            utr = self.pool.get('product.product').search(cr, uid, [('cusm_id','=',tu.part_aid.id)])
            for get_cust in utr:
                brw_pdr = self.pool.get('product.product').browse(cr, uid, get_cust, context)
                apnd_cus.append(brw_pdr.id)
                lolo_apenx.append(brw_pdr.aui_acl_prod)
            mx_cust_id = max(apnd_cus)
            max_lolo = max(lolo_apenx)
            bwwe_cu = self.pool.get('product.product').browse(cr, uid, mx_cust_id, context)
            one_utr = self.pool.get('product.kip.padd').search(cr, uid, [])
            for wo_one in one_utr:
                brw_wo = self.pool.get('product.kip.padd').browse(cr, uid, wo_one, context)
                apn_apddng.append(brw_wo.id)
            mx_wo_one = max(apn_apddng)
            wo_bwe = self.pool.get('product.kip.padd').browse(cr, uid, mx_wo_one, context)          
            bdsu = bwwe_cu.aui_acl_prod
            one_bdsu = max_lolo
            str_bwe_wo = str(wo_bwe.padding_kip) 
            star_pin = int(one_bdsu) + 1
            for aktipe in aktip:
                gu_bre = self.pool.get('product.product').browse(cr, uid, aktipe, context)
                if gu_bre.no_kiip == False:
                    kosong_apn.append(gu_bre.id)
            for kgs in kosong_apn:
                pdfuc = "%0"+str_bwe_wo+"d"
                one_pdf = pdfuc % (star_pin)
                ngab = "-".join((str(tu.part_aid.ref),str(one_pdf)))
                cr.execute("UPDATE product_product SET no_kiip = %s, cusm_id = %s, aui_acl_prod = %s WHERE id = %s",(ngab, tu.part_aid.id, star_pin, kgs))
                star_pin += 1
            #raise osv.except_osv(_('Warning!'), _(kosong_apn))
        return True
    def onchange_gate_id(self, cr, uid, ids, gate_id, context=None):
        # for each partner, determine corresponding portal.wizard.user records
        res_partner = self.pool.get('product.product')
        partner_ids = context and context.get('active_ids') or []
        contact_ids = set()
        user_changes = []
        for partner in res_partner.browse(cr, SUPERUSER_ID, partner_ids, context):
            #for contact in (partner.child_ids or [partner]):
                # make sure that each contact appears at most once in the list
                #if contact.id not in contact_ids:
                contact_ids.add(partner.id)
                on_select = False
                #if partner.user_ids:
                #        on_select = gate_id in [g.id for g in contact.aut_line[0].groups_id]
                user_changes.append((0, 0, {
                        'produ_id': partner.id,
                        'on_select': on_select,
                    }))
        return {'value': {'aut_line': user_changes}}
   
aut_wizard()    
class aut_wizard_line(osv.osv_memory):
    _name = "automate_kip.aut_wizard_line"
    _columns = {
                    'wiz_id': fields.many2one('automate_kip.aut_wizard', 'Bla Bla'),
                    'produ_id': fields.many2one('product.product', 'Product'),
                    'on_select': fields.boolean('Onselect'),
                }
aut_wizard_line()        
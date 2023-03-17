'''
Created on Nov 10, 2014

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

from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools


class obj_padd(osv.osv_memory):
    _name="customer_acl_v2.obj_padd"
    _description="abjad for customer acl"
    _columns={
                'partner_type' : fields.selection([
                                                   ('1', 'Customer'),
                                                   ('2', 'Supplier'),
                                                   ],'Partner_type',required=True,help="Type Of partner for abjad"),
                'padding_g'  : fields.char('Padding'),
              }
    def generate_pad_abj(self, cr, uid, ids, context=None):
        rtuu = self.browse(cr, uid, ids[0], context)
        #raise osv.except_osv(_('Warning!'), _(rtuu.partner_type))
         
        if rtuu.partner_type == '1':
            cr.execute("UPDATE customer_acl_v2_abj SET padd = %s",(rtuu.padding_g,))
        else:
            cr.execute("UPDATE customer_acl_v2_abj SET padd_sup = %s",(rtuu.padding_g,))    
        return {'type': 'ir.actions.act_window_close'}
        
obj_padd()    
class abj(osv.osv):
    _name="customer_acl_v2.abj"
    _description="abjad for customer acl"
    _columns={
                'name'  : fields.char('Abjad'),
                'partner_ttype' : fields.selection([
                                                   ('1', 'Customer'),
                                                   ('2', 'Supplier'),
                                                   ],'Partner_type',required=True,help="Type Of partner for abjad"),
                'padd'   : fields.char('Padding'),
                'padd_sup': fields.char('Padding'),
                'last_incre':fields.char('Last Increment'),
                'last_incre_sup' : fields.char('Last Increment'),
                'cus_bol'   : fields.boolean('Bol'),
                'cuss'  : fields.char('Bol1')
              }
    _sql_constraints = [
                       ('name', 'unique(name)', ("Hey Abjadnya sama loh !!!"))
                      ]
    _defaults = {
                 'partner_ttype': '1',
                 }
    
abj()      
class res_partner(osv.osv):
    _inherit="res.partner"
    _columns={
                'abj_id'        : fields.many2one('customer_acl_v2.abj', 'Abjad'),
                'cust_auto'     :fields.integer('Code'),
                'franco'        : fields.boolean('Shipping Service'),
                'npwp_acl'      : fields.char('NPWP'),
                'user_id'       : fields.many2one('res.users', 'Salesperson', domain = "[('code_for_sale','>',0)]", select=True, track_visibility='onchange'),
                'franco_true'   : fields.char('Franco'),
                'area_type'     : fields.selection([
                                                    ('kb', 'Kawasan Berikat'),
                                                    ('nonkb', 'Bukan Kawasan Berikat'),
                                                    ], 'Area Type'),
                
              }
    
    def create(self, cr ,uid, vals, context=None):
        if vals.get('supplier') == False and vals.get('is_company') == True:
            abj_id     = vals.get('abj_id')
            customer   = vals.get('customer')
            pol_obj_part = self.pool.get('customer_acl_v2.abj')
            pol_obj_browse = pol_obj_part.browse(cr, uid, abj_id, context=context) 
            a = ""
            las_inc = ""
            if customer == True:
                a = pol_obj_browse.last_incre
                las_inc = 'last_incre'
            else:
                a = pol_obj_browse.last_incre_sup
                las_inc = 'last_incre_sup'
            asl = 1
            pol_obj_part.write(cr, uid, abj_id, {las_inc : asl}, context=context)
            if a != "":
                asl=int(a)+1
                pol_obj_part.write(cr, uid, abj_id, {las_inc : asl}, context=context)
                
        else:
            if vals.get('abj_id') == True and context.get('reset_password') == False and vals.get('is_company') == True:
                abj_id     = vals.get('abj_id')
                customer   = vals.get('customer')
                pol_obj_part = self.pool.get('customer_acl_v2.abj')
                pol_obj_browse = pol_obj_part.browse(cr, uid, abj_id, context=context) 
                a = ""
                las_inc = ""
                if customer == True:
                    a = pol_obj_browse.last_incre
                    las_inc = 'last_incre'
                else:
                    a = pol_obj_browse.last_incre_sup
                    las_inc = 'last_incre_sup'
                asl = 1
                pol_obj_part.write(cr, uid, abj_id, {las_inc : asl}, context=context)
                if a != "":
                    asl=int(a)+1
                    pol_obj_part.write(cr, uid, abj_id, {las_inc : asl}, context=context)
            elif vals.get('is_company') == False:
                print "asas"
                    
        return super(res_partner, self).create(cr, uid, vals, context=context)
        
    def _gt_save(self, cr, uid, ids, context=None):
        resu = self.write(cr, uid, ids, {'ref_cloning' : 'save'}, context=context)
        return resu
    def onchange_abj(self, cr, uid, ids, abj_id, customer, supplier, context=None):
       
        #raise osv.except_osv(_('Warning!'), _(customer)) 
        pol_obj_part = self.pool.get('customer_acl_v2.abj')
        pol_obj_browse = pol_obj_part.browse(cr, uid, abj_id, context=context) 
        pddi = ""
        a = ""
        if customer == True:
            pddi = pol_obj_browse.padd
            a = pol_obj_browse.last_incre
        else:
            pddi = pol_obj_browse.padd_sup
            a = pol_obj_browse.last_incre_sup
            
        gb = pol_obj_browse.name
        pdi = str(pddi)
        pdii= "%0"+pdi+"d"
        asl = 1
        b=pdii % (1)
        gub = gb+''+b
        
        if a != "":
            asl=int(a)+1
            b = int(a)+1
            b = pdii % (b)
            gub = gb+''+b
        
        return {'value':{'ref' : gub, 'cust_auto':asl}}
        
                
'''
Created on Mar 1, 2015

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

import time
from datetime import datetime

import openerp.addons.decimal_precision as dp
from openerp.osv import fields, osv, orm
from openerp.tools import DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP
from openerp.tools import float_compare
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp import SUPERUSER_ID
from openerp.addons.product import _common



class sale_order_skp(osv.osv):
    _name = "sale.order.skp"
    _inherit = "sale.order"
    _table = "sale_order"
    _rec_name = "po_sl"
    _columns = {
                    'po_sl'    : fields.char('SKP NO'),
                }

class mrp_bom(osv.osv):
    _inherit = "mrp.bom"
    _columns = {
                    'upah_glue'                 : fields.float('Upah Glue'),
                    'sale_skp'                  : fields.many2one('sale.order.skp', 'No SKP'),
                    'upah_flexo'                : fields.float('Upah Flexo'),
                    'upah_ikat_man'             : fields.float('Upah ikat Manual'),
                    'upah_ikat_msn'             : fields.float('Upah ikat Mesin'),
                    'ikat'                      : fields.float('1 Ikat'),
                    'desc_bom'                  : fields.text('Keterangan'),
                    'jumlah_sheet'              : fields.float('Jumlah Sheet'),
                    'jumlah_out'                : fields.float('Jumlah OUT'),
                    'jumlah_order'              : fields.float('Jumlah Order'),
                    'lebar_kertas'              : fields.float('Lebar Kertas'),
                    'sheet_rusak_cor'           : fields.float('Sheet yang rusak di corr'),
                    'running_bom'               : fields.char('Running Meter'),
                    'del_date_bom'              : fields.date('Delivery Date'),
                    'no_kk_bom'                 : fields.char('No KK'),
                    'panjang_sheet_kip'         : fields.char('Panjang Sheet KIP'),
                    'subtance_bom_one'          : fields.many2one('master.subtance.subbtance','Subtance One'),
                    'subtance_bom_two'          : fields.many2one('master.subtance.subbtance','Subtance Two'),
                    'subtance_bom_three'        : fields.many2one('master.subtance.subbtance','Subtance There'),
                    'subtance_bom_four'         : fields.many2one('master.subtance.subbtance','Subtance four'),
                    'subtance_bom_five'         : fields.many2one('master.subtance.subbtance','Subtance five'),
                    'subtance_bom_value_one'    : fields.char('Value Subtance One'),
                    'subtance_bom_value_two'    : fields.char('Value Subtance Two'),
                    'subtance_bom_value_three'  : fields.char('Value Subtance There'),
                    'subtance_bom_value_four'   : fields.char('Value Subtance four'),
                    'subtance_bom_value_five'   : fields.char('Value Subtance five'), 
                }
    def compute_alo(self, cr, uid, ids, vals, context=None):
        send_y = self.browse(cr, uid, ids[0], context)
        
        one_val = 0
        two_val = 0
        three_val = 0
        four_val = 0
        five_val = 0
        kali_bagi = (float(send_y.panjang_sheet_kip) * float(send_y.jumlah_sheet))/1000
       
        if send_y.subtance_bom_one:
            one_val = (float(send_y.subtance_bom_one.nilai_subtance) * kali_bagi * float(send_y.lebar_kertas))/1000000
        if send_y.subtance_bom_two:    
            two_val = (float(send_y.subtance_bom_two.nilai_subtance) * kali_bagi * float(send_y.lebar_kertas))/1000000
        if send_y.subtance_bom_three:    
            three_val = (float(send_y.subtance_bom_three.nilai_subtance) * kali_bagi * float(send_y.lebar_kertas))/1000000    
        if send_y.subtance_bom_four:    
            four_val = (float(send_y.subtance_bom_four.nilai_subtance) * kali_bagi * float(send_y.lebar_kertas))/1000000
        if send_y.subtance_bom_five:    
            five_val = (float(send_y.subtance_bom_five.nilai_subtance) * kali_bagi * float(send_y.lebar_kertas))/1000000
        
        
        self.write(cr, uid ,ids, {'running_bom' : kali_bagi, 'subtance_bom_value_one' : one_val, 'subtance_bom_value_two' : two_val, 'subtance_bom_value_three' : three_val, 'subtance_bom_value_four' : four_val, 'subtance_bom_value_five' : five_val}, context=context)
        #self.write(cr, uid ,ids, {'running_bom' : kali_bagi}, context=context)
        
    def jml_sheet_change(self, cr, uid, ids, jumlah_sheet,panjang_sheet_kip,context=None):
        try:
            kali_bagi = (float(panjang_sheet_kip) * float(jumlah_sheet))/1000
            return {'value': {'running_bom': kali_bagi}}
        except:
            print ":)"
    def onchange_product_id(self, cr, uid, ids, product_id, name, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        ghy = 0
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            if prod.sheet_panjang:
                ghy += int(prod.sheet_panjang)
                
            return {'value': {'name': prod.name, 'product_uom': prod.uom_id.id, 'jumlah_order' : prod.jumlah_order_kip, 'panjang_sheet_kip' : ghy}}
        return {}
mrp_bom()    

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

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc
import roman
import calendar
from calendar import monthrange
import base64
from lxml import etree

class sale_order(osv.osv):
    _inherit = "sale.order"
    _columns = {
                    'po_sl'             : fields.char('SKP NO'),
                    'approve_terakhr'   : fields.many2one('res.users', 'terakhir'),
                    'warehouse_id_sale' : fields.many2one('stock.warehouse', 'Warehouse'),
                    'order_line'        : fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'approval': [('readonly', False)]}),
                    'date_delivery_so'  : fields.datetime('Date Delivery Awal'),
                    'order_line'        : fields.one2many('sale.order.line', 'order_id', 'Order Lines', readonly=True, states={'draft': [('readonly', False)], 'sent_to_ppic': [('readonly', False)], 'sent_to_costing': [('readonly', False)], 'sent_to_sale':[('readonly', False)], 'progress' : [('readonly', False)]}),
                    'category_id'       : fields.many2one('product.category','Product Type', change_default=True, domain="[('type','=','normal'),('parent_id','=',2)]" , readonly=True, states={'draft': [('readonly', False)]}, help="Select category for the current product"),
                    'partner_id'        : fields.many2one('res.partner', 'Customer', domain = "[('customer','=',True),('user_id','!=',None),('ref','!=',None)]", readonly=True, states={'draft': [('readonly', False)], 'sent': [('readonly', False)]}, required=True, change_default=True, select=True, track_visibility='always'),
                    'state'             : fields.selection([
                                                            ('draft', 'Draft'),
                                                            ('sent_to_ppic', 'PPIC'),
                                                            ('sent_to_costing', 'Costing'),
                                                            ('approval', 'Wait for Approval GM/Direksi'),
                                                            ('sent_to_sale', 'Last Check Quotation'),
                                                            ('progress', 'SKP'),
                                                            ('manual', 'SKP to Invoice'),
                                                            ('cancel', 'Cancelled'),
                                                            ('waiting_date', 'Waiting Schedule'),
                                                            ('invoice_except', 'Invoice Exception'),
                                                            ('done', 'Done'),
                                                            ], 'Status', readonly=True, track_visibility='onchange',
                                                           help="Gives the status of the quotation or sale order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked tp the sale order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date", 
                                                           select=True, ondelete="cascade"),
                }
    sql_constraints = [
        ('name_uniq', 'Check(1=1)', 'Order Reference must be unique per Company!'),
    ]
    
    def create(self, cr, uid, vals, context=None):
        apn_try = []
        if vals.get('name','/')=='/':
            vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'sale.order') or '/'
            #apn_try.append(vals['name'])
        #raise osv.except_osv(_('Test'),_(apn_try))    
        return super(sale_order, self).create(cr, uid, vals, context=context)
    def action_cancel(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        sale_order_line_obj = self.pool.get('sale.order.line')
        sale_ord = self.browse(cr, uid, ids[0], context)
        slf_sto = self.pool.get('stock.picking').search(cr, uid, [('state','=','done'),('origin','=',sale_ord.name)],count=True)
        if slf_sto >=1:
            raise osv.except_osv(_("Info"),_("Sorry You have one Delivery Order is Delivered, you can't cancel this SKP"))
        else:
            self.write(cr, uid, ids, {'state': 'cancel'})
            for or_line in sale_ord.order_line:
                cr.execute("UPDATE sale_order_line SET state=%s WHERE id=%s",('cancel',or_line.id))
            slf_sto_one = self.pool.get('stock.picking').search(cr, uid, [('state','not in',('done','cancel')),('origin','=',sale_ord.name)])
            for pickin in slf_sto_one:
                brw_picc = self.pool.get('stock.picking').browse(cr, uid, pickin, context)
                cr.execute("UPDATE stock_picking SET state = %s WHERE id = %s",('cancel',brw_picc.id))
            for or_line in sale_ord.order_line:
                brows_orlin = self.pool.get('sale.order.line').browse(cr, uid, or_line, context)
                mov_ln = self.pool.get('stock.move').search(cr, uid, [('sale_line_id','=',or_line.id),('state','=','done')])
                mov_ln_satu = self.pool.get('stock.move').search(cr, uid, [('sale_line_id','=',or_line.id),('state','not in',('done','cancel'))])
                for mov_kuah in mov_ln_satu:
                    brows_kuah = self.pool.get('stock.move').browse(cr, uid, mov_kuah, context)
                    cr.execute("UPDATE stock_move SET state= %s WHERE id = %s",('cancel',brows_kuah.id))
                
        
        return True
    def action_cancel_special(self, cr, uid, ids, context=None):
        sael_ap = []
        stock_pi = []
        multi = []
        multi_satu = []
        sale_ord = self.browse(cr, uid, ids[0], context)
        slf_sto = self.pool.get('stock.picking').search(cr, uid, [('state','=','done'),('origin','=',sale_ord.name)],count=True)
        val_two = 0
        val_theree = 0
        va_per = 0
        va_tt = 0
        if slf_sto >= 1:
            slf_sto_one = self.pool.get('stock.picking').search(cr, uid, [('state','not in',('done','cancel')),('origin','=',sale_ord.name)])
            cr.execute("UPDATE stock_move SET sisa_mark = %s, sisa_wh = %s WHERE origin = %s",(0,0,sale_ord.name))
            for pickin in slf_sto_one:
                brw_picc = self.pool.get('stock.picking').browse(cr, uid, pickin, context)
                cr.execute("UPDATE stock_picking SET state = %s WHERE id = %s",('cancel',brw_picc.id))
            for or_line in sale_ord.order_line:
                brows_orlin = self.pool.get('sale.order.line').browse(cr, uid, or_line, context)
                val = 0
                val_theree += or_line.price_subtotal
                va_per = (val_theree * 10)/100
                va_tt = val_theree + va_per
                cr.execute("UPDATE sale_order SET state= 'manual', amount_tax = %s, amount_untaxed = %s, amount_total = %s WHERE id = %s",(va_per,val_theree,va_tt,sale_ord.id))        
                mov_ln = self.pool.get('stock.move').search(cr, uid, [('sale_line_id','=',or_line.id),('state','=','done')])
                mov_ln_satu = self.pool.get('stock.move').search(cr, uid, [('sale_line_id','=',or_line.id),('state','not in',('done','cancel'))])
                for mov_kuah in mov_ln_satu:
                    brows_kuah = self.pool.get('stock.move').browse(cr, uid, mov_kuah, context)
                    cr.execute("UPDATE stock_move SET state= %s WHERE id = %s",('cancel',brows_kuah.id))
                for mov_sop in mov_ln:
                    bw_movsop = self.pool.get('stock.move').browse(cr, uid, mov_sop, context)        
                    val += bw_movsop.product_qty
                if or_line.qty_realisasi <= 0:    
                    cr.execute("UPDATE sale_order_line SET qty_realisasi = %s, product_uom_qty = %s WHERE id = %s",(or_line.product_uom_qty,val,or_line.id))    
            context.update({'cont_for_ac': 'special'})
            return {'warning':{'title':'Info', 'message':'If ammount does not change please click one more again, thank you'}}
        #return True
    def print_quotation(self, cr, uid, ids, context=None):
        '''
        This function prints the sales order and mark it as sent, so that we can see more easily the next step of the workflow
        '''
        assert len(ids) == 1, 'This option should only be used for a single id at a time'
        
        datas = {
                 'model': 'sale.order',
                 'ids': ids,
                 'form': self.read(cr, uid, ids[0], context=context),
        }
        return {'type': 'ir.actions.report.xml', 'report_name': 'sale.order', 'datas': datas, 'nodestroy': True}
    def snd_ppic(self, cr, uid, ids, context=None):
            dtbs_take = self.browse(cr, uid, ids[0], context=context)
            if dtbs_take.date_delivery_so == False:
                raise osv.except_osv(_('Warning'),_('Tanggal delivery belum diisi'))
            else:
                obj_stock_mvo = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',dtbs_take.id)], count=True)
                if obj_stock_mvo <= 0:
                    raise osv.except_osv(_('Warning!'), _("Line Harus diisi"))
                else:
                    self.write(cr, uid, ids, {'state' : 'sent_to_ppic'}, context=context)
                    get_parent_id   =   self.browse(cr, uid, ids, context=context)[0]
                    gd_odline       = self.pool.get('sale.order.line')
                    gd_sch = gd_odline.search(cr, uid, [('order_id', '=', get_parent_id.id)]) 
                    for idwx in gd_sch:
                        bw_line_ppi = self.pool.get('sale.order.line').browse(cr, uid, idwx, context)
                        #tole = bw_line_ppi.toleransi_skp
                        #tole_satu = int(tole) + int(bw_line_ppi.product_uom_qty)
                        #gd_odline.write(cr, uid, idwx, {'state' : 'sent_to_ppic','product_uom_qty' : tole_satu}, context=context)
                        gd_odline.write(cr, uid, idwx, {'state' : 'sent_to_ppic'}, context=context)
                    return {  
                        'type'      : 'ir.actions.act_window',
                        'view_type' : 'form',
                        'view_mode' : 'tree,form',
                        #'view_id'   : ids[0],
                        'res_model' : 'sale.order',
                        'target'    : 'current',
                        'domain'    : [('state', '=', 'draft')],
                        }    
            
    def approv(self, cr, uid, ids, context=None):
            dtbs_take = self.browse(cr, uid, ids[0], context=context)
            obj_stock_mvo_two = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',dtbs_take.id),('price_unit','=', 0)], count=True)
        
            if obj_stock_mvo_two > 0:
                raise osv.except_osv(_('Warning!'), _("please define price unit"))
            else:
                obj_stock_mvo = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',dtbs_take.id)], count=True)
                if obj_stock_mvo <= 0:
                    raise osv.except_osv(_('Warning!'), _("Line Harus diisi"))
                else:
                    cr.execute("SELECT view_id FROM ir_act_window WHERE name = %s",('Sales Order Costing',))
                    view_iid = cr.fetchone()[0] 
                    self.write(cr, uid, ids, {'state' : 'approval'}, context=context)
                    get_parent_id   =   self.browse(cr, uid, ids, context=context)[0]
                    gd_odline       = self.pool.get('sale.order.line')
                    gd_sch = gd_odline.search(cr, uid, [('order_id', '=', get_parent_id.id)]) 
                    for idwx in gd_sch:
                        gd_odline.write(cr, uid, idwx, {'state' : 'approval'}, context=context)
                    return {  
                        'type'      : 'ir.actions.act_window',
                        'view_type' : 'tree',
                        'view_mode' : 'tree',
                        'view_id'   : view_iid,
                        'res_model' : 'sale.order',
                        'target'    : 'current',
                        'domain'    : [('state', '=', 'sent_to_costing')],
                        }    
                    
    def snd_costing(self, cr, uid, ids, vals, context=None):
        dtbs_take = self.browse(cr, uid, ids[0], context=context)
        obj_stock_mvo_one = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',dtbs_take.id),('product_id','=', False)], count=True)
        obb_yu = self.pool.get('sale.order.line').search(cr, uid, [('mrp_no_kip','=',False),('order_id','=',dtbs_take.id)], count=True)
        if obj_stock_mvo_one > 0:
            raise osv.except_osv(_('Warning!'), _("tidak ada product yang dipilih"))
        elif obb_yu > 0:
            raise osv.except_osv(_('Warning!'), _('no kip belum diisi'))
        else:
            cr.execute("SELECT view_id FROM ir_act_window WHERE name = %s",('Sales Order Manufacturing',))
            view_iid = cr.fetchone()[0]    
            #raise osv.except_osv(_('Warning!'), _(view_iid))
            
            self.write(cr, uid, ids, {'state' : 'sent_to_costing'}, context=context)
            get_parent_id   =   self.browse(cr, uid, ids, context=context)[0]
            gd_odline       = self.pool.get('sale.order.line')
            gd_sch = gd_odline.search(cr, uid, [('order_id', '=', get_parent_id.id)]) 
            for idwx in gd_sch:
                gd_odline.write(cr, uid, idwx, {'state' : 'sent_to_costing'}, context=context)
            
            return {  
                    'type': 'ir.actions.act_window',
                    'view_type': 'tree',
                    'view_mode': 'tree',
                    'view_id': view_iid,
                    'res_model': 'sale.order',
                    'target': 'current',
                    'domain'    : [('state', '=', 'sent_to_ppic')],
                    #'nodestroy': True,
                   }
                        
    def onchange_partner_id_new(self, cr, uid, ids, part, context=None):
        tm_ref = time.strftime("%S:%M:%H %Y-%m-%d ")
        pool_res        = self.pool.get('res.partner')
        pool_res_browse = pool_res.browse(cr, uid, part, context=context)
        cba = pool_res_browse.ref   
        if not part:
            return {'value': {'partner_invoice_id': False, 'partner_shipping_id': False,  'payment_term': False, 'fiscal_position': False}}

        part = self.pool.get('res.partner').browse(cr, uid, part, context=context)
        addr = self.pool.get('res.partner').address_get(cr, uid, [part.id], ['delivery', 'invoice', 'contact'])
        
        tst_ref = tm_ref+' '+cba
        
        pricelist = part.property_product_pricelist and part.property_product_pricelist.id or False
        payment_term = part.property_payment_term and part.property_payment_term.id or False
        fiscal_position = part.property_account_position and part.property_account_position.id or False
        dedicated_salesman = part.user_id and part.user_id.id or uid
        sale_tem_acl = part.section_id and part.section_id.id 
        val = {
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'],
            'payment_term': payment_term,
            'fiscal_position': fiscal_position,
            'user_id': dedicated_salesman,
            'client_order_ref' : tst_ref or '',
            'section_id'            : sale_tem_acl, 
        }
        if pricelist:
            val['pricelist_id'] = pricelist
        return {'value': val, 'domain': {'prod_id':[('no_kiip','like', cba)]}}
    def action_button_confirm(self, cr, uid, ids, context=None):
        #ck_po_marketing = self.browse(cr, uid, ids[0],context=context)
    
        dtbs_take = self.browse(cr, uid, ids[0], context=context)
        obj_stock_mvo_two = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',dtbs_take.id),('price_unit','=', 0)], count=True)
        
        if obj_stock_mvo_two > 0:
            raise osv.except_osv(_('Warning!'), _("please define price unit"))
        else:
            #assert len(ids) == 1, 'This option should only be used for a single id at a time.'
            wf_service = netsvc.LocalService('workflow')
            wf_service.trg_validate(uid, 'sale.order', ids[0], 'order_confirm', cr)
        
                # redisplay the record as a sales order
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'sale', 'view_order_form')
            view_id = view_ref and view_ref[1] or False,
                
            res_partner_obj = self.pool.get('res.partner')
            sale_order_obj = self.pool.get('sale.order')
            sale_order_line_obj = self.pool.get('sale.order.line')
            res_users_obj = self.pool.get('res.users')
            crm_case_section_obj = self.pool.get('crm.case.section')
            dtbs_take = self.browse(cr, uid, ids[0], context=context)
            #id_ordd = 
            sale_order_line_obj_srch = sale_order_line_obj.search(cr, uid, [('order_id','=',dtbs_take.id),('purchase_customer_no','=',False)], count=True)
            
            if sale_order_line_obj_srch != 0:
                raise osv.except_osv(_('Warning!'), _('One or more of your product has not PO number'))
            else:
                part_id = dtbs_take.partner_id.id
                com_idy = dtbs_take.company_id.id
                #prdt_type = dtbs_take.product_type_acl
                ctage_id = dtbs_take.category_id.name
                wstart = 1001
                res_partner_obj_browse = res_partner_obj.browse(cr, uid, part_id, context=context)
                crm_case_section_obj_bros = crm_case_section_obj.browse(cr, uid, res_partner_obj_browse.section_id.id, context=context)
                cbatwo = crm_case_section_obj_bros.code
                res_partner_obj_browse = res_partner_obj.browse(cr, uid, part_id, context=context)
                res_users_obj_bws = res_users_obj.browse(cr , uid, res_partner_obj_browse.user_id.id, context=context)
                cbafour = res_users_obj_bws.code_for_sale 
                mntl = time.strftime("%m")
                yer = time.strftime("%y")
                imntl = int(mntl)
                fmntl = "%01d" % (imntl)
                ifmntl = int(fmntl)
                tr = roman.toRoman(ifmntl)
                yerone = time.strftime("%Y")
                iyerone = int(yerone)
                ghg = monthrange(iyerone, ifmntl)[1]
                mntldif = time.strftime("%Y-%m-01")
                mntldifone = time.strftime("%Y-%m-"+str(ghg))
                tg_dte = time.strftime("%Y-%m-%d %H:%M:%S")
                tmab_t = ""
                sl_apend_id = []
                mx_id_sl = 0
                get_parent_id   =   self.browse(cr, uid, ids, context=context)[0]
                gd_odline       = self.pool.get('sale.order.line')
                gd_sch = gd_odline.search(cr, uid, [('order_id', '=', get_parent_id.id)]) 
                for idwx in gd_sch:
                        bw_line_ppi = self.pool.get('sale.order.line').browse(cr, uid, idwx, context)
                        tole = bw_line_ppi.toleransi_skp
                        tole_satu = int(tole) + int(bw_line_ppi.product_uom_qty)
                        hou = int(tole_satu)
                        #self.pool.get('stock.move').write(cr, uid, )
                        cr.execute("UPDATE stock_move SET product_uos_qty = %s, product_qty = %s WHERE sale_line_id = %s AND product_id = %s",(hou,hou,bw_line_ppi.id,bw_line_ppi.product_id.id))
                        #gd_odline.write(cr, uid, idwx, {'state' : 'sent_to_ppic','product_uom_qty' : tole_satu}, context=context)
                        #gd_odline.write(cr, uid, idwx, {'state' : 'sent_to_ppic'}, context=context)
                cr.execute
                if "Tube" in ctage_id:
                   sale_order_obj_srch = sale_order_obj.search(cr, uid, [('po_sl','like','T'),('create_date','>=',mntldif),('create_date','<=',mntldifone)], count=True)  
                   if sale_order_obj_srch != False:
                       sale_order_obj_srch_vone = sale_order_obj.search(cr, uid, [('po_sl','like','T'),('create_date','>=',mntldif),('create_date','<=',mntldifone)])
                       for idsl in sale_order_obj_srch_vone:
                           sl_apend_id.append(idsl)
                           mx_id_sl = max(sl_apend_id)
                       sale_order_obj_bwsa = sale_order_obj.browse(cr, uid, mx_id_sl, context=context)
                       spl_tube = sale_order_obj_bwsa.po_sl
                       spl_tube_one = spl_tube.split("T")
                       spl_tube_two = spl_tube_one[1].split("/")
                       wstart = int(spl_tube_two[0]) + 1
                       trplus = "T"+str(wstart)+"/"+tr+"/"+yer+"/"+cbatwo+""+str(cbafour)
                       self.write(cr, uid ,ids, {'po_sl' : trplus}, context=context)
                   else:
                       trplus = "T"+str(wstart)+"/"+tr+"/"+yer+"/"+cbatwo+""+str(cbafour)
                       self.write(cr, uid ,ids, {'po_sl' : trplus}, context=context)
                else:
                    sale_order_obj_srch = sale_order_obj.search(cr, uid, [('po_sl','not like','T'),('create_date','>=',mntldif),('create_date','<=',mntldifone)], count=True)
                    if sale_order_obj_srch != False:
                        sale_order_obj_srch_bone = sale_order_obj.search(cr, uid, [('po_sl','not like','T'),('create_date','>=',mntldif),('create_date','<=',mntldifone)])
                        for bidsl in sale_order_obj_srch_bone:
                             sl_apend_id.append(bidsl)
                             mx_id_sl = max(sl_apend_id)
                        sale_order_obj_bwsa = sale_order_obj.browse(cr, uid, mx_id_sl, context=context)
                        spl_tube = sale_order_obj_bwsa.po_sl
                        spl_tube_one = spl_tube.split("/")
                        wstart = int(spl_tube_one[0]) + 1
                        trplus = str(wstart)+"/"+tr+"/"+yer+"/"+cbatwo+""+str(cbafour)     
                        self.write(cr, uid ,ids, {'po_sl' : trplus}, context=context)
                    else:
                        trplus = str(wstart)+"/"+tr+"/"+yer+"/"+cbatwo+""+str(cbafour)
                        self.write(cr, uid ,ids, {'po_sl' : trplus}, context=context)
                
                daate = datetime.strptime(tg_dte, "%Y-%m-%d %H:%M:%S")
                ndate = daate + timedelta(days=7)
                self.write(cr, uid ,ids, {'approve_terakhr' : uid}, context=context)
                return {
                    'type': 'ir.actions.act_window',
                    'name': _('Sales Order'),
                    'res_model': 'sale.order',
                    'view_type': 'tree',
                    'view_mode': 'tree',
                    'target': 'current',
                    'domain'    : [('state', '=', 'approval')],
                    'nodestroy': True,
                }
                
sale_order()
class sale_order_line(osv.osv):
    _inherit = "sale.order.line"
    
    '''
    def price_funcc(self, cr, uid, ids, field, args, vals, context=None):
        res = {}
        for reec in self.browse(cr, uid, ids):
            res[reec.id] = vals 
        return res
    '''
    _columns = {
                 'ukuran_marketing'     : fields.char('Ukuran Marketing'),
                 'qualitas_marketing'   : fields.char('Kualitas Marketing'),
                 'mrp_no_kip' : fields.char('No KIP', readonly=True, states={'draft': [('readonly', False)], 'sent_to_ppic' : [('readonly', False)]}),
                 'purchase_customer_no' : fields.char('PO NO', required = True, readonly=True, states={'draft': [('readonly', False)]}),
                 #'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price'), readonly=True, states={'draft': [('readonly', False)],'sent_to_costing' : [('readonly', False)]}),
                 #'price_unit_funct'     : fields.function(price_funcc,type='float',string='Unit Price'),
                 'product_uom_qty': fields.float('Quantity', digits_compute= dp.get_precision('Product UoS'), required=True),
                 'toleransi_skp'     : fields.integer('Toleransi',readonly=True,states={'draft': [('readonly', False)]}),     
                 'price_unit_hidden' : fields.float('Unit Price'),
                 'price_unit': fields.float('Unit Price', required=True, digits_compute= dp.get_precision('Product Price')),
                 'product_id': fields.many2one('product.product', 'Product', domain=[('sale_ok', '=', True),('categ_id.name','in',('Carton Box','Paper Tube'))], readonly=True, states={'draft': [('readonly', False)], 'sent_to_ppic' : [('readonly', False)]}, change_default=True),
                 'customer_semu' : fields.integer('Customer parsing'),
                 'qty_realisasi'    : fields.float('Quantity Asli', readonly=True),
                 'state'         : fields.selection([
                                                            ('draft', 'Draft'),
                                                            ('sent_to_ppic', 'PPIC'),
                                                            ('sent_to_costing', 'Costing'),
                                                            ('sent_to_sale', 'Last Check Quotation'),
                                                            ('approval', 'Wait for Approval GM/Direksi'),
                                                            ('progress', 'SKP'),
                                                            ('manual', 'SKP to Invoice'),
                                                            ('cancel', 'Cancelled'),
                                                            ('waiting_date', 'Waiting Schedule'),
                                                            ('invoice_except', 'Invoice Exception'),
                                                            ('confirmed', 'Confirmed'),
                                                            ('exception', 'Exception'),
                                                            ('done', 'Done'),
                                                            ], 'Status', readonly=True, track_visibility='onchange',
                                                           help="Gives the status of the quotation or sale order. \nThe exception status is automatically set when a cancel operation occurs in the processing of a document linked tp the sale order. \nThe 'Waiting Schedule' status is set when the invoice is confirmed but waiting for the scheduler to run on the order date", 
                                                           select=True, ondelete="cascade"),
                                                           
                }
    _defaults = {
        'price_unit': 0.0,
    }
    
    def price_history(self, cr, uid, ids, context=None):
        # raise osv.except_osv(_('Warning!'), _('TEST %s') % ids)
        ret = {}
        # lines = self.browse(cr, uid, ids)
        for lines in self.browse(cr, uid, ids):
            ret = {  
                'type': 'ir.actions.act_window',
                'name': 'History Harga',
                'view_type': 'form',
                'view_mode': 'tree',
                #'view_id': lines.id,
                'res_model': 'sale.order.line',
                'target': 'new',
                'context': context,
                'domain' : [('product_id', '=', lines.product_id.id), ('state', 'in', ('confirmed', 'done'))],
                'limit' : 10,
                # 'flags': {'form': {'action_buttons': True}}
                }
        return ret
    
    def product_id_change_new(self, cr, uid, ids, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
        context = context or {}
        lang = lang or context.get('lang',False)
        if not  partner_id:
            raise osv.except_osv(_('No Customer Defined!'), _('Before choosing a product,\n select a customer in the sales form.'))
        warning = {}
        product_uom_obj = self.pool.get('product.uom')
        partner_obj = self.pool.get('res.partner')
        product_obj = self.pool.get('product.product')
        context = {'lang': lang, 'partner_id': partner_id}
        if partner_id:
            lang = partner_obj.browse(cr, uid, partner_id).lang
        context_partner = {'lang': lang, 'partner_id': partner_id}

        if not product:
            return {'value': {'th_weight': 0,
                'product_uos_qty': qty}, 'domain': {'product_uom': [],
                   'product_uos': []}}
        if not date_order:
            date_order = time.strftime(DEFAULT_SERVER_DATE_FORMAT)

        result = {}
        warning_msgs = ''
        product_obj = product_obj.browse(cr, uid, product, context=context_partner)
        cr.execute("SELECT no_kiip FROM product_product WHERE id=%s",(product_obj.id,))
        dgf = cr.fetchone()[0]
        result['mrp_no_kip'] = dgf
        uom2 = False
        if uom:
            uom2 = product_uom_obj.browse(cr, uid, uom)
            if product_obj.uom_id.category_id.id != uom2.category_id.id:
                uom = False
        if uos:
            if product_obj.uos_id:
                uos2 = product_uom_obj.browse(cr, uid, uos)
                if product_obj.uos_id.category_id.id != uos2.category_id.id:
                    uos = False
            else:
                uos = False
        fpos = fiscal_position and self.pool.get('account.fiscal.position').browse(cr, uid, fiscal_position) or False
        if update_tax: #The quantity only have changed
            result['tax_id'] = self.pool.get('account.fiscal.position').map_tax(cr, uid, fpos, product_obj.taxes_id)

        if not flag:
            result['name'] = self.pool.get('product.product').name_get(cr, uid, [product_obj.id], context=context_partner)[0][1]
            if product_obj.description_sale:
                result['name'] += '\n'+product_obj.description_sale
        domain = {}
        if (not uom) and (not uos):
            result['product_uom'] = product_obj.uom_id.id
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
                uos_category_id = product_obj.uos_id.category_id.id
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
                uos_category_id = False
            result['th_weight'] = qty * product_obj.weight
            domain = {'product_uom':
                        [('category_id', '=', product_obj.uom_id.category_id.id)],
                        'product_uos':
                        [('category_id', '=', uos_category_id)]}
        elif uos and not uom: # only happens if uom is False
            result['product_uom'] = product_obj.uom_id and product_obj.uom_id.id
            result['product_uom_qty'] = qty_uos / product_obj.uos_coeff
            result['th_weight'] = result['product_uom_qty'] * product_obj.weight
        elif uom: # whether uos is set or not
            default_uom = product_obj.uom_id and product_obj.uom_id.id
            q = product_uom_obj._compute_qty(cr, uid, uom, qty, default_uom)
            if product_obj.uos_id:
                result['product_uos'] = product_obj.uos_id.id
                result['product_uos_qty'] = qty * product_obj.uos_coeff
            else:
                result['product_uos'] = False
                result['product_uos_qty'] = qty
            result['th_weight'] = q * product_obj.weight        # Round the quantity up

        if not uom2:
            uom2 = product_obj.uom_id
        # get unit price

        if not pricelist:
            warn_msg = _('You have to select a pricelist or a customer in the sales form !\n'
                    'Please set one before choosing a product.')
            warning_msgs += _("No Pricelist ! : ") + warn_msg +"\n\n"
        else:
            price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
            if price is False:
                warn_msg = _("Cannot find a pricelist line matching this product and quantity.\n"
                        "You have to change either the product, the quantity or the pricelist.")

                warning_msgs += _("No valid pricelist line found ! :") + warn_msg +"\n\n"
            else:
                cr.execute("SELECT MAX(id) FROM stock_move WHERE product_id = %s AND state = %s AND location_dest_id = 9",(product_obj.id,'done'))
                auoo = cr.fetchone()[0]
                try:
                    cr.execute("SELECT sale_line_id FROM stock_move WHERE id = %s",(auoo,))
                    auoo_one = cr.fetchone()[0]
                #raise osv.except_osv(_('warning'),_(auoo))
                    if auoo_one >= 0:
                        cr.execute("SELECT price_unit FROM sale_order_line WHERE id = %s",(auoo_one,))
                        auoo_two = cr.fetchone()[0]
                        #self.price_funcc(cr, uid, ids, auoo_two, context)
                        result.update({'price_unit': auoo_two})
                        result.update({'price_unit_hidden': auoo_two})
                        
                    #return {'value':result, 'domain': domain, 'warning': warning}  
                except:
                    price = self.pool.get('product.pricelist').price_get(cr, uid, [pricelist],
                    product, qty or 1.0, partner_id, {
                        'uom': uom or result.get('product_uom'),
                        'date': date_order,
                        })[pricelist]
                    result.update({'price_unit': price})
                    result.update({'price_unit_hidden': price})     
                return {'value':result, 'domain': domain, 'warning': warning}  
                
        if warning_msgs:
            warning = {
                       'title': _('Configuration Error!'),
                       'message' : warning_msgs
                    }
        return {'value': result, 'domain': domain, 'warning': warning}
    def price_unit_new(self, cr, uid, ids, price_unit_hidden, context=None):
        return {'value':{'price_unit' : price_unit_hidden}}
sale_order_line()    
class shan_ju(osv.osv_memory):
    _name="sale.shan_ju"
    _columns = {
                    'pd_type' : fields.selection([
                                                  ('box','Box'),
                                                  ('tube', 'Tube'),
                                                  ],'Product Type'),
                }
    
    def ts_prt(self, cr, uid, ids, context=None):
        tutut = self.browse(cr, uid, ids[0], context=context)
        tutu = tutut.pd_type
        #context.set(tutu)
        #raise osv.except_osv(_('move id'), _(tutu))
        return { 'type': 'ir.actions.report.xml', 'report_name': 'lo.mako', 'context':{'pd_type':tutu}}
        #return True
shan_ju()


    
    
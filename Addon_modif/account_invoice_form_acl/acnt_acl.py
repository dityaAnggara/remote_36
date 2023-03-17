'''
Created on Nov 17, 2014

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
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions
import roman
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _




apn_dura = []
ooop = []
ui_loooo = ""
get_or = []
class account_invoice(osv.osv):
    _inherit = "account.invoice"
    _description = "inherit account invoice"
   
    _columns    = {
                    'invoice_number_acl'    : fields.char('No Invoice'),
                    'no_faktur'             : fields.char('No Faktur Pajak'),
                    'no_invoice_supp'       : fields.char('No Faktur'),
                    'stock_ones'            : fields.many2many('stock_acl_v2.out_acl', 'invoice_do_rel_one_again', 'invoice_id_one', 'stock_id_one',string='DO line'),
                    
                   }
    _sql_constraints = [
        ('number_uniq', 'unique(number, company_id, journal_id, type)', 'Invoice Number must be unique per Company!'),
        
    ]
    
    def write(self, cr, uid, ids, values, context = None):
       add_apn = []     
       self_try = self.browse(cr, uid, ids[0], context)
       res = super(account_invoice, self).write(cr, uid, ids, values, context = context)
       for opi in self_try.stock_ones:
          cr.execute("SELECT COUNT(stock_id_one) FROM invoice_do_rel_one_again WHERE stock_id_one = %s",(opi.id,))
          frt = cr.fetchone()[0]
          if frt > 1:
              raise osv.except_osv(_('WARNING'), _("Surat Jalan "+opi.surat_jalan+" sudah terpakai di invoice")) 
      
       return res
    
    def view_pick(self, cr, uid, ids, context=None):
        hiu = self.browse(cr, uid, ids[0], context)
        raise osv.except_osv(_('eewr'),_(hiu.id))
        
    
    def create_number_inv(self, cr, uid, ids, context=None):
        context.update({'id_updt': ids[0]})
        brw_self = self.browse(cr, uid, ids, context=context)[0]
        no_faktur = brw_self.no_faktur
        pol_account_setting = self.pool.get('account_setting_acl.account_config_settings')
        pol_customer_obj = self.pool.get('res_partner')
        pol_invoice_obj = self.pool.get('account.invoice')
        hsl_rng = 0
        year_awl = time.strftime("%Y-01-01")
        year_akh = time.strftime("%Y-12-31")
        year_tok = time.strftime("%Y")
        mntl = time.strftime("%m")
        imntl = int(mntl)
        fmntl = "%01d" % (imntl)
        ifmntl = int(fmntl)
        tr = roman.toRoman(ifmntl)
        '''
        test
        '''
        pol_account_setting_search = pol_account_setting.search(cr, uid, [])
        appen_id = []
        tnh_cvv = ""
        tnh_cvv_a = ""
        kb_code = ""
        nokb_code = ""
        ukb_code = ""
        rang_pertama = ""
        rang_terakhir = ""
        brw_accnt_inv = self.browse(cr, uid, ids, context=context)[0]
        kawasn_type = brw_accnt_inv.partner_id.area_type  
        for idx in pol_account_setting_search:
            appen_id.append(idx)
            gt_ac_id = int(max(appen_id))
            pol_account_setting_browse = pol_account_setting.browse(cr, uid, gt_ac_id, context=context)
            tnh_cvv = pol_account_setting_browse.tahun_pajak_acl
            tnh_cvv_v2 = tnh_cvv[-2:] 
            tnh_cvv_a = pol_account_setting_browse.no_urut_k_pajak_acl
            kb_code = pol_account_setting_browse.kb_code_acl
            nokb_code = pol_account_setting_browse.nonkb_code_acl
            rang_pertama = pol_account_setting_browse.nmr_urut_pajak_pertama
            rang_pertama = str(rang_pertama)
            rang_terakhir = pol_account_setting_browse.nmr_urut_pajak_terakhir
            rang_terakhir = str(rang_terakhir)
            if kawasn_type == 'kb':
                ukb_code = kb_code
            else:
                ukb_code = nokb_code   
        
        pol_invoice_search = pol_invoice_obj.search(cr, uid, [('no_faktur','=',False)], count=True)
        #pol_invoice_obj_srch = pol_invoice_obj.search(cr, uid, [('create_date','>=',year_awl),('create_date','<=',year_akh),('no_faktur','!=',False)], count=True)
        pol_invoice_obj_srch = pol_invoice_obj.search(cr, uid, [('no_faktur','!=',False)], count=True)
        if no_faktur == False:
           if "OUT" in brw_self.origin:
               if pol_invoice_obj_srch != 0:
                    apn_id = []
                    gt_id_lx = ""
                    pol_invoice_obj_srch_m = pol_invoice_obj.search(cr, uid, [('no_faktur','!=',False)])
                    for lxid in pol_invoice_obj_srch_m:
                        apn_id.append(lxid)
                        gt_id_lx = int(max(apn_id))
                    
                        
                    pol_invoice_obj_brw_m = pol_invoice_obj.browse(cr, uid, gt_id_lx, context=context)
                    pr_fktur = pol_invoice_obj_brw_m.no_faktur[-8:]
                    in_pr_fktur = int(pr_fktur)+1
                    str_in_pr_fktur = str(in_pr_fktur)
                    in_rang_terakhir = int(rang_terakhir)
                    krng_bingit = in_rang_terakhir - in_pr_fktur
                    if krng_bingit <= 0:
                       raise osv.except_osv(_('Warning!'), _('Range No Pajak Anda sudah Habis'))       
                    else:
                        qsss_one = ukb_code+"."+tnh_cvv_a+"-"+tnh_cvv_v2+"."+str_in_pr_fktur
                        #self.write(cr, uid, ids, {'no_faktur': qsss_one}, context=context)
                        cr.execute("UPDATE account_invoice SET no_faktur = %s WHERE id = %s",(qsss_one, brw_accnt_inv.id))
                        get_fktr_one = self.browse(cr, uid, ids, context=context)[0]
                        get_fktr_one_v2 = get_fktr_one.no_faktur[-5:] 
                        qss_one = get_fktr_one_v2+"/ACL/"+tr+"/"+year_tok
                        #self.write(cr, uid, ids, {'invoice_number_acl': qss_one}, context=context)
                        cr.execute("UPDATE account_invoice SET invoice_number_acl = %s WHERE id = %s",(qss_one, brw_accnt_inv.id))
               else:
                    qsss = ukb_code+"."+tnh_cvv_a+"-"+tnh_cvv_v2+"."+rang_pertama
                    #self.write(cr, uid, ids, {'no_faktur': qsss}, context=context)
                    cr.execute("UPDATE account_invoice SET no_faktur = %s WHERE id = %s",(qsss, brw_accnt_inv.id))
                    get_fktr = self.browse(cr, uid, ids, context=context)[0]
                    get_fktr_v2 = get_fktr.no_faktur[-5:] 
                    qss = get_fktr_v2+"/ACL/"+tr+"/"+year_tok
                    #self.write(cr, uid, ids, {'invoice_number_acl': qss}, context=context)
                    cr.execute("UPDATE account_invoice SET invoice_number_acl = %s WHERE id = %s",(qss, brw_accnt_inv.id))    
           else:
                if pol_invoice_obj_srch != 0:
                    apn_id = []
                    gt_id_lx = ""
                    pol_invoice_obj_srch_m = pol_invoice_obj.search(cr, uid, [('no_faktur','!=',False)])
                    for lxid in pol_invoice_obj_srch_m:
                        apn_id.append(lxid)
                        gt_id_lx = int(max(apn_id))
                    
                        
                    pol_invoice_obj_brw_m = pol_invoice_obj.browse(cr, uid, gt_id_lx, context=context)
                    pr_fktur = pol_invoice_obj_brw_m.no_faktur[-8:]
                    in_pr_fktur = int(pr_fktur)+1
                    str_in_pr_fktur = str(in_pr_fktur)
                    in_rang_terakhir = int(rang_terakhir)
                    krng_bingit = in_rang_terakhir - in_pr_fktur
                    if krng_bingit <= 0:
                       raise osv.except_osv(_('Warning!'), _('Range No Pajak Anda sudah Habis'))       
                    else:
                        qsss_one = ukb_code+"."+tnh_cvv_a+"-"+tnh_cvv_v2+"."+str_in_pr_fktur
                        #self.write(cr, uid, ids, {'no_faktur': qsss_one}, context=context)
                        cr.execute("UPDATE account_invoice SET no_faktur = %s WHERE origin = %s",(qsss_one, brw_accnt_inv.origin))
                        get_fktr_one = self.browse(cr, uid, ids, context=context)[0]
                        get_fktr_one_v2 = get_fktr_one.no_faktur[-5:] 
                        qss_one = get_fktr_one_v2+"/ACL/"+tr+"/"+year_tok
                        #self.write(cr, uid, ids, {'invoice_number_acl': qss_one}, context=context)
                        cr.execute("UPDATE account_invoice SET invoice_number_acl = %s WHERE origin = %s",(qss_one, brw_accnt_inv.origin))
                else:
                    qsss = ukb_code+"."+tnh_cvv_a+"-"+tnh_cvv_v2+"."+rang_pertama
                    #self.write(cr, uid, ids, {'no_faktur': qsss}, context=context)
                    cr.execute("UPDATE account_invoice SET no_faktur = %s WHERE origin = %s",(qsss, brw_accnt_inv.origin))
                    get_fktr = self.browse(cr, uid, ids, context=context)[0]
                    get_fktr_v2 = get_fktr.no_faktur[-5:] 
                    qss = get_fktr_v2+"/ACL/"+tr+"/"+year_tok
                    #self.write(cr, uid, ids, {'invoice_number_acl': qss}, context=context)
                    cr.execute("UPDATE account_invoice SET invoice_number_acl = %s WHERE origin = %s",(qss, brw_accnt_inv.origin))    
            
        else:
            raise osv.except_osv(_('Warning!'), _('No Faktur Sudah Terbit.'))
        return True
class account_invoice_line(osv.osv):
    _inherit = "account.invoice.line"
    _columns = {
                    'qty_realisasi' : fields.float('Quantity Realisasi', digits_compute= dp.get_precision('Product Unit of Measure'), required=True),
                }
class account_voucher(osv.osv):
    _inherit = "account.voucher"
    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
            '''
            mov_brow = self.pool.get('stock.move').browse(cr, uid, move_line_id, context)
            cr.execute("SELECT order_policy FROM sale_order WHERE origin = %s",(mov_brow.origin,))
            lala = cr.fetchone()[0]
            if lala == 'manual':
                cr.execute("SELECT count(id) FROM stock_picking WHERE origin = %s AND state NOT IN ('done','cancel')",(mov_brow.origin,))
                luluj = cr.fetchone()[0]
                if luluj > 0:
                    cr.execute("UPDATE sale_order SET state = 'manual' WHERE origin = %s",(mov_brow.origin,))
            '''
        #raise osv.except_osv(_('test'),_())         
        return True
class surat_jalan_line(osv.osv):
    _name = "account_invoice_form_acl.surat_jalan_line"
    _columns = {
                    #'stock_pickings' : fields.many2many('stock.picking', 'invoice_do_rel', 'stock_id', 'invoice_id',string='DO line'),
                }
    
#class new_sj_new(osv.osv):

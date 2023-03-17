from mx import DateTime
from lxml import etree

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
import openerp.addons.decimal_precision as dp
from openerp import netsvc

class account_invoice(osv.osv):
    _inherit="account.invoice"
    
    def create(self, cr, uid, vals, context=None):
        if 'nomor_faktur_id' in vals:
            self.pool.get('nomor.faktur.pajak').write(cr, uid, vals['nomor_faktur_id'], {'status':'1'})
        return super(account_invoice, self).create(cr, uid, vals, context=context)
    
    def _nomor_faktur_company(self, cr, uid, ids, nomorfaktur, arg, context=None):
        res = {}
        for nomor in self.browse(cr, uid, ids, context):
            if nomor.partner_id.kode_transaksi != False and nomor.partner_id.kode_status != False:
                res[nomor.id] = "%s%s." % (nomor.partner_id.kode_transaksi, nomor.partner_id.kode_status)
            else:
                res[nomor.id] = ""
        return res
    
    def onchange_partner_id(self, cr, uid, ids, type, partner_id,\
            date_invoice=False, payment_term=False, partner_bank_id=False, company_id=False):
        partner_payment_term = False
        acc_id = False
        bank_id = False
        fiscal_position = False
        
        opt = [('uid', str(uid))]
        if partner_id:

            opt.insert(0, ('id', partner_id))
            p = self.pool.get('res.partner').browse(cr, uid, partner_id)
            if company_id:
                if (p.property_account_receivable.company_id and (p.property_account_receivable.company_id.id != company_id)) and (p.property_account_payable.company_id and (p.property_account_payable.company_id.id != company_id)):
                    property_obj = self.pool.get('ir.property')
                    rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('res_id','=','res.partner,'+str(partner_id)+''),('company_id','=',company_id)])
                    if not rec_pro_id:
                        rec_pro_id = property_obj.search(cr,uid,[('name','=','property_account_receivable'),('company_id','=',company_id)])
                    if not pay_pro_id:
                        pay_pro_id = property_obj.search(cr,uid,[('name','=','property_account_payable'),('company_id','=',company_id)])
                    rec_line_data = property_obj.read(cr,uid,rec_pro_id,['name','value_reference','res_id'])
                    pay_line_data = property_obj.read(cr,uid,pay_pro_id,['name','value_reference','res_id'])
                    rec_res_id = rec_line_data and rec_line_data[0].get('value_reference',False) and int(rec_line_data[0]['value_reference'].split(',')[1]) or False
                    pay_res_id = pay_line_data and pay_line_data[0].get('value_reference',False) and int(pay_line_data[0]['value_reference'].split(',')[1]) or False
                    if not rec_res_id and not pay_res_id:
                        raise osv.except_osv(_('Configuration Error!'),
                            _('Cannot find a chart of accounts for this company, you should create one.'))
                    account_obj = self.pool.get('account.account')
                    rec_obj_acc = account_obj.browse(cr, uid, [rec_res_id])
                    pay_obj_acc = account_obj.browse(cr, uid, [pay_res_id])
                    p.property_account_receivable = rec_obj_acc[0]
                    p.property_account_payable = pay_obj_acc[0]

            if type in ('out_invoice', 'out_refund'):
                acc_id = p.property_account_receivable.id
                partner_payment_term = p.property_payment_term and p.property_payment_term.id or False
            else:
                acc_id = p.property_account_payable.id
                partner_payment_term = p.property_supplier_payment_term and p.property_supplier_payment_term.id or False
            fiscal_position = p.property_account_position and p.property_account_position.id or False
            if p.bank_ids:
                bank_id = p.bank_ids[0].id
        
        p = self.pool.get('res.partner').browse(cr, uid, partner_id)        
        faktur = ""
        if p.kode_transaksi != False and p.kode_status != False:
            faktur = "%s%s." % (p.kode_transaksi,p.kode_status)

        result = {'value': {
            'account_id': acc_id,
            'nomor_faktur_company': faktur,
            'payment_term': partner_payment_term,
            'fiscal_position': fiscal_position
            }
        }

        if type in ('in_invoice', 'in_refund'):
            result['value']['partner_bank_id'] = bank_id

        if payment_term != partner_payment_term:
            if partner_payment_term:
                to_update = self.onchange_payment_term_date_invoice(
                    cr, uid, ids, partner_payment_term, date_invoice)
                result['value'].update(to_update['value'])
            else:
                result['value']['date_due'] = False

        if partner_bank_id != bank_id:
            to_update = self.onchange_partner_bank(cr, uid, ids, bank_id)
            result['value'].update(to_update['value'])
        return result
    
    _columns = {
            'phone': fields.related('partner_id', 'mobile', type='char', string='Phone', readonly=True),
            'nomor_faktur_id': fields.many2one('nomor.faktur.pajak', string='Nomor Faktur Pajak'),
            'nomor_faktur_company': fields.function(_nomor_faktur_company, type='char', string="Nomor Faktur", store=True),        
    }
    
    def _get_nomor(self, cr, uid, partner_id=False, context=None):
        if context is None:
            context = {}
        user = self.pool.get('res.partner').browse(cr,uid,partner_id,context=context)
        faktur = ""
        if user != False:
            faktur = "%s%s." % (user.kode_transaksi, user.kode_status)
        return faktur 
        
    _defaults = {
            'nomor_faktur_company': _get_nomor,
    }
account_invoice()

class custom_payment(osv.osv):
    _inherit="account.voucher"
    _columns = {
                'invoice_name': fields.related('line_ids','name',type='char',string='Invoice',readonly=True),
    }
custom_payment()
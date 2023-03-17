'''
Created on Dec 7, 2014

@author: innotek
'''
from datetime import datetime
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _

class faktur_umum(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        super(faktur_umum, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'cr':cr,
            'uid': uid,
            'account_inv' : self.account_invoice,
            'acn_line'    : self.account_invoice_kosong,
            'acn_line_one': self.account_invoice_gkosong,
            'acn_ln_bw'   : self.brow_line,
            'satu'        : self.acn_asline,
            'dua'         : self.acn_browse,
            'tiga'        : self.acn_as_li, 
        })  
            
    def account_invoice(self):
        return self.pool.get('account.invoice').browse(self.cr, self.uid, self.ids) or False
    def acn_asline(self):
        return self.pool.get('account.invoice').search(self.cr,self.uid,[('reference','=',False)])
    def acn_as_li(self, nam):
        return self.pool.get('account.invoice').search(self.cr,self.uid,[('origin','=',nam)])
    def acn_browse(self, ig):
        return self.pool.get('account.invoice').browse(self.cr, self.uid, ig)
    def account_invoice_kosong(self, inv_id):
        return self.pool.get('account.invoice.line').search(self.cr,self.uid,[('product_id','=',False),('invoice_id','=',inv_id)])
    def account_invoice_gkosong(self, inv_id):
        return self.pool.get('account.invoice.line').search(self.cr,self.uid,[('product_id','!=',False),('invoice_id','=',inv_id)])
    def brow_line(self, id):
        return self.pool.get('account.invoice.line').browse(self.cr, self.uid, id)
        
    
        
report_sxw.report_sxw('report.faktur.pajak.mako', 'account.invoice', 'account_invoice_form_acl/rept/faktur_pajak.mako', parser=faktur_umum, header=False)
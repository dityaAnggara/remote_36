'''
Created on Dec 7, 2014

@author: innotek
'''
# from datetime import datetime
from openerp.report import report_sxw
# from openerp.osv import osv
# from openerp.tools.translate import _

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
    def brow_line(self, ids):
        return self.pool.get('account.invoice.line').browse(self.cr, self.uid, ids)
        
report_sxw.report_sxw('report.faktur.pajak.mako.2', 'account.invoice', 'sale_report_ok/report/mako/faktur_pajak.html', parser=faktur_umum)

class khusus_outstanding(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        
        super(khusus_outstanding, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'cr':cr,
                'uid': uid,
                'get_records': self._get_records,
                'get_ord' : self._get_sale_order,
                'brw_movv' : self.brw_mov,
                'rcrd_toe' : self.rcrd_two,
                
            })

    def _get_sale_order(self):
        order_brows = self.pool.get('sale.order').search(self.cr, self.uid,[]) 
        return self.pool.get('sale.order').browse(self.cr, self.uid, self.ids) or False
    def _get_records(self, ormov):
        return self.pool.get('stock.move').search(self.cr, self.uid, [('origin','=', ormov),('state','=','done')])
    def brw_mov(self, id):
        return self.pool.get('stock.move').browse(self.cr, self.uid, id)
    def rcrd_two(self, orme, pdi):
        return self.pool.get('stock.move').search(self.cr, self.uid, [('origin','=', orme),('state','=','done'),('sale_line_id','=',pdi)])
        
report_sxw.report_sxw('report.outstanding_one.out.mako.2', 'sale.order', 'sale_report_ok/report/mako/sale_skp_out.html', parser=khusus_outstanding)


class tnd_terima(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        
        super(tnd_terima, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'cr':cr,
                'uid': uid,
                'tgl_terima' : self._tgl_terima,
                'tgl_trm' : self._tgl_trm,
            })

    def _tgl_terima(self, tgl):
        return self.pool.get('stock.picking').search(self.cr, self.uid, [('name','=', tgl)])
    
    def _tgl_trm(self, id):
        return self.pool.get('stock.picking').browse(self.cr, self.uid, id)
    
report_sxw.report_sxw('report.tanda_terima.mako.2', 'account.invoice', 'sale_report_ok/report/mako/tanda_terima.html', parser=tnd_terima)

class kwt(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        
        super(kwt, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'cr':cr,
                'uid': uid,
                'id_in' : self._id_in,
                'deskrip' : self._desk,
            })

    def _id_in(self, tgl):
        return self.pool.get('account.invoice').search(self.cr, self.uid, [('number','=', tgl)])
    
    def _desk(self, id):
        return self.pool.get('account.invoice').browse(self.cr, self.uid, id)
    
report_sxw.report_sxw('report.acc.voucher.report.kwitansi', 'account.voucher', 'sale_report_ok/report/mako/kwitansi.html', parser=kwt)

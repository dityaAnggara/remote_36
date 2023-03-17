'''
Created on Jan 4, 2015

@author: innotek
'''
from datetime import datetime
from report import report_sxw
from osv import osv
import pooler
from tools.translate import _

class khusus_test_sale(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        super(khusus_test_sale, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'cr':cr,
            'uid': uid,
            'ctx' : context.get('pd_type'),
            'apen_test' : self.get_sale,
            'bws'       : self.brw_sale,
            'pick'      : self.get_pick,
            'pick_line' : self.bws_pick,
            
        })
    def get_sale(self,ctx):
        ser_cat_pod = self.pool.get('product.category').search(self.cr, self.uid, [('name','=ilike', ctx)])
        apnd_id = []
        for uoi in ser_cat_pod:
            bwqs = self.pool.get('product.category').browse(self.cr, self.uid, uoi)
            apnd_id.append(bwqs.id)
        max_apn = max(apnd_id) 
        return self.pool.get('sale.order').search(self.cr, self.uid, [('category_id','=', max_apn)])
    def brw_sale(self, id):
        return self.pool.get('sale.order').browse(self.cr, self.uid, id)
    def get_pick(self, id):
        return self.pool.get('stock.picking').search(self.cr, self.uid, [('sale_id','=', id),('surat_jalan','!=',False)])
    def bws_pick(self, id):       
        return self.pool.get('stock.picking').browse(self.cr, self.uid, id)    
        
report_sxw.report_sxw('report.lo.mako', 'sale.shan_ju', 'sale_acl_v3/ngerepoti/test_sale.mako', parser=khusus_test_sale, header=False)

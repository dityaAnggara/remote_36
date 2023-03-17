from datetime import datetime
from report import report_sxw
from openerp.osv import osv
import pooler
from tools.translate import _

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
        
report_sxw.report_sxw('report.outstanding_one.out.mako', 'sale.order', 'sale_acl_v3/ngerepoti/outstanding_one.mako', parser=khusus_outstanding, header=False)

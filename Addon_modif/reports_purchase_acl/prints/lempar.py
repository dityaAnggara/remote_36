from datetime import datetime
from openerp.report import report_sxw
from openerp.osv import osv
from openerp import pooler
from openerp.tools.translate import _

class purchase_lempar(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        super(purchase_lempar, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'cr'                : cr,
            'uid'               : uid,
            'jenis_report'      : context.get('jenis_report'),
            'date_start'        : context.get('date_start'),
            'date_end'          : context.get('date_end'),
            'purchase_type'     : context.get('purchase_type'),
            'all'               : context.get('all'),
            'supplier_list'     : context.get('supplier_list'),
            'type_view'         : context.get('type_view'),
            'fktr_browse'       : self.fktr_browse,
            'get_p_type'        : self.get_p_type,
            'get_p_brows'       : self.get_p_brows,
            'rel_inv'           : self.rel_inv,
            'rel_inv_one'       : self.rel_inv_one,
            'get_id_iinv'       : self.get_id_iinv,
            'invoice_data'      : self.invoice_data,
            'invoice_data_one'  : self.invoice_data_one,
            'invoice_broww'     : self.invoice_broww,
            'get_sj_pu'         : self.get_sj_pu,
            'get_sj_line'       : self.get_sj_line,
            'get_move_line'     : self.get_move_line,
            'get_move_brose'    : self.get_move_brose,
            'get_sj_pu_sup'     : self.get_sj_pu_sup,
        })  
            
    def fktr_browse(self, ids): 
        return self.pool.get('account.invoice').browse(self.cr, self.uid, ids)
    def get_p_type(self, typp):
        return self.pool.get('purchase.order').search(self.cr, self.uid, [('purchase_state','=',typp)])
    def get_p_brows(self, ids):
        return self.pool.get('purchase.order').browse(self.cr, self.uid, ids)
    def rel_inv(self):
        self.cr.execute("SELECT order_line_id FROM purchase_order_line_invoice_rel")
        return self.cr.fetchall()
    def rel_inv_one(self, ids):
        self.cr.execute("SELECT invoice_id FROM purchase_order_line_invoice_rel WHERE order_line_id IN %s",(tuple(ids),))
        return self.cr.fetchall()
    def get_id_iinv(self, ids):
        self.cr.execute("SELECT invoice_id FROM account_invoice_line WHERE id IN %s",(tuple(ids),))
        return self.cr.fetchall()
    def invoice_data(self, ids, tanggal_start, tanggal_end):
        self.cr.execute("SELECT id FROM account_invoice WHERE id IN %s AND date_invoice BETWEEN %s AND %s",(tuple(ids),tanggal_start,tanggal_end))
        return self.cr.fetchall()
    def invoice_data_one(self, ids, sup_list, tanggal_start, tanggal_end):
        self.cr.execute("SELECT id FROM account_invoice WHERE  id IN %s AND partner_id = %s AND date_invoice BETWEEN %s AND %s",(tuple(ids),sup_list,tanggal_start,tanggal_end))
        return self.cr.fetchall()
    def invoice_broww(self, ids):
        return self.pool.get('account.invoice').browse(self.cr, self.uid, ids)
    def get_sj_pu(self, ids, tanggal_start, tanggal_end):
        return self.pool.get('stock.picking').search(self.cr, self.uid, [('purchase_id','in',(ids)),('date_done','>=',tanggal_start),('date_done','<=',tanggal_end),('type','=','in'),('state','=','done')])
    def get_sj_line(self, ids):
        return self.pool.get('stock.picking').browse(self.cr, self.uid, ids)
    def get_move_line(self, ids):
        return self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id','=',ids)])
    def get_move_brose(self, ids):
        return self.pool.get('stock.move').browse(self.cr, self.uid, ids)
    def get_sj_pu_sup(self, ids, tanggal_start, tanggal_end, sup_id):
        return self.pool.get('stock.picking').search(self.cr, self.uid, [('purchase_id','in',(ids)),('date_done','>=',tanggal_start),('date_done','<=',tanggal_end),('partner_id','=',sup_id),('type','=','in'),('state','=','done')])
    #def fty(self): 

# report_sxw.report_sxw('report.pr_vall.mako', 'purchase.pr_rp_val', 'reports_purchase_acl/prints/purchase_sj.html', parser=purchase_lempar, header=False)
report_sxw.report_sxw('report.pr_vall.mako', 'purchase.pr_rp_val', parser=purchase_lempar)

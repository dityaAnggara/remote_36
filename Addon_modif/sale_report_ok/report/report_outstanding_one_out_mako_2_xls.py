'''
Created on 2 Apr 2015

@author: innotek
'''
import xlwt
import time
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import _
import logging
import base64
import mx.DateTime

_logger = logging.getLogger(__name__)

class report_outstanding_one_out_mako_2_xls(report_xls):
    
    def oe_datetime_format(self, obj, format='%Y-%m-%d %H:%M:%S'):
        if obj.val:
            if hasattr(obj, 'name') and (obj.name):
                return mx.DateTime.strptime(obj.name, format)
            else:
                return False
        else:
            return False

    def chdf(self, obj, format1, format2):
        return datetime.strptime(obj, format1).strftime(format2)
    
    '''
    def get_ord(self):
        # order_brows = self.pool.get('sale.order').search(self.cr, self.uid, []) 
        return self.pool.get('sale.order').browse(self.cr, self.uid, self.ids) or False
    '''
    
    def get_records(self, ormov):
        return self.pool.get('stock.move').search(self.cr, self.uid, [
                                                                      ('origin', '=', ormov),
                                                                      ('state', '=', 'done')
                                                                      ])
    
    def brw_mov(self, id):
        return self.pool.get('stock.move').browse(self.cr, self.uid, id)
    
    def rcrd_two(self, orme, pdi):
        return self.pool.get('stock.move').search(self.cr, self.uid, [
                                                                      ('origin', '=', orme),
                                                                      ('state', '=', 'done'),
                                                                      ('sale_line_id', '=', pdi)
                                                                      ])
    
    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet('Report Outstanding SKP')
        baris = 0
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        a = "" 
        d = ""
        ap = []
        orgnnmm = ""
        for o in objects:
            d = o.create_date
            f = d.split(" ")
            fdate = f[0].split("-")
            ap.append(f[0])
            orgnnmm = o.name
        ws.write_merge(baris, baris, 0, 7, 'Report Outstanding SKP')
        baris += 1
        ws.write_merge(baris, baris, 0, 7, (('Periode : %s s.d %s') % (min(ap), max(ap))))
        baris += 2
        ws.write(baris, 0, 'Date')
        ws.write(baris, 1, 'No SKP')
        ws.write(baris, 2, 'Customer Code')
        ws.write(baris, 3, 'Customer Name')
        ws.write(baris, 4, 'Status')
        ws.write(baris, 5, 'Total Qty')
        ws.write(baris, 6, 'Total Delivery')
        ws.write(baris, 7, 'Sisa Delivery')
        baris += 1
        for o in objects:
            tot_qty = 0
            tot_del = 0
            for mo_s in self.get_records(o.name):
                df = self.brw_mov(mo_s)
                tot_del += df.product_qty
            for line in o.order_line:
                tot_qty += line.product_uom_qty
            stto = ""
            if o.partner_id.active == True:
                stto = "active"
            else:
                stto = "inactive"
            siss_dl = tot_qty - tot_del
            ws.write(baris, 0, (o.create_date or ''))
            ws.write(baris, 1, (o.po_sl or ''))
            ws.write(baris, 2, (o.partner_id.ref or ''))
            ws.write(baris, 3, (o.partner_id.name or ''))
            ws.write(baris, 4, (stto or ''))
            ws.write(baris, 5, (tot_qty or 0))
            ws.write(baris, 6, (tot_del or 0))
            ws.write(baris, 7, (siss_dl or 0))
            baris += 1
            ws.write(baris, 3, 'Customer Name')
            ws.write(baris, 4, 'Status')
            ws.write(baris, 5, 'Total Qty')
            ws.write(baris, 6, 'Total Delivery')
            ws.write(baris, 7, 'Sisa Delivery')
            baris += 1
            for linc in o.order_line:
                too_dl = 0
                for dfg in self.rcrd_two(o.name, linc.id):
                    line_f = self.brw_mov(dfg)
                    too_dl += line_f.product_qty
                kurang_banget = linc.product_uom_qty - too_dl
                ws.write(baris, 3, (linc.mrp_no_kip or ''))
                ws.write(baris, 4, (linc.product_id.name or ''))
                ws.write(baris, 5, (linc.product_uom_qty or ''))
                ws.write(baris, 6, (too_dl or 0))
                ws.write(baris, 7, (kurang_banget or 0))
                baris += 1
            baris += 1

report_outstanding_one_out_mako_2_xls('report.outstanding_one.out.mako.2.xls', 'sale.order')

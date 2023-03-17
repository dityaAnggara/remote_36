'''
Created on 30 Mar 2015

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

class report_purchase_po_xls(report_xls):
    
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

    def lines(self, state, start, end, done=True, partner=None):
        cond = [('date_order', '>=', start), ('date_order', '<=', end), ('purchase_state', '=', state)]
        if not partner is None:
            cond.append(('partner_id', '=', partner))

        if not done :
            cond.append(('state', '!=', 'done'))

        step1 = self.pool.get('purchase.order').search(self.cr, self.uid, cond)
        return self.pool.get('purchase.order').browse(self.cr, self.uid, step1)
    
    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet('Penerimaan Bahan Baku')
        baris = 0
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        for o in objects:
            i = 1
            ws.write_merge(baris, baris, 0, 8, 'Laporan Penerimaan Bahan Baku')
            baris += 1
            ws.write(baris, 0, 'Dari Tanggal')
            ws.write(baris, 1, ':')
            ws.write(baris, 2, (o.date_start or ''))
            baris += 1
            ws.write(baris, 0, 'Hingga Tanggal')
            ws.write(baris, 1, ':')
            ws.write(baris, 2, (o.date_end or ''))
            baris += 1
            if not o.all :
                ws.write(baris, 0, 'Supplier')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, (o.partner_id and o.partner_id.name or ''))
                baris += 1
            baris += 1
            ws.write_merge(baris, baris + 1, 0, 0, 'Tgl.')
            ws.write_merge(baris, baris, 1, 3, 'Nomor')
            ws.write_merge(baris, baris + 1, 4, 4, 'Supplier')
            ws.write_merge(baris, baris + 1, 5, 5, 'Kend')
            ws.write_merge(baris, baris + 1, 6, 6, 'Barang')
            ws.write_merge(baris, baris + 1, 7, 7, 'Satuan')
            ws.write_merge(baris, baris + 1, 8, 8, 'Jumlah')
            baris += 1
            ws.write(baris, 1, 'PO')
            ws.write(baris, 2, 'IN')
            ws.write(baris, 3, 'SJ')
            baris += 1
            if o.all :
                plines = self.lines(
                    'PO',
                    self.oe_datetime_format(o.date_start, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    self.oe_datetime_format(o.date_end, '%Y-%m-%d').strftime('%Y-%m-%d'))
            else :
                plines = self.lines(
                    'PO',
                    self.oe_datetime_format(o.date_start, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    self.oe_datetime_format(o.date_end, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    partner=o.partner_id.id)
            terima = 0.0
            for line in plines:
                for line3 in line.picking_ids:
                    for line4 in line3.move_lines:
                        if line4.state == 'done':
                            ws.write(baris, 0, (line3.date_done or ''))
                            ws.write(baris, 1, (line.name or ''))
                            ws.write(baris, 2, (line3.name or ''))
                            ws.write(baris, 3, (line3.surat_jalan_masuk or ''))
                            ws.write(baris, 4, (line.partner_id and line.partner_id.name or ''))
                            ws.write(baris, 5, (line3.no_kendaraan or ''))
                            ws.write(baris, 6, (("%s\n%s") % ((line4.product_id and line4.product_id.name or ''), (line4.name or ''))))
                            ws.write(baris, 7, (line4.product_uom and line4.product_uom.name or ''))
                            ws.write(baris, 8, (line4.product_qty or ''))
                            baris += 1
                            
report_purchase_po_xls('report.purchase.po.xls', 'purchase.po')

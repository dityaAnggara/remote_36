'''
Created on 31 Mar 2015

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

class report_purchase_spk_xls(report_xls):
    
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
        ws = wb.add_sheet('SPK')
        baris = 0
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        for o in objects:
            i = 1
            ws.write_merge(baris, baris, 0, 9, 'Laporan SPK')
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
            ws.write(baris, 0, 'Tgl.')
            ws.write(baris, 1, 'No.')
            ws.write(baris, 2, 'Supplier')
            ws.write(baris, 3, 'Tlp')
            ws.write(baris, 4, 'Kend')
            ws.write(baris, 5, 'Barang')
            ws.write(baris, 6, 'Qty')
            ws.write(baris, 7, 'Satuan')
            ws.write(baris, 8, 'Harga Satuan')
            ws.write(baris, 9, 'Harga Total')
            baris += 1
            if o.all :
                plines = self.lines(
                    'SPK',
                    self.oe_datetime_format(o.date_start, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    self.oe_datetime_format(o.date_end, '%Y-%m-%d').strftime('%Y-%m-%d'))
            else :
                plines = self.lines(
                    'SPK',
                    self.oe_datetime_format(o.date_start, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    self.oe_datetime_format(o.date_end, '%Y-%m-%d').strftime('%Y-%m-%d'),
                    partner=o.partner_id.id)
            for line in plines:
                for line2 in line.order_line:
                    ws.write(baris, 0, (line.date_order or ''))
                    ws.write(baris, 1, (line.name or ''))
                    ws.write(baris, 2, (line.partner_id.name or ''))
                    ws.write(baris, 3, (line.partner_id.phone or ''))
                    kend = ''
                    for pick in line.picking_ids:
                        kend += ((pick.no_kendaraan or '') + '\n')
                    ws.write(baris, 4, kend)
                    ws.write(baris, 5, (("%s\n%s") % ((line2.product_id and line2.product_id.name or ''), (line2.name or ''))))
                    ws.write(baris, 6, (line2.product_qty or ''))
                    ws.write(baris, 7, (line2.product_uom and line2.product_uom.name or ''))
                    ws.write(baris, 8, (line2.price_unit or ''))
                    ws.write(baris, 9, (line2.price_subtotal or ''))
                    baris += 1
                ws.write_merge(baris, baris, 0, 8, 'Total')
                ws.write(baris, 9, (line.amount_total or ''))
                baris += 1
    
report_purchase_spk_xls('report.purchase.spk.xls', 'purchase.spk')

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

class report_purchase_sj_xls(report_xls):
            
    def fktr_browse(self, ids): 
        return self.pool.get('account.invoice').browse(self.cr, self.uid, ids)
    
    def get_p_type(self, typp):
        return self.pool.get('purchase.order').search(self.cr, self.uid, [('purchase_state', '=', typp)])
    
    def get_p_brows(self, ids):
        return self.pool.get('purchase.order').browse(self.cr, self.uid, ids)
    
    def rel_inv(self):
        self.cr.execute("SELECT order_line_id FROM purchase_order_line_invoice_rel")
        return self.cr.fetchall()
    
    def rel_inv_one(self, ids):
        self.cr.execute("SELECT invoice_id FROM purchase_order_line_invoice_rel WHERE order_line_id IN %s", (tuple(ids),))
        return self.cr.fetchall()
    
    def get_id_iinv(self, ids):
        self.cr.execute("SELECT invoice_id FROM account_invoice_line WHERE id IN %s", (tuple(ids),))
        return self.cr.fetchall()
    
    def invoice_data(self, ids, tanggal_start, tanggal_end):
        self.cr.execute("SELECT id FROM account_invoice WHERE id IN %s AND date_invoice BETWEEN %s AND %s", (tuple(ids), tanggal_start, tanggal_end))
        return self.cr.fetchall()
    
    def invoice_data_one(self, ids, sup_list, tanggal_start, tanggal_end):
        self.cr.execute("SELECT id FROM account_invoice WHERE  id IN %s AND partner_id = %s AND date_invoice BETWEEN %s AND %s", (tuple(ids), sup_list, tanggal_start, tanggal_end))
        return self.cr.fetchall()
    
    def invoice_broww(self, ids):
        return self.pool.get('account.invoice').browse(self.cr, self.uid, ids)
    
    def get_sj_pu(self, ids, tanggal_start, tanggal_end):
        return self.pool.get('stock.picking').search(self.cr, self.uid, [
                                                                         ('purchase_id', 'in', (ids)),
                                                                         ('date_done', '>=', tanggal_start),
                                                                         ('date_done', '<=', tanggal_end),
                                                                         ('type', '=', 'in'), ('state', '=', 'done')
                                                                         ])
        
    def get_sj_line(self, ids):
        return self.pool.get('stock.picking').browse(self.cr, self.uid, ids)
    
    def get_move_line(self, ids):
        return self.pool.get('stock.move').search(self.cr, self.uid, [('picking_id', '=', ids)])
    
    def get_move_brose(self, ids):
        return self.pool.get('stock.move').browse(self.cr, self.uid, ids)
    
    def get_sj_pu_sup(self, ids, tanggal_start, tanggal_end, sup_id):
        return self.pool.get('stock.picking').search(self.cr, self.uid, [
                                                                         ('purchase_id', 'in', (ids)),
                                                                         ('date_done', '>=', tanggal_start),
                                                                         ('date_done', '<=', tanggal_end),
                                                                         ('partner_id', '=', sup_id),
                                                                         ('type', '=', 'in'), ('state', '=', 'done')
                                                                         ])
    
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
    
    def generate_xls_report(self, _p, _xs, data, objects, wb):
        po_lain = []
        comp_po = []
        po_kumpul = []
        inv_kumpul = []
        inv_kumpul_two = []
        inv_kumpul_tiga = []
        po_kumpul_one = []
        po_kumpul_two = []
        
        ws = wb.add_sheet('Rekap Faktur')
        baris = 0
        style = xlwt.XFStyle()
        style.alignment.wrap = 1
        for o in objects:
            if o.jenis_report == 'faktur':
                ws.write_merge(baris, baris, 0, 7, 'Rekap Pembelian Berdasarkan Faktur')
                baris += 1
                ws.write(baris, 0, 'Purchase Type')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, o.purchase_type)
                baris += 1
                ws.write(baris, 0, 'Awal Periode')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, self.chdf(o.date_start, '%Y-%m-%d', '%d %B %Y'))
                baris += 1
                ws.write(baris, 0, 'Akhir Periode')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, self.chdf(o.date_end, '%Y-%m-%d', '%d %B %Y'))
                baris += 2
                ws.write(baris, 0, 'Tgl')
                ws.write(baris, 1, 'No Faktur')
                ws.write(baris, 2, 'No Pembelian')
                ws.write(baris, 3, 'Nama Supplier')
                ws.write(baris, 4, 'NPWP')
                ws.write(baris, 5, 'DPP (Rp)')
                ws.write(baris, 6, 'PPN (Rp)')
                ws.write(baris, 7, 'Jumlah (Rp)')
                baris += 1
                if all:
                    for uin in self.get_p_type(o.purchase_type):
                        bgh = self.get_p_brows(uin)
                        for iin in bgh.order_line:
                            po_kumpul.append(iin.id)
                    for ool in self.rel_inv():
                        po_lain.append(ool[0])
                    for moo in (set(po_kumpul) & set(po_lain)):
                        comp_po.append(moo)
                    for ioic in self.rel_inv_one(comp_po):
                        inv_kumpul.append(ioic[0])
                    for in_two in self.get_id_iinv(inv_kumpul):
                        inv_kumpul_two.append(in_two[0])
                    for in_there in set(inv_kumpul_two):
                        inv_kumpul_tiga.append(in_there)
                    
                    total_untaxed = 0
                    total_tax = 0
                    total = 0
                    for id_ii in self.invoice_data(inv_kumpul_tiga, o.date_start, o.date_end):
                        test_parsing_value = self.invoice_broww(id_ii[0])
                        bgh = False
                        for uin in self.get_p_type(o.purchase_type):
                            bgh = self.get_p_brows(uin)
                        ws.write(baris, 0, self.chdf(test_parsing_value.date_invoice, '%Y-%m-%d', '%d/%m/%Y'))
                        ws.write(baris, 1, test_parsing_value.number or '')
                        ws.write(baris, 2, bgh and bgh.name or '')
                        ws.write(baris, 3, test_parsing_value.partner_id.name)
                        ws.write(baris, 4, test_parsing_value.partner_id.npwp_acl or '')
                        ws.write(baris, 5, (test_parsing_value.amount_untaxed))
                        ws.write(baris, 6, (test_parsing_value.amount_tax))
                        ws.write(baris, 7, (test_parsing_value.amount_total))
                        total_untaxed = total_untaxed + test_parsing_value.amount_untaxed
                        total_tax = total_tax + test_parsing_value.amount_tax
                        total = total + test_parsing_value.amount_total
                        baris += 1
                    ws.write_merge(baris, baris, 0, 4, 'Total')
                    ws.write(baris, 5, total_untaxed)
                    ws.write(baris, 6, total_tax)
                    ws.write(baris, 7, total)
                    baris += 1
                else:
                    for uin in self.get_p_type(o.purchase_type):
                        bgh = self.get_p_brows(uin)
                        for iin in bgh.order_line:
                            po_kumpul.append(iin.id)
                    for ool in self.rel_inv():
                        po_lain.append(ool[0])
                    for moo in (set(po_kumpul) & set(po_lain)):
                        comp_po.append(moo)
                    for ioic in self.rel_inv_one(comp_po):
                        inv_kumpul.append(ioic[0])
                    for in_two in self.get_id_iinv(inv_kumpul):
                        inv_kumpul_two.append(in_two[0])
                    for in_there in set(inv_kumpul_two):
                        inv_kumpul_tiga.append(in_there)
                    
                    total_untaxed = 0
                    total_tax = 0
                    total = 0
                    for id_ii in self.invoice_data_one(inv_kumpul_tiga, o.supplier_list, o.date_start, o.date_end):
                        test_parsing_value = self.invoice_broww(id_ii[0])
                        bgh = False
                        for uin in self.get_p_type(o.purchase_type):
                            bgh = self.get_p_brows(uin)
                        ws.write(baris, 0, self.chdf(test_parsing_value.date_invoice, '%Y-%m-%d', '%d/%m/%Y'))
                        ws.write(baris, 1, test_parsing_value.number or '')
                        ws.write(baris, 2, bgh and bgh.name or '')
                        ws.write(baris, 3, test_parsing_value.partner_id.name)
                        ws.write(baris, 4, test_parsing_value.partner_id.npwp_acl or '')
                        ws.write(baris, 5, (test_parsing_value.amount_untaxed))
                        ws.write(baris, 6, (test_parsing_value.amount_tax))
                        ws.write(baris, 7, (test_parsing_value.amount_total))
                        total_untaxed = total_untaxed + test_parsing_value.amount_untaxed
                        total_tax = total_tax + test_parsing_value.amount_tax
                        total = total + test_parsing_value.amount_total
                        baris += 1
                    ws.write_merge(baris, baris, 0, 4, 'Total')
                    ws.write(baris, 5, total_untaxed)
                    ws.write(baris, 6, total_tax)
                    ws.write(baris, 7, total)
                    baris += 1
            else:
                ws.write_merge(baris, baris, 0, 10, 'Rekap Pembelian Berdasarkan Surat Jalan')
                baris += 1
                ws.write(baris, 0, 'Purchase Type')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, o.purchase_type)
                baris += 1
                ws.write(baris, 0, 'Awal Periode')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, self.chdf(o.date_start, '%Y-%m-%d', '%d %B %Y'))
                baris += 1
                ws.write(baris, 0, 'Akhir Periode')
                ws.write(baris, 1, ':')
                ws.write(baris, 2, self.chdf(o.date_end, '%Y-%m-%d', '%d %B %Y'))
                baris += 2
                ws.write_merge(baris, baris + 1, 0, 0, 'Tgl')
                ws.write_merge(baris, baris + 1, 1, 1, 'No SJ')
                ws.write_merge(baris, baris + 1, 2, 2, 'No PO')
                ws.write_merge(baris, baris + 1, 3, 3, 'Supplier')
                ws.write_merge(baris, baris + 1, 4, 4, 'Berat SJ')
                ws.write_merge(baris, baris, 5, 10, 'Detail Surat Jalan')
                baris += 1
                ws.write(baris, 5, 'Qty SJ')
                ws.write(baris, 6, 'Qty PO')
                ws.write(baris, 7, 'Harga')
                ws.write(baris, 8, 'DPP')
                ws.write(baris, 9, 'PPN')
                ws.write(baris, 10, 'Total')
                baris += 1
                total_dpp = 0
                total_ppn = 0
                total_all = 0
                if all:
                    for uin in self.get_p_type(o.purchase_type):
                        bgh = self.get_p_brows(uin)
                        po_kumpul_two.append(bgh.id)
                        for iin in bgh.order_line:
                            po_kumpul_one.append(iin.id)
                    for sj_one in self.get_sj_pu(po_kumpul_two, o.date_start, o.date_end):
                        line_pu = self.get_sj_line(sj_one)
                        ws.write(baris, 0, (self.chdf(line_pu.date_done, '%Y-%m-%d %H:%M:%S', '%d/%m/%Y')))
                        ws.write(baris, 1, (line_pu.surat_jalan_masuk or ''))
                        ws.write(baris, 2, (line_pu.purchase_id and line_pu.purchase_id.name or ''))
                        ws.write(baris, 3, (line_pu.purchase_id and line_pu.purchase_id.partner_id and line_pu.purchase_id.partner_id.name or ''))
                        ws.write(baris, 4, (("Bruto : %s") % (line_pu.b_bruto or 0)))
                        ws.write(baris + 1, 4, (("Kend : %s") % (line_pu.b_kend or 0)))
                        ws.write(baris + 2, 4, (("Netto : %s") % (line_pu.b_netto or 0)))
                        # baris += 3
                        
                        baris2 = 0
                        for line_move_sj in self.get_move_line(line_pu.id):
                            move_line_brow = self.get_move_brose(line_move_sj)
                            ws.write_merge(baris + baris2, baris + baris2, 5, 10, (move_line_brow.product_id and move_line_brow.product_id.name or ''))
                            baris2 += 1
                            ws.write(baris + baris2, 5, (move_line_brow.product_qty or 0))
                            for po_line_data in line_pu.purchase_id.order_line:
                                if move_line_brow.product_id == po_line_data.product_id:
                                    dpp = (po_line_data.price_unit * move_line_brow.product_qty)
                                    ppn = 0
                                    for taxx_in in po_line_data.taxes_id:
                                        txa = (taxx_in.amount * 100)
                                        ppn = float((po_line_data.price_unit * txa) / 100)
                                    total = (dpp + ppn)
                                    total_dpp = total_dpp + dpp
                                    total_ppn = total_ppn + ppn
                                    total_all = total_all + total
                                    ws.write(baris + baris2, 6, (po_line_data.product_qty or 0))
                                    ws.write(baris + baris2, 7, (po_line_data.price_unit or 0))
                                    ws.write(baris + baris2, 8, (dpp or 0))
                                    ws.write(baris + baris2, 9, (ppn or 0))
                                    ws.write(baris + baris2, 10, (total or 0))
                                    baris2 += 1
                        if baris2 <= 3 :
                            baris += 3
                        else:
                            baris += baris2
    
report_purchase_sj_xls('report.pr_vall.mako.xls', 'purchase.pr_rp_val')

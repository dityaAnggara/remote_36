'''
Created on 17 Nov 2014

@author: innotek
'''

import time
from openerp.osv import osv, fields
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import re
from roman import toRoman

class purchase_requisition(osv.Model):
    _name = 'purchase.requisition'
    _inherit = 'purchase.requisition'
    _columns = {
                'purchase_ids': fields.one2many('purchase.order', 'requisition_id', 'Purchase Orders',
                                                 states={'done': [('readonly', True)]}),
                'line_ids': fields.one2many('purchase.requisition.line', 'requisition_id', 'Products to Purchase',
                                             states={ # 'urgent': [('readonly', True)],
                                                      # 'acc_gm':[('readonly', True)],
                                                      'in_progress':[('readonly', True)],
                                                      'done':[('readonly', True)],
                                                     }),
                'urgent': fields.boolean('Urgent', states={'urgent': [('readonly', True)],
                                                      'acc_gm':[('readonly', True)],
                                                      'in_progress':[('readonly', True)],
                                                      'done':[('readonly', True)]
                                                      }, track_visibility='always'),
                'purchase_state': fields.selection(
                                                   [
                                                    ('LOP', 'Laporan Orientasi Pembelian (LOP)'),
                                                    ('KP', 'Konfirmasi Pembelian (KP)'),
                                                    ('PO', 'Purchase Order (PO)'),
                                                    ('SPK', 'Surat Perintah Kerja (SPK)')
                                                    ], string='Purchase Type', required=True, states={
                                                      'acc_gm':[('readonly', True)],
                                                      'acc_kabag':[('readonly', True)],
                                                      'in_progress':[('readonly', True)],
                                                      'done':[('readonly', True)]
                                                      }),
                'state': fields.selection(
                                          [
                                           ('draft', 'Baru'),
                                           ('acc_kabag', 'Acc Kabag'),
                                           ('acc_gm', 'Acc GM'),
                                           ('in_progress', 'Acc Direksi'),
                                           ('urgent', 'Urgent'),
                                           ('cancel', 'Dibatalkan'),
                                           ('done', 'Requisition Done')
                                           ], 'Status', track_visibility='onchange', required=True),
                'kabag_id': fields.many2one('res.users', 'Kabag'),
                'gm_id': fields.many2one('res.users', 'GM'),
                'direksi_id': fields.many2one('res.users', 'Direksi'),
                'no_nota': fields.char('No. Order Pembelian', required=True),
                'exclusive': fields.selection([('exclusive','Purchase Requisition (exclusive)'),('multiple','Multiple Requisitions')],
                                      'Requisition Type', required=True, readonly=True,
                                      states={'draft':[('readonly',False)]},
                                      help="""Purchase Requisition (exclusive):
                                      On the confirmation of a purchase order, it cancels the remaining purchase order.
                                      Purchase Requisition(Multiple):  It allows to have multiple purchase orders.
                                      On confirmation of a purchase order it does not cancel the remaining orders"""),
                }
    _defaults = {
                 'exclusive': 'exclusive',
                 'purchase_state': 'PO',
                 'no_nota': '-',
                 }
    
    def acc_kabag(self, cr, uid, ids, context=None):
        # is_kabag = self.pool['res.users'].browse(cr, uid, uid, context=context).kabag
        # is_kabag = True
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'Kepala Bagian / Umum')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        step3 = self.read(cr, uid, ids, context=context)[0]['line_ids']
        if len(step3) > 0:
            if uid in step2:
                self.write(cr, uid, ids, {'kabag_id':uid} , context=context)
                return self.write(cr, uid, ids, {'state':'acc_kabag'} , context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('Maaf, anda bukan Kepala Bagian, silakan menghubungi Kepala Bagian anda.'))
                return 0
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, barang masih kosong.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'acc_kabag'} , context=context)
    
    def acc_gm(self, cr, uid, ids, context=None):
        # is_gm = self.pool['res.users'].browse(cr, uid, uid, context=context).gm
        # is_gm = True
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'General Manager')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        if uid in step2:
            if self.read(cr, uid, ids)[0]['urgent']:
                return self.write(cr, uid, ids, {'state':'urgent'} , context=context)
            else:
                self.write(cr, uid, ids, {'gm_id':uid} , context=context)
                return self.write(cr, uid, ids, {'state':'acc_gm'} , context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, anda bukan General Manager, silakan menghubungi General Manager anda.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'acc_gm'} , context=context)
        
    def tender_in_progress(self, cr, uid, ids, context=None):
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'Direksi')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        if uid in step2:
            self.write(cr, uid, ids, {'direksi_id':uid} , context=context)
            return self.write(cr, uid, ids, {'state':'in_progress'} , context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, anda bukan Direktur, silakan menghubungi Direktur anda.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'in_progress'} ,context=context)
        
    def tender_done(self, cr, uid, ids, context=None):
        tender = self.read(cr, uid, ids)[0]
        if tender['line_ids']:
            if tender['purchase_ids']:
                for po in self.pool['purchase.order'].read(cr,uid,tender['purchase_ids']):
                    if po['state'] in ['draft','price_confirm']:
                        self.pool['purchase.order'].write(cr,uid,po['id'],{'state':'cancel'},context=context)
                return self.write(cr, uid, ids, {'state':'done', 'date_end':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
            else:
                raise osv.except_osv(_('Warning!'), _('Maaf, supplier kosong.'))
                return 0
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, produk kosong.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'done', 'date_end':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
    
    def tender_done_inherit(self, cr, uid, ids, context=None):
        tender = self.read(cr, uid, ids)[0]
        if tender['exclusive'] != 'exclusive':
            self.tender_done(self, cr, uid, ids, context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('For Multiple Requisition Only.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'done', 'date_end':time.strftime('%Y-%m-%d %H:%M:%S')}, context=context)
    
    def make_purchase_order(self, cr, uid, ids, partner_id, context=None):
        """
        Create New RFQ for Supplier
        """
        if context is None:
            context = {}
        assert partner_id, 'Supplier should be specified'
        purchase_order = self.pool.get('purchase.order')
        purchase_order_line = self.pool.get('purchase.order.line')
        res_partner = self.pool.get('res.partner')
        fiscal_position = self.pool.get('account.fiscal.position')
        supplier = res_partner.browse(cr, uid, partner_id, context=context)
        supplier_pricelist = supplier.property_product_pricelist_purchase or False
        res = {}
        for requisition in self.browse(cr, uid, ids, context=context):
            if supplier.id in filter(lambda x: x, [rfq.state <> 'cancel' and rfq.partner_id.id or None for rfq in requisition.purchase_ids]):
                raise osv.except_osv(_('Warning!'), _('You have already one %s purchase order for this partner, you must cancel this purchase order to create a new quotation.') % rfq.state)
            location_id = requisition.warehouse_id.lot_input_id.id
            last_ids = purchase_order.search(cr, uid, [('purchase_state', 'ilike', requisition.purchase_state + '%')], order='name')
            # if len(last_ids) > 0:
            #     last_seq = purchase_order.read(cr, uid, last_ids[-1])['name']
            # else:
            #     last_seq = '0'
            # last_seq = last_seq.replace((requisition.purchase_state + '/'), '')
            # last_sqi = int(last_seq[:4])
            # print str(last_seq[:5]) + '\n'
            # last_sqi = int(re.sub('[^0-9]', '', last_seq[:-4]))
            # print str(last_sqi) + '\n'
            # last_sqi = int(re.compile(r'[^\d.]+').sub('', last_seq[:5]))
            
            last_sqi = 0
            for last_id in last_ids:
                last_seq = purchase_order.read(cr, uid, last_id)['name']
                last_seq = last_seq.replace((requisition.purchase_state + '/'), '')
                # print str(last_seq) + '\n'
                try:
                    curr_sqi = int(re.sub('[^0-9]', '', last_seq[:5]))
                except:
                    curr_sqi = 0
                # print str(curr_sqi) + '\n'
                if last_sqi < curr_sqi:
                    last_sqi = curr_sqi
                # print str(last_sqi) + '\n'
            
            last_sqi = last_sqi + 1
            last_seq = str(last_sqi).zfill(5)
            # raise osv.except_osv(_('Warning!'), _('%s') % last_seq)
            
            def payterm(pr_state):
                if pr_state in ['LOP']:
                    return 1
                else:
                    return False
            
            purchase_id = purchase_order.create(cr, uid, {
                        'name': ("%s/%s/%s/%s" % (requisition.purchase_state, last_seq, toRoman(int(time.strftime('%m'))), time.strftime('%Y'))),
                        'origin': requisition.name,
                        'partner_id': supplier.id,
                        'pricelist_id': supplier_pricelist.id,
                        'location_id': location_id,
                        'company_id': requisition.company_id.id,
                        'fiscal_position': supplier.property_account_position and supplier.property_account_position.id or False,
                        'requisition_id':requisition.id,
                        'notes':requisition.description,
                        'warehouse_id':requisition.warehouse_id.id,
                        'purchase_state':requisition.purchase_state,
                        'payment_term_id':payterm(requisition.purchase_state),
                        # 'dept_id':requisition.dept_id.id,
                        'urgent':requisition.urgent,
                        'invoice_method' : 'picking',
                        # 'single_price_unit':single_price_unit,
            })
            res[requisition.id] = purchase_id
            for line in requisition.line_ids:
                product = line.product_id
                seller_price, qty, default_uom_po_id, date_planned = self._seller_details(cr, uid, line, supplier, context=context)
                taxes_ids = product.supplier_taxes_id
                taxes = fiscal_position.map_tax(cr, uid, supplier.property_account_position, taxes_ids)
                purchase_order_line.create(cr, uid, {
                    'order_id': purchase_id,
                    'name': product.partner_ref,
                    'product_qty': qty,
                    'product_id': product.id,
                    'product_uom': default_uom_po_id,
                    'price_unit': seller_price,
                    # 'date_planned': date_planned,
                    'date_planned': line.date_planned or date_planned,
                    'taxes_id': [(6, 0, taxes)],
                    'dept_id' : line.dept_id.id,
                    'keterangan' : line.keterangan,
                }, context=context)
                
        return res
    
purchase_requisition

class purchase_requisition_line(osv.Model):
    _name = "purchase.requisition.line"
    _inherit = "purchase.requisition.line"
    _rec_name = 'product_id'

    _columns = {
                'product_id': fields.many2one('product.product', 'Product', domain="[('purchase_ok','=',True)]"),
                'standard_price': fields.float('Harga Beli Satuan'),
                'date_planned': fields.date('Tgl Permintaan Pengiriman'),
                'keterangan' : fields.text('Keterangan'),
                'dept_id' : fields.many2one('hr.dept.prc', 'Department'),
                'purchase_state' : fields.related('requisition_id','purchase_state',type='selection',string='Purchase Type'),
                # 'dept_id' : fields.related('id', 'note', type='many2one', relation='hr.department', string='Dept'),
    }

    def onchange_product_id(self, cr, uid, ids, product_id, product_uom_id, context=None):
        """ Changes UoM and name if product_id changes.
        @param name: Name of the field
        @param product_id: Changed product_id
        @return:  Dictionary of changed values
        """
        value = {'product_uom_id': ''}
        if product_id:
            prod = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
            value = {
                     'product_uom_id': prod.uom_id.id,
                     'standard_price': prod.standard_price,
                     'product_qty':1.0,
                     }
        return {'value': value}
    
    def price_history(self, cr, uid, ids, context=None):
        # raise osv.except_osv(_('Warning!'), _('TEST %s') % ids)
        ret = {}
        # lines = self.browse(cr, uid, ids)
        for lines in self.browse(cr, uid, ids):
            ret = {  
                'type': 'ir.actions.act_window',
                'name': 'History Harga',
                'view_type': 'form',
                'view_mode': 'tree,form',
                # 'view_id': False,
                'res_model': 'purchase.order.line',
                'target': 'new',
                'context': context,
                'domain' : [('product_id', '=', lines.product_id.id), ('state', 'in', ('confirmed', 'done'))],
                'limit' : 10,
                # 'flags': {'form': {'action_buttons': True}}
                }
        return ret

purchase_requisition_line

class purchase_order(osv.Model):
    _name = 'purchase.order'
    _inherit = 'purchase.order'
    
    STATE_SELECTION = [
                        ('draft', 'Draft PO'),
                        ('price_confirm', 'Price Confirmed'),
                        ('acc_sby', 'Acc Surabaya'),
                        ('sent', 'RFQ Sent'),
                        ('confirmed', 'Supplier OK'),
                        ('acc_kabag', 'Acc Kabag'),
                        ('acc_gm', 'Acc GM'),
                        ('approved', 'Purchase Order'),
                        ('except_picking', 'Shipping Exception'),
                        ('except_invoice', 'Invoice Exception'),
                        ('done', 'Done'),
                        ('cancel', 'Cancelled')
                        ]
    
    _columns = {
                'purchase_state': fields.selection(
                                                   [
                                                    ('LOP', 'Laporan Orientasi Pembelian (LOP)'),
                                                    ('KP', 'Konfirmasi Pembelian (KP)'),
                                                    ('PO', 'Purchase Order (PO)'),
                                                    ('SPK', 'Surat Perintah Kerja (SPK)')
                                                    ], string='Purchase Type', required=True, readonly=True),
                'order_line': fields.one2many('purchase.order.line', 'order_id', 'Order Lines',
                                              states={
                                                      # 'price_confirm':[('readonly', True)],
                                                      'acc_sby':[('readonly', True)],
                                                      'sent':[('readonly', True)],
                                                      'confirmed':[('readonly', True)],
                                                      'acc_gm':[('readonly', True)],
                                                      'acc_kabag':[('readonly', True)],
                                                      'approved':[('readonly', True)],
                                                      'done':[('readonly', True)]
                                                      }),
                'invoice_method': fields.selection([
                                                    ('picking', 'Based on incoming shipments'),
                                                    ('manual', 'Based on Purchase Order lines'),
                                                    ('order', 'Based on generated draft invoice')],
                                                    'Invoicing Control', required=True,
                                                    readonly=True, states={'draft':[('readonly', False)], 'sent':[('readonly', False)]},
                                                    help="Based on Purchase Order lines: place individual lines in 'Invoice Control > Based on P.O. lines' from where you can selectively create an invoice.\n" \
                                                        "Based on generated invoice: create a draft invoice you can validate later.\n" \
                                                        "Bases on incoming shipments: let you create an invoice when receptions are validated."),
                'state': fields.selection(STATE_SELECTION, 'Status', readonly=True,
                                          help="The status of the purchase order or the quotation request. A quotation is a purchase order in a 'Draft' status. Then the order has to be confirmed by the user, the status switch to 'Confirmed'. Then the supplier must confirm the order to change the status to 'Approved'. When the purchase order is paid and received, the status becomes 'Done'. If a cancel action occurs in the invoice or in the reception of goods, the status becomes in exception.",
                                          select=True),
                'urgent' : fields.boolean('Urgent', readonly=True, track_visibility='always'),
                'sby_id': fields.many2one('res.users', 'Direksi Surabaya'),
                'kabag_id': fields.many2one('res.users', 'Kabag'),
                'gm_id': fields.many2one('res.users', 'GM'),
                'direksi_id': fields.many2one('res.users', 'Direksi'),
                'review': fields.boolean('Review Direksi', track_visibility='always'),
                'correct_id': fields.many2one('res.users', 'Pengoreksi'),
                }
    _defaults = {
                 'purchase_state': 'PO',
                 'invoice_method': 'picking',
                 'review': False,
                 }
    
    def price_confirm(self, cr, uid, ids, context=None):
        lanjut = True
        step1 = self.read(cr, uid, ids)[0]['order_line']
        step2 = self.pool['purchase.order.line'].read(cr, uid, step1)
        for line in step2:
            if line['price_unit'] < 1:
                lanjut = False
        if lanjut:
            return self.write(cr, uid, ids, {'state':'price_confirm'} , context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, harga produk masih ada yang kosong.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'price_confirm'} , context=context)
    
    def acc_sby(self, cr, uid, ids, context=None):
        # is_pr_sby = self.pool['res.users'].browse(cr, uid, uid, context=context).pr_sby
        # is_pr_sby = True
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'Purchases / Direksi Surabaya')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        if uid in step2:
            for po in self.browse(cr, uid, ids, context=context):
                if not po.order_line:
                    raise osv.except_osv(_('Error!'), _('Empty purchase order line.'))
                step3 = self.read(cr, uid, ids)[0]['origin']
                step4 = self.search(cr, uid, [('origin', '=', step3)])
                step4.remove(ids[0])
                if po.requisition_id.exclusive != 'multiple':
                    self.write(cr, uid, step4, {'state':'draft'}, context=context)
            # raise osv.except_osv(_('Error!'),_('%s --- %s') % (step4,ids[0]))
            self.write(cr, uid, ids, {'sby_id':uid} , context=context)
            return self.write(cr, uid, ids, {'state':'acc_sby'} , context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, anda bukan Purchasing Surabaya, silakan menghubungi Purchasing Surabaya.'))
            return 0
        
    def acc_kabag(self, cr, uid, ids, context=None):
        # is_kabag = self.pool['res.users'].browse(cr, uid, uid, context=context).kabag
        # is_kabag = True
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'Kepala Bagian / Pembelian')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        if uid in step2:
            self.write(cr, uid, ids, {'kabag_id':uid} , context=context)
            return self.write(cr, uid, ids, {'state':'acc_kabag'} , context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, anda bukan Kepala Bagian Pembelian, silakan menghubungi Kepala Bagian Pembelian.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'acc_kabag'} , context=context)
    
    def acc_gm(self, cr, uid, ids, context=None):
        # is_gm = self.pool['res.users'].browse(cr, uid, uid, context=context).gm
        # is_gm = True
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'General Manager')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        if uid in step2:
            self.write(cr, uid, ids, {'gm_id':uid} , context=context)
            return self.write(cr, uid, ids, {'state':'acc_gm'} , context=context)
        else:
            raise osv.except_osv(_('Warning!'), _('Maaf, anda bukan General Manager, silakan menghubungi General Manager anda.'))
            return 0
        # return self.write(cr, uid, ids, {'state':'acc_gm'} , context=context)
        
    def confirm_order(self, cr, uid, ids, context=None):
        todo = []
        for po in self.browse(cr, uid, ids, context=context):
            if not po.order_line:
                raise osv.except_osv(_('Error!'), _('You cannot confirm a purchase order without any purchase order line.'))
            for line in po.order_line:
                if line.state == 'draft':
                    todo.append(line.id)

        self.pool.get('purchase.order.line').action_confirm(cr, uid, todo, context)
        for id1 in ids:
            # self.write(cr, uid, ids, {'direksi_id':uid} , context=context)
            self.write(cr, uid, [id1], {'state' : 'confirmed', 'validator' : uid})
        return True
    
    def reviewed(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'direksi_id':uid} , context=context)
        self.write(cr, uid, ids, {'review':True} , context=context)
        return True
    
    def mark_urgent(self, cr, uid, ids, context=None):
        self.write(cr, uid, ids, {'gm_id':uid} , context=context)
        self.write(cr, uid, ids, {'direksi_id':uid} , context=context)
        self.write(cr, uid, ids, {'urgent':True} , context=context)
        return True
    
    def wkf_approve_order(self, cr, uid, ids, context=None):
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'General Manager')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        if uid in step2:
            self.write(cr, uid, ids, {'gm_id':uid} , context=context)
        self.write(cr, uid, ids, {'direksi_id':uid} , context=context)
        self.write(cr, uid, ids, {'state': 'approved', 'date_approve': fields.date.context_today(self, cr, uid, context=context)})
        return True
    
    def view_ship(self, cr, uid, ids, context=None):
        ret = {}
        # self.write(cr, uid, ids, {'correct_id':uid} , context=context)
        for lines in self.browse(cr, uid, ids):
            ret = {  
                'type': 'ir.actions.act_window',
                'name': 'Incoming Shipment',
                'view_type': 'form',
                'view_mode': 'tree,form',
                'res_model': 'stock.picking.in',
                'target': 'new',
                'context': context,
                'domain' : [('purchase_id', '=', lines.id)],
                # 'limit' : 10,
                }
        return ret
    
    def validate_except(self,cr,uid,ids,context=None):
        return self.write(cr, uid, ids, {'correct_id':uid} , context=context)
    
purchase_order

class purchase_order_line(osv.osv):
    _name = 'purchase.order.line'
    _inherit = 'purchase.order.line'
    
    _columns = {
                'name': fields.text('Description', required=True, readonly=True),
                'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), required=True),
                'product_uom': fields.many2one('product.uom', 'Product Unit of Measure', required=True, readonly=True),
                'product_id': fields.many2one('product.product', 'Product', domain=[('purchase_ok','=',True)], change_default=True, readonly=True),
                'company_id': fields.related('order_id','company_id',type='many2one',relation='res.company',string='Company', store=True, readonly=True),
                'partner_id': fields.related('order_id','partner_id',string='Partner',readonly=True,type="many2one", relation="res.partner", store=True),
                'date_order': fields.related('order_id','date_order',string='Order Date',readonly=True,type="date"),
                
                'requisition_id': fields.many2one('purchase.requisition', 'Latest Requisition'),
                
                'price_unit': fields.float('Harga Satuan', required=True, track_visibility='always', digits_compute=dp.get_precision('Product Price')),
                'date_planned': fields.date('Tgl Permintaan Pengiriman', required=True, select=True, readonly=True),
                'dept_id' : fields.many2one('hr.dept.prc', 'Department', readonly=True),
                'keterangan' : fields.text('Keterangan'),
                }

purchase_order_line

class product_product(osv.osv):
    _inherit = 'product.product'
    
    def _get_uom_kg(self, cr, uid, *args):
        return self.pool['product.uom'].search(cr, uid, [('name', 'ilike', 'kg')])[0] or 1;

    _columns = {
        'purchase_requisition': fields.boolean('Purchase Requisition', help="Check this box to generates purchase requisition instead of generating requests for quotation from procurement.")
    }
    _defaults = {
        'purchase_requisition': True,
        'type': 'product',
        'uom_id': _get_uom_kg,
        'uom_po_id': _get_uom_kg,
    }

product_product

class procurement_order(osv.Model):
    _inherit = 'procurement.order'
    
    def make_po(self, cr, uid, ids, context=None):
        res = {}
        requisition_obj = self.pool.get('purchase.requisition')
        non_requisition = []
        for procurement in self.browse(cr, uid, ids, context=context):
            if procurement.product_id.purchase_requisition:
                user_company = self.pool['res.users'].browse(cr, uid, uid, context=context).company_id
                req = res[procurement.id] = requisition_obj.create(cr, uid, {
                    'origin': procurement.origin,
                    'date_end': procurement.date_planned,
                    'warehouse_id': self._get_warehouse(procurement, user_company),
                    'company_id': procurement.company_id.id,
                    'line_ids': [(0, 0, {
                        'product_id': procurement.product_id.id,
                        'product_uom_id': procurement.product_uom.id,
                        'product_qty': procurement.product_qty,
                        'standard_price': self.pool['product.product'].browse(cr, uid, procurement.product_id.id, context=context).standard_price,
                    })],
                })
                procurement.write({
                    'state': 'running',
                    'requisition_id': req
                })
            else:
                non_requisition.append(procurement.id)

        if non_requisition:
            res.update(super(procurement_order, self).make_po(cr, uid, non_requisition, context=context))

        return res
    
    def action_po_assign(self, cr, uid, ids, context=None):
        """ This is action which call from workflow to assign purchase order to procurements
        @return: True
        """
        flag = False
        res = super(procurement_order, self).action_po_assign(cr, uid, ids, context=context)
        for proc in self.browse(cr, uid, ids, context):
            if proc.product_id.purchase_requisition:
                flag = True
        return res and not flag and res or 0
        # return res and not flag or 0

procurement_order

class res_users(osv.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    _columns = {
                'sign':fields.binary('Tanda Tangan', filters='*.png,*.jpg', readonly=False)
                }
    
res_users

class stock_picking(osv.Model):
    _inherit = "stock.picking"
    _columns = {
                'surat_jalan_masuk' : fields.char('Surat Jalan Masuk',required=True,states={'done':[('readonly', True)]}),
                }
    _defaults = {
        'surat_jalan_masuk':'-'
    }
    
stock_picking

class stock_picking_in(osv.Model):
    _inherit = "stock.picking.in"
    _columns = {
                'surat_jalan_masuk' : fields.char('Surat Jalan Masuk',required=True,states={'done':[('readonly', True)]}),
                # 'keterangan_return' : fields.text('Keterangan Return', readonly=True),
                'jasa_angkut'       : fields.many2one('res.partner', 'Pengangkutan', states={'done': [('readonly', False)]}, store=True, domain=[('franco', '=', True)]),
                'no_kendaraan'      : fields.char('No Kendaraan'),
                'sopir'             : fields.char('Sopir'),
                'b_kend'            : fields.float('Berat Kendaraan', digits_compute=dp.get_precision('Product Unit of Measure')),
                'b_bruto'           : fields.float('Berat Bruto', digits_compute=dp.get_precision('Product Unit of Measure')),
                'b_netto'           : fields.float('Berat Netto', digits_compute=dp.get_precision('Product Unit of Measure')),
                }
    _defaults = {
        'surat_jalan_masuk':'-'
    }
    
stock_picking_in

"""
class purchase_picking_view(osv.Model):
    _name = 'purchase.picking.view'
    _inherit = "stock.picking.in"
    _table = "stock_picking"
    
purchase_picking_view
"""

class hr_dept_prc(osv.osv):
    _name = "hr.dept.prc"
    _inherit = "hr.department"
    _table = "hr_department"
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            # if record['parent_id']:
            #     name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res
    
    def name_get_(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        if not ids:
            return []
        reads = self.read(cr, uid, ids, ['name','parent_id'], context=context)
        res = []
        for record in reads:
            name = record['name']
            if record['parent_id']:
                name = record['parent_id'][1]+' / '+name
            res.append((record['id'], name))
        return res

    def _dept_name_get_fnc(self, cr, uid, ids, prop, unknow_none, context=None):
        res = self.name_get_(cr, uid, ids, context=context)
        return dict(res)

hr_dept_prc

'''
class purchase_timbang(osv.Model):
    _name = 'purchase.timbang'
    _columns = {
                'partner_id':fields.many2one('res.partner', 'Supplier', required=True, states={'confirmed':[('readonly',True)], 'approved':[('readonly',True)]},track_visibility='always'),
                'picking_id': fields.many2one('stock.picking.in', 'purchase_id', 'Picking List', readonly=True, help="This is the list of incoming shipments that have been generated for this purchase order."),
                }
'''

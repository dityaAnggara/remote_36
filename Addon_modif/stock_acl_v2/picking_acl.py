'''
Created on Nov 30, 2014

@author: innotek
'''
# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import stock
from lxml import etree
from operator import itemgetter
from itertools import groupby
import roman
import calendar
from calendar import monthrange
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
from openerp import netsvc
from openerp import tools
from openerp.tools import float_compare, DEFAULT_SERVER_DATETIME_FORMAT
import openerp.addons.decimal_precision as dp
from array import *
from datetime import datetime
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from openerp.osv.orm import setup_modifiers



class stock_picking(osv.osv):
    _inherit = "stock.picking"
    
    def mark_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context):
            res[pick.id] = {
                                'marketing_total': 0.0,
                            }
            val = 0.0
            for lin in pick.move_line_new:
                val += lin.marketing_request_quantity
            res[pick.id] = val    
        return res
    def del_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context):
            res[pick.id] = {
                                'delivery_total': 0.0,
                            }
            val1 = 0.0
            for lin in pick.move_line_new:
                val1 += lin.warehouse_realise
            res[pick.id] = val1    
        return res
    
    def create(self, cr, user, vals, context=None):
        if ('name' not in vals) or (vals.get('name') == '/'):
            seq_obj_name = self._name
            vals['name'] = self.pool.get('ir.sequence').get(cr, user, seq_obj_name)
        new_id = super(stock_picking, self).create(cr, user, vals, context)
        return new_id
    _columns = {
                    'surat_jalan'       : fields.char('Surat Jalan'),
                    'sequence_picking'  : fields.integer('Sequence'),
                    'origin'            : fields.char('Reference', size=64, select=True),
                    'date'              : fields.datetime('Creation Date', help="Creation date, usually the time of the order.", select=True, readonly=True),
                    'stock_journal_id'  : fields.many2one('stock.journal', 'Stock Journal', select=True),
                    'partner_id'        : fields.many2one('res.partner', 'Partner'),
                    'gen_do'            : fields.char('DO No'),
                    'delivery_date'     : fields.datetime('Delivery Date', store=True, states={'done':[('readonly', True)]}, domain="[('delivery_date', '&lt;', (context_today()-datetime.timedelta(weeks=1)).strftime('%Y-%m-%d'))]"),
                    'marketing_re_date' : fields.datetime('Marketing Request Date', store=True),
                    'jasa_angkut'       : fields.many2one('res.partner', 'Pengangkutan', states={'done': [('readonly', False)]}, store=True, domain=[('franco', '=', True)]),
                    'no_kendaraan'      : fields.char('No Kendaraan'),
                    'sopir'             : fields.char('Sopir'),
                    'jumlah_ikat'       : fields.char('Jumlah per satuan ikat'),
                    'b_kend'            : fields.float('Berat Kendaraan', digits_compute=dp.get_precision('Product Unit of Measure')),
                    'b_bruto'           : fields.float('Berat Bruto', digits_compute=dp.get_precision('Product Unit of Measure')),
                    'b_netto'           : fields.float('Berat Netto', digits_compute=dp.get_precision('Product Unit of Measure')),
                    'move_line_new'     : fields.one2many('stock.move', 'picking_id', 'Internal Moves', domain=[('type', '=', 'out')]),
                    'partial_back'      : fields.integer('Partial Back'),
                    'prepare_button'    : fields.boolean('bool'),
                    'partial_button'    : fields.boolean('bool'),
                    'button_one'        : fields.boolean('bool'),
                    'button_two'        : fields.boolean('bool'),
                    'keterangan_return' : fields.text('Keterangan Return', readonly=True),
                    'sequence_per'      : fields.integer('Sequence'),
                    'marketing_total'   : fields.function(mark_total, string='Marketing Total Request'),
                    'delivery_total'    : fields.function(del_total, string='Delivery Total'),
                }
    _defaults = {
        'marketing_re_date': lambda *a: time.strftime('%Y-%m-%d'),
        'delivery_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def action_process_ret(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.partial.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }
    '''
    def write(self, cr, uid, ids, context=None):
        raise osv.except_osv(_('Warning!'), _(ids))
        return super(stock_picking, self)
    '''
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        dtbs_take = self.browse(cr, uid, ids, context=context)[0]
        count_so_ori = self.pool.get('stock.picking').search(cr , uid, [('origin', '=', dtbs_take.origin), ('state', 'not in', ('done', 'cancel'))], count=True)
        brwe_so_ori = self.pool.get('sale.order').browse(cr, uid, dtbs_take.sale_id.id, context=context)
        
        """
        if count_so_ori > 0:
            raise osv.except_osv(_('test'),_(count_so_ori))
        return True
        """
        tipe = dtbs_take.type
        if tipe == 'in':
            
           # raise osv.except_osv(_('move id'), _(dtbs_take.id))
        
            
            if context is None:
                context = {}
            else:
                context = dict(context)
            res = {}
            move_obj = self.pool.get('stock.move')
            product_obj = self.pool.get('product.product')
            currency_obj = self.pool.get('res.currency')
            uom_obj = self.pool.get('product.uom')
            sequence_obj = self.pool.get('ir.sequence')
            wf_service = netsvc.LocalService("workflow")
            for pick in self.browse(cr, uid, ids, context=context):
                new_picking = None
                complete, too_many, too_few = [], [], []
                move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
                for move in pick.move_lines:
                    if move.state in ('done', 'cancel'):
                        continue
                    partial_data = partial_datas.get('move%s' % (move.id), {})
                    product_qty = partial_data.get('product_qty', 0.0)
                    move_product_qty[move.id] = product_qty
                    product_uom = partial_data.get('product_uom', False)
                    product_price = partial_data.get('product_price', 0.0)
                    product_currency = partial_data.get('product_currency', False)
                    prodlot_id = partial_data.get('prodlot_id')
                    prodlot_ids[move.id] = prodlot_id
                    product_uoms[move.id] = product_uom
                    partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                    if move.product_qty == partial_qty[move.id]:
                        complete.append(move)
                    elif move.product_qty > partial_qty[move.id]:
                        too_few.append(move)
                    else:
                        too_many.append(move)
    
                    # Average price computation
                    if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                        product = product_obj.browse(cr, uid, move.product_id.id)
                        move_currency_id = move.company_id.currency_id.id
                        context['currency_id'] = move_currency_id
                        qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
    
                        if product.id not in product_avail:
                            # keep track of stock on hand including processed lines not yet marked as done
                            product_avail[product.id] = product.qty_available
    
                        if qty > 0:
                            new_price = currency_obj.compute(cr, uid, product_currency,
                                    move_currency_id, product_price, round=False)
                            new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                    product.uom_id.id)
                            if product_avail[product.id] <= 0:
                                product_avail[product.id] = 0
                                new_std_price = new_price
                            else:
                                # Get the standard price
                                amount_unit = product.price_get('standard_price', context=context)[product.id]
                                new_std_price = ((amount_unit * product_avail[product.id])\
                                    + (new_price * qty)) / (product_avail[product.id] + qty)
                            # Write the field according to price type field
                            product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
    
                            # Record the values that were chosen in the wizard, so they can be
                            # used for inventory valuation if real-time valuation is enabled.
                            move_obj.write(cr, uid, [move.id],
                                    {'price_unit': product_price,
                                     'price_currency_id': product_currency})
    
                            product_avail[product.id] += qty
    
    
    
                for move in too_few:
                    product_qty = move_product_qty[move.id]
                    if not new_picking:
                        new_picking_name = pick.name
                        self.write(cr, uid, [pick.id],
                                   {'name': sequence_obj.get(cr, uid,
                                                'stock.picking.%s' % (pick.type)),
                                   })
                        new_picking = self.copy(cr, uid, pick.id,
                                {
                                    'name': new_picking_name,
                                    'move_lines' : [],
                                    'state':'draft',
                                })
                    if product_qty != 0:
                        defaults = {
                                'product_qty' : product_qty,
                                'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                                'picking_id' : new_picking,
                                'state': 'assigned',
                                'move_dest_id': False,
                                'price_unit': move.price_unit,
                                'product_uom': product_uoms[move.id],
                                
                        }
                        prodlot_id = prodlot_ids[move.id]
                        if prodlot_id:
                            defaults.update(prodlot_id=prodlot_id)
                        move_obj.copy(cr, uid, move.id, defaults)
                    move_obj.write(cr, uid, [move.id],
                            {
                                'product_qty': move.product_qty - partial_qty[move.id],
                                'product_uos_qty': move.product_qty - partial_qty[move.id],  # TODO: put correct uos_qty
                                'prodlot_id': False,
                                'tracking_id': False,
                            })
    
                if new_picking:
                    move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
                for move in complete:
                    defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id]}
                    if prodlot_ids.get(move.id):
                        defaults.update({'prodlot_id': prodlot_ids[move.id]})
                    move_obj.write(cr, uid, [move.id], defaults)
                for move in too_many:
                    product_qty = move_product_qty[move.id]
                    defaults = {
                        'product_qty' : product_qty,
                        'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                        'product_uom': product_uoms[move.id]
                    }
                    prodlot_id = prodlot_ids.get(move.id)
                    if prodlot_ids.get(move.id):
                        defaults.update(prodlot_id=prodlot_id)
                    if new_picking:
                        defaults.update(picking_id=new_picking)
                    move_obj.write(cr, uid, [move.id], defaults)
    
                # At first we confirm the new picking (if necessary)
                if new_picking:
                    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                    # Then we finish the good picking
                    self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                    self.action_move(cr, uid, [new_picking], context=context)
                    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                    wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                    delivered_pack_id = pick.id
                    back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                    self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
                else:
                    self.action_move(cr, uid, [pick.id], context=context)
                    wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                    delivered_pack_id = pick.id
    
                delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
                res[pick.id] = {'delivered_picking': delivered_pack.id or False}
    
            return res
            
        else:
            
            if context is None:
                context = {}
            else:
                context = dict(context)
            res = {}
            move_obj = self.pool.get('stock.move')
            product_obj = self.pool.get('product.product')
            currency_obj = self.pool.get('res.currency')
            uom_obj = self.pool.get('product.uom')
            sequence_obj = self.pool.get('ir.sequence')
            wf_service = netsvc.LocalService("workflow")
            for pick in self.browse(cr, uid, ids, context=context):
                new_picking = None
                complete, too_many, too_few = [], [], []
                move_product_qty, prodlot_ids, product_avail, partial_qty, product_uoms = {}, {}, {}, {}, {}
                for move in pick.move_lines:
                    if move.state in ('done', 'cancel'):
                        continue
                    
                    partial_data = partial_datas.get('move%s' % (move.id), {})
                    product_qty = partial_data.get('product_qty', 0.0)
                    
                    move_product_qty[move.id] = product_qty
                    product_uom = partial_data.get('product_uom', False)
                    product_price = partial_data.get('product_price', 0.0)
                    product_currency = partial_data.get('product_currency', False)
                    prodlot_id = partial_data.get('prodlot_id')
                    prodlot_ids[move.id] = prodlot_id
                    product_uoms[move.id] = product_uom
                    partial_qty[move.id] = uom_obj._compute_qty(cr, uid, product_uoms[move.id], product_qty, move.product_uom.id)
                    if move.product_qty == partial_qty[move.id]:
                        complete.append(move)
                    elif move.product_qty > partial_qty[move.id]:
                        too_few.append(move)
                    else:
                        too_many.append(move)
    
                    # Average price computation
                    if (pick.type == 'in') and (move.product_id.cost_method == 'average'):
                        product = product_obj.browse(cr, uid, move.product_id.id)
                        move_currency_id = move.company_id.currency_id.id
                        context['currency_id'] = move_currency_id
                        qty = uom_obj._compute_qty(cr, uid, product_uom, product_qty, product.uom_id.id)
    
                        if product.id not in product_avail:
                            product_avail[product.id] = product.qty_available
    
                        if qty > 0:
                            new_price = currency_obj.compute(cr, uid, product_currency,
                                    move_currency_id, product_price, round=False)
                            new_price = uom_obj._compute_price(cr, uid, product_uom, new_price,
                                    product.uom_id.id)
                            if product_avail[product.id] <= 0:
                                product_avail[product.id] = 0
                                new_std_price = new_price
                            else:
                                amount_unit = product.price_get('standard_price', context=context)[product.id]
                                new_std_price = ((amount_unit * product_avail[product.id])\
                                    + (new_price * qty)) / (product_avail[product.id] + qty)
                            product_obj.write(cr, uid, [product.id], {'standard_price': new_std_price})
    
                            move_obj.write(cr, uid, [move.id],
                                    {'price_unit': product_price,
                                     'price_currency_id': product_currency})
    
                            product_avail[product.id] += qty
    
    
    
                for move in too_few:
                    product_qty = move_product_qty[move.id]
                    if not new_picking:
                        new_picking_name = pick.name
                        self.write(cr, uid, [pick.id],
                                   {'name': sequence_obj.get(cr, uid,
                                                'stock.picking.%s' % (pick.type)),
                                   })
                        new_picking = self.copy(cr, uid, pick.id,
                                {
                                    'name': new_picking_name,
                                    'move_lines' : [],
                                    'state':'draft',
                                })
                    if product_qty != 0:
                        defaults = {
                                'product_qty' : product_qty,
                                'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                                'picking_id' : new_picking,
                                'state': 'assigned',
                                'move_dest_id': False,
                                'price_unit': move.price_unit,
                                'product_uom': product_uoms[move.id],
                                'warehouse_realise' : product_qty,
                        }
                        prodlot_id = prodlot_ids[move.id]
                        if prodlot_id:
                            defaults.update(prodlot_id=prodlot_id)
                        move_obj.copy(cr, uid, move.id, defaults)
                    move_obj.write(cr, uid, [move.id],
                            {
                                'product_qty': move.product_qty - partial_qty[move.id],
                                'product_uos_qty': move.product_qty - partial_qty[move.id],  # TODO: put correct uos_qty
                                # 'product_uos_qty': move.warehouse_realise,
                                'prodlot_id': False,
                                'tracking_id': False,
                            })
    
                if new_picking:
                    move_obj.write(cr, uid, [c.id for c in complete], {'picking_id': new_picking})
                for move in complete:
                    defaults = {'product_uom': product_uoms[move.id], 'product_qty': move_product_qty[move.id], 'warehouse_realise' : move_product_qty[move.id]}
                    if prodlot_ids.get(move.id):
                        defaults.update({'prodlot_id': prodlot_ids[move.id]})
                    move_obj.write(cr, uid, [move.id], defaults)
                for move in too_many:
                    product_qty = move_product_qty[move.id]
                    defaults = {
                        'product_qty' : product_qty,
                        'product_uos_qty': product_qty,  # TODO: put correct uos_qty
                        'product_uom': product_uoms[move.id],
                        'warehouse_realise' : product_qty,
                    }
                    prodlot_id = prodlot_ids.get(move.id)
                    if prodlot_ids.get(move.id):
                        defaults.update(prodlot_id=prodlot_id)
                    if new_picking:
                        defaults.update(picking_id=new_picking)
                    move_obj.write(cr, uid, [move.id], defaults)
    
                if new_picking:
                    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
                    self.write(cr, uid, [pick.id], {'backorder_id': new_picking})
                    self.action_move(cr, uid, [new_picking], context=context)
                    wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_done', cr)
                    wf_service.trg_write(uid, 'stock.picking', pick.id, cr)
                    delivered_pack_id = pick.id
                    back_order_name = self.browse(cr, uid, delivered_pack_id, context=context).name
                    self.message_post(cr, uid, new_picking, body=_("Back order <em>%s</em> has been <b>created</b>.") % (back_order_name), context=context)
                else:
                    self.action_move(cr, uid, [pick.id], context=context)
                    wf_service.trg_validate(uid, 'stock.picking', pick.id, 'button_done', cr)
                    delivered_pack_id = pick.id
    
                delivered_pack = self.browse(cr, uid, delivered_pack_id, context=context)
                res[pick.id] = {'delivered_picking': delivered_pack.id or False}
            dtbs_take = self.browse(cr, uid, ids, context=context)[0]
            cr.execute("SELECT max(id) FROM stock_move WHERE state = 'confirmed' AND picking_id = %s", (dtbs_take.id,))
            roows = cr.fetchone()[0]
            
            cr.execute("SELECT max(wizard_id) FROM stock_partial_picking_line WHERE move_id = %s", (roows,))
            val_one = cr.fetchone()[0]
            cr.execute("SELECT * FROM stock_partial_picking_line WHERE wizard_id = %s", (val_one,))
            getmark_set = cr.fetchall()
           
            count_so_ori = self.pool.get('stock.picking').search(cr , uid, [('origin', '=', dtbs_take.origin), ('state', 'not in', ('done', 'cancel'))], count=True)
            ori_taa = self.pool.get('stock.picking').search(cr, uid, [('origin', '=', dtbs_take.origin), ('state', 'in', ('done', 'cancel'))])
            so_sale_id = dtbs_take.sale_id.id
            if so_sale_id:
                brwe_so_ori = self.pool.get('sale.order').browse(cr, uid, so_sale_id, context=context)
                if brwe_so_ori.order_policy == 'manual':
                    sudda = 'manual'
                else:
                    sudda = 'progress'
            
            cr.execute("UPDATE stock_move SET state = 'done' WHERE picking_id = %s", (dtbs_take.id,))
            cr.execute("UPDATE stock_picking SET state = 'done', button_one = 'False' WHERE id = %s", (dtbs_take.id,))
            apnd_sisa_wh = []
            hit_sisq = 0
            for linn in dtbs_take.move_line_new:
                hit_sisq += linn.sisa_wh 
            if hit_sisq > 0:
                cr.execute("UPDATE sale_order SET state = %s, shipped = %s WHERE id = %s", (sudda, False, so_sale_id))
                xixa_wh = 0
                ori_apend = []
                ori_apend_one = []
                for taa_ori in ori_taa:
                    ori_taa_one = self.pool.get('stock.picking').browse(cr, uid, taa_ori, context)
                    ori_apend.append(ori_taa_one.id)
                ori_taa_two = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', ori_apend)])
                for taa_ori_one in ori_taa_two:
                    taa_ori_two = self.pool.get('stock.move').browse(cr, uid, taa_ori_one, context)
                    xixa_wh += int(taa_ori_two.sisa_wh)
                if xixa_wh != 0:
                    cr.execute("UPDATE sale_order SET state= %s WHERE id = %s", (sudda, dtbs_take.sale_id.id,))
                else:
                    yui_oot = ori_taa = self.pool.get('stock.picking').search(cr, uid, [('origin', '=', dtbs_take.origin), ('state', 'not in', ('done', 'cancel'))])
                    for yui_oot_one in yui_oot:
                        yui_oot_two = self.pool.get('stock.picking').browse(cr, uid, yui_oot_one, context)
                        cr.execute("UPDATE stock_picking SET state='cancel' WHERE id = %s", (yui_oot_two.id,))
                        ori_apend_one.append(yui_oot_two.id)
                    yui_oor = self.pool.get('stock.move').search(cr, uid, [('picking_id', '=', ori_apend_one)])
                    for yui_oor_one in yui_oor:
                        yui_oor_two = self.pool.get('stock.move').browse(cr, uid, yui_oor_one, context)
                        cr.execute("UPDATE stock_move SET state='cancel' WHERE id = %s", (yui_oor_two.id,))        
            '''
            else:
                      cr.execute("UPDATE sale_order SET state = %s, shipped = %s WHERE id = %s",('done', True, so_sale_id))   
            '''
        return True
        
    def action_process_marketing(self, cr, uid, ids, context=None):
        partial = self.browse(cr, uid, ids[0], context=context)
        get_name_stck_pick = partial.id
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'picking_id_mark': get_name_stck_pick,
            
        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock_picking_acl.market_req_quan',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }

stock_picking()
class stock_picking_in(osv.osv):
    _inherit = "stock.picking.in"
    _columns = {
                  'keterangan_return' : fields.text('Keterangan Return', readonly=True),
                }
stock_picking_in()
            
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    
    def mark_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context):
            res[pick.id] = {
                                'marketing_total': 0.0,
                            }
            val = 0.0
            for lin in pick.move_line_new:
                val += lin.marketing_request_quantity
            res[pick.id] = val    
        return res
    def del_total(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context):
            res[pick.id] = {
                                'delivery_total': 0.0,
                            }
            val1 = 0.0
            for lin in pick.move_line_new:
                val1 += lin.warehouse_realise
            res[pick.id] = val1    
        return res
    def quantity_so(self, cr, uid, ids, field_name, arg, context=None):
        res = {}
        for pick in self.browse(cr, uid, ids, context):
            res[pick.id] = {
                                'delivery_total': 0.0,
                            }
            val1 = 0.0
            for lin in pick.move_line_new:
                val1 += lin.warehouse_realise
            res[pick.id] = val1    
        return res
    _columns = {
                    'surat_jalan'       : fields.char('Surat Jalan'),
                    'sequence_picking'  : fields.integer('Sequence'),
                    'origin'            : fields.char('Reference', size=64, select=True),
                    'date'              : fields.datetime('Creation Date', help="Creation date, usually the time of the order.", select=True, readonly=True),
                    'stock_journal_id'  : fields.many2one('stock.journal', 'Stock Journal', select=True),
                    'partner_id'        : fields.many2one('res.partner', 'Partner'),
                    'gen_do'            : fields.char('DO No'),
                    'delivery_date'     : fields.datetime('Delivery Date', store=True, states={'done':[('readonly', True)]}, domain="[('delivery_date', '&lt;', (context_today()-datetime.timedelta(weeks=1)).strftime('%Y-%m-%d'))]"),
                    'marketing_re_date' : fields.datetime('Marketing Request Date', store=True),
                    'jasa_angkut'       : fields.many2one('res.partner', 'Pengangkutan', states={'done': [('readonly', False)]}, store=True, domain=[('franco', '=', True)]),
                    'no_kendaraan'      : fields.char('No Kendaraan'),
                    'sopir'             : fields.char('Sopir'),
                    'jumlah_ikat'       : fields.char('Jumlah per satuan ikat'),
                    'b_kend'            : fields.float('Berat Kendaraan', digits_compute=dp.get_precision('Product Unit of Measure')),
                    'b_bruto'           : fields.float('Berat Bruto', digits_compute=dp.get_precision('Product Unit of Measure')),
                    'b_netto'           : fields.float('Berat Netto', digits_compute=dp.get_precision('Product Unit of Measure')),
                    'move_line_new'     : fields.one2many('stock.move', 'picking_id', 'Internal Moves'),
                    'partial_back'      : fields.integer('Partial Back'),
                    'prepare_button'    : fields.boolean('bool'),
                    'partial_button'    : fields.boolean('bool'),
                    'button_one'        : fields.boolean('bool'),
                    'button_two'        : fields.boolean('bool'),
                    'keterangan_return' : fields.text('Keterangan Return', readonly=True),
                    'so_original'       : fields.function(quantity_so, string='Quantity SO'),
                    'sequence_per'      : fields.integer('Sequence'),
                    'marketing_total'   : fields.function(mark_total, string='Marketing Total Request'),
                    'delivery_total'    : fields.function(del_total, string='Delivery Total'),
                }
    _defaults = {
        'marketing_re_date': lambda *a: time.strftime('%Y-%m-%d'),
        'delivery_date': lambda *a: time.strftime('%Y-%m-%d'),
    }
    
    def action_process_ret(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        """Open the partial picking wizard"""
        context.update({
            'active_model': self._name,
            'active_ids': ids,
            'active_id': len(ids) and ids[0] or False
        })
        return {
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'stock.partial.picking',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': context,
            'nodestroy': True,
        }
        
    def onchange_date_del(self, cr, uid, ids, delivery_date, context=None):
        obj = self.browse(cr, uid, ids[0], context=context)
        if delivery_date < time.strftime('%Y-%m-%d %H:%M:%S'):
            return {'value':{'delivery_date' : time.strftime('%Y-%m-%d %H:%M:%S')}}
        else:
            return {'value':{'delivery_date' : delivery_date}}
    def action_assign_new(self, cr, uid, ids, vals, context=None):
        take_test = self.browse(cr, uid, ids[0], context=context)  
        if take_test.delivery_date == False:
            raise osv.except_osv(_('Warning!'), _('delivery date harus diisi'))
        else:
            sale_order_line_obj = self.pool.get('sale.order.line')
            product_obj = self.pool.get('product.product')
            stck_move_obj = self.pool.get('stock.move')
            stc_pck_obj = self.pool.get('stock.picking')
            browse_pick = self.browse(cr, uid, ids, context=context)[0]
            sl_id = browse_pick.sale_id.id
            pcck_id = browse_pick.id 
            
            sale_order_line_obj_srch = sale_order_line_obj.search(cr, uid, [('order_id', '=', sl_id)])
            apnd_ord_line_id = []
            prd_id_appen = []
            onhnd_apnd = []
            mj_on = 0
            msn = ""
            for ord_ln_id in sale_order_line_obj_srch:
                stck_move_obj_srch = stck_move_obj.search(cr , uid, [('picking_id', '=', pcck_id)])
                
                apnd_ord_line_id.append(ord_ln_id)
                sale_order_line_obj_bws = sale_order_line_obj.browse(cr, uid, ord_ln_id, context=context)
                prd_id_appen.append(sale_order_line_obj_bws.product_id.id)
                product_obj_brwse = product_obj.browse(cr, uid, sale_order_line_obj_bws.product_id.id, context=context) 
                onhnd_apnd.append(product_obj_brwse.qty_available) 
                # for stc_id in stck_move_obj_srch:
                      
                
                if product_obj_brwse.qty_available <= 0:
                    msn = "one or more your product has zero or last than zero value in onhand quantity"
            if msn != "":
                raise osv.except_osv(_('Warning!'), _(msn))
            else:
                self.write(cr, uid , pcck_id, {'state' : 'assigned', 'button_two' : True}, context=context)
                stck_move_obj_srch_two = stck_move_obj.search(cr, uid, [('picking_id', '=', pcck_id)])
                for idmov_stck in stck_move_obj_srch_two:
                    stck_move_obj.write(cr, uid , idmov_stck, {'state' : 'assigned'}, context=context)
            
        
        return True
    def action_prepare(self, cr, uid, ids, vals, context=None):
   #    
        take_test = self.browse(cr, uid, ids[0], context=context)  
        if take_test.marketing_re_date == False:
            raise osv.except_osv(_('Warning!'), _('please set marketing request date'))
        else:
            
            result = super(stock_picking_out, self).write(cr, uid, ids, vals, context=context)
            mov_ln_ob = self.pool.get('stock.move')
            mov_ln_ob_serch = mov_ln_ob.search(cr, uid, [('take_over', '=', False), ('picking_id', '=', ids)], count=True)
            pck_part = self.pool.get('stock.picking')
            picking_move_line_obj = self.pool.get('stock.move')
            picking_move_line_obj_dua = self.pool.get('stock.move')
            picking_move_line_obj_tiga = self.pool.get('stock.move')
            picking_move_line_obj_empat = self.pool.get('stock.move')
            cr.execute("SELECT MAX(sequence_picking) FROM stock_picking WHERE origin = %s", (take_test.origin,))
            max_sq_pick = cr.fetchone()[0]
            if max_sq_pick != None:
                int_pulss = int(max_sq_pick) + 1
                cr.execute("UPDATE stock_picking SET sequence_picking = %s WHERE id = %s", (int_pulss, take_test.id)) 
            else:
                cr.execute("UPDATE stock_picking SET sequence_picking = %s WHERE id = %s", (1, take_test.id))
                
            val = 0
            # vax = 0
            if mov_ln_ob_serch != 0:
                raise osv.except_osv(_('Warning!'), _('Check position state in your line product maybe is empty'))
            else:
                
                for statement in self.browse(cr, uid, ids, context):
                    for line in statement.move_line_new:
                        qs = line.sisa_mark - line.marketing_request_quantity
                        picking_move_line_obj.write(cr, uid, [line.id], {'sisa_mark': qs}, context=context)
                        # val += qs
                        picking_move_line_obj_tiga.write(cr, uid, [line.id], {'prepare_delivery': 'Marketing'}, context=context)
                        
                
                dtbs_take = self.browse(cr, uid, ids, context=context)[0]
                wstart = 1
                mntl = time.strftime("%m")
                yer = time.strftime("%y")
                imntl = int(mntl)
                fmntl = "%01d" % (imntl)
                ifmntl = int(fmntl)
                tr = roman.toRoman(ifmntl)
                yerone = time.strftime("%Y")
                iyerone = int(yerone)
                ghg = monthrange(iyerone, ifmntl)[1]
                mntldif = time.strftime("%Y-01-01")
                mntldifone = time.strftime("%Y-12-" + str(ghg))
                cr.execute("SELECT count(gen_do) FROM stock_picking WHERE create_date BETWEEN  %s AND %s", (mntldif, mntldifone))
                htung = cr.fetchone()[0]
                if htung != 0:
                    cr.execute("SELECT MAX(id) FROM stock_picking WHERE gen_do != '' AND create_date BETWEEN  %s AND %s", (mntldif, mntldifone))
                    gt_maxidpo = cr.fetchone()[0]
                    cr.execute("SELECT gen_do FROM stock_picking WHERE id = %s", (gt_maxidpo,))
                    getpo = cr.fetchone()[0]
                    split_getpo = getpo.split("/")
                    wstart = split_getpo[0]
                    wstart = int(wstart) + 1
                        # semu_vab = True    
                trplus = str(wstart) + "/" + tr + "/" + yer
                cr.execute("UPDATE stock_picking SET gen_do = %s WHERE id = %s", (trplus, dtbs_take.id))
                self.write(cr, uid, ids, {'prepare_button' : True, 'partial_button' : True}, context=context)
        
    def action_prepare_new(self, cr, uid, ids, vals, context=None):
   #      
        result = super(stock_picking_out, self).write(cr, uid, ids, vals, context=context)
        pck_part = self.pool.get('stock.picking')
        pckb_id = self.browse(cr, uid, ids[0], context=context)
        mov_ln_ob = self.pool.get('stock.move')
        mov_ln_ob_serch = mov_ln_ob.search(cr, uid, [('take_over', '=', 'Take Over'), ('picking_id', '=', ids)], count=True)
        mov_ln_ob_serch_luluh = mov_ln_ob.search(cr, uid, [('take_over', '=', False), ('picking_id', '=', ids)], count=True)
        marketing = "Marketing" 
        picking_move_line_obj = self.pool.get('stock.move')
        picking_move_line_obj_dua = self.pool.get('stock.move')
        picking_move_line_obj_tiga = self.pool.get('stock.move')
        picking_move_line_obj_empat = self.pool.get('stock.move')
        if mov_ln_ob_serch != 0:
            raise osv.except_osv(_('Warning!'), _('Check position state in your line product maybe one of them not in position Take Over Warehouse'))
        elif mov_ln_ob_serch_luluh != 0:
            raise osv.except_osv(_('Warning!'), _('Check position state in your line product maybe one of them not in position Take Over Warehouse'))
        else:
            for statement in self.browse(cr, uid, ids, context):
                for line in statement.move_line_new:
                    qs = line.sisa_wh - line.warehouse_realise
                    picking_move_line_obj.write(cr, uid, [line.id], {'sisa_wh': qs}, context=context)
                    picking_move_line_obj_tiga.write(cr, uid, [line.id], {'prepare_delivery': 'Prepare Delivery Warehouse'}, context=context)
                    prd_id = line.product_id.id
                    orgn_di = line.origin
                    cr.execute("UPDATE stock_move SET sisa_wh = %s, sisa_mark = %s WHERE product_id = %s AND origin = %s", (qs, qs, prd_id, orgn_di))
                    cr.execute("UPDATE stock_move SET sisa_wh = %s, product_qty = %s WHERE product_id = %s AND origin = %s AND prepare_delivery = %s", (qs, qs, prd_id, orgn_di, 'Marketing'))                  
            self.write(cr, uid, ids, {'button_one' : True, 'button_two' : False}, context=context)
        # return result
    def action_partial_do(self, cr, uid, ids, vals, context=None):
        
        partial = self.browse(cr, uid, ids[0], context=context)
        get_name_stck_pick = partial.id
        mov_ob_obj = self.pool.get("stock.move")
        get_nam_stock_bak = partial.id or ''
        # mov_srch_count = mov_ob_obj.mov_srch_count(cr, uid, [('picking_id')], count=True)
        
        
        cr.execute("SELECT SUM(sisa_mark) FROM stock_move WHERE picking_id = %s", (get_name_stck_pick,))
        qspl = cr.fetchone()[0]
        
        if qspl <= 0:
           raise osv.except_osv(_('Warning!'), _('Sisa Quantity Habis')) 
        elif partial.marketing_re_date == False:
            raise osv.except_osv(_('Warning!'), _('marketing request date harus diisi'))
        else:
            brw_pkk_qwe = self.browse(cr, uid, get_name_stck_pick, context=context)
            get_orgn = brw_pkk_qwe.origin
            get_partnerr = brw_pkk_qwe.partner_id.id
            get_cmpn = brw_pkk_qwe.company_id.id
            get_sll = brw_pkk_qwe.sale_id.id
            get_origina_so = brw_pkk_qwe.sale_id.order_policy
            invoic_stt = ""
            if get_origina_so == 'picking':
                invoic_stt = "2binvoiced"
            else:
                invoic_stt = "none"
            
            tg_dte = time.strftime("%Y-%m-%d %H:%M:%S")
            daate = datetime.strptime(tg_dte, "%Y-%m-%d %H:%M:%S")
            ndate = daate + timedelta(days=10)
            pick_cons = self.pool.get('ir.sequence').search(cr, uid, [('name', '=', 'Picking OUT')])
            lokkk = ""
            for constraint_bp_satu in pick_cons:
                pick_bwr = self.pool.get('ir.sequence').browse(cr, uid, constraint_bp_satu, context)
                klmn = str(pick_bwr.number_next_actual)
                lokkk += klmn
            '''
            cr.execute("SELECT MAX(name) FROM stock_picking WHERE type = 'out'")
            get_name_pick_out = cr.fetchone()[0]
            split_nm_pick_out = get_name_pick_out.split("/")
            '''
                
            sum_nm_pick_out = int(lokkk) - 1
            sum_nm_pick_out_two = int(lokkk) + 2
            fmt_sum_nm_pick_out = "%05d" % (sum_nm_pick_out)
            join_nm_pick_out = "OUT/" + fmt_sum_nm_pick_out
            cr.execute("SELECT id FROM stock_journal WHERE name='Delivery Orders'")
            jrn = cr.fetchone()[0]
            
            for constraint_bp in pick_cons:
                self.pool.get('ir.sequence').write(cr, uid, constraint_bp, {'number_next_actual' : sum_nm_pick_out_two}, context=context)
                
            cr.execute('INSERT INTO stock_picking(create_uid,'\
                        'create_date, write_date, write_uid, origin,'\
                        'min_date, date, partner_id, stock_journal_id, backorder_id, name,'\
                        'move_type, company_id, invoice_state,'\
                        'state, max_date, auto_picking, type, sale_id, partial_back)'\
                        'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'\
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s)' , (uid, tg_dte, tg_dte, uid, get_orgn,
                                                        ndate, tg_dte, get_partnerr, jrn, get_nam_stock_bak,
                                                        join_nm_pick_out, 'direct',
                                                        get_cmpn, invoic_stt, 'confirmed', ndate, 'FALSE', 'out', get_sll, get_name_stck_pick))
            cr.execute("SELECT MAX(id) FROM stock_picking WHERE origin = %s AND state = %s", (get_orgn, 'confirmed'))
            get_new_pck_id = cr.fetchone()[0]
            # qw = 0
            mov_ob_obj_srch_mov = mov_ob_obj.search(cr, uid, [('sisa_mark', '!=', 0), ('picking_id', '=', get_name_stck_pick)])
            # cr.execute("SELECT * FROM stock_move WHERE quantity_semu != 0 AND picking_id = %s",(get_name_stck_pick,))
            # rwws = cr.fetchall()
            
            for idmvb in mov_ob_obj_srch_mov:
                rww = mov_ob_obj.browse(cr, uid, idmvb, context=context)
            
                try:
                    cr.execute("SELECT SUM(marketing_request_quantity) FROM stock_move WHERE origin = %s AND product_id = %s", (rww.origin, rww.product_id.id))
                    qw = cr.fetchone()[0]
                    cr.execute('INSERT INTO stock_move(create_uid,'\
                               'create_date, write_date, write_uid, origin,'\
                               'date_expected, product_uom,'\
                               'price_unit, date, product_qty, product_uos,'\
                               'partner_id, name, product_id, auto_validate, location_id,'\
                               'company_id, picking_id, priority, state,'\
                               'location_dest_id, sale_line_id, weight_uom_id, sisa_wh, sisa_mark)'\
                               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'\
                               '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)', (uid, tg_dte, tg_dte, uid, rww.origin, rww.date_expected, rww.product_uom.id,
                                                                              rww.price_unit, rww.date, rww.sisa_mark, rww.product_uos.id, rww.partner_id.id, rww.name, rww.product_id.id,
                                                                              'FALSE', 12, rww.company_id.id, get_new_pck_id, 1, 'confirmed', 9, rww.sale_line_id.id, rww.weight_uom_id.id, rww.sisa_wh, rww.sisa_mark))
                except:
                    cr.execute("SELECT SUM(marketing_request_quantity) FROM stock_move WHERE origin = %s AND product_id = %s", (rww.origin, rww.product_id.id))
                    qw = cr.fetchone()[0]
                    cr.execute('INSERT INTO stock_move(create_uid,'\
                               'create_date, write_date, write_uid, origin,'\
                               'date_expected, product_uom,'\
                               'price_unit, date, product_qty, product_uos,'\
                               'partner_id, name, product_id, auto_validate, location_id,'\
                               'company_id, picking_id, priority, state,'\
                               'location_dest_id, sale_line_id, sisa_wh, marketing_request_quantity, sisa_mark)'\
                               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'\
                               '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)', (uid, tg_dte, tg_dte, uid, rww.origin, rww.date_expected, rww.product_uom.id,
                                                                              rww.price_unit, rww.date, rww.sisa_mark, rww.product_uos.id, rww.partner_id.id, rww.name, rww.product_id.id,
                                                                              'FALSE', 12, rww.company_id.id, get_new_pck_id, 1, 'confirmed', 9, rww.sale_line_id.id, rww.sisa_wh, 1, rww.sisa_mark))
            
            view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'stock', 'view_picking_form')
            self.write(cr, uid, ids, {'partial_button' : False}, context=context)
            view_id = view_ref and view_ref[1] or False,
            return {
                'type': 'ir.actions.act_window',
                'name': _('Stock Picking'),
                'res_model': 'stock.picking.out',
                'res_id': get_new_pck_id,
                'view_type': 'form',
                'view_mode': 'form',
                'view_id': view_id,
                'target': 'current',
                
            } 
    
stock_picking_out()

class stock_move(osv.osv):
    _inherit = "stock.move"
    _columns = {
                   'marketing_request_quantity'     : fields.float('Marketing Request Quantity', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done':[('readonly', True)]}),
                   'warehouse_realise'              : fields.float('Warehouse Quantity Apply', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done':[('readonly', True)]}),
                   'sisa_mark'                      : fields.float('sisa quantity', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done':[('readonly', True)]}),
                   'sisa_wh'                        : fields.float('sisa quantity', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done':[('readonly', True)]}),
                   'total_permintaan'               : fields.float('value asli per product per so', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done':[('readonly', True)]}),
                   'product_qty'                    : fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
                                                                   required=True, readonly=False, states={'done':[('readonly', True)]},
                                                                   help="This is the quantity of products from an inventory "
                                                                   "point of view. For moves in the state 'done', this is the "
                                                                   "quantity of products that were actually moved. For other "
                                                                   "moves, this is the quantity of product that is planned to "
                                                                   "be moved. Lowering this quantity does not generate a "
                                                                   "backorder. Changing this quantity on assigned moves affects "
                                                                   "the product reservation, and should be done with care."
                                                                   ),
                   'product_uos_qty'                : fields.float('Quantity (UOS)', digits_compute=dp.get_precision('Product Unit of Measure')),
                   'prepare_delivery'               : fields.char('Prepare', states={'done':[('readonly', True)]}),
                   'take_over'                      : fields.char('Position', states={'done':[('readonly', True)]}),
                   'ikat_jumlah'                    : fields.char('Jumlah Ikat', states={'done':[('readonly', True)]}),
                   
                }
    _default = {
                 'marketing_request_quantity'     : 1,
                 'warehouse_realise'             : 1,
                 
               }
    def sis_change(self, cr, uid, ids, sisa_mark, marketing_request_quantity, context=None):
        # bwq_self = self.browse(cr, uid, ids[0], context)
        # if bwq_self.marketing_request_quantity == marketing_request_quantity and sisa_mark != bwq_self.sisa_mark:
        #    return {'value':{'sisa_mark' : bwq_self.sisa_mark,'marketing_request_quantity' : bwq_self.marketing_request_quantity},'warning':{'title':'Warning', 'message':'anda tidak diperkenankan merubah kolom ini'}}
        return True
    def sis_change_satu(self, cr, uid, ids, sisa_wh, warehouse_realise, context=None):
        # bqw_self = self.browse(cr, uid, ids[0], context)
        return True
    def us_prod(self, cr, uid, ids, context=None):
        
        yupp = {}
        for prd_line in self.browse(cr, uid, ids, context):
            # self.write(cr, uid, ids, {'sisa_mark' : prd_line.product_qty, 'product_qty' : 0, 'marketing_request_quantity' : 0 , 'take_over': 'Take Over'}, context) 
            if prd_line.product_qty:
                self.write(cr, uid, ids, {'sisa_mark' : prd_line.product_qty, 'product_qty' : 0, 'marketing_request_quantity' : 0 , 'take_over': 'Take Over'}, context) 
            else:
                print ":)"
                   
        # return  {'value':yupp}
    def us_prod_lj(self, cr, uid, ids, context=None):
        
        yupp = {}
        for prd_line in self.browse(cr, uid, ids, context):
             
            if prd_line.product_qty:
                self.write(cr, uid, ids, {'sisa_wh' : prd_line.product_qty, 'product_qty' : 0, 'warehouse_realisasi' : 0 , 'take_over': 'Take Over Warehouse'}, context) 
            else:
                print ":)"
            # raise osv.except_osv(_('move id'), _(prd_line.id))   
        # return  {'value':yupp}    
    def undo_prod(self, cr, uid, ids, context=None):
        
        yupp_one = []
        yupp_two = []
        yupp_four = []
        yupp_there = 0
        yupp_five = []
        yupp_six = []
        for prd_line_undo in self.browse(cr, uid, ids, context):
            yupp_one = prd_line_undo.origin
            yupp_two = prd_line_undo.product_id.id
            yupp_four = prd_line_undo.id
        ob_stc_mv = self.pool.get('stock.move').search(cr, uid, [('origin', '=', yupp_one), ('product_id', '=', yupp_two), ('id', '!=', yupp_four)])
        for okl in ob_stc_mv:
            brq = self.pool.get('stock.move').browse(cr, uid, okl, context)
            yupp_there += brq.product_qty
        ob_sal_ord = self.pool.get('sale.order').search(cr, uid, [('name', '=', yupp_one)])
        for otw in ob_sal_ord:
            brg = self.pool.get('sale.order').browse(cr, uid, otw, context)
            yupp_five = brg.id
        ob_sal_ord_line = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', yupp_five), ('product_id', '=', yupp_two)])
        for kuch in ob_sal_ord_line:
            brh = self.pool.get('sale.order.line').browse(cr, uid, kuch, context)
            yupp_six = brh.product_uos_qty
        kurang_in = yupp_six - yupp_there
        # raise osv.except_osv(_(yupp_there),_(yupp_six))                
        self.write(cr, uid, ids, {'sisa_mark' : yupp_there, 'product_qty' : yupp_there, 'marketing_request_quantity' : 0 , 'take_over': ''}, context)  
    def onmov(self, cr, uid, ids, marketing_request_quantity, product_qty, sisa_wh, sisa_mark, context):
        get_wtf_id = product_qty
        ssw_wh = sisa_wh
        pick_ob_obj = self.pool.get("stock.picking")
        sale_lin_obj = self.pool.get("sale.order.line")
        get_mvee_id = self.browse(cr, uid, ids[0], context=context)
        get_orgn = get_mvee_id.origin
        coutn_delv_pick = pick_ob_obj.search(cr , uid, [('origin', '=', get_orgn), ('state', '=', 'done')], count=True)
        brw_mov_line = self.browse(cr, uid, ids[0], context=context)
        brw_line_sale = sale_lin_obj.browse(cr, uid, brw_mov_line.sale_line_id.id, context=context)
        total_plus_tol = int(brw_line_sale.product_uom_qty) + int(brw_line_sale.toleransi_skp)
        if sisa_wh != False or sisa_wh != 0:
            if marketing_request_quantity > sisa_wh:
                    return {'value':{'marketing_request_quantity' : 0}, 'warning':{'title':'check quantity', 'message':'marketing request quantity more than quantity be permitted'}}
            if marketing_request_quantity == 0:
                return {'value':{'sisa_mark' : product_qty, 'marketing_request_quantity' : 0 , 'product_qty' : 0, 'total_permintaan' : total_plus_tol, 'take_over' : 'Take Over'}}
            else:
                return {'value':{'sisa_mark' : product_qty, 'product_qty' : marketing_request_quantity, 'total_permintaan' : total_plus_tol, 'take_over' : 'Take Over'}}
        else:
            if marketing_request_quantity > get_wtf_id:
                    return {'value':{'marketing_request_quantity' : 0}, 'warning':{'title':'check quantity', 'message':'marketing request quantity more than quantity be permitted'}}
            if marketing_request_quantity == 0:
                return {'value':{'sisa_mark' : product_qty, 'marketing_request_quantity' : 0 , 'product_qty' : 0, 'total_permintaan' : total_plus_tol, 'take_over' : 'Take Over'}}
            else:
                return {'value':{'sisa_mark' : product_qty, 'product_qty' : marketing_request_quantity, 'total_permintaan' : total_plus_tol, 'take_over' : 'Take Over'}}
    def onmov_w(self, cr, uid, ids, warehouse_realise, product_qty, sisa_wh, sisa_mark, context):
        get_wtf_id = product_qty
        
        pick_ob_obj = self.pool.get("stock.picking")
        prd_ob_obj = self.pool.get('product.product')
        get_mvee_id = self.browse(cr, uid, ids[0], context=context)
        get_orgn = get_mvee_id.origin
        ttal_permin = get_mvee_id.total_permintaan
        str_ttal_permin = str(ttal_permin)
        prd_id_mov = get_mvee_id.product_id.id
        coutn_delv_pick = pick_ob_obj.search(cr , uid, [('origin', '=', get_orgn), ('state', '=', 'done')], count=True)
        prd_ob_obj_brw = prd_ob_obj.browse(cr, uid, prd_id_mov, context=context)
        onh_prd = prd_ob_obj_brw.qty_available
        str_onh = str(onh_prd)
        name_prdd = prd_ob_obj_brw.name_template
        
        if coutn_delv_pick == 0:
            if warehouse_realise > onh_prd:
                # mgs = "product "+name_prdd+" only have quantity onhand "+str_onh
                return {'value':{'warehouse_realise' : 0}, 'warning':{'title':'check quantity', 'message':'product tidak sesuai quantity onhand'}}
            if warehouse_realise > ttal_permin:
                # mgs = "product "+name_prdd+" only have request quantity "+str_ttal_permin
                return {'value':{'warehouse_realise' : 0}, 'warning':{'title':'check quantity', 'message':ttal_permin}}
            if warehouse_realise == 0:
                    return {'value':{'warehouse_realise' : 0 , 'product_qty' : 0, 'take_over' : 'Take Over Warehouse'}}
            else:
                return {'value':{'sisa_wh' : ttal_permin, 'product_qty' : warehouse_realise, 'product_uos_qty' : warehouse_realise, 'take_over' : 'Take Over Warehouse'}}     
        else: 
            if warehouse_realise > onh_prd:
                # mgs = "product "+name_prdd+" only have quantity onhand "+str_onh
                return {'value':{'warehouse_realise' : 0}, 'warning':{'title':'check quantity', 'message':'product tidak sesuai quantity onhand'}}
            if warehouse_realise > ttal_permin:
                # mgs = "product "+name_prdd+" only have request quantity "+str_ttal_permin
                return {'value':{'warehouse_realise' : 0}, 'warning':{'title':'check quantity', 'message':ttal_permin}}
            if warehouse_realise == 0:
                    return {'value':{'warehouse_realise' : 0 , 'product_qty' : 0, 'take_over' : 'Take Over Warehouse'}}
            else:
                return {'value':{'product_qty' : warehouse_realise, 'product_uos_qty' : warehouse_realise, 'take_over' : 'Take Over Warehouse'}}
        
stock_move()
class out_acl(osv.osv):
    _name = "stock_acl_v2.out_acl"
    _inherit = "stock.picking"
    _table = "stock_picking"
    _description = "Delivery Orders"
    def default_get(self, cr, uid, fields_list, context=None):
        # merge defaults from stock.picking with possible defaults defined on stock.picking.out
        raise osv.except_osv(_('Info'), _('Access Denied: anda tidak diperkenankan melakukkan ini'))
    
    _defaults = {
        'type': 'out',
    }

class stock_return_picking(osv.osv_memory):
    _inherit = "stock.return.picking"
    _columns = {
                    'return_reasons' : fields.text('Return Reason'),
                    
                }
    
    def create_returns(self, cr, uid, ids, context=None):
        """ 
         Creates return picking.
         @param self: The object pointer.
         @param cr: A database cursor
         @param uid: ID of the user currently logged in
         @param ids: List of ids selected
         @param context: A standard dictionary
         @return: A dictionary which of fields with values.
        """
        
        if context is None:
            context = {} 
        record_id = context and context.get('active_id', False) or False
        move_obj = self.pool.get('stock.move')
        pick_obj = self.pool.get('stock.picking')
        uom_obj = self.pool.get('product.uom')
        data_obj = self.pool.get('stock.return.picking.memory')
        act_obj = self.pool.get('ir.actions.act_window')
        model_obj = self.pool.get('ir.model.data')
        wf_service = netsvc.LocalService("workflow")
        pick = pick_obj.browse(cr, uid, record_id, context=context)
        data = self.read(cr, uid, ids[0], context=context)
        data_onee = self.browse(cr, uid, ids[0], context=context)
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0
        orgni = pick.origin
        ambl_dua = str(orgni)
      
#        Create new picking for returned products
        
        seq_obj_name = 'stock.picking'
        new_type = 'internal'
        if pick.type == 'out':
            new_type = 'in'
            seq_obj_name = 'stock.picking.in'
        elif pick.type == 'in':
            new_type = 'out'
            seq_obj_name = 'stock.picking.out'
        new_pick_name = self.pool.get('ir.sequence').get(cr, uid, seq_obj_name)
        new_picking = pick_obj.copy(cr, uid, pick.id, {
                                        'name': _('%s-%s-return') % (new_pick_name, pick.name),
                                        'move_lines': [],
                                        'state':'draft',
                                        'type': new_type,
                                        'date':date_cur,
                                        'invoice_state': data['invoice_state'],
        })
        
        val_id = data['product_return_moves']
        for v in val_id:
            data_get = data_obj.browse(cr, uid, v, context=context)
            mov_id = data_get.move_id.id
            if not mov_id:
                raise osv.except_osv(_('Warning !'), _("You have manually created product lines, please delete them to proceed"))
            new_qty = data_get.quantity
            move = move_obj.browse(cr, uid, mov_id, context=context)
            new_location = move.location_dest_id.id
            returned_qty = move.product_qty
            for rec in move.move_history_ids2:
                returned_qty -= rec.product_qty

            if returned_qty != new_qty:
                set_invoice_state_to_none = False
            if new_qty:
                returned_lines += 1
                new_move = move_obj.copy(cr, uid, move.id, {
                                            'product_qty': new_qty,
                                            'product_uos_qty': uom_obj._compute_qty(cr, uid, move.product_uom.id, new_qty, move.product_uos.id),
                                            'picking_id': new_picking,
                                            'state': 'draft',
                                            'location_id': new_location,
                                            'location_dest_id': move.location_id.id,
                                            'date': date_cur,
                })
                move_obj.write(cr, uid, [move.id], {'move_history_ids2':[(4, new_move)]}, context=context)
        if not returned_lines:
            raise osv.except_osv(_('Warning!'), _("Please specify at least one non-zero quantity."))

        if set_invoice_state_to_none:
            pick_obj.write(cr, uid, [pick.id], {'invoice_state':'none'}, context=context)
        wf_service.trg_validate(uid, 'stock.picking', new_picking, 'button_confirm', cr)
        pick_obj.force_assign(cr, uid, [new_picking], context)
        
        # Update view id in context, lp:702939
        model_list = {
                'out': 'stock.picking.out',
                'in': 'stock.picking.in',
                'internal': 'stock.picking',
        }
        
        
        rtu = pick_obj.search(cr, uid, [('type', '=', 'in')])
        for urt in rtu:
            yut = pick_obj.browse(cr, uid, urt, context=context) 
            cr.execute("DELETE FROM stock_move WHERE location_dest_id = %s AND picking_id = %s", (9, yut.id))
        
        if ambl_dua[0:2] == "SO":
            lala_rkoo = pick_obj.search(cr, uid, [('type', '=', 'in'), ('origin', '=', pick.origin)])
            rkoo_append = []
            for rkoo in lala_rkoo:
                lala_rkoo_bw = pick_obj.browse(cr, uid, rkoo, context=context) 
                rkoo_append.append(lala_rkoo_bw.id)
            rkoo_maks = max(rkoo_append)
            cr.execute("UPDATE stock_picking SET keterangan_return = %s WHERE id = %s", (data_onee.return_reasons, rkoo_maks))      
        else:
            lala_rkoo_ho = pick_obj.search(cr, uid, [('type', '=', 'out'), ('origin', '=', pick.origin)])
            rkoo_append_ho = []
            for rkoo_ho in lala_rkoo_ho:
                lala_rkoo_bw_ho = pick_obj.browse(cr, uid, rkoo_ho, context=context) 
                rkoo_append_ho.append(lala_rkoo_bw_ho.id)
            rkoo_maks_ho = max(rkoo_append_ho)
            cr.execute("UPDATE stock_picking SET keterangan_return = %s WHERE id = %s", (data_onee.return_reasons, rkoo_maks_ho))
        # uytu = cr.execute("SELECT max(id) FROM stock_picking ") 
        
        return {
            'domain': "[('id', 'in', [" + str(new_picking) + "])]",
            'name': _('Returned Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type':'ir.actions.act_window',
            'context':context,
            
        }
        
        
stock_return_picking()

class invoice_directly(osv.osv_memory):
    _inherit = 'stock.partial.picking'

    def do_partial(self, cr, uid, ids, context=None):
        """Launch Create invoice wizard if invoice state is To be Invoiced,
           after processing the partial picking.
        """
        if context is None: context = {}
        result = super(invoice_directly, self).do_partial(cr, uid, ids, context)
        partial = self.browse(cr, uid, ids[0], context)
        if partial.picking_id.state != 'done' and partial.picking_id.backorder_id:
            # delivery is not finished, opening invoice on backorder
            picking = partial.picking_id.backorder_id
        else:
            picking = partial.picking_id
        context.update(active_model='stock.picking',
                       active_ids=[picking.id])
        '''
        if picking.invoice_state == '2binvoiced':
            return {
                'name': 'Create Invoice',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'stock.invoice.onshipping',
                'type': 'ir.actions.act_window',
                'target': 'new',
                'context': context
            }
        return {'type': 'ir.actions.act_window_close'}
        '''
invoice_directly()
class stock_return_picking_memory(osv.osv_memory):
    _inherit = "stock.return.picking.memory"
class ir_sequence(osv.osv):
    _inherit = "ir.sequence"
class stock_invoice_onshipping(osv.osv_memory):
      _inherit = "stock.invoice.onshipping"
class stock_partial_picking(osv.osv_memory):
    _inherit = "stock.partial.picking"
    
    def do_partial(self, cr, uid, ids, context=None):
        """Launch Create invoice wizard if invoice state is To be Invoiced,
           after processing the partial picking.
        """
        if context is None: context = {}
        result = super(invoice_directly, self).do_partial(cr, uid, ids, context)
        partial = self.browse(cr, uid, ids[0], context)
        if partial.picking_id.state != 'done' and partial.picking_id.backorder_id:
            # delivery is not finished, opening invoice on backorder
            picking = partial.picking_id.backorder_id
        else:
            picking = partial.picking_id
        context.update(active_model='stock.picking',
                       active_ids=[picking.id])
        
        return {'type': 'ir.actions.act_window_close'}


    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        # override of fields_view_get in order to change the label of the process button and the separator accordingly to the shipping type
        print context
        if context is None:
            context = {}
        res = super(stock_partial_picking, self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)
        type = context.get('default_type', False)
        if type:
            doc = etree.XML(res['arch'])
            for node in doc.xpath("//button[@name='do_partial']"):
                if type == 'in':
                    node.set('string', _('_Receive'))
                elif type == 'out':
                    node.set('string', _('_Deliver'))
            for node in doc.xpath("//separator[@name='product_separator']"):
                if type == 'in':
                    node.set('string', _('Receive Products'))
                elif type == 'out':
                    node.set('string', _('Deliver Products'))
            for node in doc.xpath("//field[@name='move_ids']/tree[@name='test_name_pp']"):
                if type == 'in':
                    node.set('edit', 'true')
                elif type == 'out':
                    node.set('editable', 'false')    
                setup_modifiers(node, res['tree']['test_name_pp'])    
            res['arch'] = etree.tostring(doc)
        return res
    

           

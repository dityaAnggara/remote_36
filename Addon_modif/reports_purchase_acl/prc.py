'''
Created on Jan 8, 2015

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

from openerp.report import report_sxw
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
    
    def do_partial(self, cr, uid, ids, partial_datas, context=None):
        
        partial = self.browse(cr, uid, ids[0], context=context)
        get_name_stck_pick = partial.id
        dtbs_take = self.browse(cr, uid, ids, context=context)[0]
        
        get_prc = self.browse(cr, uid, get_name_stck_pick, context=context).purchase_id.id
        if get_prc:
            """ Makes partial picking and moves done.
            @param partial_datas : Dictionary containing details of partial picking
                              like partner_id, partner_id, delivery_date,
                              delivery moves with product_id, product_qty, uom
            @return: Dictionary of values
            """
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
                                'state': 'draft',
                                'move_dest_id': False,
                                'price_unit': move.price_unit,
                                'product_uom': product_uoms[move.id]
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
            return super(stock_picking, self).do_partial(cr, uid, ids, partial_datas, context=context)
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
                brwe_so_ori = self.pool.get('sale.order').browse(cr, uid, dtbs_take.sale_id.id, context=context)
                ori_taa = self.pool.get('stock.picking').search(cr, uid, [('origin', '=', dtbs_take.origin), ('state', 'in', ('done', 'cancel'))])
                so_sale_id = dtbs_take.sale_id.id
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
        """

stock_picking

class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    _columns = {
        'purchase_id': fields.many2one('purchase.order', 'Purchase Order',
            ondelete='set null', select=True),
    }
    
    """
    def action_prepare(self, cr, uid, ids, vals, context=None):
        partial = self.browse(cr, uid, ids[0], context=context)
        get_name_stck_pick = partial.id
        get_prc = self.pool['stock.picking.in'].browse(cr, uid, get_name_stck_pick, context=context).purchase_id.id
        if get_prc:
            return self.action_process(cr, uid, ids, context=context)
        
        take_test = self.browse(cr, uid, ids[0], context=context)  
        if take_test.marketing_re_date == False:
            raise osv.except_osv(_('Warning!'), _('please set marketing request date'))
        else:
            
            result = super(stock_picking_out, self).write(cr, uid, ids, vals, context=context)
            mov_ln_ob = self.pool.get('stock.move')
            mov_ln_ob_serch = mov_ln_ob.search(cr, uid, [('take_over','=',False),('picking_id','=',ids)], count=True)
            pck_part = self.pool.get('stock.picking')
            picking_move_line_obj = self.pool.get('stock.move')
            picking_move_line_obj_dua = self.pool.get('stock.move')
            picking_move_line_obj_tiga = self.pool.get('stock.move')
            picking_move_line_obj_empat = self.pool.get('stock.move')
            cr.execute("SELECT MAX(sequence_picking) FROM stock_picking WHERE origin = %s",(take_test.origin,))
            max_sq_pick = cr.fetchone()[0]
            if max_sq_pick != None:
                int_pulss = int(max_sq_pick) + 1
                cr.execute("UPDATE stock_picking SET sequence_picking = %s WHERE id = %s",(int_pulss,take_test.id)) 
            else:
                cr.execute("UPDATE stock_picking SET sequence_picking = %s WHERE id = %s",(1,take_test.id))
                
            val = 0
            #vax = 0
            if mov_ln_ob_serch != 0:
                raise osv.except_osv(_('Warning!'), _('Check position state in your line product maybe is empty'))
            else:
                
                for statement in self.browse(cr, uid, ids, context):
                    for line in statement.move_line_new:
                        qs = line.sisa_mark - line.marketing_request_quantity
                        picking_move_line_obj.write(cr, uid, [line.id], {'sisa_mark': qs}, context=context)
                        #val += qs
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
                mntldifone = time.strftime("%Y-12-"+str(ghg))
                cr.execute("SELECT count(gen_do) FROM stock_picking WHERE create_date BETWEEN  %s AND %s", (mntldif,mntldifone))
                htung = cr.fetchone()[0]
                if htung != 0:
                    cr.execute("SELECT MAX(id) FROM stock_picking WHERE gen_do != '' AND create_date BETWEEN  %s AND %s", (mntldif,mntldifone))
                    gt_maxidpo = cr.fetchone()[0]
                    cr.execute("SELECT gen_do FROM stock_picking WHERE id = %s", (gt_maxidpo,))
                    getpo = cr.fetchone()[0]
                    split_getpo = getpo.split("/")
                    wstart = split_getpo[0]
                    wstart = int(wstart) + 1
                        #semu_vab = True    
                trplus = str(wstart)+"/"+tr+"/"+yer
                cr.execute("UPDATE stock_picking SET gen_do = %s WHERE id = %s",(trplus, dtbs_take.id))
                self.write(cr, uid, ids, {'prepare_button' : True, 'partial_button' : True}, context=context)
    
    def action_partial_do(self, cr, uid, ids, vals, context=None):
        
        partial = self.browse(cr, uid, ids[0], context=context)
        get_name_stck_pick = partial.id
        mov_ob_obj = self.pool.get("stock.move")
        get_nam_stock_bak = partial.id or ''
        get_prc = self.pool['stock.picking.in'].browse(cr, uid, get_name_stck_pick, context=context).purchase_id.id
        #mov_srch_count = mov_ob_obj.mov_srch_count(cr, uid, [('picking_id')], count=True)
        
        
        cr.execute("SELECT SUM(sisa_mark) FROM stock_move WHERE picking_id = %s",(get_name_stck_pick,))
        qspl = cr.fetchone()[0]
        
        if get_prc:
            return self.action_process(cr, uid, ids, context=context)
        
        if qspl <= 0:
            if not get_prc:
                raise osv.except_osv(_('Warning!'), _('Sisa Quantity Habis')) 
        elif partial.marketing_re_date == False:
            if not get_prc:
                raise osv.except_osv(_('Warning!'), _('marketing request date harus diisi'))
        else:
            brw_pkk_qwe = self.browse(cr, uid, get_name_stck_pick, context=context)
            get_orgn = brw_pkk_qwe.origin
            get_partnerr = brw_pkk_qwe.partner_id.id
            get_cmpn =  brw_pkk_qwe.company_id.id
            get_sll = brw_pkk_qwe.sale_id.id
            # get_prc = self.pool['stock.picking.in'].browse(cr, uid, get_name_stck_pick, context=context).purchase_id.id
            get_origina_so = brw_pkk_qwe.sale_id.order_policy
            invoic_stt = ""
            if get_origina_so == 'picking':
                invoic_stt = "2binvoiced"
            else:
                invoic_stt = "none"
            
            tg_dte = time.strftime("%Y-%m-%d %H:%M:%S")
            daate = datetime.strptime(tg_dte, "%Y-%m-%d %H:%M:%S")
            ndate = daate + timedelta(days=10)
            cr.execute("SELECT MAX(name) FROM stock_picking WHERE type = 'out'")
            get_name_pick_out = cr.fetchone()[0]
            split_nm_pick_out = get_name_pick_out.split("/")
            sum_nm_pick_out = int(split_nm_pick_out[1].split('-')[0]) + 1
            sum_nm_pick_out_two = int(split_nm_pick_out[1].split('-')[0]) + 2
            fmt_sum_nm_pick_out = "%05d" % (sum_nm_pick_out)
            join_nm_pick_out =  split_nm_pick_out[0]+"/"+fmt_sum_nm_pick_out
            cr.execute("SELECT id FROM stock_journal WHERE name='Delivery Orders'")
            jrn = cr.fetchone()[0]
            pick_cons = self.pool.get('ir.sequence').search(cr, uid, [('name','=','Picking OUT')])
            for constraint_bp in pick_cons:
                self.pool.get('ir.sequence').write(cr, uid, constraint_bp, {'number_next_actual' : sum_nm_pick_out_two}, context=context)
            
            if get_sll:
                cr.execute('INSERT INTO stock_picking(create_uid,'\
                        'create_date, write_date, write_uid, origin,'\
                        'min_date, date, partner_id, stock_journal_id, backorder_id, name,'\
                        'move_type, company_id, invoice_state,'\
                        'state, max_date, auto_picking, type, sale_id, partial_back)'\
                        'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'\
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s)' ,(uid, tg_dte, tg_dte, uid, get_orgn, 
                                                        ndate, tg_dte, get_partnerr, jrn, get_nam_stock_bak, 
                                                        join_nm_pick_out, 'direct', 
                                                        get_cmpn, invoic_stt, 'confirmed', ndate, 'FALSE', 'out', get_sll, get_name_stck_pick))
            else:
                cr.execute('INSERT INTO stock_picking(create_uid,'\
                        'create_date, write_date, write_uid, origin,'\
                        'min_date, date, partner_id, stock_journal_id, backorder_id, name,'\
                        'move_type, company_id, invoice_state,'\
                        'state, max_date, auto_picking, type, purchase_id, partial_back)'\
                        'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,'\
                        '%s, %s, %s, %s, %s, %s, %s, %s, %s)' ,(uid, tg_dte, tg_dte, uid, get_orgn, 
                                                        ndate, tg_dte, get_partnerr, jrn, get_nam_stock_bak, 
                                                        join_nm_pick_out, 'direct', 
                                                        get_cmpn, invoic_stt, 'confirmed', ndate, 'FALSE', 'out', get_prc, get_name_stck_pick))
                
            cr.execute("SELECT MAX(id) FROM stock_picking WHERE origin = %s AND state = %s",(get_orgn,'confirmed'))
            get_new_pck_id = cr.fetchone()[0]
            #qw = 0
            mov_ob_obj_srch_mov = mov_ob_obj.search(cr,uid,[('sisa_mark','!=',0),('picking_id','=',get_name_stck_pick)])
            #cr.execute("SELECT * FROM stock_move WHERE quantity_semu != 0 AND picking_id = %s",(get_name_stck_pick,))
            #rwws = cr.fetchall()
            
            for idmvb in mov_ob_obj_srch_mov:
                rww = mov_ob_obj.browse(cr,uid,idmvb,context=context)
                
                if get_sll:
                    try:
                        cr.execute("SELECT SUM(marketing_request_quantity) FROM stock_move WHERE origin = %s AND product_id = %s",(rww.origin, rww.product_id.id))
                        qw = cr.fetchone()[0]
                        cr.execute('INSERT INTO stock_move(create_uid,'\
                               'create_date, write_date, write_uid, origin,'\
                               'date_expected, product_uom,'\
                               'price_unit, date, product_qty, product_uos,'\
                               'partner_id, name, product_id, auto_validate, location_id,'\
                               'company_id, picking_id, priority, state,'\
                               'location_dest_id, sale_line_id, weight_uom_id, sisa_wh, sisa_mark)'\
                               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'\
                               '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)',(uid, tg_dte, tg_dte, uid, rww.origin, rww.date_expected, rww.product_uom.id,
                                                                              rww.price_unit, rww.date, rww.sisa_mark, rww.product_uos.id, rww.partner_id.id, rww.name, rww.product_id.id,
                                                                              'FALSE', 12, rww.company_id.id, get_new_pck_id, 1, 'confirmed', 9, rww.sale_line_id.id, rww.weight_uom_id.id, rww.sisa_wh, rww.sisa_mark))
                    except:
                        cr.execute("SELECT SUM(marketing_request_quantity) FROM stock_move WHERE origin = %s AND product_id = %s",(rww.origin, rww.product_id.id))
                        qw = cr.fetchone()[0]
                        cr.execute('INSERT INTO stock_move(create_uid,'\
                               'create_date, write_date, write_uid, origin,'\
                               'date_expected, product_uom,'\
                               'price_unit, date, product_qty, product_uos,'\
                               'partner_id, name, product_id, auto_validate, location_id,'\
                               'company_id, picking_id, priority, state,'\
                               'location_dest_id, sale_line_id, sisa_wh, sisa_mark)'\
                               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'\
                               '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)',(uid, tg_dte, tg_dte, uid, rww.origin, rww.date_expected, rww.product_uom.id,
                                                                              rww.price_unit, rww.date, rww.sisa_mark, rww.product_uos.id, rww.partner_id.id, rww.name, rww.product_id.id,
                                                                              'FALSE', 12, rww.company_id.id, get_new_pck_id, 1, 'confirmed', 9, rww.sale_line_id.id, rww.sisa_wh, rww.sisa_mark))
                else:
                    try:
                        cr.execute("SELECT SUM(marketing_request_quantity) FROM stock_move WHERE origin = %s AND product_id = %s",(rww.origin, rww.product_id.id))
                        qw = cr.fetchone()[0]
                        cr.execute('INSERT INTO stock_move(create_uid,'\
                               'create_date, write_date, write_uid, origin,'\
                               'date_expected, product_uom,'\
                               'price_unit, date, product_qty, product_uos,'\
                               'partner_id, name, product_id, auto_validate, location_id,'\
                               'company_id, picking_id, priority, state,'\
                               'location_dest_id, purchase_line_id, weight_uom_id, sisa_wh, sisa_mark)'\
                               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'\
                               '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s, %s)',(uid, tg_dte, tg_dte, uid, rww.origin, rww.date_expected, rww.product_uom.id,
                                                                              rww.price_unit, rww.date, rww.sisa_mark, rww.product_uos.id, rww.partner_id.id, rww.name, rww.product_id.id,
                                                                              'FALSE', 12, rww.company_id.id, get_new_pck_id, 1, 'confirmed', 9, rww.purchase_line_id.id, rww.weight_uom_id.id, rww.sisa_wh, rww.sisa_mark))
                    except:
                        cr.execute("SELECT SUM(marketing_request_quantity) FROM stock_move WHERE origin = %s AND product_id = %s",(rww.origin, rww.product_id.id))
                        qw = cr.fetchone()[0]
                        cr.execute('INSERT INTO stock_move(create_uid,'\
                               'create_date, write_date, write_uid, origin,'\
                               'date_expected, product_uom,'\
                               'price_unit, date, product_qty, product_uos,'\
                               'partner_id, name, product_id, auto_validate, location_id,'\
                               'company_id, picking_id, priority, state,'\
                               'location_dest_id, purchase_line_id, sisa_wh, sisa_mark)'\
                               'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'\
                               '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s, %s)',(uid, tg_dte, tg_dte, uid, rww.origin, rww.date_expected, rww.product_uom.id,
                                                                              rww.price_unit, rww.date, rww.sisa_mark, rww.product_uos.id, rww.partner_id.id, rww.name, rww.product_id.id,
                                                                              'FALSE', 12, rww.company_id.id, get_new_pck_id, 1, 'confirmed', 9, rww.purchase_line_id.id, rww.sisa_wh, rww.sisa_mark))
            
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
    
    def action_assign_new(self, cr, uid, ids, vals, context=None):
        take_test = self.browse(cr, uid, ids[0], context=context)  
        if take_test.delivery_date == False:
            raise osv.except_osv(_('Warning!'), _('delivery date harus diisi'))
        else:
            sale_order_line_obj = self.pool.get('sale.order.line')
            pr_order_line_obj = self.pool.get('purchase.order.line')
            product_obj = self.pool.get('product.product')
            stck_move_obj = self.pool.get('stock.move')
            stc_pck_obj = self.pool.get('stock.picking')
            browse_pick = self.browse(cr, uid, ids, context=context)[0]
            sl_id = browse_pick.sale_id.id
            pr_id = self.pool['stock.picking.in'].browse(cr, uid, ids, context=context)[0].purchase_id.id
            pcck_id = browse_pick.id
            
            if sl_id:
                sale_order_line_obj_srch = sale_order_line_obj.search(cr, uid, [('order_id','=',sl_id)])
                apnd_ord_line_id = []
                prd_id_appen = []
                onhnd_apnd = []
                mj_on = 0
                msn = ""
                for ord_ln_id in sale_order_line_obj_srch:
                    stck_move_obj_srch = stck_move_obj.search(cr , uid, [('picking_id','=',pcck_id)])
                    
                    apnd_ord_line_id.append(ord_ln_id)
                    sale_order_line_obj_bws = sale_order_line_obj.browse(cr, uid, ord_ln_id, context=context)
                    prd_id_appen.append(sale_order_line_obj_bws.product_id.id)
                    product_obj_brwse = product_obj.browse(cr, uid, sale_order_line_obj_bws.product_id.id, context=context) 
                    onhnd_apnd.append(product_obj_brwse.qty_available) 
                #for stc_id in stck_move_obj_srch:
            else:
                pr_order_line_obj_srch = pr_order_line_obj.search(cr, uid, [('order_id','=',pr_id)])
                apnd_ord_line_id = []
                prd_id_appen = []
                onhnd_apnd = []
                mj_on = 0
                msn = ""
                for ord_ln_id in pr_order_line_obj_srch:
                    stck_move_obj_srch = stck_move_obj.search(cr , uid, [('picking_id','=',pcck_id)])
                    apnd_ord_line_id.append(ord_ln_id)
                    pr_order_line_obj_bws = pr_order_line_obj.browse(cr, uid, ord_ln_id, context=context)
                    prd_id_appen.append(pr_order_line_obj_bws.product_id.id)
                    product_obj_brwse = product_obj.browse(cr, uid, pr_order_line_obj_bws.product_id.id, context=context)
                    onhnd_apnd.append(product_obj_brwse.qty_available)
                
                if product_obj_brwse.qty_available <= 0:
                    msn = "one or more your product has zero or last than zero value in onhand quantity"
            if msn != "":
                raise osv.except_osv(_('Warning!'), _(msn))
            else:
                self.write(cr, uid , pcck_id, {'state' : 'assigned', 'button_two' : True}, context=context)
                stck_move_obj_srch_two = stck_move_obj.search(cr, uid, [('picking_id','=',pcck_id)])
                for idmov_stck in stck_move_obj_srch_two:
                    stck_move_obj.write(cr, uid , idmov_stck, {'state' : 'assigned'}, context=context)
            
        
        return True
        """
    
stock_picking_out

"""
class stock_move(osv.osv):
    _inherit = "stock.move"

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
        ob_stc_mv = self.pool.get('stock.move').search(cr, uid, [('origin','=',yupp_one),('product_id','=',yupp_two),('id','!=',yupp_four)])
        for okl in ob_stc_mv:
            brq = self.pool.get('stock.move').browse(cr, uid, okl, context)
            yupp_there += brq.product_qty
            
        ob_sal_ord = self.pool.get('sale.order').search(cr, uid, [('name','=',yupp_one)])
        for otw in ob_sal_ord:
            brg = self.pool.get('sale.order').browse(cr, uid, otw, context)
            yupp_five = brg.id
            
        ob_prc_ord = self.pool.get('purchase.order').search(cr, uid, [('name','=',yupp_one)])
        for otw in ob_prc_ord:
            brg = self.pool.get('purchase.order').browse(cr, uid, otw, context)
            yupp_five_p = brg.id
        
        ob_sal_ord_line = self.pool.get('sale.order.line').search(cr, uid, [('order_id','=',yupp_five),('product_id','=',yupp_two)])
        for kuch in ob_sal_ord_line:
            brh = self.pool.get('sale.order.line').browse(cr, uid, kuch, context)
            yupp_six = brh.product_uos_qty
        
        ob_prc_ord_line = self.pool.get('purchase.order.line').search(cr, uid, [('order_id','=',yupp_five_p),('product_id','=',yupp_two)])
        for kuch in ob_prc_ord_line:
            brh = self.pool.get('purchase.order.line').browse(cr, uid, kuch, context)
            yupp_six_p = brh.product_uos_qty
            
        kurang_in = yupp_six - yupp_there
        if kurang_in <= 0:
            kurang_in = yupp_six_p - yupp_there
                
        self.write(cr, uid, ids, {'sisa_mark' : kurang_in, 'product_qty' : kurang_in, 'marketing_request_quantity' : 0 , 'take_over': ''}, context)
          
    def onmov(self, cr, uid, ids, marketing_request_quantity, product_qty, sisa_wh, sisa_mark, context):
        get_wtf_id = product_qty
        ssw_wh = sisa_wh
        pick_ob_obj = self.pool.get("stock.picking")
        sale_lin_obj = self.pool.get("sale.order.line")
        prc_lin_obj = self.pool.get("purchase.order.line")
        get_mvee_id = self.browse(cr,uid,ids[0],context=context)
        get_orgn = get_mvee_id.origin
        coutn_delv_pick = pick_ob_obj.search(cr , uid, [('origin','=',get_orgn),('state','=','done')], count=True)
        brw_mov_line = self.browse(cr, uid, ids[0], context=context)
        brw_line_sale = sale_lin_obj.browse(cr, uid, brw_mov_line.sale_line_id.id, context=context)
        brw_line_prc = prc_lin_obj.browse(cr, uid, brw_mov_line.purchase_line_id.id, context=context)
       
        if sisa_wh != False or sisa_wh != 0:
            if marketing_request_quantity > sisa_wh:
                    return {'value':{'marketing_request_quantity' : 0},'warning':{'title':'check quantity', 'message':'marketing request quantity more than quantity be permitted'}}
                
            prcs = False
            try:
                for brw in brw_line_sale:
                    prcs = True
            except:
                prcs = False
                    
            if prcs:
                if marketing_request_quantity == 0:
                        return {'value':{'sisa_mark' : product_qty,'marketing_request_quantity' : 0 ,'product_qty' : 0, 'total_permintaan' : brw_line_sale.product_uom_qty, 'take_over' : 'Take Over'}}
                else:
                        return {'value':{'sisa_mark' : product_qty, 'product_qty' : marketing_request_quantity, 'total_permintaan' : brw_line_sale.product_uom_qty, 'take_over' : 'Take Over'}}
            else:
                if marketing_request_quantity == 0:
                        return {'value':{'sisa_mark' : product_qty,'marketing_request_quantity' : 0 ,'product_qty' : 0, 'total_permintaan' : brw_line_prc.product_qty, 'take_over' : 'Take Over'}}
                else:
                        return {'value':{'sisa_mark' : product_qty, 'product_qty' : marketing_request_quantity, 'total_permintaan' : brw_line_prc.product_qty, 'take_over' : 'Take Over'}}
                    
        else:
            if marketing_request_quantity > get_wtf_id:
                    return {'value':{'marketing_request_quantity' : 0},'warning':{'title':'check quantity', 'message':'marketing request quantity more than quantity be permitted'}}
                
            prcs = False
            try:
                for brw in brw_line_sale:
                    prcs = True
            except:
                prcs = False
                    
            if prcs:
                if marketing_request_quantity == 0:
                    return {'value':{'sisa_mark' : product_qty,'marketing_request_quantity' : 0 ,'product_qty' : 0, 'total_permintaan' : brw_line_sale.product_uom_qty, 'take_over' : 'Take Over'}}
                else:
                    return {'value':{'sisa_mark' : product_qty, 'product_qty' : marketing_request_quantity, 'total_permintaan' : brw_line_sale.product_uom_qty, 'take_over' : 'Take Over'}}
            else:
                if marketing_request_quantity == 0:
                    return {'value':{'sisa_mark' : product_qty,'marketing_request_quantity' : 0 ,'product_qty' : 0, 'total_permintaan' : brw_line_prc.product_qty, 'take_over' : 'Take Over'}}
                else:
                    return {'value':{'sisa_mark' : product_qty, 'product_qty' : marketing_request_quantity, 'total_permintaan' : brw_line_prc.product_qty, 'take_over' : 'Take Over'}}
                
stock_move
"""

class stock_return_picking(osv.osv_memory):
    _inherit = "stock.return.picking"
    
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
        date_cur = time.strftime('%Y-%m-%d %H:%M:%S')
        set_invoice_state_to_none = True
        returned_lines = 0
        
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
        # pick_obj.write(cr, uid, pick.id,{'move_lines': []})
        move_ids = []
        new_move_ids = []
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
                move_ids.append(move.id)
                new_move_ids.append(new_move)

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
        
        data_onee = self.browse(cr, uid, ids[0], context=context)
        orgni = pick.origin
        ambl_dua = str(orgni)
        
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

        # pick_obj.write(cr, uid, new_picking, {'state':'draft'}, context=context)
        # move_obj.write(cr, uid, move_ids, {'state':'draft'}, context=context)
        # move_obj.write(cr, uid, new_move_ids, {'state':'draft'}, context=context)
        
        step1 = pick_obj.browse(cr, uid, new_picking).move_lines
        for step2 in step1:
            # move_id = step2.id
            step3 = pick_obj.browse(cr, uid, new_picking).move_lines
            move_obj.write(cr, uid, step2.id, {'state':'draft'}, context=context)
            for step4 in step3:
                if step2.id != step4.id:
                    if step2.product_id.id == step4.product_id.id:
                        print step2.id, "=", step4.id
                        if isinstance(step2.id, (int, long)):
                            step2.id = [step2.id]
                        print move_obj.unlink(cr, uid, step2.id)
            try:
                move_obj.write(cr, uid, step2.id, {'state':'assigned'}, context=context)
            except:
                True
        
        return {
            'domain': "[('id', 'in', [" + str(new_picking) + "])]",
            'name': _('Returned Picking'),
            'view_type':'form',
            'view_mode':'tree,form',
            'res_model': model_list.get(new_type, 'stock.picking'),
            'type':'ir.actions.act_window',
            'context':context,
        }
        
stock_return_picking

"""
Model Transisi
"""

class pr_rp_val(osv.osv_memory):
    _name = "purchase.pr_rp_val"
    _columns = {
                    'jenis_report'  : fields.selection([
                                                       ('faktur', 'Faktur'),
                                                       ('sj', 'Surat Jalan'),
                                                       ], string='Jenis Report', required=True),
                    'purchase_type' : fields.selection(
                                                   [
                                                    ('LOP', 'Laporan Orientasi Pembelian (LOP)'),
                                                    ('KP', 'Konfirmasi Pembelian (KP)'),
                                                    ('PO', 'Purchase Order (PO)'),
                                                    ('SPK', 'Surat Perintah Kerja (SPK)')
                                                    ], string='Purchase Type', required=True),
                    'date_start'    : fields.date('Awal Period', required=True),
                    'date_end'      : fields.date('Akhir Period', required=True),
                    'supplier_list' : fields.many2one('res.partner', 'Supplier List', domain="[('supplier','=',True)]"),
                    'all'           : fields.boolean('Supplier List All'),
                    'type_view'     : fields.selection([
                                                            ('summary', 'Summary'),
                                                            ('detail', 'Detail'),
                                                        ], string='View Type Report'),
                }
    _defaults = {
                    'all' : True,
                    'jenis_report'  : 'faktur',
                    'type_view'     : 'summary',
                }

    def purc_prnt(self, cr , uid, ids, context=None):
        report_name = 'pr_vall.mako'
        if context is None:
            context = {}
        else:
            try:
                if context['xls_export']:
                    report_name = 'pr_vall.mako.xls'
            except:
                False
        
        tutut = self.browse(cr, uid, ids[0], context=context)
        context['jenis_report'] = tutut.jenis_report
        context['date_start'] = tutut.date_start
        context['date_end'] = tutut.date_end
        context['purchase_type'] = tutut.purchase_type
        context['all'] = tutut.all
        context['supplier_list'] = tutut.supplier_list.id

        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'context': context,
                }


pr_rp_val()

class purchase_outstand(osv.osv_memory):
    _name = 'purchase.outstand'
    _description = 'Outstanding Purchase'

    _columns = {
                'purchase_state' : fields.selection([('LOP', 'Laporan Orientasi Pembelian (LOP)'),
                                                    ('KP', 'Konfirmasi Pembelian (KP)'),
                                                    ('PO', 'Purchase Order (PO)'),
                                                    ('SPK', 'Surat Perintah Kerja (SPK)')
                                                    ], string='Purchase Type', required=True),
                'date_start' : fields.date('Tanggal Awal', required=True),
                'date_end' : fields.date('Tanggal Akhir', required=True),
                'all' : fields.boolean('All Supplier '),
                'partner_id' : fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
                }

    _defaults = {'all' : True}

    def cetak(self, cr , uid, ids, context=None):
        report_name = 'purchase.outstand'
        if context is None:
            context = {}
        else:
            try:
                if context['xls_export']:
                    report_name = 'purchase.outstand.xls'
            except:
                False
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'context' : context,
                }

purchase_outstand

class purchase_spk(osv.osv_memory):
    _name = 'purchase.spk'
    _description = 'Laporan SPK'

    _columns = {
                'date_start' : fields.date('Tanggal Awal', required=True),
                'date_end' : fields.date('Tanggal Akhir', required=True),
                'all' : fields.boolean('All Supplier '),
                'partner_id' : fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
                }

    _defaults = {'all' : False}

    def cetak(self, cr , uid, ids, context=None):
        report_name = 'purchase.spk'
        if context is None:
            context = {}
        else:
            try:
                if context['xls_export']:
                    report_name = 'purchase.spk.xls'
            except:
                False
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'context' : context,
                }

purchase_spk

class purchase_po(osv.osv_memory):
    _name = 'purchase.po'
    _description = 'Laporan Penerimaan Bahan Baku'

    _columns = {
                'date_start' : fields.date('Tanggal Awal', required=True),
                'date_end' : fields.date('Tanggal Akhir', required=True),
                'all' : fields.boolean('All Supplier '),
                'partner_id' : fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
                }

    _defaults = {'all' : False}

    def cetak(self, cr , uid, ids, context=None):
        report_name = 'purchase.po'
        if context is None:
            context = {}
        else:
            try:
                if context['xls_export']:
                    report_name = 'purchase.po.xls'
            except:
                False
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'context' : context,
                }

purchase_po

class purchase_bantu(osv.osv_memory):
    _name = 'purchase.bantu'
    _description = 'Laporan Penerimaan Bahan Pembantu'

    _columns = {
                'date_start' : fields.date('Tanggal Awal', required=True),
                'date_end' : fields.date('Tanggal Akhir', required=True),
                'all' : fields.boolean('All Supplier '),
                'partner_id' : fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
                }

    _defaults = {'all' : False}

    def cetak(self, cr , uid, ids, context=None):
        report_name = 'purchase.bantu'
        if context is None:
            context = {}
        else:
            try:
                if context['xls_export']:
                    report_name = 'purchase.bantu.xls'
            except:
                False
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'context' : context,
                }

purchase_bantu

class purchase_part(osv.osv_memory):
    _name = 'purchase.part'
    _description = 'Laporan Penerimaan Sparepart'

    _columns = {
                'date_start' : fields.date('Tanggal Awal', required=True),
                'date_end' : fields.date('Tanggal Akhir', required=True),
                'all' : fields.boolean('All Supplier '),
                'partner_id' : fields.many2one('res.partner', 'Supplier', domain="[('supplier','=',True)]"),
                }

    _defaults = {'all' : False}

    def cetak(self, cr , uid, ids, context=None):
        report_name = 'purchase.part'
        if context is None:
            context = {}
        else:
            try:
                if context['xls_export']:
                    report_name = 'purchase.part.xls'
            except:
                False
        return {
                'type': 'ir.actions.report.xml',
                'report_name': report_name,
                'context' : context,
                }

purchase_part

"""
Parser
"""

class purchase_outstand_cetak(report_sxw.rml_parse):
    def __init__(self, cr, uid, ids, context):
        print "Context", context
        super(purchase_outstand_cetak, self).__init__(cr, uid, ids, context=context)
        objects = self.pool.get('purchase.outstand').browse(cr, uid, ids)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'ids' : ids,
            'objects' : objects,
            'lines' : self.lines,
        })

    def lines(self, state, start, end, done=True, partner=None):
        cond = [('date_order', '>=', start), ('date_order', '<=', end), ('purchase_state', '=', state)]
        if not partner is None:
            cond.append(('partner_id', '=', partner))

        if not done :
            cond.append(('state', '!=', 'done'))

        step1 = self.pool.get('purchase.order').search(self.cr, self.uid, cond)
        return self.pool.get('purchase.order').browse(self.cr, self.uid, step1)

class purchase_spk_cetak(report_sxw.rml_parse):
    def __init__(self, cr, uid, ids, context):
        print "Context", context
        super(purchase_spk_cetak, self).__init__(cr, uid, ids, context=context)
        objects = self.pool.get('purchase.spk').browse(cr, uid, ids)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'ids' : ids,
            'objects' : objects,
            'lines' : self.lines,
        })

    def lines(self, state, start, end, done=True, partner=None):
        cond = [('date_order', '>=', start), ('date_order', '<=', end), ('purchase_state', '=', state)]
        if not partner is None:
            cond.append(('partner_id', '=', partner))

        if not done :
            cond.append(('state', '!=', 'done'))

        step1 = self.pool.get('purchase.order').search(self.cr, self.uid, cond)
        return self.pool.get('purchase.order').browse(self.cr, self.uid, step1)

class purchase_po_cetak(report_sxw.rml_parse):
    def __init__(self, cr, uid, ids, context):
        print "Context", context
        super(purchase_po_cetak, self).__init__(cr, uid, ids, context=context)
        objects = self.pool.get('purchase.po').browse(cr, uid, ids)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'ids' : ids,
            'objects' : objects,
            'lines' : self.lines,
        })

    def lines(self, state, start, end, done=True, partner=None):
        cond = [('date_order', '>=', start), ('date_order', '<=', end), ('purchase_state', '=', state)]
        if not partner is None:
            cond.append(('partner_id', '=', partner))

        if not done :
            cond.append(('state', '!=', 'done'))

        step1 = self.pool.get('purchase.order').search(self.cr, self.uid, cond)
        return self.pool.get('purchase.order').browse(self.cr, self.uid, step1)

class purchase_bantu_cetak(report_sxw.rml_parse):
    def __init__(self, cr, uid, ids, context):
        print "Context", context
        super(purchase_bantu_cetak, self).__init__(cr, uid, ids, context=context)
        objects = self.pool.get('purchase.bantu').browse(cr, uid, ids)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'ids' : ids,
            'objects' : objects,
            'lines' : self.lines,
        })

    def lines(self, start, end, done=True, partner=None):
        cond = [('date_order', '>=', start), ('date_order', '<=', end)]
        if not partner is None:
            cond.append(('partner_id', '=', partner))

        if not done :
            cond.append(('state', '!=', 'done'))

        step1 = self.pool.get('purchase.order').search(self.cr, self.uid, cond)
        return self.pool.get('purchase.order').browse(self.cr, self.uid, step1)

class purchase_part_cetak(report_sxw.rml_parse):
    def __init__(self, cr, uid, ids, context):
        print "Context", context
        super(purchase_part_cetak, self).__init__(cr, uid, ids, context=context)
        objects = self.pool.get('purchase.part').browse(cr, uid, ids)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'ids' : ids,
            'objects' : objects,
            'lines' : self.lines,
        })

    def lines(self, start, end, done=True, partner=None):
        cond = [('date_order', '>=', start), ('date_order', '<=', end)]
        if not partner is None:
            cond.append(('partner_id', '=', partner))

        if not done :
            cond.append(('state', '!=', 'done'))

        step1 = self.pool.get('purchase.order').search(self.cr, self.uid, cond)
        return self.pool.get('purchase.order').browse(self.cr, self.uid, step1)
    
"""
Parsing
"""

report_sxw.report_sxw('report.purchase.outstand', 'purchase.outstand', parser=purchase_outstand_cetak)
report_sxw.report_sxw('report.purchase.spk', 'purchase.spk', parser=purchase_spk_cetak)
report_sxw.report_sxw('report.purchase.po', 'purchase.po', parser=purchase_po_cetak)
report_sxw.report_sxw('report.purchase.bantu', 'purchase.bantu', parser=purchase_bantu_cetak)
report_sxw.report_sxw('report.purchase.part', 'purchase.part', parser=purchase_part_cetak)

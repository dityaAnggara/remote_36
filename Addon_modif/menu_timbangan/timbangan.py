'''
Created on Jan 29, 2015

@author: innotek
'''

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

class pick_out_one(osv.osv):
    _name = "menu_timbangan.pick_out_one"
    _inherit = "stock.picking.out"
    _table = "stock_picking"
    _description = "Delivery Orders"
    _columns = {
                    'jasa_angkut' : fields.many2one('menu_timbangan.part', 'Pengangkutan', states={'done': [('readonly', False)]}, store=True, domain=[('franco','=',True)]),
                }
    def action_print_sj(self, cr, uid, ids, context=None):
        
        brw_stock_pick = self.browse(cr, uid, ids, context=context)[0]
        if brw_stock_pick.surat_jalan == '-':
            
            take_sj = brw_stock_pick.surat_jalan
            obj_sj_conf = self.pool.get("sj_conf.stock_config_setting")
            obj_stok_pick = self.pool.get("stock.picking")
            
            obj_sj_conf_search = obj_sj_conf.search(cr, uid, [])
            count_sj_stock = obj_stok_pick.search(cr, uid, [('type','=','out'),('origin','like','SO%'),('surat_jalan','!=','-'),('name','not like','%return')], count=True)
            apen_sj_id = []
            for sj_ids in obj_sj_conf_search:
                bwr_obj_sj = obj_sj_conf.browse(cr, uid, sj_ids, context=context)
                apen_sj_id.append(bwr_obj_sj.id)
            max_sj_id = max(apen_sj_id)   
            brow_valu_sj = obj_sj_conf.browse(cr, uid, max_sj_id, context=context)
            
            pad_sj = str(brow_valu_sj.padding_sj)
            pad_sj_one = "%0"+pad_sj+"d"
            awl_sjn = int(brow_valu_sj.awal_sj) + 1
            awal_sjn_one = pad_sj_one % (awl_sjn)
            #raise osv.except_osv(_('ss'),_(count_sj_stock))
            
            if count_sj_stock != 0:
                lokk_sj = obj_stok_pick.search(cr, uid, [('type','=','out'),('origin','like','SO%'),('surat_jalan','!=','-'),('name','not like','%return')])
                apen_stock_ids = []
                for stc_ids in lokk_sj:
                    brwe_ids_stc_id = obj_stok_pick.browse(cr, uid, stc_ids, context=context)
                    lohh = int(brwe_ids_stc_id.surat_jalan)
                    apen_stock_ids.append(lohh)
                max_stc_id = max(apen_stock_ids)
                bwr_spick = obj_stok_pick.browse(cr, uid, max_stc_id, context=context)
                pad_sj = str(brow_valu_sj.padding_sj)
                pad_sj_one = "%0"+pad_sj+"d"
                awl_sjn = int(max_stc_id) + 1
                awal_sjn_one = pad_sj_one % (awl_sjn)
            
            cr.execute("UPDATE stock_picking SET surat_jalan = %s WHERE id = %s",(awal_sjn_one,brw_stock_pick.id))
            
        else:    
            raise osv.except_osv(_('Warning!'), _('surat jalan sudah terbit'))
        return True
class part(osv.osv):
    _name = "menu_timbangan.part"
    _inherit = "res.partner"
    _table = "res_partner"
    _defaults = {
                    'is_company' : True,
                    'franco' : True,
                 }
    
class stock_picking_out(osv.osv):
    _inherit = "stock.picking.out"
    

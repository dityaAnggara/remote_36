'''
Created on Dec 20, 2014

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
from openerp import pooler
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT, DATETIME_FORMATS_MAP, float_compare
#import openerp.addons.decimal_precision as dp
from openerp import netsvc
import roman
import calendar
from calendar import monthrange
import base64

class generate_kip(osv.osv_memory):
    _name = "generate.kip"
    _description = "generate the kip number"
    _columns = {
                    'typel'  : fields.selection([
                                                ('1', 'Number'),
                                                ('2', 'Roman'),
                                                ('3', 'Abjad'),
                                                ],'Type Category', required=True),
                    'jumlah' : fields.integer('Jumlah generate', required=True),
                }
    
    def generate_kip_act(self, cr, uid, ids, vals, context=None):
        obj_pd_kp_child = self.pool.get('product.kip.child')
        fui = self.browse(cr, uid, ids[0], context)
        tambah_satu = (fui.jumlah) + 1
        #raise osv.except_osv(_('Warning!'), _(tambah_satu)) 
        cr.execute("DELETE FROM product_kip_child")
        cr.commit()
        if fui.typel == '1':
            for jh in range(1, tambah_satu):
                #obj_pd_kp_child.create(cr, uid, {'number' : jh, 'alias' : jh}, context=context)
                cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,jh))
                cr.commit()
                
        elif fui.typel == '2':
                for jh in range(1, tambah_satu):
                #obj_pd_kp_child.create(cr, uid, {'number' : jh, 'alias' : jh}, context=context)
                    cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,roman.toRoman(jh)))
                    cr.commit()
        else:   
                batas = (26, 53, 78, 105, 131, 157, 183, 209, 235, 261, 287, 313, 339, 365, 391, 417, 443, 469, 495, 521, 547, 573, 599, 625, 651, 677, 703)
                yuo = 0
                gho = []
                for jh in range(1, tambah_satu):
                #obj_pd_kp_child.create(cr, uid, {'number' : jh, 'alias' : jh}, context=context)
                
                    for yo in range(0, 26):
                        if yuo == batas[yo]:
                            yuo = 0
                    if jh <= 26:
                        cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,chr(yuo + ord('A'))))
                        cr.commit()
                        
                    elif jh > 26 and jh <= 26*2:
                         ru = "A"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*2 and jh <= 26*3:
                         ru = "B"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()     
                    elif jh > 26*3 and jh <= 26*4:
                         ru = "C"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*4 and jh <= 26*5:
                         ru = "D"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()     
                    elif jh > 26*5 and jh <= 26*6:
                         ru = "E"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*6 and jh <= 26*7:
                         ru = "F"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*7 and jh <= 26*8:
                         ru = "G"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*8 and jh <= 26*9:
                         ru = "H"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*9 and jh <= 26*10:
                         ru = "I"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*10 and jh <= 26*11:
                         ru = "J"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*11 and jh <= 26*12:
                         ru = "K"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*12 and jh <= 26*13:
                         ru = "L"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*13 and jh <= 26*14:
                         ru = "M"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*14 and jh <= 26*15:
                         ru = "N"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*15 and jh <= 26*16:
                         ru = "O"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*16 and jh <= 26*17:
                         ru = "P"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*17 and jh <= 26*18:
                         ru = "Q"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()     
                    elif jh > 26*18 and jh <= 26*19:
                         ru = "R"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*19 and jh <= 26*20:
                         ru = "S"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*20 and jh <= 26*21:
                         ru = "T"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*21 and jh <= 26*22:
                         ru = "U"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*22 and jh <= 26*23:
                         ru = "V"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*23 and jh <= 26*24:
                         ru = "W"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*24 and jh <= 26*25:
                         ru = "X"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*25 and jh <= 26*26:
                         ru = "Y"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    elif jh > 26*26 and jh <= 26*27:
                         ru = "Z"+""+chr(yuo + ord('A'))
                         cr.execute("INSERT INTO product_kip_child(number,alias) VALUES(%s,%s)",(jh,ru))
                         cr.commit()
                    yuo +=1          
        return  {'type': 'ir.actions.act_window_close', 'type': 'ir.actions.act_window', 'res_model': 'product.kip.child', 'view_mode' : 'tree', 'view_type': 'form',}           
   
    
generate_kip()
    
'''
Created on Feb 26, 2015

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

class master(osv.osv):
    _name = "master_penting.master"
    _columns = {
                    'id' : fields.integer('ID'),
                    'name' : fields.char('Nama', required=True),
                    'alias_name' : fields.char('Alias',required=True),
                    'aktif' : fields.boolean('Status Aktif',help="centang jika ingin muncul pada tab yang dipentingkan di product"),
                }
    def create(self, cr, uid, vals, context=None):
        namee = vals.get('name')
        aliaas = vals.get('alias_name')
        cr.execute("ALTER TABLE product_product ADD COLUMN "+namee+" boolean DEFAULT TRUE")
        cr.execute("COMMENT ON COLUMN product_product."+namee+" IS '"+aliaas+"'")
        return super(master,self).create(cr, uid, vals, context)
    
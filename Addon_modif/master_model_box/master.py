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

class main(osv.osv):
    _name = "master_model_box.main"
    _columns = {
                    'name' : fields.char('Box Model Name',required=True),
                    'description_model' : fields.text('Description Model'),
                    'box_line'    : fields.one2many('master_model_box.line', 'box_id', 'Model Box Lines'),
                }
class line(osv.osv):
    _name = "master_model_box.line"
    _columns = {
                    'box_id'            : fields.many2one('master_model_box.main', 'Model Box Reference', required=True, ondelete='cascade', select=True),
                    'panjang_satu'      : fields.float('Panjang Satu'),
                    'panjang_dua'       : fields.float('Panjang Dua'),
                    'flap_atas_satu'    : fields.float('Flap atas Satu'),
                    'flap_atas_dua'     : fields.float('Flap atas Dua'),
                    'flap_bawah_satu'   : fields.float('Flap bawah Satu'),
                    'flap_bawah_dua'    : fields.float('Flap bawah Dua'),
                    'lebar_satu'        : fields.float('Lebar Satu'),
                    'lebar_dua'         : fields.float('Lebar Dua'),
                }    
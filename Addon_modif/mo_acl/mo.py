'''
Created on Apr 6, 2015

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

from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import datetime 
import time

class mrp_production(osv.osv):
    _inherit = "mrp.production"
    _columns = {
                    'prioritas_acl' : fields.integer('Prioritas'),
                }
    
    def change_prioor(self, cr, uid, ids, context=None):
        prio = self.browse(cr, uid, ids[0], context)
        dtte = prio.date_planned
        spliit = dtte.split(" ")
        app_en = []
        conv_dat = datetime.datetime.strptime(spliit[0]+" 00:00:00","%Y-%m-%d %H:%M:%S")
        conv_dat_sat =  datetime.datetime.strptime(spliit[0]+" 23:59:59","%Y-%m-%d %H:%M:%S")
        cr.execute("SELECT MIN(id) FROM mrp_production WHERE date_planned BETWEEN %s AND %s",(conv_dat,conv_dat_sat))
        fgy = cr.fetchone()[0]
        cr.execute("SELECT id FROM mrp_production WHERE state NOT IN ('done') AND date_planned BETWEEN %s AND %s ORDER BY id",(conv_dat,conv_dat_sat))
        fgyh = cr.fetchall()
        
        for uyh in fgyh:
            lhpu = self.browse(cr, uid, uyh[0], context)
            
            if uyh[0] == prio.id:
                break
            
            app_en.append(lhpu.id)
        
        self.write(cr, uid, ids[0], {'prioritas_acl' : 1}, context=context)
        for uyt in app_en:
            tutu = self.browse(cr, uid, uyt, context)
            tambah_prro = int(tutu.prioritas_acl) + 1
            self.write(cr, uid, uyt, {'prioritas_acl' : tambah_prro}, context=context)
         
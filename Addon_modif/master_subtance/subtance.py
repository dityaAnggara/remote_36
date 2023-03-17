'''
Created on Mar 24, 2015

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


class subbtance(osv.osv):
    _name = "master.subtance.subbtance"
    _description = "asasas"
    _rec_name = 'hiden_value'
    _columns = {
                    'name'           : fields.char('Abjad Subtance',required=True),
                    'nilai_subtance' : fields.char('Value Subtance',required=True),
                    'hiden_value'    : fields.char('Gabungan Name'),
                }
    
    def create(self, cr, uid, vals, context=None):
        try:
            nme = vals.get('name')+""+vals.get('nilai_subtance') 
            vals['hiden_value'] = nme
        except:
            print ":)"
        res = super(subbtance, self).create(cr, uid, vals, context)
        return res    
    def write(self, cr, uid, ids, vals, context=None):
        brw_mast_subc = self.browse(cr, uid, ids, context)[0]
        res = super(subbtance, self).write(cr, uid, ids, vals, context = context) 
        
        
        
        nmee = ""
        nme = ""
        if vals.get('name') == None:
            nme = brw_mast_subc.name
        else:
            nme = vals.get('name')    
        if vals.get('nilai_subtance') == None:
            nmee = brw_mast_subc.nilai_subtance
        else:    
            nmee = vals.get('nilai_subtance')
        nmme = nme+""+nmee
        cr.execute("UPDATE master_subtance_subbtance SET hiden_value = %s WHERE id = %s",(nmme,brw_mast_subc.id))
        
        return res            
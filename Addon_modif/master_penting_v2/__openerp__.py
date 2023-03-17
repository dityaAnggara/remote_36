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


{
    'name': 'Master YD v2',
    'version': '1.1',
    'author': 'Innotek',
    'category': 'Master yang dipentingkan',
    'depends': ['base', 'product', 'stock', 'mrp', 'purchase'],
    'demo': [],
    'description': """
            Master yang dipentingkan
    """,
    'data': [
        'security/ir.model.access.csv',     
        'master_penting.xml',
        
    ],
    'test': [
        
    ],
    'installable': True,
    'auto_install': False,
    'application'  : False,
    'images': [],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

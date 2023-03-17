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
    'name': 'Rekap quotation ACL',
    'version': '1.1',
    'author': 'Innotek',
    'category': 'print sale quotation',
    'depends': ['base', 'decimal_precision', 'mail', 'crm'],
    'demo': [],
    'description': """
            create crm for acl
    """,
    'data': [
        'report/rekap_sale.xml',
        
    ],
    'test': [
        
    ],
    'installable': True,
    'auto_install': False,
    'application'  : True,
    'images': ['images/innotek.jpeg'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:


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

    'name' : 'menu_timbangan',
    'version' : '1.0',
    'author' : 'Innotek',
    'category': 'timbangan',
    'description' : 'part to information about supllier and product price',
    'website': 'http://www.innotek.com',
    'depends' : ['base_setup', 'base', 'product', 'stock', 'stock_acl_v2'], # list of dependencies, conditioning startup order
    'data' : [
         'timbangan.xml',     
        #'security/user_timbang_security.xml',
        'security/ir.model.access.csv',
        'report/sj_report_timbang.xml',
    ],
    'demo': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
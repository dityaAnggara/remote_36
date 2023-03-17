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

    'name' : 'Purchase Report ACL',
    'version' : '3.0',
    'author' : 'Innotek',
    'category': 'purchase',
    'description' : 'Purchase Report ACL',
    'website': 'http://www.innotek.co.id',
    'depends' : ['base','purchase','purchase_requisition_acl','stock_acl_v2','report_xls'], # list of dependencies, conditioning startup order
    'data' : [
              'prc.xml',
              'view_prc.xml',
              'report/report.xml'
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
}

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

    'name' : 'sale acl',
    'version' : '3.0',
    'author' : 'Innotek',
    'category': 'workflow and button',
    'description' : 'new workflow for mrp in state change',
    'website': 'http://www.innotek.com',
    'depends' : ['base', 'sale', 'mrp', 'product', 'stock', 'mrp'], # list of dependencies, conditioning startup order
    'data' : [
              'report/skp_report.xml',
              'outstanding_one.xml',
              'sale_acl.xml',
              'test_pr.xml',
              #'workflow_acl.xml',
              'security/ir.model.access.csv'
              #'security/sale_security.xml'
    ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
}

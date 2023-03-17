# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    
#    Copyright (c) 2013 Eezee-it nv/sa (www.eezee-it.com). All rights reserved.
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
    'name': 'Execute Scheduler',
    'version': '1.0',
    'author': 'Eezee-It',
    'website': 'http://www.eezee-it.com',
    'category': 'Generic Modules/Others',
    'description': """
Scheduled action executer.
==========================
This module allows any user with access to the scheduler to execute any scheduled action at any moment.
It adds a button on each view 'scheduled actions' to run it directly.

**Path to access :** Settings/Technical/Scheduler/Scheduled Actions""",

    'depends': ['base'],
    'demo_xml': [],
    'init_xml': [],
    'data': [
        'view/execute_scheduler_view.xml',
    ],
    'update_xml' : [],
    'active': False,
    'installable': True,
    'images':['images/sc_scheduled_action_02.jpeg'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

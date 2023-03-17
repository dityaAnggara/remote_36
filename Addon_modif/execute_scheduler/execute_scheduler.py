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

from openerp.osv import osv, fields

class Cron(osv.osv):
    _inherit = "ir.cron"

    def name_get(self, cr, uid, ids, context=None):
        vals= []
        if not all(ids):
            return vals
        for cron in self.browse(cr, uid, ids, context=context):
            name = "%d. %s - %s.%s%s" % (cron.id, cron.name, cron.model, cron.function, cron.args)
            vals.append((cron.id,name))
        return vals

    def execute_scheduler(self, cr, uid, ids, context=None):
        cron = self.browse(cr, uid, ids)[0]

        if not cron:
            raise osv.except_osv(('Error!'),("No scheduler find for the ID %d" % ids[0]))

        try:
            print "Start %s" % cron.name_get()
            self._callback(cr, uid, cron.model, cron.function, cron.args, cron.id)
        except:
            raise osv.except_osv(('Error!'),("Error during the execution of the scheduler"))

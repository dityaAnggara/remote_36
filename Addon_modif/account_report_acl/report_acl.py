'''
Created on 5 Feb 2015

@author: innotek
'''
from openerp.osv import fields, osv
from datetime import datetime
from openerp.report import report_sxw
from openerp import pooler
from openerp.tools.translate import _

class accounting_report(osv.osv_memory):
    _inherit = 'accounting.report'
    _description = 'Accounting Report'
    
    def check_report_acl(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'acc.report.acl',
                'context' : context,
                }

    def cetak_xls(self, cr , uid, ids, context=None):
        if context is None:
            context = {}
        return {
                'type': 'ir.actions.report.xml',
                'report_name': 'acc.report.acl.xls',
                'context' : context,
                }

accounting_report

class parser(report_sxw.rml_parse):
    def __init__(self, cr, uid, ids, context):
        print "Context",context
        super(parser, self).__init__(cr, uid, ids, context=context)
        acc_report = self.pool.get('accounting.report').browse(cr, uid, ids)
        # perido = self.pool.get('account.period').search(cr, uid, [('fiscalyear_id', 'in', acc_report.fiscalyear_id.id)])
        # pesera = self.pool.get('account.move.line').search(cr, uid, [('period_id', 'in', perido)])
        # move_line = self.pool.get('account.move.line').browse(cr, uid, pesera)
        self.localcontext.update({
            'cr' : cr,
            'uid' : uid,
            'ids' : ids,
            'objects' : acc_report,
            'move_line' : self.move_line,
        })
        
    def move_line(self, period, account):
        step1 = self.pool.get('account.move.line').search(self.cr, self.uid, [('period_id', '=', period),('account_id', '=', account)])
        return self.pool.get('account.move.line').browse(self.cr, self.uid, step1)

report_sxw.report_sxw('report.acc.report.acl', 'accounting.report', parser=parser)
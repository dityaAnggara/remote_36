'''
Created on 27 Mar 2015

@author: innotek
'''
import xlwt
import time
from datetime import datetime
from openerp.osv import orm
from openerp.report import report_sxw
from openerp.addons.report_xls.report_xls import report_xls
from openerp.addons.report_xls.utils import rowcol_to_cell, _render
from openerp.tools.translate import _
import logging
import base64
import mx.DateTime

_logger = logging.getLogger(__name__)

class report_acc_report_acl_xls(report_xls):
    
    def oe_datetime_format(self,obj,format='%Y-%m-%d %H:%M:%S'):
        if obj.val:
            if hasattr(obj,'name') and (obj.name):
                return mx.DateTime.strptime(obj.name,format)
            else:
                return False
        else:
            return False

    def chdf(self,obj,format1,format2):
        return datetime.strptime(obj,format1).strftime(format2)
    
    def move_line(self, period, account):
        step1 = self.pool.get('account.move.line').search(self.cr, self.uid, [('period_id', '=', period),('account_id', '=', account)])
        return self.pool.get('account.move.line').browse(self.cr, self.uid, step1)
    
    def generate_xls_report(self, _p, _xs, data, objects, wb):
        ws = wb.add_sheet('General Report')
        baris = 0
        for o in objects:
            if (o.account_report_id and o.account_report_id.name) == 'Profit and Loss':
                True
            elif (o.account_report_id and o.account_report_id.name) == 'Balance Sheet':
                ws.write(baris,0,(o.company_id and o.company_id.name or ''))
                baris+=1
                ws.write(baris,0,(o.account_report_id and o.account_report_id.name or ''))
                baris+=1
                ws.write(baris,0,(('TAHUN %s') % (o.fiscalyear_id and o.fiscalyear_id.name or '')))
                baris+=2
                total={}
                kolom=1
                for period in o.fiscalyear_id.period_ids:
                    total[period.id]=0
                    try:
                        period_name = self.chdf(str(period.name), '%m/%Y', '%B')
                    except:
                        period_name = period.name
                    ws.write(baris,kolom,period_name)
                    kolom+=1
                baris+=1
                for coa1 in o.chart_account_id.child_parent_ids:
                    if not((coa1.debit == 0) and (coa1.credit == 0)):
                        kolom=0
                        acc_total = {}
                        ws.write(baris,kolom,(coa1.name or ''))
                        kolom+=1
                        for period in o.fiscalyear_id.period_ids:
                            acc_total[period.id] = 0
                            debit = 0
                            credit = 0
                            for line in self.move_line(period.id, coa1.id):
                                debit = debit + line.debit
                                credit = credit + line.credit
                            if (debit-credit) != 0:
                                acc_total[period.id] = acc_total[period.id] + (debit - credit)
                                ws.write(baris,kolom,(debit-credit))
                            kolom+=1
                        baris+=1
                        for coa2 in coa1.child_parent_ids:
                            if not((coa2.debit == 0) and (coa2.credit == 0)):
                                kolom=0
                                ws.write(baris,kolom,(('    %s') % (coa2.name or '')))
                                kolom+=1
                                for period in o.fiscalyear_id.period_ids:
                                    debit = 0
                                    credit = 0
                                    for line in self.move_line(period.id, coa2.id):
                                        debit = debit + line.debit
                                        credit = credit + line.credit
                                    if (debit-credit) != 0:
                                        acc_total[period.id] = acc_total[period.id] + (debit - credit)
                                        ws.write(baris,kolom,(debit-credit))
                                    kolom+=1
                                baris+=1
                                for coa3 in coa2.child_parent_ids:
                                    if not((coa3.debit == 0) and (coa3.credit == 0)):
                                        kolom=0
                                        ws.write(baris,kolom,(('        %s') % (coa3.name or '')))
                                        kolom+=1
                                        for period in o.fiscalyear_id.period_ids:
                                            debit = 0
                                            credit = 0
                                            for line in self.move_line(period.id, coa3.id):
                                                debit = debit + line.debit
                                                credit = credit + line.credit
                                            if (debit-credit) != 0:
                                                acc_total[period.id] = acc_total[period.id] + (debit - credit)
                                                ws.write(baris,kolom,(debit-credit))
                                            kolom+=1
                                        baris+=1
                                        for coa4 in coa3.child_parent_ids:
                                            if not((coa4.debit == 0) and (coa4.credit == 0)):
                                                kolom=0
                                                ws.write(baris,kolom,(('            %s') % (coa4.name or '')))
                                                kolom+=1
                                                for period in o.fiscalyear_id.period_ids:
                                                    debit = 0
                                                    credit = 0
                                                    for line in self.move_line(period.id, coa4.id):
                                                        debit = debit + line.debit
                                                        credit = credit + line.credit
                                                    if (debit-credit) != 0:
                                                        acc_total[period.id] = acc_total[period.id] + (debit - credit)
                                                        ws.write(baris,kolom,(debit-credit))
                                                    kolom+=1
                                                baris+=1
                                                for coa5 in coa4.child_parent_ids:
                                                    if not((coa5.debit == 0) and (coa5.credit == 0)):
                                                        kolom=0
                                                        ws.write(baris,kolom,(('                %s') % (coa5.name or '')))
                                                        kolom+=1
                                                        for period in o.fiscalyear_id.period_ids:
                                                            debit = 0
                                                            credit = 0
                                                            for line in self.move_line(period.id, coa5.id):
                                                                debit = debit + line.debit
                                                                credit = credit + line.credit
                                                            if (debit-credit) != 0:
                                                                acc_total[period.id] = acc_total[period.id] + (debit - credit)
                                                                ws.write(baris,kolom,(debit-credit))
                                                            kolom+=1
                                                        baris+=1
                        kolom=0
                        ws.write(baris,kolom,(('Jumlah %s') % (coa1.name or '')))
                        kolom+=1
                        for period in o.fiscalyear_id.period_ids:
                            if acc_total[period.id] != 0:
                                total[period.id] = total[period.id] + acc_total[period.id]
                                ws.write(baris,kolom,(acc_total[period.id]))
                            kolom+=1
                        baris+=2
    
report_acc_report_acl_xls('report.acc.report.acl.xls','accounting.report')
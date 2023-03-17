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

import base64
import time
from lxml import etree
from openerp.osv import fields
from openerp.osv import osv
from openerp import tools
from openerp.tools.translate import _
from BBM_additional import convert_to_words
import roman
import calendar
from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import time
import openerp.addons.decimal_precision as dp


class bbm_case(osv.Model):
    _name           = "buktibank_masuk.bbm_case"
    #_inherit        = "res.partner"
    _description    = "testing menu"
    def numb_bbm(self, cr, uid, ids, context=None):
        defa_nil = 1
        mntl = time.strftime("%m")
        yer = time.strftime("%y")
        imntl = int(mntl)
        fmntl = "%01d" % (imntl)
        ifmntl = int(fmntl)
        tr = roman.toRoman(ifmntl)
        yerone = time.strftime("%Y")
        iyerone = int(yerone)
        ghg = monthrange(iyerone, ifmntl)[1]
        mntldif = time.strftime("%Y-%m-01")
        mntldifone = time.strftime("%Y-%m-"+str(ghg))
        tg_dte = time.strftime("%Y-%m-%d %H:%M:%S")
        frmt_nnl = "%03d" % defa_nil
        cr.execute("SELECT COUNT(nomor_reg_bbm) FROM buktibank_masuk_bbm_case WHERE create_date BETWEEN  %s AND %s", (mntldif,mntldifone))
        jml_nmreg = cr.fetchone()[0]
        if jml_nmreg != 0:
            cr.execute("SELECT MAX(nomor_reg_bbm) FROM buktibank_masuk_bbm_case WHERE create_date BETWEEN  %s AND %s", (mntldif,mntldifone))
            getpo = cr.fetchone()[0]
            split_getpo = getpo.split("/")
            frmt_nnl = split_getpo[0]
            frmt_nnl = int(frmt_nnl) + 1
            frmt_nnl = "%03d" % frmt_nnl  
        df_nil = str(frmt_nnl)+"/BBMP/"+tr+"/"+yer    
        return df_nil
   
    def n_deff(self, cr ,uid, ids, field, arg, context=None):
        res = {}
        fgh_appned = []
        for bbm in self.browse(cr, uid, ids, context=context):
            for bbm1 in bbm.bbm_uraian_ids:
                fgh_appned.append(bbm1.tempo_float)
        return sum(fgh_appned)
    
    
    def summ2(self, cr, uid, ids, field, arg, context=None):
        ''''
        res = {}
        for bbm in self.browse(cr, uid, ids, context=context):
            res[bbm.id] = {
                'total': 0,
            }
            val = 0
            for bbm1 in bbm.bbm_uraian_ids:
                val += bbm1.tempo
            res[bbm.id] = convert_to_words.amount_to_text(val, 'id', 'idr')
            '''
        return 0 
    '''
    def n_deff(self, cr ,uid, ids, field, arg, context=None):
        res = {}
        for bbm in self.browse(cr, uid, ids, context=context):
            res[bbm.id] = {
                'total': 0,
            }
            val = 0
            for bbm1 in bbm.bbm_uraian_ids:
                val += bbm1.tempo
            res[bbm.id] = 'Rp. '+('{0:,}'.format(int(val)))+'.00'
            
        return res
    
    
    def summ2(self, cr, uid, ids, field, arg, context=None):
        #~ import ipdb;ipdb.set_trace();
        res = {}
        for bbm in self.browse(cr, uid, ids, context=context):
            res[bbm.id] = {
                'total': 0,
            }
            val = 0
            for bbm1 in bbm.bbm_uraian_ids:
                val += bbm1.tempo
            res[bbm.id] = convert_to_words.amount_to_text(val, 'id', 'idr')
        
        return res 
    '''
    _columns        = {
                            'cm_id'         : fields.many2one('res.partner', string='Costumer', required=True),
                            'date_bbm'      : fields.date('Tanggal', required=True, select=True),
                            'nomor_reg_bbm' : fields.char('Nomor', required=True),
                            #'fungsi_tblg'   : fields.function(summ2, type='text', string='Fungsi Terbilang'),
                            'total_semu'    : fields.function(n_deff, type='char',string='Total'),
                            #'total_float'   : fields.char('total float'),
                            'bbm_uraian_ids': fields.one2many('buktibank_masuk.bbm_uraian', 'bbm_case_id', 'Uraian', ondelete='cascade'),
                       }
    _defaults         ={
                            'date_bbm'  : fields.date.context_today,
                            'nomor_reg_bbm': numb_bbm,
                       }
    
class bbm_uraian(osv.Model):
    _name           = "buktibank_masuk.bbm_uraian"
    _description    = "uraian Bukti Bank Masuk"
    
    def f_cur(self, cr, uid, ids, jml_bbm, total_unfunction, context=None):
        d = '{0:,}'.format(float(jml_bbm))
        #tt = self.pool.get('buktibank_masuk.bbm_case').id
        return {'value':{'jml_bbm':'Rp. '+d+'0', ']tempo_float' : float(jml_bbm)}}
    
    
    _columns        = {
                            'nmor_perkiraan'    : fields.char('Nomor Perkiraan'),
                            'uraian_bbm'        : fields.text('uraian'),
                            'jml_bbm'           : fields.char('Jumlah'),
                            'tempo'             : fields.integer('Temporary'),
                            'tempo_float'       : fields.float('Temporary float version'),
                            'bbm_case_id'       : fields.many2one('buktibank_masuk.bbm_case', 'Case', required=True, ondelete='cascade', select=True, readonly=True),
                       }    
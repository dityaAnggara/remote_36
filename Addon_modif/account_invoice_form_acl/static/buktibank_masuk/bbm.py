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

class bbm_case(osv.Model):
    _name           = "buktibank_masuk.bbm_case"
    #_inherit        = "res.partner"
    _description    = "testing menu"
    
    def summ1(self, cr, uid, ids, field, arg, context=None):
        #~ import ipdb;ipdb.set_trace();
        res = {}
        for bbm in self.browse(cr, uid, ids, context=context):
            res[bbm.id] = {
                'total': 0,
            }
            val = 0
            for bbm1 in bbm.bbm_uraian_ids:
                val += bbm1.tempo
            res[bbm.id] = val
        return res
    def n_deff(self, cr ,uid, ids, field, arg, context=None):
        res = {}
        for bbm in self.browse(cr, uid, ids, context=context):
            res[bbm.id] = {
                'total': 0,
            }
            val = 0
            for bbm1 in bbm.bbm_uraian_ids:
                val += bbm1.tempo
            res[bbm.id] = 'Rp. '+('{0:,}'.format(float(val)))+'0'
            
        return res
    
       
    def numToWords(self, cr, uid, ids, field, arg, context=None):
        res = {}
        for bbm in self.browse(ids):
            res[bbm.id] = {
                'total': 0,
            }
            val = 0
            for bbm1 in bbm.bbm_uraian_ids:
                val += bbm1.tempo
        res[bbm.id] = val
        return val 
    def numtoword(self,uid, ids):
        angka=["","Satu","Dua","Tiga","Empat","Lima","Enam","Tujuh","Delapan","Sembilan","Sepuluh","Sebelas"]
        Hasil =" "
        #n = int(self.summ1(cr, uid, ids, field, arg, context))
        n  = int(self.numToWords())
        if n >= 0 and n <= 11:
            Hasil = Hasil + angka[n]
        elif n < 20:
            Hasil = self.numToWords(n % 10) + " Belas"
        elif n < 100:
            Hasil = self.numToWords(n / 10) + " Puluh" + self.numToWords(n % 10)
        elif n < 200:
            Hasil = " Seratus" + self.numToWords(n - 100)
        elif n < 1000:
            Hasil = self.numToWords(n / 100) + " Ratus" + self.numToWords(n % 100)
        elif n < 2000:
            Hasil = " Seribu" + self.numToWords(n - 1000)
        elif n < 1000000:
            Hasil = self.numToWords(n / 1000) + " Ribu" + self.numToWords(n % 1000)
        elif n < 1000000000:
            Hasil = self.numToWords(n / 1000000) + " Juta" + self.numToWords(n % 1000000)
        else:
            Hasil = self.numToWords(n / 1000000000) + " Milyar" + self.numToWords(n % 100000000)
        return Hasil
    
    _columns        = {
                            'cm_id'         : fields.many2one('res.partner', string='Costumer', required=True),
                            'date_bbm'      : fields.date('Tanggal', required=True, select=True),
                            'nomor_reg_bbm' : fields.char('Nomor', required=True),
                            'fungsi_tblg'   : fields.function(numToWords, type='text', string='Fungsi Terbilang'),
                            'total_semu'    : fields.function(n_deff, type='char',string='Total'),
                            'total'         : fields.function(summ1,type='integer',string='Total jumlah'),
                            'bbm_uraian_ids': fields.one2many('buktibank_masuk.bbm_uraian', 'bbm_case_id', 'Uraian', ondelete='cascade'),
                       }
    _defaults         ={
                            'date_bbm'  : fields.date.context_today,
                            #'total_semu': n_deff,
                       }
    
class bbm_uraian(osv.Model):
    _name           = "buktibank_masuk.bbm_uraian"
    _description    = "uraian Bukti Bank Masuk"
    
    def f_cur(self, cr, uid, ids, jml_bbm, context):
        d = '{0:,}'.format(float(jml_bbm))
        return {'value':{'jml_bbm':'Rp. '+d+'0', 'tempo':int(jml_bbm)}}
    
    
    _columns        = {
                            'nmor_perkiraan'    : fields.char('Nomor Perkiraan'),
                            'uraian_bbm'        : fields.text('uraian'),
                            'jml_bbm'           : fields.char('Jumlah'),
                            'tempo'             : fields.integer('Temporary'),
                            'bbm_case_id'       : fields.many2one('buktibank_masuk.bbm_case', 'Case', required=True, ondelete='cascade', select=True, readonly=True),
                       }    
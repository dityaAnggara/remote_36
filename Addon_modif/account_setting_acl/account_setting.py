# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Business Applications
#    Copyright (C) 2004-2012 OpenERP S.A. (<http://openerp.com>).
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

import time
import datetime
from dateutil.relativedelta import relativedelta

import openerp
from openerp import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF
from openerp.tools.translate import _
from openerp.osv import fields, osv

class account_config_settings(osv.osv):
    _name = "account_setting_acl.account_config_settings"
    _description = "account setting for acl"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(account_config_settings, self).default_get(cr, uid, fields, context=context)
        
        jml_nmreg = self.search(cr, uid, [], count=True)
        if jml_nmreg != 0:
            ob_acn_set = self.pool.get('account_setting_acl.account_config_settings')
            ob_acn_set_ids = self.search(cr, uid, [])
            id_acp = []
            for swe in ob_acn_set_ids:
                mx_id = ob_acn_set.browse(cr, uid, swe, context=context)
                id_acp.append(mx_id.id)
                mxx_id = max(id_acp)
                df = self.browse(cr, uid, mxx_id) 
                res['kb_code_acl'] = df.kb_code_acl
                res['nonkb_code_acl'] = df.nonkb_code_acl
                res['tahun_pajak_acl'] = df.tahun_pajak_acl
                res['no_urut_k_pajak_acl'] = df.no_urut_k_pajak_acl
                res['nmr_urut_pajak_pertama'] = df.nmr_urut_pajak_pertama
                res['nmr_urut_pajak_terakhir'] = df.nmr_urut_pajak_terakhir
        return res
    
    _columns   = {
                   'kb_code_acl'             : fields.char('Kawasan Berikat Code', help="kawasan berikat code exp: 070", store=True),
                   'nonkb_code_acl'          : fields.char('Non Kawasan Berikat Code', help="non kawasan berikat code exp: 010", store=True),
                   'tahun_pajak_acl'         : fields.char('Tahun Pajak', help="save Tahun Pajak", store=True),
                   'no_urut_k_pajak_acl'     : fields.char('Nomor Urut Permintaan ke kantor Pajak', store=True),
                   'nmr_urut_pajak_pertama'  : fields.integer('Nomor urut Pertama Pajak', store=True),
                   'nmr_urut_pajak_terakhir' : fields.integer('Nomor urut Terakhir Pajak', store=True),
                  }
                 
    
   
    
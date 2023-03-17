'''
Created on Nov 11, 2014

@author: innotek
'''
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

from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import math

class product_product(osv.osv):
    _inherit        = "product.product"
    _description    = "Relation customer with product"
    
    def luas_fc(self, cr, uid, ids, field, arg, context=None):
        res={}

        for rec in self.browse(cr, uid, ids):
            res[rec.id] = 0.0
        
        return res
    def berat_fc(self, cr, uid, ids, field, arg, context=None):
        res={}

        for rec in self.browse(cr, uid, ids):
            res[rec.id] = 0.0
        
        return res
    _columns        = {
                        'subtance_hasil'    : fields.char('Subtance'),
                        'printing_line'     : fields.one2many('product.printing.line', 'print_id', 'Printing Lines'),
                        'mpnt_line'         : fields.one2many('product.master.penting', 'mpnt_id', 'Master Penting Lines'),
                        'jumlah_order_kip'  : fields.float('Jumlah Order'),
                        'skp_customer'      : fields.many2one('sale.order','Sale Order'),
                        'cusm_id'           : fields.many2one('res.partner', String="Customer Name", domain="[('ref','!=',False)]"),
                        'aui_acl_prod'      : fields.integer('AUI'),
                        'no_kiip'           : fields.char('Nomor KIP'),
                        'ukur_panjang'      : fields.char('Ukuran Panjang'),
                        'ukur_lebar'        : fields.char('Ukuran Lebar'),
                        'ukur_tinggi'       : fields.char('Ukuran Tinggi'),
                        'ukuran_panjang'    : fields.float('Ukuran Panjang'),
                        'ukuran_lebar'      : fields.float('Ukuran Lebar'),
                        'ukuran_tinggi'     : fields.float('Ukuran Tinggi'),
                        'sheet_panjang'     : fields.char('Sheet Panjang'),
                        'sheet_lebar'       : fields.char('Sheet Lebar'),
                        'dimension'         : fields.char('Panjang Sheet'),
                        'dimension_one'     : fields.char('Lebar Sheet'),
                        'subtance'          : fields.char('Panjang Product'),
                        'subtance_one'      : fields.char('Lebar Product'),
                        'subtance_two'      : fields.char('Tinggi Product'),
                        'sbt_one'           : fields.float('Satu'),
                        'sbt_dua'           : fields.float('Dua'),
                        'sbt_tiga'          : fields.float('Tiga'),
                        'sbt_empat'         : fields.float('Empat'),
                        'sbt_lima'          : fields.float('Lima'),
                        'pnjg_satu'         : fields.float('P Satu'),
                        'pnjg_dua'          : fields.float('P Satu'),
                        'pnjg_tiga'         : fields.float('P Satu'),
                        'pnjg_empat'        : fields.float('P Satu'),
                        'pnjg_lima'         : fields.float('P Satu'),
                        'pnjg_enam'         : fields.float('P Satu'),
                        'pnjg_tujuh'        : fields.float('P Satu'),
                        'pnjg_lapan'        : fields.float('P Satu'),
                        'pnjg_smbl'         : fields.float('P Satu'),
                        'pnjg_sph'          : fields.float('P Satu'),
                        'lbr_satu'          : fields.float('P Satu'),
                        'lbr_dua'           : fields.float('P Satu'),
                        'lbr_tiga'          : fields.float('P Satu'),
                        'lbr_empat'         : fields.float('P Satu'),
                        'lbr_lima'          : fields.float('P Satu'),
                        'lbr_enam'          : fields.float('P Satu'),
                        'lbr_tujuh'         : fields.float('P Satu'),
                        'lbr_lapan'         : fields.float('P Satu'),
                        'lbr_smbl'          : fields.float('P Satu'),
                        'lbr_sph'           : fields.float('P Satu'),
                        #'model'             : fields.many2one('master_model_box.main','Model Box'),
                        'model_box_new'     : fields.many2one('master_model_box.main', 'Model Box'),
                        'flute'             : fields.many2one('product.flute.acl', 'Flute'),
                        'color'             : fields.char('Warna'),
                        'child_product'     : fields.boolean('Is Child ?'),
                        'stich'             : fields.boolean('Stitching'),
                        'glue'              : fields.boolean('Glue'),
                        'set_kip'           : fields.char('Set'),
                        'pcs_kip'           : fields.char('Pcs'),
                        'luas_kip'          : fields.char('Luas'),
                        'berat_kip'         : fields.char('Berat'),
                        'ikat_kip'          : fields.float('Bundel/Ikat'),
                        'prod_parent'       : fields.many2one('product.product','Parent Product', domain="[('child_product','=',False),('type','!=','service')]"),
                        'subtance_one'      : fields.many2one('master.subtance.subbtance','Subtance One'),
                        'subtance_two'      : fields.many2one('master.subtance.subbtance','Subtance Two'),
                        'subtance_three'    : fields.many2one('master.subtance.subbtance','Subtance There'),
                        'subtance_four'     : fields.many2one('master.subtance.subbtance','Subtance four'),
                        'subtance_five'     : fields.many2one('master.subtance.subbtance','Subtance five'),
                       }
    _defaults = {
                  'child_product' : False,
                  
                 }
    
    def fields_view_get(self, cr, uid, view_id=None, view_type='form', context=None, toolbar=False, submenu=False):
        
        cr.execute("SELECT id FROM ir_module_category WHERE name = 'Manufacturing'")
        tyh = cr.fetchone()[0]
        
        
        res = super(product_product,self).fields_view_get(cr, uid, view_id=view_id, view_type=view_type, context=context, toolbar=toolbar, submenu=submenu)

        get_grop_id = self.pool.get('res.groups').search(cr, uid, [('name','=','Manager'),('category_id','=',tyh)])
        brow_grp = self.pool.get('res.groups').browse(cr, uid, get_grop_id, context)[0]
        cr.execute("SELECT COUNT(uid) FROM res_groups_users_rel WHERE uid = %s AND gid = %s",(uid, brow_grp.id))
        find = cr.fetchone()[0]
        
        for field in res['fields']:
            if find >= 1: 
                if field == 'categ_id':
                    #res['fields'][field]['domain'] = [('parent_id','=','2'),('|',('name','like','Carton Box'),('name','like','Paper Tube'))]
                    res['fields'][field]['domain'] = [('parent_id','!=','2'),('name','in',('Carton Box','Paper Tube'))]
                    #res['fields'][field]['domain'] = ['|',('name','=like','Carton Box')]
        return res
    def default_get(self, cr, uid, fields, context=None):
        if context is None:
            context = {}
        #print context
        #raise osv.except_osv(_('Warning!'), _(context.get('view_type')))
        res = super(product_product, self).default_get(cr, uid, fields, context=context) 
        if context.get('cusm_id') is None:    
            print "not in sale order"
            
        else:
            print context
            quantity = context.get('quantity')
            toler = context.get('toleransi')
            int_quantity = int(quantity)
            int_tolers = int(toler)
            jmlh_tmbh = int_quantity + int_tolers 
            #raise osv.except_osv(_('Test'),_(context.get('quantity')))
            res.update({'jumlah_order_kip' : jmlh_tmbh,'cusm_id': context['cusm_id']})
            
            '''
               
            bwose = self.pool.get('res.partner').browse(cr, uid, context['cusm_id'], context=context)    
            if bwose.supplier == False:
                raise osv.except_osv(_('Warning!'), _("Customer"))
            else:
                raise osv.except_osv(_('Warning!'), _("sUPPLIER"))
        '''
        return res
    def create(self, cr, uid, vals, context=None):
        ty = []
        get_grop_id = self.pool.get('res.groups').search(cr, uid, [('name','=like','See all Leads')])
        brow_grp = self.pool.get('res.groups').browse(cr, uid, get_grop_id, context)[0]
        cr.execute("SELECT COUNT(uid) FROM res_groups_users_rel WHERE uid = %s AND gid = %s",(uid, brow_grp.id))
        find = cr.fetchone()[0]
        no_kipp = vals.get('no_kiip')
        cusm_id = vals.get('cusm_id')
        if cusm_id == True and no_kipp == False:
            raise osv.except_osv(_('Warning!'), _('test'))
        if find >= 1:
            raise osv.except_osv(_('Warning!'), _('Access denied : you cannot create product, please contact your administrator'))
        return super(product_product, self).create(cr, uid, vals, context=context)    
    def onchange_parent_prod(self, cr, uid, ids, prod_parent, context=None):
        ob_rs_partner = self.pool.get('product.product')
        ob_rs_uio = self.pool.get('product.kip.child')
        ob_rs_partner_sch = ob_rs_partner.search(cr, uid, [('prod_parent','=',prod_parent)], count=True)
        brw_part_res = ob_rs_partner.browse(cr, uid, prod_parent, context=context)
        apnx_id = []
        ob_rs_uio_id = ob_rs_uio.search(cr, uid, [('number','=', 1)])
        for ite_rat in ob_rs_uio_id:
            id_ietar = ob_rs_uio.browse(cr, uid, ite_rat)
            apnx_id.append(id_ietar.alias)
        max_tampung = max(apnx_id)
        #raise osv.except_osv(_('Warning!'), _(max_tampung))
        ob_rs_uio_bwe = ob_rs_uio.browse(cr, uid, max_tampung, context=context)
        aliass = ob_rs_uio_bwe.alias 
        id = 1
        id_str = str(max_tampung)
        kkip = str(brw_part_res.no_kiip)
        gann = kkip+"-"+id_str
        if  ob_rs_partner_sch != 0:
            apd_op = []
            go_int = int(ob_rs_partner_sch)+1
            str_go_int = str(go_int)
            ob_rs_uio_id_one = ob_rs_uio.search(cr, uid, [('number','=', go_int)], count=True)
            ob_rs_uio_id_two = ob_rs_uio.search(cr, uid, [('number','=', go_int)])
            if ob_rs_uio_id_one == 0:
                raise osv.except_osv(_('Warning!'), _("alias for number "+str_go_int+" undifened")) 
            else:
                for ite_rat in ob_rs_uio_id_two:
                    id_ietar = ob_rs_uio.browse(cr, uid, ite_rat)
                    apd_op.append(id_ietar.alias)
                    max_tampung_one = max(apd_op)
                    str_max_tampung_one = str(max_tampung_one)
                    gann = kkip+"-"+str_max_tampung_one
        return {'value':{'no_kiip':gann}}
        
    def onchange_cusm_id(self, cr, uid, ids, cusm_id, context=None):
        pool_obj_partner        = self.pool.get('res.partner')
        pool_obj_partner_browse = pool_obj_partner.browse(cr, uid, cusm_id, context=context)
        cr.execute("SELECT MAX(id) FROM product_kip_padd")
        patd = cr.fetchone()[0]
        cr.execute("SELECT padding_kip FROM product_kip_padd WHERE id = %s",(patd,))
        patd_one = cr.fetchone()[0]
        patd_one_str = str(patd_one)
        cba     = pool_obj_partner_browse.ref
        fgh=1
        odop_ae = "%0"+patd_one_str+"d"
        ghf= odop_ae % (fgh)
        if cba:
            cr.execute('SELECT max(id) FROM product_product WHERE cusm_id = %s AND aui_acl_prod IS NOT NULL',(cusm_id,))
            dfg = cr.fetchone()[0]
            if dfg:
                cr.execute('SELECT aui_acl_prod FROM product_product WHERE id = %s',(dfg,))
                fgh = cr.fetchone()[0]
                #raise osv.except_osv(_("sas"),_(fgh))
                fgh = int(fgh)+1
                #fgh = "%012d" % ( (int(fgh)+1) , 3)
                odop_ae = "%0"+patd_one_str+"d"
                ghf= odop_ae % (fgh)
             
        gab = "-".join((str(cba),str(ghf)))
        return {'value':{'no_kiip':gab, 'aui_acl_prod':fgh}}
    def compute_all_one(self,cr,uid,ids,vals,context=None):
        
        jgu = self.browse(cr, uid, ids[0], context)
        shet_panjang = float(jgu.sheet_panjang)
        shet_lebar   = float(jgu.sheet_lebar)
        haslnya = (shet_panjang * shet_lebar)/1000000
        subt_bw = self.browse(cr, uid, ids[0], context)
        ms = 0
        if subt_bw.subtance_one:
            ht1 = subt_bw.subtance_one.nilai_subtance
            hy = float(ht1)*1
            ms += hy 
        if subt_bw.subtance_two:
            ht2 = subt_bw.subtance_two.nilai_subtance
            hy1 = float(ht2)*1.4
            ms += hy1
        if subt_bw.subtance_three:
            ht3 = subt_bw.subtance_three.nilai_subtance
            hy2 = float(ht3)*1
            ms += hy2
        if subt_bw.subtance_four:
            ht4 = subt_bw.subtance_four.nilai_subtance
            hy3 = float(ht4)*1.5
            ms += hy3
        if subt_bw.subtance_five:                
            ht5 = subt_bw.subtance_five.nilai_subtance          
            hy4 = float(ht5)*1                 
            ms += hy4
            
        me = ms/1000
        berat_gabung = haslnya*me
        self.write(cr, uid ,ids, {'luas_kip' : haslnya,'subtance_hasil': me,'berat_kip' : berat_gabung}, context=context)
        
        mbn = self.pool.get('master_model_box.main').browse(cr, uid, jgu.model_box_new.id, context)
        mvx =  self.pool.get('product.flute.acl').browse(cr, uid, jgu.flute.id, context)
        pd_bsr = self.browse(cr, uid, ids[0], context)
        
        if mbn.name == "B1":
            typ_flute = ""
            pnj_satu_satu = ""
            lebb = ""
            pnj_duak = ""
            leeb = ""
            flap_bawh = ""
            if mvx.type_flute == '0':
                typ_flute = 30
            else:
                typ_flute = 50
            if mvx.name == "A":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 2
                flap_bawh = (lbv * 0.5) + 4
                tgng = float(pd_bsr.ukur_tinggi) 
            elif mvx.name == "B":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 2
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 3
                pnj_duak = pnj_satu + 3
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 2
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "C":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 4
                pnj_duak = pnj_satu + 4
                leeb = lbv + 1
                flap_bawh = (lbv * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "E":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 1
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 2
                pnj_duak = pnj_satu + 2
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 1
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "AB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 7
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 10
                pnj_duak = pnj_satu + 8
                leeb = lbv + 5
                flap_bawh = (lbv * 0.5) + 6
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "BC":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 4
                flap_bawh = (lbv * 0.5) + 5
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "EB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 5
                pnj_duak = pnj_satu + 4
                leeb = lbv + 3
                flap_bawh = (lbv * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)    
            self.write(cr, uid ,ids, {'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_bawh,'lbr_dua' : tgng,'lbr_tiga' : flap_bawh}, context=context)
            return {'value':{'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_bawh,'lbr_dua' : tgng,'lbr_tiga' : flap_bawh}}        
        elif mbn.name == "B1 B0":
            typ_flute = ""
            pnj_satu_satu = ""
            lebb = ""
            pnj_duak = ""
            leeb = ""
            flap_bawh = ""
            if mvx.type_flute == '0':
                typ_flute = 30
            else:
                typ_flute = 50
            if mvx.name == "A":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 2
                flap_bawh = (lbv * 0.5) + 4
                tgng = float(pd_bsr.ukur_tinggi) 
            elif mvx.name == "B":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 2
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 3
                pnj_duak = pnj_satu + 3
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 2
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "C":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 4
                pnj_duak = pnj_satu + 4
                leeb = lbv + 1
                flap_bawh = (lbv * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "E":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 1
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 2
                pnj_duak = pnj_satu + 2
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 1
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "AB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 7
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 10
                pnj_duak = pnj_satu + 8
                leeb = lbv + 5
                flap_bawh = (lbv * 0.5) + 6
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "BC":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 4
                flap_bawh = (lbv * 0.5) + 5
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "EB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 5
                pnj_duak = pnj_satu + 4
                leeb = lbv + 3
                flap_bawh = (lbv * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            self.write(cr, uid ,ids, {'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_bawh,'lbr_dua' : tgng,'lbr_tiga' : 0}, context=context)        
            return {'value':{'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_bawh,'lbr_dua' : tgng,'lbr_tiga' : 0}} 
        elif mbn.name == "B0":
            typ_flute = ""
            pnj_satu_satu = ""
            lebb = ""
            pnj_duak = ""
            leeb = ""
            flap_bawh = ""
            if mvx.type_flute == '0':
                typ_flute = 30
            else:
                typ_flute = 50
            if mvx.name == "A":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 2
                flap_bawh = (lbv * 0.5) + 4
                tgng = float(pd_bsr.ukur_tinggi) 
            elif mvx.name == "B":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 2
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 3
                pnj_duak = pnj_satu + 3
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 2
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "C":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 4
                pnj_duak = pnj_satu + 4
                leeb = lbv + 1
                flap_bawh = (lbv * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "E":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 1
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 2
                pnj_duak = pnj_satu + 2
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 1
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "AB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 7
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 10
                pnj_duak = pnj_satu + 8
                leeb = lbv + 5
                flap_bawh = (lbv * 0.5) + 6
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "BC":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 4
                flap_bawh = (lbv * 0.5) + 5
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "EB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 5
                pnj_duak = pnj_satu + 4
                leeb = lbv + 3
                flap_bawh = (lbv * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            self.write(cr, uid ,ids, {'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : 0,'lbr_dua' : tgng,'lbr_tiga' : 0}, context=context)        
            return {'value':{'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : 0,'lbr_dua' : tgng,'lbr_tiga' : 0}}
        elif mbn.name == "B3":
            typ_flute = ""
            pnj_satu_satu = ""
            lebb = ""
            pnj_duak = ""
            leeb = ""
            flap_bawh = ""
            if mvx.type_flute == '0':
                typ_flute = 30
            else:
                typ_flute = 50
            if mvx.name == "A":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 2
                flap_bawh = math.ceil((lbv * 1) + 4)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 4)
                tgng = float(pd_bsr.ukur_tinggi) 
            elif mvx.name == "B":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 2
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 3
                pnj_duak = pnj_satu + 3
                leeb = lbv + 0
                flap_bawh = math.ceil((lbv * 1) + 2)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 2)
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "C":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 4
                pnj_duak = pnj_satu + 4
                leeb = lbv + 1
                flap_bawh = math.ceil((lbv * 1) + 3)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 3)
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "E":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 1
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 2
                pnj_duak = pnj_satu + 2
                leeb = lbv + 0
                flap_bawh = math.ceil((lbv * 1) + 1)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 1)
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "AB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 7
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 10
                pnj_duak = pnj_satu + 8
                leeb = lbv + 5
                flap_bawh = math.ceil((lbv * 1) + 6)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 6)
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "BC":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 4
                flap_bawh = math.ceil((lbv * 1) + 5)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 5)
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "EB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 5
                pnj_duak = pnj_satu + 4
                leeb = lbv + 3
                flap_bawh = math.ceil((lbv * 1) + 3)
                flap_bawh_satu = math.ceil((lbv * 0.5) + 3)
                tgng = float(pd_bsr.ukur_tinggi)
            self.write(cr, uid ,ids, {'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_bawh_satu,'lbr_dua' : tgng,'lbr_tiga' : flap_bawh}, context=context)        
            return {'value':{'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_bawh_satu,'lbr_dua' : tgng,'lbr_tiga' : flap_bawh}}
        elif mbn.name == "B4":
            typ_flute = ""
            pnj_satu_satu = ""
            lebb = ""
            pnj_duak = ""
            leeb = ""
            flap_bawh = ""
            if mvx.type_flute == '0':
                typ_flute = 30
            else:
                typ_flute = 50
            if mvx.name == "A":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 2
                flap_bawh = (lbv * 0.5) + 4
                flap_pnj = (pnj_satu * 0.5) + 4
                tgng = float(pd_bsr.ukur_tinggi) 
            elif mvx.name == "B":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 2
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 3
                pnj_duak = pnj_satu + 3
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 2
                flap_pnj = (pnj_satu * 0.5) + 2
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "C":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 4
                pnj_duak = pnj_satu + 4
                leeb = lbv + 1
                flap_bawh = (lbv * 0.5) + 3
                flap_pnj = (pnj_satu * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "E":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 1
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 2
                pnj_duak = pnj_satu + 2
                leeb = lbv + 0
                flap_bawh = (lbv * 0.5) + 1
                flap_pnj = (pnj_satu * 0.5) + 1
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "AB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 7
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 10
                pnj_duak = pnj_satu + 8
                leeb = lbv + 5
                flap_bawh = (lbv * 0.5) + 6
                flap_pnj = (pnj_satu * 0.5) + 6
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "BC":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 5
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 7
                pnj_duak = pnj_satu + 6
                leeb = lbv + 4
                flap_bawh = (lbv * 0.5) + 5
                flap_pnj = (pnj_satu * 0.5) + 5
                tgng = float(pd_bsr.ukur_tinggi)
            elif mvx.name == "EB":
                pnj_satu = float(pd_bsr.ukur_panjang)
                pnj_satu_satu = pnj_satu + 3
                lbv = float(pd_bsr.ukur_lebar)
                lebb = lbv + 5
                pnj_duak = pnj_satu + 4
                leeb = lbv + 3
                flap_bawh = (lbv * 0.5) + 3
                flap_pnj = (pnj_satu * 0.5) + 3
                tgng = float(pd_bsr.ukur_tinggi)
            self.write(cr, uid ,ids, {'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_pnj,'lbr_dua' : tgng,'lbr_tiga' : flap_bawh}, context=context)        
            return {'value':{'pnjg_satu' : typ_flute,'pnjg_dua':pnj_satu_satu,'pnjg_tiga': lebb,'pnjg_empat' : pnj_duak,'pnjg_lima' : leeb,'lbr_satu' : flap_pnj,'lbr_dua' : tgng,'lbr_tiga' : flap_bawh}}
        else:
            print ":)"
        return True
               
product_product()
class product_printing_line(osv.osv):
    _name = "product.printing.line"
    _columns = {
                 'print_id'     : fields.many2one('product.product', 'Printing Refernce', required=True, ondelete='cascade', select=True),
                 'mesin_woc'    : fields.many2one('mrp.workcenter','No Mesin'),
                 'tinta_satu'   : fields.char('Tinta I'),
                 'tinta_dua'    : fields.char('Tinta II'),
                 'tinta_tiga'   : fields.char('Tinta III'),
                 'tinta_empat'  : fields.char('Tinta IV'),
                 'no_klise'     : fields.char('No Klise'),  
                }
product_printing_line()
class product_master_penting(osv.osv):
    _name = "product.master.penting"
    _columns = {
                    'mpnt_id'       : fields.many2one('product.product', 'Penting Reference', required=True, ondelete='cascade',select=True),
                    'master_pnt'    : fields.many2one('model.master.penting', 'Master Penting'),
                }
product_master_penting()
class product_flute_acl(osv.osv):
    _name  = "product.flute.acl"
    _decription = "master of flute product"
    _columns = {
                    'name'          : fields.char('Flute Kind', size=200),
                    'flute_line'    : fields.one2many('product.flute.line', 'flute_id', 'Float Lines'),
                    'flute_value'   : fields.float('Flute Value'),
                    'type_flute'    : fields.selection([
                                                        ('0','Single'),
                                                        ('1','Double')
                                                        ],'Type Of Flute'),
                    'description'   : fields.text('Note'),
                }
    _defaults = {
                    'type_flute' : '0',
                 }
product_flute_acl()
class product_flute_line(osv.osv):
    _name = "product.flute.line"
    _description = "Master float line"
    _columns = {
                    'flute_id'          : fields.many2one('product.flute.acl', 'Flute Reference', required=True, ondelete='cascade', select=True),
                    'panjang_satu'      : fields.float('Panjang Satu'),
                    'panjang_dua'       : fields.float('Panjang Dua'),
                    'flap_atas_satu'    : fields.float('Flap atas Satu'),
                    'flap_atas_dua'     : fields.float('Flap atas Dua'),
                    'flap_bawah_satu'   : fields.float('Flap bawah Satu'),
                    'flap_bawah_dua'    : fields.float('Flap bawah Dua'),
                    'lebar_satu'        : fields.float('Lebar Satu'),
                    'lebar_dua'         : fields.float('Lebar Dua'),
                }
product_flute_line()    
class product_kip_padd(osv.osv):
    _name = "product.kip.padd"
    _descrription = "configuration number KIP"
    _columns = {
                    'padding_kip' : fields.integer('Padding'),
                }
product_kip_padd()
class product_kip_child(osv.osv):
    _name  = "product.kip.child"
    _description = "configuration child kip"
    _columns = {
                    'number' : fields.integer('Number Childs'),
                    'alias'  : fields.char('Alias Number'),
                }
product_kip_child()
class product_pulled_flow(osv.osv):
    _inherit = 'product.pulled.flow'
    _defaults = {
        'procure_method': 'make_to_order',
    }
product_pulled_flow()         
class product_template(osv.osv):
    _inherit = 'product.template'
    _defaults = {
        'procure_method': 'make_to_order',
        'supply_method': 'produce',
    }
product_template()
    
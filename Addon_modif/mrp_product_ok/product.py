'''
Created on 8 Apr 2015

@author: innotek
'''
from openerp import addons
import logging
from openerp.osv import fields, osv
from openerp.tools.translate import _
from openerp import tools
import math

class product_product(osv.osv):
    _inherit = "product.product"
    
    _columns = {
                'product_mrp_img_ids' : fields.one2many('product.mrp.img', 'product_id', 'Gambar Produksi'),
                'cusm_id' : fields.many2one('res.partner', String="Customer Name", domain="[('ref','!=',False)]"),
                }
    
    def create(self, cr, uid, vals, context=None):
        step1 = self.pool['res.groups'].search(cr, uid, [('full_name', 'like', 'Product Create (Force)')])
        step2 = self.pool['res.groups'].read(cr, uid, step1)[0]['users']
        
        if uid in step2:
            return osv.Model.create(self, cr, uid, vals, context=context)
            # raise osv.except_osv(_('Perhatian!'), _('Product Create (Force) telah berhasil dilakukan'))
            # return 0
        else:
            return super(product_product, self).create(cr, uid, vals, context=context)
    
product_product

class res_partner(osv.osv):
    _inherit = 'res.partner'
    
    _columns = {
                'sp_product_ids' : fields.one2many('product.product','cusm_id','Produk'),
                }
    
res_partner

class product_mrp_img(osv.osv):
    _name = 'product.mrp.img'
    _description = 'Gambar Produksi'
    
    _columns = {
                'product_id' : fields.many2one('product.product', 'Produk'),
                'name' : fields.char('Short Description', required=True),
                'image' : fields.binary('Gambar', filters='*.jpg,*.png'),
                }
    
product_mrp_img

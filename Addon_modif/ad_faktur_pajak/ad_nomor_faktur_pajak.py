from osv import osv, fields
from openerp.tools.translate import _

class nomor_faktur_pajak(osv.osv):
    
    _name = 'nomor.faktur.pajak'
    _description = 'Nomor faktur Pajak'

    def _nomor_faktur(self, cr, uid, ids, nomorfaktur, arg, context=None):
        res = {}
        for nomor in self.browse(cr, uid, ids, context):    
            res[nomor.id] = "%s.%s.%s" % (nomor.nomor_perusahaan, nomor.tahun_penerbit, nomor.nomor_urut)
        return res
    
    _columns = {
        'nomor_perusahaan' : fields.char('Nomor Perusahaan', size=3),
        'tahun_penerbit': fields.char('Tahun Penerbit', size=2),
        'nomor_urut': fields.char('Nomor Urut', size=8),
        'name': fields.function(_nomor_faktur, type='char', string="Nomor Faktur", store=True),
        'status': fields.selection([('1','Used'),('0','Not Used')],'Status'),
        'account_invoice_ids': fields.one2many('account.invoice', 'nomor_faktur_id', string='Account Invoice'),
    }
    
    _defaults = {
        'status': '0',
    }
nomor_faktur_pajak()


class generate_faktur_pajak(osv.osv_memory):
    _name = 'generate.faktur.pajak'
    
    def generate_faktur(self, cr, uid, ids, context=None):
        if not context: context={}
        wizard = self.browse(cr, uid, ids[0], context)
        while (wizard.nomor_awal <= wizard.nomor_akhir):
            nomor = ''
            if (len(str(wizard.nomor_awal)) == 8):
                nomor = str(wizard.nomor_awal)
            elif (len(str(wizard.nomor_awal)) == 7):
                nomor = '0'+str(wizard.nomor_awal)
            elif (len(str(wizard.nomor_awal)) == 6):
                nomor = '00'+str(wizard.nomor_awal)
            value = {
                'nomor_perusahaan': wizard.nomor_perusahaan,
                'tahun_penerbit': wizard.tahun,
                'nomor_urut': nomor,
                'status': '0',
            }
            self.pool.get('nomor.faktur.pajak').create(cr,uid,value,context=context)
            wizard.nomor_awal += 1
        return {'type': 'ir.actions.act_window_close'}
    
    def onchange_nomor_faktur(self, cr, uid, ids, akhir, context=None):
        res = {}
        wizard = self.browse(cr, uid, ids[0], context)
        if akhir <= wizard.nomor_awal:
            warning = {
                'title': _('Warning'),
                'message': _('Wrong Format must 15 digit'),
            }
            return {'warning': warning, 'value' : {'nomor_akhir' : False}}
        return res
    
    _columns = {
                'nomor_perusahaan' : fields.char('Nomor Perusahaan', size=3, required=True),
                'nomor_awal' : fields.integer('Nomor Awal', size=8, required=True),
                'nomor_akhir' : fields.integer('Nomor Akhir', size=8, required=True),
                'tahun' : fields.char('Tahun Penerbit', size=2,  required=True),
                }
    
generate_faktur_pajak()
from osv import osv, fields
from tools.translate import _

class res_partner(osv.osv):
    _inherit = 'res.partner'
    _description = 'res partner'
    
    def onchange_npwp(self, cr, uid, ids, npwp, context=None):
        res = {}
        vals = {}
        if npwp == False:
            return res
        elif len(npwp)==20:
            return {"value":npwp}
        elif len(npwp)==15:
            formatted_npwp = npwp[:2]+'.'+npwp[2:5]+'.'+npwp[5:8]+'.'+npwp[8:9]+'-'+npwp[9:12]+'.'+npwp[12:15]
            vals={
                  "npwp" : formatted_npwp
            }
            return {"value":vals}
        else:
            warning = {
                'title': _('Warning'),
                'message': _('Wrong Format must 15 digit'),
            }
            return {'warning': warning, 'value' : {'npwp' : False}}
        return res
    
    
    _columns = {
        'ktp': fields.char('KTP', size=128),
        'npwp': fields.char('NPWP', size=128),
        'kawasan': fields.selection([('yes','YES'),('no','NO')], 'Kawasan', help=''),
        'pemegang_siupal': fields.selection([('yes','YES'),('no','NO')], 'Pemegang SIUPAL', help=''),
        'trade': fields.selection([('trade','Trade'),('non_trade','Non Trade')], 'Trade', help=''),
        'property_account_payable_usd': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Payable USD",
            view_load=True,
            domain="[('type', '=', 'payable')]",
            help="This account will be used instead of the default one as the payable account for the current partner",
            required=True),
        'property_account_receivable_usd': fields.property(
            'account.account',
            type='many2one',
            relation='account.account',
            string="Account Receivable USD",
            view_load=True,
            domain="[('type', '=', 'receivable')]",
            help="This account will be used instead of the default one as the receivable account for the current partner",
            required=True),
        'kode_transaksi': fields.char('kode transaksi', size=2),
        'kode_status': fields.char('kode status', size=1),
    }
res_partner()

class res_company(osv.osv):
    _inherit = 'res.company'
    _description = 'res.company'
    
    _columns = {
        'kode_transaksi': fields.char('kode transaksi', size=2),
        'kode_status': fields.char('kode status', size=1),
        'kode_cabang': fields.char('kode cabang', size=3),
    }
res_company()
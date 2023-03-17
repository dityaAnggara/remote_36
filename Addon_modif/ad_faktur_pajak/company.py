import netsvc
from osv import fields, osv

class company(osv.osv):
    _inherit = "res.company"
    _columns = {
        'npwp':fields.char('NPWP',size=64),
        }
company()
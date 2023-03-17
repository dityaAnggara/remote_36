'''
Created on Apr 2, 2015

@author: niswa
'''
from openerp.report import report_sxw


class ijin(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        
        super(ijin, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'cr':cr,
                'uid': uid,
                'id_in' : self._id_in,
                'isi_id' : self._isi_id,
                'id_in_sa' : self._id_in_sa,
                'isi_sa' : self._isi_sa,
            })

    def _id_in_sa(self, nama):
        return self.pool.get('config_absen.empat_absen').search(self.cr, self.uid, [('empat_id.name','=', nama)])
    
    def _isi_sa(self, ida):
        return self.pool.get('config_absen.empat_absen').browse(self.cr, self.uid, ida)
    
    def _id_in(self, nama):
        return self.pool.get('hr.holidays').search(self.cr, self.uid, [('employee_id.name','=', nama),('type','=','remove')])
    
    def _isi_id(self, ida):
        return self.pool.get('hr.holidays').browse(self.cr, self.uid, ida)
        
report_sxw.report_sxw('report.absen_inno_2', 'config_absen.lima_absen', 'config_absen/Kehadiran.html', parser=ijin)


class ijin2(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        print "Context",context
        
        super(ijin2, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
                'cr':cr,
                'uid': uid,
                'id_in_sa' : self._id_in_sa,
                'isi_sa' : self._isi_sa,
            })

    def _id_in_sa(self, nama):
        return self.pool.get('config_absen.empat_absen').search(self.cr, self.uid, [('empat_id.name','=', nama)])
    
    def _isi_sa(self, ida):
        return self.pool.get('config_absen.empat_absen').browse(self.cr, self.uid, ida)
        
report_sxw.report_sxw('report.absen_inno_3', 'config_absen.lima_absen', 'config_absen/abs.html', parser=ijin2)

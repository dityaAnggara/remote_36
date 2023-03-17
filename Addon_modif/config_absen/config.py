'''
Created on Feb 23, 2015

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

import time
from lxml import etree
import openerp.addons.decimal_precision as dp
import openerp.exceptions
import roman
from openerp import netsvc
from openerp import pooler
from openerp.osv import fields, osv, orm
from openerp.tools.translate import _
import socket             
import os
from lxml import etree
import xml.dom.minidom
from decimal import Decimal
import datetime 
import time
from io import StringIO, BytesIO
from xml.etree.ElementTree import ElementTree
from xml.etree.ElementTree import Element 
import xml.etree.ElementTree as etree

class satu_absen(osv.osv):
    _name = "config_absen.satu_absen"
    _columns = {
                    'id' : fields.integer('ID'),
                    'name': fields.char('Name'),
                    'absen_line' : fields.one2many('config_absen.empat_absen','empat_id','Absen Lines'),
                    #'absen_line_satu' : fields.one2many('config_absen.lima_absen', 'lima_id', 'Absen Lines'),
                }
satu_absen()    

class dua_absen(osv.osv_memory):
    _name = "config_absen.dua_absen"
    _columns = {
                    'field_waste' : fields.char('Bla Bla'),
                }
    def tarikk(self, cr, uid, ids, context=None):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         
        host = '192.168.2.20' 
        port = 80
        s.connect((host, port))
        if s:
            sop_buntut = "<GetAttLog><ArgComKey xsi:type=\'xsd:integer\'>0</ArgComKey><Arg><PIN xsi:type=\'xsd:integer\'>all</PIN></Arg></GetAttLog>" 
            len_ne = "\r\n"
            berhenti = "berhenti"
            panjang_sop = len(sop_buntut)
            acr = "POST /iWsService HTTP/1.0"+len_ne    
            s.sendall(acr)
            acr_satu = "Content-Type: text/xml"+len_ne
            s.sendall(acr_satu)
            acr_dua = "Content-Length: "+str(panjang_sop)+len_ne+len_ne
            s.sendall(acr_dua)
            acr_tiga = sop_buntut    
            s.sendall(acr_tiga)    
            # data = s.recv()
                
            #lui = s.accept()
            buf = ""
            Response=True
            while Response:
                Response=s.recv(1024)
                buf += Response
        else:
            print "unconnect"
        def test_parser(a,b,c):
            a = " "+a
            rst = ""
            begn = a.find(b)
            begn = begn+19
            if begn != "":
                endd = a.find(c)
                if endd != "":
                    rst = a[begn:endd]
            return rst
        def test_parser_satu(a,b,c):
            a = " "+a
            rst = ""
            begn = a.find(b)
            begn = begn+5
            if begn != "":
                endd = a.find(c)
                if endd != "":
                    rst = a[begn:endd]
            return rst
        def test_parser_dua(a,b,c):
            a = " "+a
            rst = ""
            begn = a.find(b)
            begn = begn+10
            if begn != "":
                endd = a.find(c)
                if endd != "":
                    rst = a[begn:endd]
            return rst
        def test_parser_tiga(a,b,c):
            a = " "+a
            rst = ""
            begn = a.find(b)
            begn = begn+8
            if begn != "":
                endd = a.find(c)
                if endd != "":
                    rst = a[begn:endd]
            return rst
        buf =  test_parser(buf,"<GetAttLogResponse>","</GetAttLogResponse>")
        
        cnt = buf.count("<Row>")
        cnt = cnt + 1
        buf = buf.split("\r\n")
        #cr.execute("DELETE FROM config_absen_empat_absen")
        for oi in range(1,cnt):
            bulu = test_parser_satu(buf[oi],"<Row>","</Row>")
            bulu_satu = test_parser_satu(bulu,"<PIN>","</PIN>");
            bulu_dua = test_parser_dua(bulu,"<DateTime>","</DateTime>")
            bulu_tiga = test_parser_dua(bulu,"<Verified>","</Verified>")
            bulu_empat = test_parser_tiga(bulu,"<Status>","</Status>")
            dtm_pisa = bulu_dua.split(" ")
            con_at = datetime.datetime.strptime(bulu_dua, "%Y-%m-%d %H:%M:%S")
            plus_dat = con_at - datetime.timedelta(hours=7)
            cr.execute("SELECT COUNT(date_ab) FROM config_absen_empat_absen WHERE date_ab = %s",(plus_dat,))
            ty_cont = cr.fetchone()[0]
            if ty_cont < 1:
            #raise osv.except_osv(_('Warning'),_(ty_cont))
                cr.execute("INSERT INTO config_absen_empat_absen(empat_id,status,date_ab) VALUES(%s,%s,%s)",(bulu_satu,bulu_empat,plus_dat))
        return s.close()
dua_absen()

class tiga_absen(osv.osv_memory):
    _name = "config_absen.tiga_absen"
    _columns = {
                    'dat_car' : fields.date('Date'),
                }
    def count_jamker(self, cr, uid, ids, context=None):
        kj = self.browse(cr, uid, ids, context)[0]
        apnd_jam_test = []
        
        cr.execute("SELECT COUNT(id) FROM config_absen_satu_absen")
        hit_jam= cr.fetchone()[0]
        hit_jam_plus = hit_jam + 1
        conn_dat = datetime.datetime.strptime(kj.dat_car+" 00:00:00","%Y-%m-%d %H:%M:%S")
        plus_x = conn_dat - datetime.timedelta(hours=7)
        conn_dat_sat =  datetime.datetime.strptime(kj.dat_car+" 23:59:59","%Y-%m-%d %H:%M:%S")
        
        
        
        for oxz in range(1,hit_jam_plus):
            
            #print cr.execute("SELECT MIN(date_ab) FROM config_absen_empat_absen WHERE date_ab LIKE %s",(kj.dat_car+'%',))
            cr.execute("SELECT MIN(date_ab) FROM config_absen_empat_absen WHERE status = %s AND empat_id = %s AND date_ab BETWEEN %s AND %s ",('0',oxz,plus_x,conn_dat_sat))
            lopix = cr.fetchone()[0]
            cr.execute("SELECT MAX(date_ab) FROM config_absen_empat_absen WHERE status = %s AND empat_id = %s AND date_ab BETWEEN %s AND %s ",('1',oxz,conn_dat,conn_dat_sat))
            lopix_satu = cr.fetchone()[0]
        
            vert_satu = ""
            vert_dua = ""
            min_vert = ""
            try:
                if lopix == None:
                    vert_satu = datetime.datetime.strptime("1111-11-11 00:00:00","%Y-%m-%d %H:%M:%S")
                    vert_dua  = datetime.datetime.strptime(lopix_satu,"%Y-%m-%d %H:%M:%S")
                    min_vert = "-1"
                elif lopix_satu == None:
                    vert_satu = datetime.datetime.strptime(lopix,"%Y-%m-%d %H:%M:%S")
                    vert_dua = datetime.datetime.strptime("1111-11-11 00:00:00","%Y-%m-%d %H:%M:%S")
                    min_vert = "-2"
                else:
                    vert_satu = datetime.datetime.strptime(lopix,"%Y-%m-%d %H:%M:%S")
                    vert_dua  = datetime.datetime.strptime(lopix_satu,"%Y-%m-%d %H:%M:%S")
                    min_vert = vert_dua - vert_satu
                cr.execute("INSERT INTO config_absen_lima_absen(lima_id,tanggal_date,jam_masuk,jam_pulang,jumlah_jam) VALUES(%s,%s,%s,%s,%s)",(oxz,kj.dat_car,vert_satu,vert_dua,min_vert))           
            except:
                print ":)"        
             
tiga_absen()

class empat_absen(osv.osv):
    _name = "config_absen.empat_absen"
    _columns = {
                    'empat_id' : fields.many2one('config_absen.satu_absen', 'Name'),
                    'status' : fields.selection([
                                                 ('0','Masuk'),
                                                 ('1','Pulang'),
                                                 ('2','Keluar'),
                                                 ('3','Kembali'),
                                                 ('4','Lembur mulai'),
                                                 ('5','Lembur selesai'),
                                                 ],'Status'),
                    'date_ab' : fields.datetime('Date'),
                    #'time_ab' : fields.char('Time'),
                    
                }
    _order = "date_ab desc"
empat_absen()

class lima_absen(osv.osv):
    _name = "config_absen.lima_absen"
    _columns = {
                    'lima_id' : fields.many2one('config_absen.satu_absen', 'Name'),
                    'tanggal_date' : fields.date('Tanggal'),
                    'jam_masuk' : fields.datetime('Jam Masuk'),
                    'jam_pulang' : fields.datetime('Jam Pulang'),
                    'jumlah_jam' : fields.char('Jumlah Jam kerja'),
                    'absen_masuk': fields.integer('absen masuk'),
                    'absen_pulang': fields.integer('absen pulang'),
                    
                }
lima_absen()
# -*- encoding: utf-8 -*-
##############################################################################
#    
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2009 Tiny SPRL (<http://tiny.be>).
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
from osv import fields, osv
import locale
import logging
import xmlrpclib
import time

_logger = logging.getLogger(__name__)

class DefaultConfig(object):
    APPS_SERVER = 'http://localhost:8069'
    APPS_USERNAME = 'iman@adsoft.co.id'
    APPS_PWD = 'a'
    APPS_DBNAME = 'proj80_saasmaster'
    URL_COMMON ='%s/xmlrpc/common' %(APPS_SERVER)
    URL_OBJECT ='%s/xmlrpc/object' %(APPS_SERVER)

config = DefaultConfig()

def openerp_connect():
    """
    Connect to the OpenERP API.
    """
    sock_common = xmlrpclib.ServerProxy(config.URL_COMMON)
    uid = sock_common.login(config.APPS_DBNAME, config.APPS_USERNAME, config.APPS_PWD)
    return uid

def sock_object_execute(resource_path, action_name, *args, **kwargs):
    """
    Define sock_object
    """    
    sock_object = xmlrpclib.ServerProxy(config.URL_OBJECT)
    sock_object_execute = sock_object.execute(config.APPS_DBNAME, openerp_connect(), config.APPS_PWD, resource_path, action_name, *args, **kwargs)
    return sock_object_execute

def get_translate_from_saasmaster(src=False):
    kamus_ids = sock_object_execute('kamus.openerp', 'search', [('src','=',src)],{})
    kamus_list = sock_object_execute('kamus.openerp', 'read', kamus_ids, ['value'])
    for val in kamus_list:
        return val['value']
    return False

class ir_translation(osv.osv):
    _inherit = "ir.translation"
    _description = 'ir.translation'
    _columns = {
        'need_review': fields.boolean('Need review', help="If terms need to review"),
    }
    _default = {
    }

    def synch_to_kamus_master(self, cr, uid, lang=False, update_all=False, context=None):
        
        if not lang:
            return True
        
        start_time = time.time()
        _logger.info('Synchronizing translation started ...')
        if update_all:
            _logger.warning('Synchronize all terms, will take longer time.')
            trans_ids = self.search(cr,uid,[],context=context)
        else:
            trans_ids = self.search(cr,uid,[('state','=','to_translate')],context=context)
            
        n=0
        for trans in self.browse(cr, uid, trans_ids, context=context):
            n+=1
            res = get_translate_from_saasmaster(trans.src)
            if res:
                t = res
                self.write(cr, uid, trans.id, {'value':t,'state':'translated','need_review':True})

        _logger.info('Cron: Translation process was done in %s seconds!' % (locale.format("%.2f", time.time()-start_time, grouping=True)))
        return True

    def confirm(self, cr, uid, ids=None, context=None):
        self.write(cr, uid, ids[0], {'state':'inprogress','need_review':True})
    
    def reset_to_draft(self, cr, uid, ids=None, context=None):
        self.write(cr, uid, ids[0], {'state':'to_translate','need_review':True})
        
    def approve_translate(self, cr, uid, ids=None, context=None):
        self.write(cr, uid, ids[0], {'state':'translated','need_review':False})

        
    
    '''
    def process_translate(self, cr, uid, ids=None, context=None):
        if context is None:
            context = {}

        start_time = time.time()
        _logger.info('Cron: Translation is starting ...')
        
        def get_translate_from_saasmaster(src=False):
            kamus_ids = sock_object_execute('kamus.openerp', 'search', [('src','=',src)],{})
            kamus_list = sock_object_execute('kamus.openerp', 'read', kamus_ids, ['value'])
            for val in kamus_list:
                return val['value']
            return False

        n=0
        trans_ids = self.search(cr,uid,[('state','=','to_translate')],context=context)
        for trans in self.browse(cr, uid, trans_ids, context=context):
            s = trans.src
            t = False
            if trans.lang == 'en_US':
                _logger.info("Delete English to English translation ...")
                self.unlink(cr, uid, trans.id, context=context)
            if trans.lang == 'id_ID':
                n+=1
                print n
                for x in not2translate:
                    if x in s:
                        break

                res = get_translate_from_saasmaster(trans.src)
                if res:
                    t = res
                
                self.write(cr, uid, trans.id, {'value':t,'state':'translated','need_review':True})
        
        _logger.info('Cron: Translation process was done in %s seconds!' % (locale.format("%.2f", time.time()-start_time, grouping=True)))
        return True
        '''
        
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
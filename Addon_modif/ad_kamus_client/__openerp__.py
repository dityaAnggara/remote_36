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

{
    "name" : "Kamus Client",
    "version": "1.0",
    "author" : "ADSOFT",
    "website" : "http://adsoft.co.id",
    "category" : "Generic Modules/Others",
    "depends" : ["base"],
    "description": '''This module will synchronize Bahasa Indonesia terms to Kamus Master''',
    "init_xml" : [
    ],
    "data": [
        "wizard/base_update_translations_view.xml",
        "kamus_client_view.xml", 
    ],
    'css': [
        #'static/src/css/style.css',
    ],
    "active": False,
    "installable": True
}
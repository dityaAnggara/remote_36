# -*- coding: utf-8 -*-
##############################################################################
#
#    Author: Stanislav Silnitskiy <user@mailgate.us>
#    Copyright (C) Stanislav Silnitskiy
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
        "name" : "Partners Geo-Localization Map",
        "version" : "1.0",
        "author" : "Stanislav Silnitskiy <user@mailgate.us>",
        "website" : "",
        "category" : "Customer Relationship Management",
        "description": """
The module places a Google Map widget within Geo Localization tab, brought by Partners Geo-Localization module.
It also automates geo localization of newly created partners.
""",
        "depends" : ["crm_partner_assign", "web"],
        "update_xml" : ["view.xml"],
        "installable": True,
        'js' : ["static/src/js/location_map.js"],
        'css' : [],
        'qweb' : ['static/src/xml/*.xml'],
        "active": True,
        "application": True,
        "web": True,
} 


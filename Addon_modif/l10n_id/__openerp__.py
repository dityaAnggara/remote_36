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
{
    'name': 'Indonesia - Chart of accounts Details',
    'version': '1.1',
    'author': 'ADSOFT',
    'category': 'Localization/Account Charts',
    'description': """
Indonesia - Chart of accounts.
==================================
    """,
    'website': 'http://www.adsoft.co.id',
    'depends': ['account_chart'],
    'data': [
        'l10n_id_account_type.xml',
        'account_chart_template.xml',
        'account.account.template.csv',
        "data/template_accounting/account.account.template.csv",
        "data/template_advertising/account.account.template.csv",
        "data/template_agriculture/account.account.template.csv",
        "data/template_art/account.account.template.csv",
        "data/template_automotive/account.account.template.csv",
        "data/template_construction_general/account.account.template.csv",
        "data/template_construction_trade/account.account.template.csv",
        "data/template_design/account.account.template.csv",
        "data/template_estatebroker/account.account.template.csv",
        "data/template_financial_service/account.account.template.csv",
        "data/template_general_product/account.account.template.csv",
        "data/template_general_service/account.account.template.csv",
        "data/template_hairorbeautyshop/account.account.template.csv",
        "data/template_healthservice/account.account.template.csv",
        "data/template_insuranceagency/account.account.template.csv",
        "data/template_itcomputerssoftware/account.account.template.csv",
        "data/template_landscaping/account.account.template.csv",
        "data/template_legal_service/account.account.template.csv",
        "data/template_lodging/account.account.template.csv",
        "data/template_maintenance/account.account.template.csv",
        "data/template_manufacturer/account.account.template.csv",
        "data/template_manufacturing/account.account.template.csv",
        "data/template_nonprofitorganizations/account.account.template.csv",
        "data/template_other/account.account.template.csv",
        "data/template_professional/account.account.template.csv",
        "data/template_propertymanagement/account.account.template.csv",
        "data/template_religiousorganization/account.account.template.csv",
        "data/template_rental/account.account.template.csv",
        "data/template_restaurant/account.account.template.csv",
        "data/template_retailshop/account.account.template.csv",
        "data/template_salesindependent/account.account.template.csv",
        "data/template_transport/account.account.template.csv",
        "data/template_wholesalesdistribution/account.account.template.csv",
        'account_tax_code_template.xml',
        'account_tax_template.xml',
        'account_chart_template_after.xml',
        'l10n_id_wizard.xml'
    ],
    'demo': [],
    'test': [],
    'installable': True,
    'auto_install': False,
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:

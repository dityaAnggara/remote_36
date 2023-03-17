{
    "name": "ADSOFT",
    "version": "1.0",
    "depends": ["sale","report_webkit","account","base"],
    "author": "Adsoft",
    "category": "Custom",
    "description": """
    This module provide :
    Create Purchase Order Form
    
    Added :
        - Blank Line
    
    Wekit Setting:
        - /usr/local/bin/wkhtmltopdf
    """,
    "init_xml": [],
    'update_xml': [
                   "report/faktur_pajak.xml",
                   'partner_view.xml',
                   "company_view.xml",
                   "ad_nomor_faktur_pajak_view.xml",
                   "account_invoice_view.xml",
                   "wizard_generate.xml",                  
                   ],
    'demo_xml': [],
    'installable': True,
    'active': False,
#    'certificate': 'certificate',
}
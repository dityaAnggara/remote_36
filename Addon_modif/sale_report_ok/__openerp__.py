{
    'name' : 'Sale Report ACL',
    'version' : '1.0',
    'depends' : [
                 'base',
                 'account_invoice_form_acl',
                 'purchase_requisition_acl',
                 'sale_acl_v3',
                 'stock_acl_v2',
                 'security_timbang_v3',
                 'menu_timbangan',
                 ],
    'author' : 'Innotek',
    'category' : 'account',
    'description' : 'Account Report ACL',
    'data' : [
              'report/sale_report.xml',
              ],
    'demo' : [],
    'update_xml' : [],
    'installable' : True,
    'auto_install' : False,
}
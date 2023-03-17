{
    'name' : 'Account Report ACL',
    'version' : '1.0',
    'depends' : [
                 'account',
                 'document_ftp',
                 'account_cash_register_webkit',
                 'purchase_requisition_acl',
                 ],
    'author' : 'Innotek',
    'category' : 'account',
    'description' : 'Account Report ACL',
    'data' : [
              'view/ac_acl.xml',
              'report/report_acl.xml',
              ],
    'demo' : [],
    'update_xml' : [],
    'installable' : True,
    'auto_install' : False,
}
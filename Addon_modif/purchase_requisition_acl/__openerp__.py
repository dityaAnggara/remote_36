{
    "name": "Purchase Requisition ACL",
    "version": "1.0",
    "depends": [
                "base",
                "purchase",
                "purchase_requisition",
                "account_accountant",
                "account_asset",
                "account_payment",
                "report_webkit",
                "stock",
                "mrp",
                "hr",
                # "stock_acl_v2",
                # "product_acl_v2",
                # "product_visible_discount",
                "mrp_acl_v3",
                "account_invoice_form_acl",
                "account_master_materai",
                "account_setting_acl",
                "automate_kip",
                "button_add_oppr",
                "costing_security",
                "costing_acl_v3",
                "customer_acl_v2",
                "stock_acl_v2",
                "product_acl_v2",
                "generate_kip_child",
                # "sale_acl_v3",
                # "sale_add_acl",
                # "sale_team_acl",
                "sj_conf",
                "acl_crm_lead",
                "acl_rekap_quotation",
                ],
    "author": "Innotek",
    "category": "purchase",
    "description": """\
        Purchase Requisition ACL
    """,
    "data": [
             "security/pr_sby_security.xml",
             "view/pr_acl2.xml",
             "view/pr_acl_type.xml",
             "report/pr_template.xml",
             "report/pr_comparison.xml",
             "report/pr_partner.xml",
             "report/pr_po.xml",
             "report/pr_tpb.xml",
             'security/ir.model.access.csv',
             # "view/pr_sby.xml",
             # "view/pr_acl_partner.xml",
             # "control/purchase_acl_workflow.xml"
             ],
    "demo": [],
    "test": [],
    # "update_xml": ['security/ir.model.access.csv'],
    "installable": True,
    "auto_install": False,
}
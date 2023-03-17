# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
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

from openerp.addons.base_status.base_stage import base_stage
import crm
from datetime import datetime
from operator import itemgetter
from openerp.osv import fields, osv, orm
import time
from openerp import SUPERUSER_ID
from openerp import tools
from openerp.tools.translate import _
from openerp.tools import html2plaintext
import re
from openerp.osv import fields, osv
from openerp.tools.translate import _

from base.res.res_partner import format_address


class crm_lead(base_stage, format_address, osv.osv):
    _inherit = "crm.lead"
    _description = "test lead"
    _columns = {
                    'visit_date'    : fields.datetime('Visit Date', required=True),
                    'user_id'       : fields.many2one('res.users', 'Salesperson', domain = "[('code_for_sale','>',0)]", select=True, track_visibility='onchange', required=True),
                    'state_2'       : fields.boolean('State Two'),
                    'abj_id'        : fields.many2one('customer_acl_v2.abj', 'Abjad'),
                    'ref_lead'      : fields.char('Reference/Code'),
                    'section_id': fields.many2one('crm.case.section', 'Sales Team',
                        select=True, track_visibility='onchange', help='When sending mails, the default email address is taken from the sales team.'), 
                }
    _defaults = {
                    'section_id' : 1,
                    'user_id': '',
                    'state_2'    : False, 
                 }
    def convert_opportunity(self, cr, uid, ids, partner_id, user_ids=False, section_id=False, context=None):
        
        customer = False
        if partner_id:
            partner = self.pool.get('res.partner')
            customer = partner.browse(cr, uid, partner_id, context=context)
        for lead in self.browse(cr, uid, ids, context=context):
            if lead.state in ('done', 'cancel'):
                continue
            vals = self._convert_opportunity_data(cr, uid, lead, customer, section_id, context=context)
            self.write(cr, uid, [lead.id], vals, context=context)
        self.message_post(cr, uid, ids, body=_("Lead <b>converted into an Opportunity</b>"), subtype="crm.mt_lead_convert_to_opportunity", context=context)

        if user_ids or section_id:
            self.allocate_salesman(cr, uid, ids, user_ids, section_id, context=context)

        return True
    def handle_partner_assignation(self, cr, uid, ids, action='create', partner_id=False, context=None):
        """
        Handle partner assignation during a lead conversion.
        if action is 'create', create new partner with contact and assign lead to new partner_id.
        otherwise assign lead to the specified partner_id

        :param list ids: leads/opportunities ids to process
        :param string action: what has to be done regarding partners (create it, assign an existing one, or nothing)
        :param int partner_id: partner to assign if any
        :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this is a duplication of the handle_partner_assignation method of crm_phonecall
        partner_ids = {}
        # If a partner_id is given, force this partner for all elements
        force_partner_id = partner_id
        for lead in self.browse(cr, uid, ids, context=context):
            # If the action is set to 'create' and no partner_id is set, create a new one
            if action == 'create':
                partner_id = force_partner_id or self._create_lead_partner(cr, uid, lead, context)
            self._lead_set_partner(cr, uid, lead, partner_id, context=context)
            partner_ids[lead.id] = partner_id
        return partner_ids
    def _create_lead_partner(self, cr, uid, lead, context=None):
        partner_id = False
        if lead.partner_name and lead.contact_name:
            partner_id = self._lead_create_contact(cr, uid, lead, lead.partner_name, True, context=context)
            partner_id = self._lead_create_contact(cr, uid, lead, lead.contact_name, False, partner_id, context=context)
        elif lead.partner_name and not lead.contact_name:
            partner_id = self._lead_create_contact(cr, uid, lead, lead.partner_name, True, context=context)
        elif not lead.partner_name and lead.contact_name:
            partner_id = self._lead_create_contact(cr, uid, lead, lead.contact_name, False, context=context)
        elif lead.email_from and self.pool.get('res.partner')._parse_partner_name(lead.email_from, context=context)[0]:
            contact_name = self.pool.get('res.partner')._parse_partner_name(lead.email_from, context=context)[0]
            partner_id = self._lead_create_contact(cr, uid, lead, contact_name, False, context=context)
        else:
            raise osv.except_osv(
                _('Warning!'),
                _('No customer name defined. Please fill one of the following fields: Company Name, Contact Name or Email ("Name <email@address>")')
            )
        return partner_id
    def _lead_create_contact(self, cr, uid, lead, name, is_company, parent_id=False, context=None):
        
        partner = self.pool.get('res.partner')
        vals = {'name': name,
            'user_id': lead.user_id.id,
            'comment': lead.description,
            'section_id': lead.section_id.id or False,
            'parent_id': parent_id,
            'phone': lead.phone,
            'mobile': lead.mobile,
            'email': tools.email_split(lead.email_from) and tools.email_split(lead.email_from)[0] or False,
            'fax': lead.fax,
            'title': lead.title and lead.title.id or False,
            'function': lead.function,
            'street': lead.street,
            'street2': lead.street2,
            'zip': lead.zip,
            'city': lead.city,
            'country_id': lead.country_id and lead.country_id.id or False,
            'state_id': lead.state_id and lead.state_id.id or False,
            'is_company': is_company,
            'type': 'contact',
            'abj_id' : lead.abj_id.id,
            'ref' : lead.ref_lead, 
        }
        partner = partner.create(cr, uid, vals, context=context)
        return partner
        
crm_lead()

class crm_partner_binding(osv.osv_memory):
    _inherit = "crm.partner.binding"
    
    def default_get(self, cr, uid, fields, context=None):
        res = super(crm_partner_binding, self).default_get(cr, uid, fields, context=context)
        partner_id = self._find_matching_partner(cr, uid, context=context)

        if 'action' in fields:
            res['action'] = partner_id and 'exist' or 'create'
        if 'partner_id' in fields:
            res['partner_id'] = partner_id
        

        return res
crm_partner_binding()

class crm_lead2opportunity_partner(osv.osv_memory):
    _inherit = "crm.lead2opportunity.partner"
    
    def def_id_abj(self, cr, uid, ids, context=None):
        tyu     = []
        ree = ""
        abj_obj = self.pool.get('customer_acl_v2.abj').search(cr, uid, [('name','=','A')])
        for uy in abj_obj:
            abj_brow = self.pool.get('customer_acl_v2.abj').browse(cr, uid, uy, context)
            ree = abj_brow.id
        #ree = int(tyu)
        return ree 
    
    _columns = {
                    'candidate_customer' : fields.char('Customer Name', readonly=True),
                    'abj_id' : fields.many2one('customer_acl_v2.abj', 'Abjad'),
                    'ref_lead'      : fields.char('Reference/Code'),
                    'last_incre_lead': fields.char('Last Increment'),
                    'email_customer' : fields.char('Email CUstomer'),
                    'leadd_id'        : fields.integer('lead id'),
                }
    _defaults = {
                    'abj_id' : def_id_abj,
                    
                 }
    
    def default_get(self, cr, uid, fields, context=None):
        """
        Default get for name, opportunity_ids.
        If there is an exisitng partner link to the lead, find all existing
        opportunities links with this partner to merge all information together
        """
        lead_obj = self.pool.get('crm.lead')

        res = super(crm_lead2opportunity_partner, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            tomerge = set([int(context['active_id'])])

            email = False
            partner_id = res.get('partner_id')
            lead = lead_obj.browse(cr, uid, int(context['active_id']), context=context)

            #TOFIX: use mail.mail_message.to_mail
            email = re.findall(r'([^ ,<@]+@[^> ,]+)', lead.email_from or '')

            if partner_id:
                # Search for opportunities that have the same partner and that arent done or cancelled
                ids = lead_obj.search(cr, uid, [('partner_id', '=', partner_id), ('state', '!=', 'done')])
                for id in ids:
                    tomerge.add(id)
            if email:
                ids = lead_obj.search(cr, uid, [('email_from', '=ilike', email[0]), ('state', '!=', 'done')])
                for id in ids:
                    tomerge.add(id)

            if 'action' in fields:
                res.update({'action' : partner_id and 'exist' or 'create'})
            if 'partner_id' in fields:
                res.update({'partner_id' : partner_id})
            if 'name' in fields:
                res.update({'name' : len(tomerge) >= 2 and 'merge' or 'convert'})
            if 'opportunity_ids' in fields and len(tomerge) >= 2:
                res.update({'opportunity_ids': list(tomerge)})
            if 'candidate_customer' in fields:
                res.update({'candidate_customer' : lead.partner_name})
            if 'email_customer' in fields:
                res.update({'email_customer': lead.email_from})
            if 'leadd_id' in fields:
                res.update({'leadd_id': lead.id})
                            

        return res
    def change_abjad(self, cr, uid, ids, abj_id, context=None):
        pol_obj_part = self.pool.get('customer_acl_v2.abj')
        pol_obj_browse = pol_obj_part.browse(cr, uid, abj_id, context=context) 
        pddi = ""
        a = ""
        pddi = pol_obj_browse.padd
        a = pol_obj_browse.last_incre
        
        gb = pol_obj_browse.name
        pdi = str(pddi)
        pdii= "%0"+pdi+"d"
        asl = 1
        b=pdii % (1)
        gub = gb+''+b
        
        if a != "":
            asl=int(a)+1
            b = int(a)+1
            b = pdii % (b)
            gub = gb+''+b
        return {'value':{'ref_lead' : gub, 'last_incre_lead' : a}}
    def _convert_opportunity(self, cr, uid, ids, vals, context=None):
        
        if context is None:
            context = {}
        lead = self.pool.get('crm.lead')
        res = False
        partner_ids_map = self._create_partner(cr, uid, ids, context=context)
        lead_ids = vals.get('lead_ids', [])
        team_id = vals.get('section_id', False)
        for lead_id in lead_ids:
            partner_id = partner_ids_map.get(lead_id, False)
            # FIXME: cannot pass user_ids as the salesman allocation only works in batch
            res = lead.convert_opportunity(cr, uid, [lead_id], partner_id, [], team_id, context=context)
        # FIXME: must perform salesman allocation in batch separately here
        user_ids = vals.get('user_ids', False)
        if user_ids:
            lead.allocate_salesman(cr, uid, lead_ids, user_ids, team_id=team_id, context=context)
        return res
    def action_apply(self, cr, uid, ids, context=None):
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        
        if context is None:
            context = {}

        w = self.browse(cr, uid, ids, context=context)[0]
        opp_ids = [o.id for o in w.opportunity_ids]
        if w.name == 'merge':
            lead_id = self.pool.get('crm.lead').merge_opportunity(cr, uid, opp_ids, context=context)
            lead_ids = [lead_id]
            lead = self.pool.get('crm.lead').read(cr, uid, lead_id, ['type'], context=context)
            if lead['type'] == "lead":
                context.update({'active_ids': lead_ids})
                self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)
        else:
            lead_ids = context.get('active_ids', [])
            
            cr.execute("UPDATE crm_lead SET abj_id = %s, ref_lead = %s, state_2 = %s WHERE id = %s",(w.abj_id.id, w.ref_lead, True, w.leadd_id))
            #cr.execute("SELECT last_incre FROM customer_acl_v2_abj WHERE id = %s",(w.abj_id.id,))
            #drtv = cr.fetchone()[0]
            gahar = self.pool.get('customer_acl_v2.abj').browse(cr, uid, w.abj_id.id, context)
            drtv = gahar.last_incre
            df = 1
            if drtv != "":
                df = int(drtv)+1
            cr.execute("UPDATE customer_acl_v2_abj SET last_incre = %s WHERE id = %s",(df, w.abj_id.id))
            self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)
            #raise osv.except_osv(_('move id'), _(lead_ids))
        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, lead_ids[0], context=context)
    '''   
    def action_apply(self, cr, uid, ids, vals, context=None):
        """
        Convert lead to opportunity or merge lead and opportunity and open
        the freshly created opportunity view.
        """
        abj_id = vals.get('abj_id')
        if context is None:
            context = {}

        w = self.browse(cr, uid, ids, context=context)[0]
        opp_ids = [o.id for o in w.opportunity_ids]
        if w.name == 'merge':
            lead_id = self.pool.get('crm.lead').merge_opportunity(cr, uid, opp_ids, context=context)
            lead_ids = [lead_id]
            lead = self.pool.get('crm.lead').read(cr, uid, lead_id, ['type'], context=context)
            if lead['type'] == "lead":
                context.update({'active_ids': lead_ids})
                self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)
            
        else:
            
            lead_ids = context.get('active_ids', [])
            #cr.execute("UPDATE crm_lead SET abj_id = %s, ref_lead = %s, state_2 = %s WHERE id = %s",(w.abj_id.id, w.ref_lead, True, w.leadd_id))
            #cr.execute("SELECT last_incre FROM customer_acl_v2_abj WHERE id = %s",(w.abj_id.id,))
            #drtv = cr.fetchone()[0]
            #drtv = 1
            #if drtv != "":
            #    drtv = int(drtv)+1
            #cr.execute("UPDATE customer_acl_v2_abj SET last_incre = %s WHERE id = %s",(drtv, w.abj_id.id))
            self._convert_opportunity(cr, uid, ids, {'lead_ids': lead_ids}, context=context)    
            #self.pool.get('crm.lead')._lead_create_contact(cr, uid, w.leadd_id, w.candidate_customer, True, False, context)
            
            #raise osv.except_osv(_('move id'), _(drtv))
        return self.pool.get('crm.lead').redirect_opportunity_view(cr, uid, w.leadd_id, context=context)
        #return True
    '''    
    def _create_partner(self, cr, uid, ids, context=None):
        """
        Create partner based on action.
        :return dict: dictionary organized as followed: {lead_id: partner_assigned_id}
        """
        #TODO this method in only called by crm_lead2opportunity_partner
        #wizard and would probably diserve to be refactored or at least
        #moved to a better place
        if context is None:
            context = {}
        lead = self.pool.get('crm.lead')
        lead_ids = context.get('active_ids', [])
        data = self.browse(cr, uid, ids, context=context)[0]
        partner_id = data.partner_id and data.partner_id.id or False
        return lead.handle_partner_assignation(cr, uid, lead_ids, data.action, partner_id, context=context)
    
crm_lead2opportunity_partner()
class abj(osv.osv):
    _inherit="customer_acl_v2.abj"
    
abj()
class crm_make_sale(osv.osv_memory):
    """ Make sale  order for crm """

    _inherit = "crm.make.sale"
    def _selectPartner(self, cr, uid, context=None):
        """
        This function gets default value for partner_id field.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param context: A standard dictionary for contextual values
        @return: default value of partner_id field.
        """
        if context is None:
            context = {}

        lead_obj = self.pool.get('crm.lead')
        active_id = context and context.get('active_id', False) or False
        if not active_id:
            return False

        lead = lead_obj.read(cr, uid, active_id, ['partner_id'], context=context)
        return lead['partner_id'][0] if lead['partner_id'] else False

    def view_init(self, cr, uid, fields_list, context=None):
        return super(crm_make_sale, self).view_init(cr, uid, fields_list, context=context)

    def makeOrder(self, cr, uid, ids, context=None):
        """
        This function  create Quotation on given case.
        @param self: The object pointer
        @param cr: the current row, from the database cursor,
        @param uid: the current user’s ID for security checks,
        @param ids: List of crm make sales' ids
        @param context: A standard dictionary for contextual values
        @return: Dictionary value of created sales order.
        """
        if context is None:
            context = {}
        # update context: if come from phonecall, default state values can make the quote crash lp:1017353
        context.pop('default_state', False)        
        
        case_obj = self.pool.get('crm.lead')
        sale_obj = self.pool.get('sale.order')
        partner_obj = self.pool.get('res.partner')
        data = context and context.get('active_ids', []) or []

        for make in self.browse(cr, uid, ids, context=context):
            partner = make.partner_id
            partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                    ['default', 'invoice', 'delivery', 'contact'])
            pricelist = partner.property_product_pricelist.id
            fpos = partner.property_account_position and partner.property_account_position.id or False
            payment_term = partner.property_payment_term and partner.property_payment_term.id or False
            new_ids = []
            for case in case_obj.browse(cr, uid, data, context=context):
                if not partner and case.partner_id:
                    partner = case.partner_id
                    fpos = partner.property_account_position and partner.property_account_position.id or False
                    payment_term = partner.property_payment_term and partner.property_payment_term.id or False
                    partner_addr = partner_obj.address_get(cr, uid, [partner.id],
                            ['default', 'invoice', 'delivery', 'contact'])
                    pricelist = partner.property_product_pricelist.id
                if False in partner_addr.values():
                    raise osv.except_osv(_('Insufficient Data!'), _('No address(es) defined for this customer.'))

                vals = {
                    'origin': _('Opportunity: %s') % str(case.id),
                    'section_id': case.section_id and case.section_id.id or False,
                    'categ_ids': [(6, 0, [categ_id.id for categ_id in case.categ_ids])],
                    'shop_id': make.shop_id.id,
                    'partner_id': partner.id,
                    'pricelist_id': pricelist,
                    'partner_invoice_id': partner_addr['invoice'],
                    'partner_shipping_id': partner_addr['delivery'],
                    'date_order': fields.date.context_today(self,cr,uid,context=context),
                    'fiscal_position': fpos,
                    'payment_term':payment_term,
                }
                if partner.id:
                    vals['user_id'] = partner.user_id and partner.user_id.id or uid
                new_id = sale_obj.create(cr, uid, vals, context=context)
                sale_order = sale_obj.browse(cr, uid, new_id, context=context)
                case_obj.write(cr, uid, [case.id], {'ref': 'sale.order,%s' % new_id})
                new_ids.append(new_id)
                message = _("Opportunity has been <b>converted</b> to the quotation <em>%s</em>.") % (sale_order.name)
                case.message_post(body=message)
            if make.close:
                case_obj.case_close(cr, uid, data)
            if not new_ids:
                return {'type': 'ir.actions.act_window_close'}
            if len(new_ids)<=1:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids and new_ids[0]
                }
            else:
                value = {
                    'domain': str([('id', 'in', new_ids)]),
                    'view_type': 'form',
                    'view_mode': 'tree,form',
                    'res_model': 'sale.order',
                    'view_id': False,
                    'type': 'ir.actions.act_window',
                    'name' : _('Quotation'),
                    'res_id': new_ids
                }
            return value

    def _get_shop_id(self, cr, uid, ids, context=None):
        cmpny_id = self.pool.get('res.users')._get_company(cr, uid, context=context)
        shop = self.pool.get('sale.shop').search(cr, uid, [('company_id', '=', cmpny_id)])
        return shop and shop[0] or False
    _columns = {
        'shop_id': fields.many2one('sale.shop', 'Shop', required=True),
        'partner_id': fields.many2one('res.partner', 'Customer', required=True, domain=[('customer','=',True)]),
        'close': fields.boolean('Mark Won', help='Check this to close the opportunity after having created the sales order.', invisible=True),
    }
    _defaults = {
        'shop_id': _get_shop_id,
        'close': True,
        'partner_id': _selectPartner,
    }

   

crm_make_sale()


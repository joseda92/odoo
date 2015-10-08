# coding: utf-8

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime


class esms_compose(models.Model):
    _name = 'esms.compose'

    def compute_default_value(self):
        return self.env.user.partner_id.mobile

    def demo(self):
        partner_id = self.env.context.get('active_id')
        return self.env['res.partner'].browse(partner_id).mobile

    def demo2(self):
        dem = tuple(self._context.get('active_ids', False))
        return [(6, 0, dem)]

    error_message = fields.Char(readonly=True)
    record_id = fields.Integer()
    model_id = fields.Char()
    sms_gateway = fields.Many2one('esms.accounts', 'SMS Gateway Account',
                                  required=True)
    from_number = fields.Char(default=compute_default_value,
                              required=True, string="From Mobile Number")
    to_number = fields.Char('To Mobile Number', required=True, readonly=True,
                            default=demo)
    sms_content = fields.Text('SMS Content')
    partner_ids = fields.Many2many('res.partner', 'compose_partner_ids',
                                   'esms_compose_id', 'partner_id',
                                   string='MMS Attachments', default=demo2)
    field_id = fields.Char('Field Name')
    template_id = fields.Many2one('esms.templates', 'Template')

    @api.onchange('template_id')
    def load_template(self):
        if self.template_id.id:
            esms_templates = self.env['esms.templates']
            sms_rendered_content = esms_templates.render_template(self.template_id.template_body,
                                                                  self.template_id.model_id.model,
                                                                  self.record_id)

            self.from_number = self.template_id.sms_from
            self.sms_content = sms_rendered_content
            self.sms_gateway = self.template_id.account_gateway.id

    @api.multi
    def send_entity(self):
        self.ensure_one()
        esms_templates = self.env['esms.templates']

        for x in self.partner_ids:
            gateway_model = self.sms_gateway.account_gateway.gateway_model_name
            sms_content = esms_templates.render_template(self.template_id.template_body,
                                                         self.template_id.model_id.model,
                                                         x.id)
            my_sms = self.env[gateway_model].send_message(self.sms_gateway.id,
                                                          self.from_number,
                                                          x.mobile,
                                                          sms_content,
                                                          self.model_id,
                                                          self.record_id,
                                                          self.field_id)

            #use the human readable error message if present
            error_message = ""
            if my_sms.human_read_error != "":
                error_message = my_sms.human_read_error
            else:
                error_message = my_sms.response_string

	        #display the screen with an error code if the sms/mms was not successfully sent
            #if my_sms.delivary_state == "failed":
             #   return {
              #      'type': 'ir.actions.act_window',
               #     'res_model': 'esms.compose',
                #    'view_type': 'form',
                 #   'view_mode': 'form',
                  #  'target': 'new',
                   # 'context': {
                    #    'default_field_id': self.field_id,
                    #    'default_sms_gateway': self.sms_gateway.id,
                    #    'default_to_number': self.to_number,
                    #    'default_record_id': self.record_id,
                    #    'default_model_id': self.model_id,
                    #    'default_error_message': error_message}
                #}
        return True

class esms_mms(models.Model):
    _name = "esms.mms"

    partner_id = fields.Many2one('esms.compose')
    mms_attachment = fields.Binary(String="Attachment")

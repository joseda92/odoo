from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)
import requests
from datetime import datetime

class esms_history(models.Model):

    _name = "esms.history"
    _order = "my_date desc"
    
    record_id = fields.Integer(readonly=True, string="Record")
    account_id = fields.Many2one('esms.accounts', readonly=True, string="SMS Account")
    gateway_id = fields.Many2one('esms.gateways', readonly=True, string="SMS Gateway")
    model_id = fields.Many2one('ir.model', readonly=True, string="Model")
    model_name = fields.Char(string="Model Name", related='model_id.model', readonly=True)
    field_id = fields.Many2one('ir.model.fields', readonly=True, string="Field")
    from_mobile = fields.Char(string="From Mobile", readonly=True)
    to_mobile = fields.Char(string="To Mobile", readonly=True)
    sms_content = fields.Text(string="SMS Message", readonly=True)
    record_name = fields.Char(string="Record Name", compute="_rec_nam")
    status_string = fields.Char(string="Response String", readonly=True)
    status_code = fields.Selection((('RECEIVED','Received'), ('failed', 'Failed to Send'), ('queued', 'Queued'), ('successful', 'Sent'), ('DELIVRD', 'Delivered'), ('EXPIRED','Timed Out'), ('UNDELIV', 'Undelivered')), string='Delivary State', readonly=True)
    sms_gateway_message_id = fields.Char(string="SMS Gateway Message ID", readonly=True)
    direction = fields.Selection((("I","INBOUND"),("O","OUTBOUND")), string="Direction", readonly=True)
    my_date = fields.Datetime(string="Send/Receive Date", readonly=True, help="The date and time the sms is received or sent")
    delivary_error_string = fields.Text(string="Delivary Error")

    @api.one
    def _rec_nam(self):
        if self.model_id != False:
            my_record = self.env[self.model_id.model].search([('id','=',self.record_id)])
            self.record_name = my_record.name
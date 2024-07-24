import datetime
import logging
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class ProductRequest(models.Model):
    _description = 'Product request'
    _inherit = ['product.template']

    # -------------------------------------------------------------------------
    # Fields
    # -------------------------------------------------------------------------

    active = fields.Boolean(default=False, copy=False)
    state = fields.Selection(
        [('rejected', 'Rejected'), ('draft', 'Draft'), ('sent', 'Sent'), ('validated', 'Valid')], default='draft',
        tracking=True, readonly=True)
    can_validate_product = fields.Boolean(default=False, compute='_onchange_assign_mail_boolean')
    has_already_approved = fields.Boolean(default=False, compute='_onchange_has_already_approved')
    department_id = fields.Many2one('hr.department', default=lambda self: self.env.user.employee_ids.department_id,
                                    string="Department", tracking=3)
    product_circuit_validation_ids = fields.One2many('product.circuit.validation', 'product_id',
                                                     string="Circuit of validation")

    def write(self, vals):
        for record in self:
            if 'active' in vals and record.state in ('rejected', 'draft'):
                raise UserError("Vous ne pouvez pas archiver ou désarchiver à cette étape.")
            elif 'active' in vals and record.state in ('rejected', 'draft', 'sent') and not record.can_validate_product:
                raise UserError("Vous ne pouvez pas archiver ou désarchiver.")
            return super(ProductRequest, self).write(vals)

    @api.onchange('product_circuit_validation_ids', 'can_validate_product')
    def _onchange_assign_mail_boolean(self):
        """
        This function is used to verify if can validate product or no
        :return Boolean
        """
        for line in self:
            line.can_validate_product = False
            if 'draft' in line.state:
                line.can_validate_product = True
            for validator in line.product_circuit_validation_ids:
                if validator.user_id.id == self.env.user.id:
                    line.can_validate_product = True
                    break
            if not line.product_circuit_validation_ids:
                line.can_validate_product = True
            if line.state in ('draft'):
                department_default_id = self.env['ir.config_parameter'].sudo().get_param(
                    'creation_request.creation_default_department_id')
                line.product_circuit_validation_ids = [(5, 0, 0)]
                default_department_id = self.env['hr.department'].sudo().search([('id', '=', department_default_id)],
                                                                                limit=1, order='id desc')
                line.product_circuit_validation_ids = [(0, 0, {'user_id': line.user_id.id, 'role': line.role}) for line
                                                       in
                                                       line.department_id.circuit_ids] if line.department_id.circuit_ids else [
                    (0, 0, {'user_id': line.user_id.id, 'role': line.role}) for line in
                    default_department_id.circuit_ids]

    def create_activity_creation_request(self, task, user_id, msg, days, activity_type_id, res_model_id, res_id):
        """
        This function is used to create activity
        :return activity
        """
        self.env['mail.activity'].sudo().create({
            'summary': task,
            'user_id': user_id.id,
            'date_deadline': datetime.datetime.now() + datetime.timedelta(days=days),
            'note': msg,
            'activity_type_id': activity_type_id,
            'res_id': res_id,
            'res_model_id': res_model_id,
        })

    def from_draft_to_sent(self):
        """
        This function is used to sent to validation to validator
        :return state
        """
        for line in self:
            activity_type_id = self.sudo().env.ref('creation_request.product_mail_activity_data_to_do').id
            res_model_id = self.env['ir.model'].sudo().search([('model', '=', line._name)], limit=1)
            validation_message = f"Veuillez valider cette demande de creation de produit {line.name}" if (
                    self.env.user.lang in 'fr_FR') else f"Please validate this request to create product {line.name}"
            days = line.department_id.activity_deadlines_number if line.department_id.can_apply_activity_deadlines else 0
            if line.department_id.can_apply_activity_deadlines:
                for validator in line.product_circuit_validation_ids:
                    line.create_activity_creation_request("Demande de validation", validator.user_id,
                                                          validation_message, days,
                                                          activity_type_id, res_model_id.id, line.id)
            line.state = 'sent'

    @api.returns('mail.message', lambda value: value.id)
    def message_post(self, *, message_type='notification', **kwargs):
        if message_type == 'email' and self.create_share_id:
            self = self.with_context(no_document=True)
        return super(ProductRequest, self).message_post(message_type=message_type, **kwargs)

    def action_refuse_product_request(self):
        self.ensure_one()
        return {
            'name': _("Refuser la création d'un produit") if self.env.user.lang in 'fr_FR' else _(
                "Refuse the creation of a product"),
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_model': 'product.refused.validation',
            'view_mode': 'form',
            'views': [[False, 'form']],
            'context': {
                'default_product_id': self.id,
            }
        }

    @api.onchange('has_already_approved', 'product_circuit_validation_ids', 'state')
    def _onchange_has_already_approved(self):
        """
        This function is used to know if already approved by current user
        :return boolean
        """
        for line in self:
            line.has_already_approved = False
            for user in line.product_circuit_validation_ids:
                if user.user_id.id == self.env.user.id and user.state and user.state in 'approved':
                    line.has_already_approved = True
                    break

    def from_sent_to_validated(self):
        """
        This function is used to validate product creation request
        :return state
        """
        for line in self:
            quorum_number = line.department_id.quorum_number if line.department_id.quorum else 0
            for any_validator in line.product_circuit_validation_ids:
                if any_validator.user_id == self.env.user:
                    any_validator.state = 'approved'
                    break
            nb_validations = 0
            for any_validator in line.product_circuit_validation_ids:
                if any_validator.state == 'approved':
                    nb_validations += 1
                    if any_validator.user_id == self.env.user and any_validator.role == 'end_validator':
                        nb_validations = quorum_number
                        break
            if nb_validations >= quorum_number:
                line.sudo().active = True
                line.state = 'validated'
                notification = {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'title': _('La création de produit a été approuvée avec succès.'),
                        'type': 'success',
                        'next': {'type': 'ir.actions.act_window_close'},
                    },
                }
                return notification

    def from_sent_to_rejected(self):
        """
        This function is used to refuse product creation request
        :return state
        """
        for line in self:
            quorum_number = line.department_id.quorum_number if line.department_id.quorum else 0
            for any_validator in line.product_circuit_validation_ids:
                if any_validator.user_id == self.env.user:
                    any_validator.state = 'refused'
                    break
            nb_validations = 0
            for any_validator in line.product_circuit_validation_ids:
                if any_validator.state == 'refused':
                    nb_validations += 1
                    if any_validator.role == 'end_validator':
                        nb_validations = quorum_number
                        break
            if nb_validations >= quorum_number:
                line.state = 'rejected'

    def put_to_draft(self):
        """
        This function is used to put in draft creation request
        :return state
        """
        self.state = 'draft'

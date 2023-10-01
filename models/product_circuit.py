from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError


class ProductCircuit(models.Model):
    _name = 'product.circuit'
    _description = 'Product circuit'

    name = fields.Char("Reference")
    user_id = fields.Many2one('res.users', string="User", ondelete="cascade")
    role = fields.Selection([('validator', 'Validator'), ('end_validator', 'Final validator')],
                            default='validator', string="Validation Profile")
    department_id = fields.Many2one('hr.department', string="Department")

    # @api.constrains('user_id', 'role')
    # def _constrains_product_role(self):
    #     for circuit in self:
    #         circuit_ids = self.env['product.circuit'].search(
    #             [('role', 'in', ('validator', 'end_validator')), ('department_id', '=', circuit._origin.department_id.id)])
    #         for employee in circuit_ids:
    #             employee = self.env['hr.employee'].search(
    #                 [('department_id', '!=', circuit._origin.department_id.id), ('user_id', '=', employee.user_id.id)])
    #             if employee:
    #                 raise UserError(
    #                     _("Cet employé (%s) ne peut pas validateur, car il n'est pas dans le service de traitement",
    #                       employee.name))


class ProductCircuitValidation(models.Model):
    _inherit = 'product.circuit'
    _name = 'product.circuit.validation'
    _table = 'product_circuit_validation'
    _description = 'Product Circuit of validation'

    product_id = fields.Many2one('product.template', string="Product")
    state = fields.Selection([('refused', 'Refused'), ('approved', 'Approved')], string="Status")

    # @api.constrains('user_id', 'role')
    # def _constrains_product_role(self):
    #     for circuit in self:
    #         circuit_ids = self.env['product.circuit'].search(
    #             [('role', 'in', ('validator', 'end_validator')), ('department_id', '=', circuit.product_id.department_id.id)])
    #         for employee in circuit_ids:
    #             employee = self.env['hr.employee'].search(
    #                 [('department_id', '!=', circuit.product_id.department_id.id),
    #                  ('user_id', '=', employee.user_id.id)])
    #             if employee:
    #                 raise UserError(
    #                     _('This employee (%s) can not bet an assignor, because it is not in the processing '
    #                       'department',
    #                       employee.name))

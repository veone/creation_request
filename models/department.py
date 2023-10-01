import logging

from odoo import fields, models, api, _
from odoo.exceptions import AccessError, UserError

_logger = logging.getLogger(__name__)


class HrDepartment(models.Model):
    _inherit = 'hr.department'
    _description = 'Hr department'
    _rec_name = 'name'

    circuit_ids = fields.One2many('product.circuit', 'department_id', string="Circuit of validation")
    can_apply_activity_deadlines = fields.Boolean(string="Can he apply the deadlines for activities", default=False)
    activity_deadlines_number = fields.Integer(string="Deadlines", default=0,
                                               help="Please provide the deadlines for the activities generated for this step. Nb: This number must be greater than or equal to zero")
    quorum = fields.Boolean(string="Quorum", default=False)
    quorum_number = fields.Integer(string="Number of quorum", default=0,
                                   help="Please enter the minimum number of validations required. Nb: This number must be less than or equal to the quorum maci total")
    quorum_number_max = fields.Integer(string="Maximum quorum number", default=0, compute='_compute_quorum_number_max')

    #     ==================== Onchange and depends Method ==============================

    @api.depends("quorum_number")
    def _compute_quorum_number_max(self):
        """
        This function is used to set quorum max by validators number
        """
        self.quorum_number_max = len(self.circuit_ids)

    @api.constrains('quorum_number')
    def _check_quorum_number(self):
        """
        This function is used to verify if quorum is superior of max quorum
        """
        if self.quorum_number > self.quorum_number_max:
            raise UserError(
                _("You must put a minimum number of validators, not greater than the number of assigned users (%s)",
                  self.quorum_number_max, ))

    @api.constrains('quorum_number')
    def _check_quorum_number(self):
        """
        This function is used to verify if quorum is superior of max quorum and inferior of zero
        """
        if self.quorum_number < 0:
            raise UserError(
                _("Quorum must be a positive number (%s)",
                  self.quorum_number, ))
        if self.quorum_number > self.quorum_number_max:
            raise UserError(
                _("You must put a minimum number of validators, not greater than the number of assigned users (%s)",
                  self.quorum_number_max, ))

    @api.onchange('circuit_ids')
    def _onchange_circuit_ids(self):
        """
        This function is used to increment or decrement quorum number by validators
        """
        for line in self:
            line.quorum_number = len(line.circuit_ids)
            line.quorum = True if len(line.circuit_ids) > 0 else False

    @api.onchange('quorum_number')
    def _onchange_quorum_number(self):
        """
        This function is used to set quorum to False when quorum number is equal zero
        """
        if self.quorum_number == 0:
            self.quorum = False

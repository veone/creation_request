from odoo import models, fields, api, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    creation_default_department_id = fields.Many2one('hr.department', 'Default department',
                                            config_parameter='creation_request.creation_default_department_id')

# -*- coding: utf-8 -*-

from odoo import fields, models, _


class ProductRefusedValidation(models.TransientModel):
    _name = 'product.refused.validation'
    _description = 'Product refused validation'

    product_id = fields.Many2one('product.template', required=True)
    reason = fields.Text(required=True, string="Reason")

    def action_refused_product_request(self):
        """
        This function is used to confirm the refuse
        """
        # Post a second message, more verbose than the tracking message
        if self.product_id.create_uid:
            message = (f'Ce produit a été réfusé par {self.env.user.name} avec le justificatif : '
                       f'{self.reason}') if self.env.user.lang in 'fr_FR' else \
                f'This product has been rejected by {self.env.user.name} with the justification: {self.reason}'
            self.product_id.message_post(body=_(message))
            self.product_id.from_sent_to_rejected()

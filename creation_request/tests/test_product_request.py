from odoo.tests import tagged
from odoo.tests.common import TransactionCase
from odoo.tests import common


@tagged('post_install', '-at_install')
class TestProductRequest(TransactionCase):

    def setUp(self, *args, **kwargs):
        super().setUp(*args, **kwargs)
        """
        Créez un enregistrement de ProductRequest pour chaque test
        """
        self.product_request = self.env['product.template'].create({
            'name': 'Test Product Request',
            'state': 'draft',
        })

    def test_default_status(self):
        """
         Vérifiez que le produit est desactivé à la creation
        """
        self.assertEqual(self.product_request.active, False)

    def test_from_draft_to_sent(self):
        """
         Vérifiez que l'état passe de 'draft' à 'sent' après l'appel de la méthode
        """
        self.product_request.from_draft_to_sent()
        self.assertEqual(self.product_request.state, 'sent')

    def test_from_sent_to_validated(self):
        """
        Vérifiez que l'état passe de 'sent' à 'validated' après l'appel de la méthode
        """
        self.product_request.from_sent_to_validated()
        self.assertEqual(self.product_request.state, 'validated')
        # Vérifiez également que le champ 'active' est défini sur True
        self.assertTrue(self.product_request.active)

    def test_from_sent_to_rejected(self):
        """
        Vérifiez que l'état passe de 'sent' à 'rejected' après l'appel de la méthode
        """
        self.product_request.from_sent_to_rejected()
        self.assertEqual(self.product_request.state, 'rejected')

    def test_put_to_draft(self):
        """
        Vérifiez que l'état passe de n'importe quel état à 'draft' après l'appel de la méthode
        """
        self.product_request.from_sent_to_validated()
        self.product_request.put_to_draft()
        self.assertEqual(self.product_request.state, 'draft')

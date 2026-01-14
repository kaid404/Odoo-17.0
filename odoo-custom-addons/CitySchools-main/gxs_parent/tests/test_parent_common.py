from odoo.tests import common


class TestParentCommon(common.TransactionCase):
    def setUp(self):
        super(TestParentCommon, self).setUp()
        self.op_parent = self.env['op.parent']
        self.op_student = self.env['op.student']
        self.subject_registration = self.env['op.subject.registration']

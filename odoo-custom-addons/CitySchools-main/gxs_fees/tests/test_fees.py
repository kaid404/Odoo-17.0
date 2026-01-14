from logging import info

from .test_fees_common import TestFeesCommon


class TestStudentFees(TestFeesCommon):

    def setUp(self):
        super(TestStudentFees, self).setUp()

    def test_case_fees(self):
        fees = self.op_student_fees.search([])
        if not fees:
            raise AssertionError(
                'Error in data, please check for student fees details')
        info('  Details Of Student Fees:.....')
        for record in fees:
            record.action_get_invoice()


class TestStudent(TestFeesCommon):

    def setUp(self):
        super(TestStudent, self).setUp()

    def test_case_student_fees(self):
        student = self.op_student.search([])
        if not student:
            raise AssertionError(
                'Error in data, please check for student fees invoice details')
        info('  Details Of Student Fees Invoice:.....')
        for record in student:
            record.action_view_invoice()


class TestWizardFees(TestFeesCommon):

    def setUp(self):
        super(TestWizardFees, self).setUp()

    def test_case_wizard_fees(self):
        wizard = self.op_fees_wizard.create({
            'fees_filter': 'student',
            'student_id': self.env.ref('gxs_core.op_student_1').id
        })
        info('  Details Of Student Fees :.....')
        wizard.print_report()


class TestFeesTerms(TestFeesCommon):

    def setUp(self):
        super(TestFeesTerms, self).setUp()

    def test_case_fees_terms(self):
        terms = self.op_fees_terms.create({
            'name': 'Library Fees',
            'line_ids': self.env.ref('gxs_fees.op_fees_term_line_6'),
        })
        info('  Details Of Fees Terms :.....')
        return terms

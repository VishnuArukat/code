from openerp import models, fields, api
from datetime import datetime
import openerp.addons.decimal_precision as dp


class AccountPaymentOrder(models.Model):
    _name = 'account.payment.order'
    _description = 'Account Payment Order'
    _rec_name = 'number'

    @api.one
    @api.depends('payment_line.amount')
    def _compute_total(self):
        self.amount_total = sum(line.amount for line in self.payment_line)

    supplier_id = fields.Many2one('res.partner', 'Supplier', domain=[('supplier', '=', True)],
                                  states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    date = fields.Date('Date', required=True, default=datetime.today(),
                       states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    partner_name = fields.Char('Name', required=True,
                               states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    amount_text = fields.Char('Amount Text', states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    cheque_no = fields.Char('Cheque No', states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    payment_type = fields.Selection([('atm', 'ATM'), ('transfer', 'Transfer'), ('cash', 'Cash'), ('cheque', 'Cheque')],
                                    'Payment Type', required=True,
                                    states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    journal_id = fields.Many2one('account.journal', 'Payment Method', domain=[('type', 'in', ['bank', 'cash'])],
                                 required=True, states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    cr_account_id = fields.Many2one('account.account', 'Credit Account', required=True,
                                    states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    state = fields.Selection([('draft', 'Draft'), ('cancel', 'Cancel'), ('post', 'Post')], required=True, copy=False,
                             default='draft', states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    number = fields.Char('Number', required=False, default='/', copy=False,
                         states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    note = fields.Char('Notes', required=True, states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    payment_line = fields.One2many('account.payment.order.line', 'order_id', 'Payment Lines', required=True, copy=True,
                                   states={'posted': [('readonly', True)], 'cancel': [('readonly', True)]})
    amount_total = fields.Float('Total Amount', digits=dp.get_precision('Account'), readonly=True,
                                compute='_compute_total', store=True)

    def get_period(self, cr, uid, context=None):
        ctx = dict(context or {})
        period_ids = self.pool.get('account.period').find(cr, uid, context=ctx)
        return period_ids[0]

    @api.multi
    def button_post(self):
        # Creating journal entry
        move_obj = self.env['account.move']
        period = self.get_period()
        move_lines = []
        cline = {
            'name': self.note,
            'partner_id': self.supplier_id.id,
            'credit': self.amount_total,
            'debit': 0.0,
            'account_id': self.cr_account_id.id,
            'date': self.date,
            'journal_id': self.journal_id.id,
            'period_id': period}
        move_lines.append(tuple((0, 0, cline)))
        for line in self.payment_line:
            dline = {
                'name':  line.memo,
                'partner_id': self.supplier_id.id,
                'debit': line.amount,
                'credit': 0.0,
                'account_id': line.dr_account_id.id,
                'date': self.date,
                'journal_id': self.journal_id.id,
                'period_id': period,
            }
            move_lines.append(tuple((0, 0, dline)))

        move_obj.create({
            'narration': self.note,
            'ref': self.partner_name,
            'partner_id': self.supplier_id.id,
            'line_id': move_lines,
            'journal_id': self.journal_id.id,
            'period_id': period,
            'date': self.date, })

        if self.number == '/':
            number = self.env['ir.sequence'].next_by_code('payment.order') or '/'
            self.write({'number': number})
        self.write({'state': 'post'})

    @api.multi
    def button_cancel(self):
        # go from post state to cancel state
        self.write({'state': 'cancel'})
        return True

    @api.multi
    def button_to_draft(self):
        # go from canceled state to draft state
        self.write({'state': 'draft'})
        return True

    @api.onchange('supplier_id')
    def onchange_supplier_id(self):
        self.partner_name = self.supplier_id.name
        if self.payment_line:
            for line in self.payment_line:
                self.payment_line = [(3, line.id)]
        self.payment_line = [(0, 0, {'dr_account_id': self.supplier_id.property_account_payable,
                                     'amount': 0.0, 'memo': '/'})]


class AccountPaymentOrderLine(models.Model):
    _name = 'account.payment.order.line'
    _description = 'Account Payment Order Line'

    dr_account_id = fields.Many2one('account.account', 'Debit Account', required=True)
    memo = fields.Char('Memo', required=True, default='/')
    amount = fields.Float('Amount', required=True)
    order_id = fields.Many2one('account.payment.order', 'Payment Order')

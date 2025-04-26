# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from dateutil.relativedelta import relativedelta  # Added import

class AccountMove(models.Model):
    _inherit = 'account.move'

    def _post(self, soft=True):
        """Override to assign membership pricelist after posting invoice"""
        res = super()._post(soft)

        for move in self.filtered(lambda m: m.move_type == 'out_invoice'):
            for line in move.invoice_line_ids:
                if line.product_id.membership_pricelist_id:
                    line.partner_id.sudo().write({
                        'property_product_pricelist': line.product_id.membership_pricelist_id.id
                    })
        return res

    def button_draft(self):
        # OVERRIDE to update the cancel date.
        res = super(AccountMove, self).button_draft()
        for move in self:
            if move.move_type == 'out_invoice':
                self.env['membership.membership_line'].search([
                    ('account_invoice_line', 'in', move.mapped('invoice_line_ids').ids)
                ]).write({'date_cancel': False})
        return res

    def button_cancel(self):
        # OVERRIDE to update the cancel date.
        res = super(AccountMove, self).button_cancel()
        for move in self:
            if move.move_type == 'out_invoice':
                self.env['membership.membership_line'].search([
                    ('account_invoice_line', 'in', move.mapped('invoice_line_ids').ids)
                ]).write({'date_cancel': fields.Date.today()})
        return res

    def write(self, vals):
        # OVERRIDE to write the partner on the membership lines.
        res = super(AccountMove, self).write(vals)
        if 'partner_id' in vals:
            self.env['membership.membership_line'].search([
                ('account_invoice_line', 'in', self.mapped('invoice_line_ids').ids)
            ]).write({'partner': vals['partner_id']})
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    def write(self, vals):
        # OVERRIDE
        res = super(AccountMoveLine, self).write(vals)

        to_process = self.filtered(lambda line:
            line.move_id.move_type == 'out_invoice'
            and line.product_id.membership
            and line.product_id.membership_duration
        )

        if not to_process:
            return res

        existing_memberships = self.env['membership.membership_line'].search([
            ('account_invoice_line', 'in', to_process.ids)])
        to_process = to_process - existing_memberships.mapped('account_invoice_line')

        if not to_process:
            return res

        memberships_vals = []
        for line in to_process:
            # Calculate dates based on duration
            invoice_date = line.move_id.invoice_date or fields.Date.today()
            duration = int(line.product_id.membership_duration)
            date_from = invoice_date
            date_to = invoice_date + relativedelta(months=duration)

            memberships_vals.append({
                'partner': line.move_id.partner_id.id,
                'membership_id': line.product_id.id,
                'member_price': line.price_unit,
                'date': fields.Date.today(),
                'date_from': date_from,
                'date_to': date_to,
                'account_invoice_line': line.id,
            })
        self.env['membership.membership_line'].create(memberships_vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        # OVERRIDE
        lines = super(AccountMoveLine, self).create(vals_list)
        to_process = lines.filtered(lambda line:
            line.move_id.move_type == 'out_invoice'
            and line.product_id.membership
            and line.product_id.membership_duration
        )

        if not to_process:
            return lines

        existing_memberships = self.env['membership.membership_line'].search([
            ('account_invoice_line', 'in', to_process.ids)])
        to_process = to_process - existing_memberships.mapped('account_invoice_line')

        if not to_process:
            return lines

        memberships_vals = []
        for line in to_process:
            # Calculate dates based on duration
            invoice_date = line.move_id.invoice_date or fields.Date.today()
            duration = int(line.product_id.membership_duration)
            date_from = invoice_date
            date_to = invoice_date + relativedelta(months=duration)

            memberships_vals.append({
                'partner': line.move_id.partner_id.id,
                'membership_id': line.product_id.id,
                'member_price': line.price_unit,
                'date': fields.Date.today(),
                'date_from': date_from,
                'date_to': date_to,
                'account_invoice_line': line.id,
            })
        self.env['membership.membership_line'].create(memberships_vals)
        return lines

    def _create_membership_line(self):
        """Update partner's pricelist when membership invoice is posted."""
        res = super(AccountMoveLine, self)._create_membership_line()
        for line in self:
            # Check if the line is for a membership product with a pricelist
            if (
                line.product_id.membership
                and line.product_id.membership_pricelist_id
                and line.move_id.move_type == 'out_invoice'
                and line.move_id.state == 'posted'
            ):
                # Update partner's pricelist using sudo() to bypass security rules
                line.partner_id.sudo().write({
                    'property_product_pricelist': line.product_id.membership_pricelist_id.id
                })
        return res
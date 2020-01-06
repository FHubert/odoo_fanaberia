# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2019-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Niyas Raphy and Sreejith P (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################

import math
import re
import pydevd_pycharm
from odoo import api, models
from datetime import datetime



class ProductAutoBarcode(models.Model):
    _inherit = 'product.product'

    @api.model
    def create(self, vals):
        try:
            context = self._context
            current_uid = context.get('uid')
            user = self.env['res.users'].browse(current_uid).email
            if user == 'falkowski.hubert@gmail.com':
                pydevd_pycharm.settrace('127.0.0.1', port=5678, stdoutToServer=True, stderrToServer=True)
        except ConnectionRefusedError as e:
            print("debugger not available")

        res = super(ProductAutoBarcode, self).create(vals)
        if not res.product_variant_id.barcode:
            if not res.x_year:
                res.x_year = str(datetime.now().year)[2:4]
            if not res.x_season:
                res.x_season = str(datetime.now().month / 4 + 1)[0:1]

            all_products_act = len(self.env['product.template'].search(
                [('categ_id', '=', res.categ_id.id), ('x_season', '=', res.x_season), ('x_year', '=', res.x_year)]))

            all_products_ina = len(self.env['product.template'].search(
                [('categ_id', '=', res.categ_id.id), ('x_season', '=', res.x_season), ('x_year', '=', res.x_year), ('active', '=', False)]))

            all_products = str(all_products_act + all_products_ina).zfill(4)

            # ean = generate_ean(str(res.id))
            if res.product_template_attribute_value_ids.name:
                ean = str(res.categ_id.x_category_id).zfill(2) + res.x_season + res.x_year + all_products + '-' + res.product_template_attribute_value_ids[0].name
            else:
                ean = str(res.categ_id.x_category_id).zfill(2) + res.x_season + res.x_year + all_products
        else:
            barcode_base = res.product_variant_id.barcode.split('-')[0]
            if res.product_template_attribute_value_ids.name:
                ean = barcode_base + '-' + res.product_template_attribute_value_ids[0].name
            else:
                ean = barcode_base

        self.barcode = ean
        # res.product_variant_id.barcode = ean
        # res.product_variant_ids.barcode = ean

        res.barcode = ean
        res.default_code = ean
        res.x_zpl_barcode = format_zpl_barcode( ean )
        return res


def format_zpl_barcode(ean):

    if re.search('-', ean):
        ean_formatted = '>;' + ean
        sign_pos = ean_formatted.find('-')
        replace_str = '>6' + ean_formatted[sign_pos-1] + '-'
        ean_formatted = ean_formatted.replace('-',replace_str)
    else:
        ean_formatted = ean
    return ean_formatted

def ean_checksum(eancode):
    """returns the checksum of an ean string of length 13, returns -1 if
    the string has the wrong length"""
    if len(eancode) != 13:
        return -1
    oddsum = 0
    evensum = 0
    eanvalue = eancode
    reversevalue = eanvalue[::-1]
    finalean = reversevalue[1:]

    for i in range(len(finalean)):
        if i % 2 == 0:
            oddsum += int(finalean[i])
        else:
            evensum += int(finalean[i])
    total = (oddsum * 3) + evensum

    check = int(10 - math.ceil(total % 10.0)) % 10
    return check


def check_ean(eancode):
    """returns True if eancode is a valid ean13 string, or null"""
    if not eancode:
        return True
    if len(eancode) != 13:
        return False
    try:
        int(eancode)
    except:
        return False
    return ean_checksum(eancode) == int(eancode[-1])


def generate_ean(ean):
    """Creates and returns a valid ean13 from an invalid one"""
    if not ean:
        return "0000000000000"
    ean = re.sub("[A-Za-z]", "0", ean)
    ean = re.sub("[^0-9]", "", ean)
    ean = ean[:13]
    if len(ean) < 13:
        ean = ean + '0' * (13 - len(ean))
    return ean[:-1] + str(ean_checksum(ean))


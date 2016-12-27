# -*- encoding: utf-8 -*-
##############################################################################
#
#    Authors: Cybrosys Technologies
#    Copyright (c) Cybrosys Technologies
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Account Payment Order',
    'version': '1.0',
    'author': 'Cybrosys Technologies',
    'license': 'AGPL-3',
    'category': 'Finance',
    'description': """
""",
    'depends': ['account'],
    'data': [
        'views/payment_order_view.xml',
        'views/payment_order_report.xml',
        ],
    'images': [],
    'demo': [],
    'installable': True,
    'application': True,
}

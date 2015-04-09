# -*- coding: utf-8 -*-
#
# Copyright (C) 2014-2015 Bitergia
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.
#
# Authors:
#     Santiago Dueñas <sduenas@bitergia.com>
#

import re

from sortinghat.db.model import UniqueIdentity
from sortinghat.matcher import IdentityMatcher, FilteredIdentity


EMAIL_ADDRESS_REGEX = ur"^(?P<email>[^\s@]+@[^\s@.]+\.[^\s@]+)$"


class EmailIdentity(FilteredIdentity):
    """Class to stored EmailName filtered identities"""

    def __init__(self, id, uuid, email):
        super(EmailIdentity, self).__init__(id, uuid)
        self.email = email


class EmailMatcher(IdentityMatcher):
    """
    Simple unique identities matcher.

    This matcher only produces a positive result when two identities
    from each unique identity share the same email address. It also
    returns a positive match when the uuid on both unique identities is equal.
    """
    def __init__(self):
        super(EmailMatcher, self).__init__()
        self.email_pattern = re.compile(EMAIL_ADDRESS_REGEX)

    def match(self, a, b):
        """Determine if two unique identities are the same.

        This method compares the email addresses of each identity to check
        if the given unique identities are the same. When the given unique
        identities are the same object or share the same UUID, this will
        also produce a positive match.

        :param a: unique identity to match
        :param b: unique identity to match

        :returns: True when both unique identities are likely to be the same.
            Otherwise, returns False.

        :raises ValueError: when any of the given unique identities is not
            an instance of UniqueIdentity class
        """
        if not isinstance(a, UniqueIdentity):
            raise ValueError('<a> is not an instance of UniqueIdentity')
        if not isinstance(b, UniqueIdentity):
            raise ValueError('<b> is not an instance of UniqueIdentity')

        if a.uuid == b.uuid:
            return True

        emails_a = self._filter_emails(a.identities)
        emails_b = self._filter_emails(b.identities)

        for email in emails_a:
            if email in emails_b:
                return True
        return False

    def match_filtered_identities(self, fa, fb):
        """Determine if two filtered identities are the same.

        The method compares the email addresses of each filtered identity
        to check if they are the same. When the given filtered identities
        are the same object or share the same UUID, this will also
        produce a positive match.

        :param fa: filtered identity to match
        :param fb: filtered identity to match

        :returns: True when both filtered identities are likely to be the same.
            Otherwise, returns False.

        :raises ValueError: when any of the given filtered identities is not
            an instance of EmailIdentity class.
        """
        if not isinstance(fa, EmailIdentity):
            raise ValueError('<fa> is not an instance of UniqueIdentity')
        if not isinstance(fb, EmailIdentity):
            raise ValueError('<fb> is not an instance of EmailNameIdentity')

        if fa.uuid == fb.uuid:
            return True

        # Compare email addresses first
        if fa.email and fa.email == fb.email:
            return True

        return False

    def filter(self, u):
        """Filter the valid identities for this matcher.

        :param u: unique identity which stores the identities to filter

        :returns: a list of identities valid to work with this matcher.

        :raises ValueError: when the unique identity is not an instance
            of UniqueIdentity class
        """
        if not isinstance(u, UniqueIdentity):
            raise ValueError('<u> is not an instance of UniqueIdentity')

        filtered = []

        for id_ in u.identities:
            email = None

            if self._check_email(id_.email):
                email = id_.email.lower()

            if email:
                fid = EmailIdentity(id_.id, id_.uuid, email)
                filtered.append(fid)

        return filtered

    def _filter_emails(self, ids):
        return [id_.email.lower() for id_ in ids \
                if self._check_email(id_.email)]

    def _check_email(self, email):
        if not email:
            return False
        return self.email_pattern.match(email) is not None
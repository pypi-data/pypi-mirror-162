from edc_auth.site_auths import site_auths

from .auth_objects import (
    CANNED_VIEW,
    CANNED_VIEW_ROLE,
    CANNED_VIEW_SUPER,
    CANNED_VIEW_SUPER_ROLE,
    canned_super_codenames,
    canned_view_codenames,
)

site_auths.add_group(*canned_view_codenames, name=CANNED_VIEW, view_only=True)
site_auths.add_group(*canned_super_codenames, name=CANNED_VIEW_SUPER, no_delete=True)
site_auths.add_role(CANNED_VIEW, name=CANNED_VIEW_ROLE)
site_auths.add_role(CANNED_VIEW_SUPER, name=CANNED_VIEW_SUPER_ROLE)

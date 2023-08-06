from edc_navbar import Navbar, site_navbars

from canned_views.navbars import navbar as canned_views_navbar

navbar = Navbar(name="canned_views_app")

for item in canned_views_navbar.items:
    navbar.append_item(item)
site_navbars.register(navbar)

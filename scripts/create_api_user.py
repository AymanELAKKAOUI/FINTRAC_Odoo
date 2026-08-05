"""Create Fintrack API user in Odoo. Run via: odoo shell -d fintrack_dev < scripts/create_api_user.py"""
import sys

LOGIN = "api_service_user"
NAME = "Fintrack API Service"
EMAIL = "api@fintrack.local"
KEY_NAME = "Fintrack Integration"

User = env["res.users"]
ApiKey = env["res.users.apikeys"]

existing = User.search([("login", "=", LOGIN)], limit=1)
if existing:
    user = existing
    print(f"User already exists: {user.id}", file=sys.stderr)
else:
    user = User.create(
        {
            "name": NAME,
            "login": LOGIN,
            "email": EMAIL,
            "groups_id": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    print(f"Created user: {user.id}", file=sys.stderr)

# Grant CRM / Purchase access via standard internal user group (already has base.group_user)
# Add sales/purchase groups for CRM and PO modules
crm_group = env.ref("sales_team.group_sale_salesman", raise_if_not_found=False)
purchase_group = env.ref("purchase.group_purchase_user", raise_if_not_found=False)
extra_groups = [g.id for g in (crm_group, purchase_group) if g]
if extra_groups:
    user.write({"groups_id": [(4, gid) for gid in extra_groups]})

# Remove old keys with same label
old_keys = ApiKey.with_user(user).search([("name", "=", KEY_NAME)])
if old_keys:
    old_keys.unlink()

plain_key = ApiKey.with_user(user)._generate("rpc", KEY_NAME)
print(plain_key)

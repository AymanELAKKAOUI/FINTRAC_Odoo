"""Inspect and fix Fintrack API user."""
import sys

LOGIN = "api_service_user"

users = env["res.users"].with_context(active_test=False).search([("login", "=", LOGIN)])
print(f"Found {len(users)} user(s) with login {LOGIN}", file=sys.stderr)
for u in users:
    print(f"  id={u.id} active={u.active} name={u.name}", file=sys.stderr)

if len(users) > 1:
    keep = users[0]
    (users - keep).unlink()
    user = keep
    print(f"Removed duplicates, kept id={user.id}", file=sys.stderr)
elif users:
    user = users[0]
else:
    user = env["res.users"].create(
        {
            "name": "Fintrack API Service",
            "login": LOGIN,
            "email": "api@fintrack.local",
            "groups_id": [(6, 0, [env.ref("base.group_user").id])],
        }
    )
    print(f"Created user id={user.id}", file=sys.stderr)

crm_group = env.ref("sales_team.group_sale_salesman", raise_if_not_found=False)
purchase_group = env.ref("purchase.group_purchase_user", raise_if_not_found=False)
extra_groups = [g.id for g in (crm_group, purchase_group) if g]
if extra_groups:
    user.write({"groups_id": [(4, gid) for gid in extra_groups]})

user.write({"active": True})
env.cr.commit()

ApiKey = env["res.users.apikeys"]
old_keys = ApiKey.with_user(user).search([])
if old_keys:
    old_keys.unlink()

plain_key = ApiKey.with_user(user)._generate("rpc", "Fintrack Integration")
env.cr.commit()
print(plain_key)


import streamlit as st
import streamlit_authenticator as stauth
import yaml, os, datetime as dt
from yaml.loader import SafeLoader
from pathlib import Path

st.set_page_config(page_title="Client Portal Pro", page_icon="🗝️", layout="wide")
st.title("🗝️ Client Portal Pro")

# ---- Load configs ----
def load_yaml(name, default):
    p = Path(name)
    if not p.exists():
        return default
    with open(p, "r", encoding="utf-8") as f:
        return yaml.load(f, Loader=SafeLoader) or default

def save_yaml(name, data):
    with open(name, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)

users_cfg = load_yaml("users.yaml", {"credentials":{"users":[]}})
packages_cfg = load_yaml("packages.yaml", {"packages":{}})
tools_cfg = load_yaml("tools.yaml", {"tools":{}})

# Build authenticator config
def to_auth_config(users_list):
    usermap = {}
    extras = {}
    for u in users_list:
        usermap[u["username"]] = {"name": u.get("name", u["username"]), "password": u.get("password","")}
        extras[u["username"]] = {
            "package": u.get("package"),
            "allowed_tools": u.get("allowed_tools", []),
            "active": bool(u.get("active", True)),
            "expires_at": u.get("expires_at")  # "YYYY-MM-DD" or None
        }
    return {"credentials":{"usernames": usermap}}, extras

auth_cfg, extras = to_auth_config(users_cfg.get("credentials",{}).get("users", []))

if len(auth_cfg["credentials"]["usernames"]) == 0:
    st.warning("⚠️ No users found in users.yaml. Add a user first.")
    st.stop()

authenticator = stauth.Authenticate(
    auth_cfg["credentials"],
    cookie_name="client_portal",
    cookie_key=os.getenv("PORTAL_COOKIE_KEY","supersecret"),
    cookie_expiry_days=14
)

name, auth_status, username = authenticator.login("Login", "main")

def is_expired(expires_at: str):
    if not expires_at: return False
    try:
        d = dt.datetime.strptime(expires_at, "%Y-%m-%d").date()
        return dt.date.today() > d
    except Exception:
        return False

if auth_status is False:
    st.error("Username/password incorrect.")
elif auth_status is None:
    st.info("Please enter your credentials.")
else:
    user_extra = extras.get(username, {})
    # Gate by active/expiry
    if not user_extra.get("active", True):
        st.error("Your account is inactive. Please contact support.")
        st.stop()
    if is_expired(user_extra.get("expires_at")):
        st.error("Your subscription has expired. Please contact billing to reactivate.")
        st.stop()

    authenticator.logout("Logout", "sidebar")
    st.sidebar.success(f"Logged in as {name}")
    st.header("Welcome 👋")
    st.write("Select a tool below to open it in a new tab.")

    # Determine allowed tools
    allowed = list(user_extra.get("allowed_tools") or [])
    pkg = user_extra.get("package")
    if pkg and pkg in packages_cfg.get("packages", {}):
        allowed = list(set(allowed) | set(packages_cfg["packages"][pkg]))
    if not allowed:
        st.warning("No tools assigned to your account. Please contact support.")
        st.stop()

    tools = tools_cfg.get("tools", {})
    cols = st.columns(3)
    i = 0
    for key in allowed:
        info = tools.get(key)
        if not info: continue
        with cols[i % 3]:
            st.markdown(f"### {info.get('name', key)}")
            st.caption(info.get("desc", ""))
            url = info.get("url")
            if url:
                st.link_button("Open", url, type="primary", use_container_width=True)
            else:
                st.button("URL not set", disabled=True, use_container_width=True)
        i += 1

    st.divider()
    st.subheader("Your Subscription")
    if pkg: st.write(f"**Package:** {pkg}")
    st.write("**Enabled tools:** ", ", ".join([tools.get(k,{}).get("name", k) for k in allowed]))
    st.write(f"**Active:** {user_extra.get('active', True)} | **Expires:** {user_extra.get('expires_at') or '—'}")

    # ---- Admin Panel ----
    admin_users = [u.strip() for u in os.getenv("ADMIN_USERS","").split(",") if u.strip()]
    if username in admin_users:
        st.markdown("---")
        st.subheader("🛠️ Admin Panel")
        st.caption("Edit users, toggle active, set expiry. Changes are written to users.yaml.")
        editable = []
        for u in users_cfg.get("credentials",{}).get("users", []):
            editable.append({
                "username": u["username"],
                "name": u.get("name",""),
                "package": u.get("package",""),
                "allowed_tools": ", ".join(u.get("allowed_tools",[])),
                "active": bool(u.get("active", True)),
                "expires_at": u.get("expires_at","")
            })
        df = st.data_editor(editable, num_rows="dynamic", use_container_width=True, key="users_table")
        if st.button("💾 Save changes"):
            # write back to YAML
            new_users = []
            for row in df:
                atools = [k.strip() for k in (row.get("allowed_tools","") or "").split(",") if k.strip()]
                # keep existing password hash if present
                old = next((x for x in users_cfg["credentials"]["users"] if x["username"]==row["username"]), None)
                new_users.append({
                    "username": row["username"],
                    "name": row.get("name") or row["username"],
                    "password": (old or {}).get("password",""),
                    "package": row.get("package") or None,
                    "allowed_tools": atools,
                    "active": bool(row.get("active", True)),
                    "expires_at": row.get("expires_at") or None
                })
            users_cfg["credentials"]["users"] = new_users
            save_yaml("users.yaml", users_cfg)
            st.success("Saved. Reload page to apply.")

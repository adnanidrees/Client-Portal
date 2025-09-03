
# Utility: Generate hashed passwords for users.yaml
import getpass
import streamlit_authenticator as stauth

print("Password Hasher")
while True:
    pwd = getpass.getpass("Enter password to hash (blank to quit): ")
    if not pwd:
        break
    hashed = stauth.Hasher([pwd]).generate()[0]
    print("Hashed:", hashed)

import sys
import os

try:
    import bcrypt
except ImportError:
    print("bcrypt is not installed. Run 'uv add bcrypt' or 'pip install bcrypt'.")
    sys.exit(1)

def hash_password(password: str) -> str:
    """Generates a bcrypt hash string for a plaintext password."""
    salt = bcrypt.gensalt(rounds=12)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password_str: str) -> bool:
    """Verifies a plaintext password against a stored bcrypt hash string."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password_str.encode('utf-8')
        )
    except Exception as e:
        print("Bcrypt check failed:", e)
        return False

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pwd = sys.argv[1]
        print(f"Plaintext Password: {pwd}")
        print(f"Bcrypt Hash:       {hash_password(pwd)}")
    else:
        print("Usage: python generate_hash.py <password>")
        print("\n--- Generating Hashes for Demo Users ---")
        demo_pwds = {
            "OFF001 (Officer)": "OfficerPass123!",
            "LAD001 (Learning Admin)": "AdminPass123!",
            "EMP001 (Employee)": "EmpPass123!"
        }
        for role, pwd in demo_pwds.items():
            print(f"{role:25} -> Password: {pwd:16} -> Hash: {hash_password(pwd)}")

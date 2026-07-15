import os
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

# Create payment key files from environment variables (for Railway deployment)
keys_dir = os.path.join(BASE_DIR, "backend", "payment_keys")
if not os.path.exists(keys_dir):
    os.makedirs(keys_dir)

# App private key
app_key = os.getenv("ALIPAY_APP_PRIVATE_KEY")
if app_key:
    with open(os.path.join(keys_dir, "app_private_key.pem"), "w") as f:
        f.write(app_key.replace("\\n", "\n"))
    print("Created app_private_key.pem from env var")

# Alipay public key
alipay_key = os.getenv("ALIPAY_PUBLIC_KEY")
if alipay_key:
    with open(os.path.join(keys_dir, "alipay_public_key.pem"), "w") as f:
        f.write(alipay_key.replace("\\n", "\n"))
    print("Created alipay_public_key.pem from env var")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting JobBoost on port {port}")
    uvicorn.run("backend.main:app", host="0.0.0.0", port=port, reload=False)

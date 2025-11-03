#!/usr/bin/env python3
"""Test device fingerprint validation"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

# Simulated device fingerprints
DEVICE_FP_1 = "abc123device1fingerprint"
DEVICE_FP_2 = "xyz789device2fingerprint"

def test_device_fingerprint():
    """Test device fingerprint binding and validation"""

    print("="*70)
    print("DEVICE FINGERPRINT VALIDATION TEST")
    print("="*70)

    # Step 1: Login with device fingerprint 1
    print("\n[1] Login with Device Fingerprint 1...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "nasri", "password": "nasri123"},
        headers={"X-Device-Fingerprint": DEVICE_FP_1}
    )

    if login_response.status_code != 200:
        print(f"[FAIL] Login failed: {login_response.text}")
        return

    login_data = login_response.json()
    access_token = login_data['access_token']
    print(f"[OK] Login successful")
    print(f"   Token: {access_token[:50]}...")

    # Step 2: Make request with same device fingerprint (should succeed)
    print("\n[2] Testing /me with SAME device fingerprint...")
    me_response_1 = requests.get(
        f"{BASE_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Device-Fingerprint": DEVICE_FP_1
        }
    )

    if me_response_1.status_code == 200:
        user_data = me_response_1.json()
        print(f"[OK] Access granted with same fingerprint")
        print(f"   User: {user_data['username']} ({user_data['email']})")
    else:
        print(f"[FAIL] Should have succeeded with same fingerprint")
        print(f"   Status: {me_response_1.status_code}")
        print(f"   Response: {me_response_1.text}")

    # Step 3: Make request with different device fingerprint (should fail)
    print("\n[3] Testing /me with DIFFERENT device fingerprint...")
    me_response_2 = requests.get(
        f"{BASE_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
            "X-Device-Fingerprint": DEVICE_FP_2
        }
    )

    if me_response_2.status_code == 401:
        print(f"[OK] Access denied with different fingerprint (token theft detected)")
        print(f"   Message: {me_response_2.json().get('detail', 'N/A')}")
    else:
        print(f"[FAIL] Should have failed with different fingerprint!")
        print(f"   Status: {me_response_2.status_code}")
        print(f"   Response: {me_response_2.text}")

    # Step 4: Make request without device fingerprint (should succeed - optional)
    print("\n[4] Testing /me WITHOUT device fingerprint...")
    me_response_3 = requests.get(
        f"{BASE_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}"
        }
    )

    if me_response_3.status_code == 200:
        print(f"[OK] Access granted without fingerprint (backward compatibility)")
    else:
        print(f"[WARN] Access denied without fingerprint")
        print(f"   Status: {me_response_3.status_code}")
        print(f"   This is acceptable if you want strict fingerprint enforcement")

    # Step 5: Login without fingerprint, then test with fingerprint
    print("\n[5] Login WITHOUT device fingerprint...")
    login_response_2 = requests.post(
        f"{BASE_URL}/auth/login",
        data={"username": "nasri", "password": "nasri123"}
    )

    if login_response_2.status_code != 200:
        print(f"[FAIL] Login failed: {login_response_2.text}")
        return

    login_data_2 = login_response_2.json()
    access_token_2 = login_data_2['access_token']
    print(f"[OK] Login successful without fingerprint")

    # Step 6: Test token without fingerprint with a fingerprint header
    print("\n[6] Testing token (no FP) with fingerprint header...")
    me_response_4 = requests.get(
        f"{BASE_URL}/auth/me",
        headers={
            "Authorization": f"Bearer {access_token_2}",
            "X-Device-Fingerprint": DEVICE_FP_1
        }
    )

    if me_response_4.status_code == 200:
        print(f"[OK] Access granted (token has no fingerprint, so validation skipped)")
    else:
        print(f"[WARN] Access denied")
        print(f"   Status: {me_response_4.status_code}")

    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70)
    print("\nSUMMARY:")
    print("- Tokens can be bound to device fingerprints")
    print("- Fingerprint mismatch blocks access (token theft detection)")
    print("- Fingerprint is optional (backward compatibility)")
    print("- Validation only occurs when both token AND header have fingerprints")
    print("="*70 + "\n")

if __name__ == "__main__":
    test_device_fingerprint()

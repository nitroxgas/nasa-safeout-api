"""Script to test NASA Earthdata authentication."""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 60)
print("NASA Earthdata Authentication Test")
print("=" * 60)

# Check if token is in environment
token = os.getenv("EARTHDATA_TOKEN")

print("\n1. Checking environment variables...")
print(f"   EARTHDATA_TOKEN: {'✓ Set' if token else '✗ Not set'}")

if not token:
    print("\n❌ ERROR: Token not found in .env file")
    print("\nPlease ensure your .env file contains:")
    print("   EARTHDATA_TOKEN=your_token")
    print("\nTo get a token:")
    print("   1. Go to https://urs.earthdata.nasa.gov/profile")
    print("   2. Click 'Generate Token'")
    print("   3. Copy the token to your .env file")
    sys.exit(1)

print(f"\n   Using Token Authentication")
print(f"   Token: {token[:50]}..." if len(token) > 50 else f"   Token: {token}")

# Try to import earthaccess
print("\n2. Checking earthaccess library...")
try:
    import earthaccess
    print("   ✓ earthaccess is installed")
except ImportError:
    print("   ✗ earthaccess is NOT installed")
    print("\nPlease install it:")
    print("   pip install earthaccess")
    sys.exit(1)

# Try to authenticate
print("\n3. Testing authentication with NASA Earthdata...")
try:
    # Set environment variable for earthaccess
    os.environ["EARTHDATA_TOKEN"] = token
    print("   Using token authentication...")
    
    # Try to login
    auth = earthaccess.login(strategy="environment", persist=True)
    
    if auth and auth.authenticated:
        print("   ✓ Authentication SUCCESSFUL!")
        print(f"   Authenticated using token")
    else:
        print("   ✗ Authentication FAILED")
        print("\nPossible issues:")
        print("   1. Invalid or expired token")
        print("   2. Token not properly formatted")
        print("   3. Network issues")
        print("\nPlease verify:")
        print("   1. Generate a new token at https://urs.earthdata.nasa.gov/profile")
        print("   2. Update your .env file with the new token")
        sys.exit(1)
        
except Exception as e:
    print(f"   ✗ Authentication ERROR: {e}")
    print("\nPossible issues:")
    print("   1. Invalid or expired token")
    print("   2. Network connectivity")
    print("   3. NASA Earthdata service unavailable")
    print("\nPlease verify:")
    print("   1. Your token at https://urs.earthdata.nasa.gov/profile")
    print("   2. Your internet connection")
    sys.exit(1)

# Try to search for data
print("\n4. Testing data search...")
try:
    from datetime import datetime, timedelta
    
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(days=1)
    
    # Try a simple search
    results = earthaccess.search_data(
        short_name="GPM_3IMERGHHE",
        temporal=(start_time.strftime("%Y-%m-%d"), end_time.strftime("%Y-%m-%d")),
        count=1
    )
    
    if results:
        print(f"   ✓ Data search SUCCESSFUL!")
        print(f"   Found {len(results)} granule(s)")
    else:
        print("   ⚠ No data found (this is normal, depends on date/location)")
        
except Exception as e:
    print(f"   ✗ Data search ERROR: {e}")
    print("\nThis might indicate:")
    print("   1. You need to approve applications at NASA Earthdata")
    print("   2. Dataset access restrictions")

# Check if applications need approval
print("\n5. Important: Application Approvals")
print("   NASA Earthdata requires you to approve applications for each dataset.")
print("\n   Please visit and approve these applications:")
print("   1. Go to: https://urs.earthdata.nasa.gov/profile")
print("   2. Click on 'Applications > Authorized Apps'")
print("   3. Search and approve:")
print("      - NASA GESDISC DATA ARCHIVE (for GPM IMERG)")
print("      - GES DISC (for MERRA-2)")
print("      - Copernicus Sentinel Data (for TROPOMI)")
print("\n   Or simply search for data once, and approve when prompted.")

print("\n" + "=" * 60)
print("✓ Authentication test completed!")
print("=" * 60)

print("\nNext steps:")
print("1. If authentication failed, check your credentials")
print("2. Approve required applications at NASA Earthdata")
print("3. Restart your API server")
print("4. Test the API endpoints")

print("\nTo test the API:")
print("   uvicorn app.main:app --reload")
print("   Then visit: http://localhost:8000/test")

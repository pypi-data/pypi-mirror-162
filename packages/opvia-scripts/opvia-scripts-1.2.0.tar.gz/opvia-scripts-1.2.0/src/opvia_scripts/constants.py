#: Firebase creds API key
import os

#: Full name of Opvia service plugin entry points
OPVIA_SERVICES_ENTRY_POINT_NAME = "opvia.services"

#: Name of special OpviaContextEntity entity added to an entity mapping
OPVIA_CONTEXT = "__OPVIA_CONTEXT"

#: Firebase creds API key
FIREBASE_API_KEY: str = os.environ.get("FIREBASE_API_KEY", "")

#: Firebase creds auth domain
FIREBASE_AUTH_DOMAIN: str = os.environ.get("FIREBASE_AUTH_DOMAIN", "")

#: Firebase creds database URL
FIREBASE_DATABASE_URL: str = os.environ.get("FIREBASE_DATABASE_URL", "")

#: Firebase creds storage bucket
FIREBASE_STORAGE_BUCKET: str = os.environ.get("FIREBASE_STORAGE_BUCKET", "")

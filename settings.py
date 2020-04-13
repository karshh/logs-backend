from dotenv import load_dotenv
import os
load_dotenv()

# OR, the same with increased verbosity
load_dotenv(verbose=True)

# OR, explicitly providing path to '.env'
from pathlib import Path  # python3 only
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

MONGO_URL = os.getenv("MONGO_URL")
TEST_MONGO_URL = os.getenv("TEST_MONGO_URL")
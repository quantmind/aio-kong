import dotenv
import os

dotenv.load_dotenv()


if not os.environ.get("PYTHON_ENV"):
    os.environ["PYTHON_ENV"] = "test"

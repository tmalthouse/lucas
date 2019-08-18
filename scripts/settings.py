from pathlib import Path

# ROOT_DIR = Path("/Users/Thomas/Documents/Reed/current/")
# The working directory is the parent directory of the scripts folder (that this file lives in)
ROOT_DIR = Path(__file__).parents[1]
print("Working directory is {}".format(ROOT_DIR))
DATA_DIR = ROOT_DIR / "data"
FIG_DIR = ROOT_DIR / "figures"

FNGEN_ID = "MY4800"
SCOPE_ID = "C044859"
METER_ID = "MY47021202"


AIRM_SPEED_PREFIX = "Intel(R) AI Reference Models -"
AIRM_IPX_PREFIX = "Intel(R)AIReferenceModels"
AIRM_IP_LIBRARY = "frameworks_ai"
AIRM_REQUIREMENTS_FILE = "3.2_requirements.txt.files.txt"
ROOT_STR_LEN = "./".__len__()
REQUIREMENTS_STR_LEN = "/requirements.txt".__len__()
DEBUG=False

def info(msg):
  print (f"INFO: {msg}")

def debug (msg):
  if DEBUG:
    print (f"{msg}")

def error (msg):
  print (f"ERROR! {msg}")
  exit(1)

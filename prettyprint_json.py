import sys
import json
with open(sys.argv[1]) as f:
  data = json.load(f)
  print(json.dumps(data, indent=2))
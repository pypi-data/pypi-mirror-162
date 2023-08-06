import os
import sys
from fbp.builder import *

# ---------------------------
#  BuildPy
# ---------------------------
def main() -> int:
  argv = sys.argv

  try:
    builder = Builder()

    return builder.run(argv)
  except FileNotFoundError as e:
    print(f'cannot open file "{e.filename}"')
  except Exception as e:
    print(f'unhandled exception have been occurred:\n\nmsg: {e.args}')
  
  return -1

# ------

if __name__ == '__main__':
  main()
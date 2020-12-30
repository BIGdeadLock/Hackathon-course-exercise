import sys, select, os
import getch

print("You have ten seconds to answer!")
i, o, e = select.select( [sys.stdin], [], [], 7)
os.system("stty raw -echo")
if i:
  c = sys.stdin.read(1)
  print("CHAR ", c)
print("nothing typed")
os.system("stty -raw -echo")

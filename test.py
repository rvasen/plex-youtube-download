import sys
from io import StringIO

backup = sys.stdout
sys.stdout = StringIO()

status_string = ('  {:,} Bytes [{:.2%}] received. Rate: [{:4.0f} '
                         'KB/s].  ETA: [{:.0f} secs]')
bytesdone = 100
total = 1000
rate=24
eta=3284
progress_stats = (bytesdone, bytesdone * 1.0 / total, rate, eta)
status = status_string.format(*progress_stats)
sys.stdout.write("\r" + status + ' ' * 4 + "\r")

out = sys.stdout.getvalue()

sys.stdout.close()
sys.stdout = backup

print(out)

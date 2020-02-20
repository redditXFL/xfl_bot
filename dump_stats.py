import csv
from utils import stats

tt_headers = []
tt_csv = []
tt_f = csv.writer(open("team_totals.csv", "w+"))

o_headers = []
o_csv = []
o_f = csv.writer(open("offense.csv", "w+"))

d_headers = []
d_csv = []
d_f = csv.writer(open("defense.csv", "w+"))

p_headers = []
p_csv = []
p_f = csv.writer(open("plays.csv", "w+"))

po_headers = []
po_csv = []
po_f = csv.writer(open("possessions.csv", "w+"))

game_id = 1
while True:
    print("Getting Game: %d" % game_id)
    data = stats.stats_as_csv(game_id=game_id)
    game_id += 1
    if data is None:
        break

    tt, o, d, p, po = data

    tt_headers = tt[0]
    tt_csv += tt[1]

    o_headers = o[0]
    o_csv += o[1]

    d_headers = d[0]
    d_csv += d[1]

    p_headers = p[0]
    p_csv += p[1]

    po_headers = po[0]
    po_csv += po[1]

tt_f.writerow(tt_headers)
tt_f.writerows(tt_csv)

o_f.writerow(o_headers)
o_f.writerows(o_csv)

d_f.writerow(d_headers)
d_f.writerows(d_csv)

p_f.writerow(p_headers)
p_f.writerows(p_csv)

po_f.writerow(po_headers)
po_f.writerows(po_csv)
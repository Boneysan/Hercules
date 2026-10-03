#!/usr/bin/env python3
"""probe.py map:cx:cy[:R] ... -> prints clear walkable tiles (3x3 all passable) nearest each center.
One temporary NPC per center (keeps each scan under the script instruction limit)."""
import sys,subprocess,re,os
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)+os.sep
spec=[a.split(':') for a in sys.argv[1:]]
src=''
for i,(m,x,y,*r) in enumerate(spec):
    R=int(r[0]) if r else 7
    src+='''-\tscript\tZZProbe%d\tFAKE_NPC,{
OnInit:
\t.@n = 0; .@out$ = "";
\tfor (.@d = 0; .@d <= %d && .@n < 5; ++.@d) {
\t\tfor (.@dx = -.@d; .@dx <= .@d && .@n < 5; ++.@dx) {
\t\t\t.@step = (.@dx == -.@d || .@dx == .@d) ? 1 : 2 * .@d;
\t\t\tfor (.@dy = -.@d; .@dy <= .@d && .@n < 5; .@dy += .@step) {
\t\t\t\t.@x = %s + .@dx; .@y = %s + .@dy;
\t\t\t\tif (!checkcell("%s", .@x, .@y, cell_chkpass)) continue;
\t\t\t\t.@out$ += " (" + .@x + "," + .@y + ")"; ++.@n;
\t\t\t}
\t\t}
\t}
\tconsolemes(CONSOLEMES_INFO, "PROBE %s near %s,%s:%%s", (.@out$ == "" ? " none" : .@out$));
\tend;
}
'''%(i,R,x,y,m,m,x,y)
path=root+'npc/custom/zz_probe.txt'; conf=root+'npc/scripts_custom.conf'
orig=open(conf).read(); open(path,'w').write(src)
open(conf,'w').write(orig.replace('"npc/custom/f15_elites.txt",','"npc/custom/f15_elites.txt",\n"npc/custom/zz_probe.txt",',1))
try:
    out=subprocess.run(['./map-server','--run-once'],cwd=root,capture_output=True,text=True,timeout=300)
    for l in (out.stdout+out.stderr).replace('\r','\n').split('\n'):
        if 'PROBE' in l: print(re.sub(r'.*PROBE','PROBE',l))
        elif 'infinity' in l: print(l[:120])
finally:
    open(conf,'w').write(orig); os.remove(path)

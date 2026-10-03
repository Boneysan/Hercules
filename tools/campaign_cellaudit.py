#!/usr/bin/env python3
"""cellaudit.py FILE... : for every 'map,x,y,f script Name' in the files, report whether the
cell is passable and, if not, the nearest clear passable cells (via map-server --run-once)."""
import sys,re,subprocess,os
root=os.path.join(os.path.dirname(os.path.abspath(__file__)),os.pardir)+os.sep
cells=[]
for f in sys.argv[1:]:
    for l in open(f,encoding='utf-8',errors='replace'):
        m=re.match(r'^(\w+),(\d+),(\d+),\d+\tscript\t([^\t]+)\t',l)
        if m: cells.append((m.group(1),int(m.group(2)),int(m.group(3)),m.group(4).split('#')[0],os.path.basename(f)))
src=''
for i,(mp,x,y,name,f) in enumerate(cells):
    src+='''-\tscript\tZZCell%d\tFAKE_NPC,{
OnInit:
\tif (checkcell("%s", %d, %d, cell_chkpass)) { consolemes(CONSOLEMES_INFO, "CELL ok %s,%d,%d %s"); end; }
\t.@n = 0; .@out$ = "";
\tfor (.@d = 1; .@d <= 8 && .@n < 3; ++.@d) {
\t\tfor (.@dx = -.@d; .@dx <= .@d && .@n < 3; ++.@dx) {
\t\t\t.@step = (.@dx == -.@d || .@dx == .@d) ? 1 : 2 * .@d;
\t\t\tfor (.@dy = -.@d; .@dy <= .@d && .@n < 3; .@dy += .@step) {
\t\t\t\tif (!checkcell("%s", %d + .@dx, %d + .@dy, cell_chkpass)) continue;
\t\t\t\t.@out$ += " (" + (%d + .@dx) + "," + (%d + .@dy) + ")"; ++.@n;
\t\t\t}
\t\t}
\t}
\tconsolemes(CONSOLEMES_INFO, "CELL BAD %s,%d,%d %s -> try%%s", (.@out$ == "" ? " none within 8" : .@out$));
\tend;
}
'''%(i,mp,x,y,mp,x,y,name,mp,x,y,x,y,mp,x,y,name)
path=root+'npc/custom/zz_probe.txt'; conf=root+'npc/scripts_custom.conf'
orig=open(conf).read(); open(path,'w').write(src)
open(conf,'w').write(orig.replace('"npc/custom/f15_elites.txt",','"npc/custom/f15_elites.txt",\n"npc/custom/zz_probe.txt",',1))
try:
    out=subprocess.run(['./map-server','--run-once'],cwd=root,capture_output=True,text=True,timeout=300)
    for l in (out.stdout+out.stderr).replace('\r','\n').split('\n'):
        if 'CELL' in l: print(re.sub(r'.*CELL','CELL',l))
finally:
    open(conf,'w').write(orig); os.remove(path)

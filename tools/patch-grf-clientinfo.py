#!/usr/bin/env python3
"""
patch-grf-clientinfo.py — set the server <address> inside the client's
GRF-embedded data\\clientinfo.xml file(s).

WHY THIS EXISTS
---------------
This client build reads `data\\clientinfo.xml` from INSIDE the GRFs, NOT from the
loose `data/clientinfo.xml` on disk (the "Read Data Folder First" client patch is
not applied). Editing the loose file has NO effect.

GRF precedence follows `DATA.INI` order and the LOWER index wins. More than one GRF
can carry its own embedded clientinfo — in this client both `renewal2021.grf` (#1)
and `data.grf` (#3) did, and #1 wins. So every GRF that contains an embedded
clientinfo must be patched to the same address, or the lowest-index stale one keeps
winning. Symptom of getting this wrong: a remote player "fails to connect to server"
even though TNC/ping to the host is fine and the firewall is open — because their
client is really dialing the embedded 127.0.0.1 (i.e. their own machine).

This tool scans the GRFs listed in DATA.INI, finds every embedded
`data\\clientinfo.xml`, and rewrites the <address> to the IP you give — in place,
with a reversible backup of the small file-table region, verified by re-reading.
Entries are written UNENCRYPTED (GRF flag 0x01), which the client reads fine, so we
never have to implement GRF's DES cipher.

USAGE
-----
  python3 tools/patch-grf-clientinfo.py --show                 # report current addresses
  python3 tools/patch-grf-clientinfo.py 192.168.20.60          # set LAN IP in every GRF + loose file
  python3 tools/patch-grf-clientinfo.py 127.0.0.1              # back to single-PC
  python3 tools/patch-grf-clientinfo.py <IP> --client /mnt/h/RO/client

After patching, players must fully relaunch the client (GRFs load on start). Hand a
friend the patched `renewal2021.grf` (smallest winning GRF) — or the whole client.
"""
import argparse, os, re, struct, sys, zlib

DEFAULT_CLIENT = "/mnt/h/RO/client"
ENTRY = b"data\\clientinfo.xml"
ADDR_RE = re.compile(rb"(<address>)([^<]*)(</address>)")

# Minimal valid clientinfo, used only if we must replace a DES-encrypted entry we
# cannot decode. Real content is preserved verbatim whenever the entry is readable.
TEMPLATE = (
    b'<?xml version="1.0" encoding="euc-kr" ?>\n<clientinfo>\n'
    b'    <desc>RO Local Server</desc>\n    <servicetype>korea</servicetype>\n'
    b'    <servertype>primary</servertype>\n    <hideaccountlist/>\n'
    b'    <passwordencrypt/>\n    <passwordencrypt2/>\n    <extendedslot/>\n'
    b'    <readfolder/>\n    <server>\n        <display>Local Server</display>\n'
    b'        <address>__IP__</address>\n        <port>6900</port>\n'
    b'        <version>55</version>\n        <langtype>1</langtype>\n        <new/>\n'
    b'    </server>\n</clientinfo>\n'
)


def grf_order(client):
    """Return GRF paths in DATA.INI order (lower index first = higher priority)."""
    ini = None
    for cand in ("DATA.INI", "data.ini"):
        p = os.path.join(client, cand)
        if os.path.exists(p):
            ini = p
            break
    names = []
    if ini:
        with open(ini, "r", errors="ignore") as f:
            for line in f:
                m = re.match(r"\s*(\d+)\s*=\s*(\S+\.grf)", line, re.I)
                if m:
                    names.append((int(m.group(1)), m.group(2)))
        names = [n for _, n in sorted(names)]
    if not names:  # fallback
        names = ["renewal2021.grf", "resources2021.grf", "data.grf", "rdata.grf"]
    return [os.path.join(client, n) for n in names if os.path.exists(os.path.join(client, n))]


def read_table(f):
    f.seek(0)
    h = f.read(46)
    toff, seed, fc, ver = struct.unpack("<IIII", h[30:46])
    if ver != 0x200:
        raise ValueError(f"unsupported GRF version 0x{ver:x}")
    f.seek(toff + 46)
    cl, ul = struct.unpack("<II", f.read(8))
    table = bytearray(zlib.decompress(f.read(cl)))
    assert len(table) == ul
    return toff, table


def find_entry(table):
    pos = 0
    while pos < len(table):
        end = table.index(b"\x00", pos)
        name = bytes(table[pos:end])
        meta = end + 1
        cs, ca, rs, fl, off = struct.unpack("<IIIBI", table[meta:meta + 17])
        if name.lower() == ENTRY.lower():
            return meta, (cs, ca, rs, fl, off)
        pos = meta + 17
    return None, None


def current_address(path):
    with open(path, "rb") as f:
        try:
            toff, table = read_table(f)
        except ValueError:
            return None
        meta, m = find_entry(table)
        if meta is None:
            return None
        cs, ca, rs, fl, off = m
        if fl != 1:
            return f"(flags={fl} DES-encrypted, unreadable)"
        f.seek(off + 46)
        content = zlib.decompress(f.read(cs))
    mm = ADDR_RE.search(content)
    return mm.group(2).decode("latin-1") if mm else "(no <address>)"


def patch(path, ip, backup):
    with open(path, "rb") as f:
        toff, table = read_table(f)
        meta, m = find_entry(table)
        if meta is None:
            return None  # no embedded clientinfo here
        cs, ca, rs, fl, off = m
        if fl == 1:
            f.seek(off + 46)
            old = zlib.decompress(f.read(cs))
            if ADDR_RE.search(old):
                new_content = ADDR_RE.sub(lambda x: x.group(1) + ip.encode() + x.group(3), old)
            else:
                new_content = TEMPLATE.replace(b"__IP__", ip.encode())
        else:  # DES-encrypted: can't read it, substitute a clean template
            new_content = TEMPLATE.replace(b"__IP__", ip.encode())

    new_blob = zlib.compress(new_content, 9)
    table[meta:meta + 17] = struct.pack("<IIIBI", len(new_blob), len(new_blob), len(new_content), 1, toff)
    new_tc = zlib.compress(bytes(table), 9)
    tail = struct.pack("<II", len(new_tc), len(table)) + new_tc

    with open(path, "rb") as f:
        f.seek(toff + 46)
        orig_tail = f.read()
    with open(backup, "wb") as b:
        b.write(struct.pack("<I", toff))
        b.write(orig_tail)

    with open(path, "r+b") as f:
        f.seek(toff + 46)
        f.write(new_blob)
        f.write(tail)
        f.truncate()
        f.seek(30)
        f.write(struct.pack("<I", toff + len(new_blob)))

    got = current_address(path)
    if got != ip:
        with open(backup, "rb") as b:
            oo = struct.unpack("<I", b.read(4))[0]
            ot = b.read()
        with open(path, "r+b") as f:
            f.seek(oo + 46)
            f.write(ot)
            f.truncate()
            f.seek(30)
            f.write(struct.pack("<I", oo))
        raise RuntimeError(f"verify failed for {path} (got {got!r}); restored original")
    return got


def main():
    ap = argparse.ArgumentParser(description="Patch server <address> in GRF-embedded clientinfo.xml")
    ap.add_argument("ip", nargs="?", help="target server IP (e.g. 192.168.20.60 or 127.0.0.1)")
    ap.add_argument("--client", default=DEFAULT_CLIENT, help=f"client dir (default {DEFAULT_CLIENT})")
    ap.add_argument("--show", action="store_true", help="only report current embedded addresses")
    args = ap.parse_args()

    grfs = grf_order(args.client)
    if not grfs:
        sys.exit(f"No GRFs found under {args.client}")

    print(f"Client: {args.client}\nGRF load order (lower index wins):")
    for i, g in enumerate(grfs, 1):
        addr = current_address(g)
        tag = "" if addr is None else f"  clientinfo <address>={addr}"
        print(f"  {i}. {os.path.basename(g)}{tag if addr else '  (no embedded clientinfo)'}")

    if args.show or not args.ip:
        if not args.ip:
            print("\n(no IP given — showing only. Pass an IP to patch.)")
        return

    print(f"\nPatching embedded clientinfo -> {args.ip}")
    changed = 0
    for g in grfs:
        bak = g + ".tablebak"
        res = patch(g, args.ip, bak)
        if res is not None:
            print(f"  {os.path.basename(g)}: OK -> {res}")
            changed += 1
            if os.path.exists(bak):
                os.remove(bak)

    # keep the loose file consistent too (harmless, and correct if a client ever
    # does read the folder)
    for cand in ("data/clientinfo.xml", "data/sclientinfo.xml"):
        p = os.path.join(args.client, cand)
        if os.path.exists(p):
            with open(p, "rb") as f:
                c = f.read()
            if ADDR_RE.search(c):
                with open(p, "wb") as f:
                    f.write(ADDR_RE.sub(lambda x: x.group(1) + args.ip.encode() + x.group(3), c))
                print(f"  {cand}: OK -> {args.ip}")

    print(f"\nDone. {changed} GRF(s) patched. Players must fully relaunch the client.")


if __name__ == "__main__":
    main()

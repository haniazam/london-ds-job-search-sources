#!/usr/bin/env python3
"""Comp enrichment for the London DS refresh (run after refresh_roles.py).

Adds an "Approx London TC" column with a THREE-TIER figure, always labelled:
  1. posted   — the employer's own range, from structured ATS fields (Greenhouse
                pay_input_ranges, Ashby compensation tiers, Lever salaryRange,
                SmartRecruiters jobAd) or a £-range regex over the posting text;
  2. sourced  — a company-level figure from Levels.fyi / Glassdoor / an aggregator
                of the listing, kept in pay_overrides.json with its source + date;
  3. market   — a band around the ITJobsWatch London median for the title
                (-15%/+25%), fetched live; falls back to the 2026-10 medians.

Usage: python3 pay_enrich.py [/tmp/ldn_ds_active.csv]  ->  /tmp/ldn_ds_active_pay.csv
"""
import json,re,sys,html,time,urllib.request,urllib.error
UA={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36","Accept":"application/json, text/html"}
def get(u,t=25):
    try:
        with urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t) as f: return f.status,f.read().decode("utf-8","replace")
    except urllib.error.HTTPError as e: return e.code,""
    except Exception as e: return -1,type(e).__name__
def strip(h): return html.unescape(re.sub(r"<[^>]+>"," ",h or ""))
NUM=r"(\d{2,3})(?:[,.](\d{3}))?\s?(k|K)?"
def tok(n,th,k):
    v=int(n+(th or "")); 
    if k and not th: v*=1000
    if v<1000: v*=1000
    return v
RANGE=re.compile(r"(?:£|GBP\s?)\s?"+NUM+r"\s*(?:-|–|—|to|and)\s*(?:£|GBP\s?)?\s?"+NUM,re.I)
UPTO=re.compile(r"(?:up to|upto|maximum of)\s*(?:£|GBP\s?)\s?"+NUM,re.I)
FROM=re.compile(r"(?:from|starting at|minimum of)\s*(?:£|GBP\s?)\s?"+NUM,re.I)
SAL=re.compile(r"(?:salary|compensation|pay|base)[^£\n]{0,60}(?:£|GBP\s?)\s?"+NUM,re.I)
def extract(txt):
    txt=txt or ""
    m=RANGE.search(txt)
    if m:
        lo,hi=tok(m.group(1),m.group(2),m.group(3)),tok(m.group(4),m.group(5),m.group(6))
        if 25000<=lo<hi<=600000: return lo,hi,"posted range"
    m=UPTO.search(txt)
    if m:
        hi=tok(m.group(1),m.group(2),m.group(3))
        if 30000<=hi<=600000: return None,hi,"posted (up to)"
    m=FROM.search(txt)
    if m:
        lo=tok(m.group(1),m.group(2),m.group(3))
        if 25000<=lo<=400000: return lo,None,"posted (from)"
    m=SAL.search(txt)
    if m:
        v=tok(m.group(1),m.group(2),m.group(3))
        if 30000<=v<=400000: return v,v,"posted (figure)"
    return None
import csv,os
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=sys.argv[1] if len(sys.argv)>1 else "/tmp/ldn_ds_active.csv"
rows=[]
with open(SRC,newline="",encoding="utf-8") as f:
    for rec in csv.DictReader(f):
        if not rec.get("Apply URL (unique active post)","").startswith("http"): continue
        rows.append({"company":rec["Company"],"title":rec["Role"],"level":rec["Level"],"url":rec["Apply URL (unique active post)"],"via":"","pay":"","_rec":rec})
OVR=json.load(open(os.path.join(HERE,"pay_overrides.json")))
ashby_cache={}
hits=0
for r in rows:
    if "(posted)" in r.get("pay",""): continue
    u=r["url"]; found=None; src=r["via"]
    try:
        if "greenhouse" in u or "gh_jid" in u or "coinbase.com/careers" in u or "ocadogroup" in u:
            m=re.search(r"greenhouse\.io/([^/]+)/jobs/(\d+)",u); jid=(m.group(2) if m else (re.search(r"gh_jid=(\d+)",u) or re.search(r"positions/(\d+)",u)).group(1))
            tokmap={"ocadogroup.com":"ocadogroup","coinbase.com":"coinbase","boards.greenhouse.io/wheely":"wheely"}
            board=m.group(1) if m else next((v for k,v in tokmap.items() if k in u),None)
            if board:
                s,b=get(f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs/{jid}?questions=false")
                if s==200:
                    d=json.loads(b)
                    pr=d.get("pay_input_ranges") or []
                    if pr:
                        p=pr[0]; lo=p.get("min_cents"); hi=p.get("max_cents"); cur=p.get("currency_type","")
                        if lo and hi: found=(lo//100,hi//100,f"posted range ({cur})")
                    if not found: found=extract(strip(d.get("content","")))
        elif "ashbyhq.com" in u:
            org=re.search(r"ashbyhq\.com/([^/]+)/",u).group(1)
            if org not in ashby_cache:
                s,b=get(f"https://api.ashbyhq.com/posting-api/job-board/{org}?includeCompensation=true"); ashby_cache[org]=json.loads(b).get("jobs",[]) if s==200 else []
            for j in ashby_cache[org]:
                if j.get("jobUrl","").split("?")[0]==u.split("?")[0]:
                    comp=j.get("compensation") or {}
                    summ=comp.get("compensationTierSummary") or comp.get("scrapeableCompensationSalarySummary") or ""
                    tiers=comp.get("compensationTiers") or []
                    if tiers:
                        c=tiers[0].get("components",[{}])[0]; lo=c.get("minValue"); hi=c.get("maxValue"); cur=c.get("currencyCode","")
                        if lo and hi: found=(int(lo),int(hi),f"posted range ({cur})")
                    if not found and summ: found=extract(summ) or extract(summ.replace("GBP","£"))
                    if not found: found=extract(strip(j.get("descriptionHtml","")))
        elif "lever.co" in u:
            m=re.search(r"lever\.co/([^/]+)/([0-9a-f-]+)",u)
            s,b=get(f"https://api.lever.co/v0/postings/{m.group(1)}/{m.group(2)}")
            if s==200:
                d=json.loads(b); sr=d.get("salaryRange") or {}
                if sr.get("min") and sr.get("max"): found=(int(sr["min"]),int(sr["max"]),f"posted range ({sr.get('currency','')})")
                if not found: found=extract(d.get("descriptionPlain") or strip(d.get("description","")))
        elif "smartrecruiters.com" in u:
            m=re.search(r"smartrecruiters\.com/([^/]+)/(\d+)",u)
            s,b=get(f"https://api.smartrecruiters.com/v1/companies/{m.group(1)}/postings/{m.group(2)}")
            if s==200:
                d=json.loads(b); secs=(d.get("jobAd") or {}).get("sections") or {}
                txt=" ".join(strip(v.get("text","")) for v in secs.values() if isinstance(v,dict))
                found=extract(txt)
        else:
            s,b=get(u,35)
            if s==200: found=extract(strip(b))
    except Exception as e: pass
    if found:
        lo,hi,how=found; hits+=1
        r["pay2"]={"lo":lo,"hi":hi,"how":how}
        print(f"  + {r['company'][:22]:22s} | {r['title'][:40]:40s} | {('£%dk'%(lo//1000)) if lo else '?'}–{('£%dk'%(hi//1000)) if hi else '?'} | {how}")
print(f"\nSTRUCTURED/TEXT PAY: +{hits} new posted figures (beyond the 5 already found)")
pass

print("\n=== ITJOBSWATCH London market bands (median / 10th–90th pct, last 6 months) ===")
bands={}
for title in ["data scientist","senior data scientist","lead data scientist","principal data scientist","staff data scientist","head of data science","data science manager"]:
    slug=title.replace(" ","%20")
    s,b=get(f"https://www.itjobswatch.co.uk/jobs/london/{slug}.do")
    if s!=200: print(f"  {title}: HTTP {s}"); continue
    t=strip(b); t=re.sub(r"\s+"," ",t)
    med=re.search(r"Median annual salary[^£]{0,80}£\s?([\d,]+)",t) or re.search(r"Median[^£]{0,40}£\s?([\d,]+)",t)
    p10=re.search(r"10th Percentile[^£]{0,60}£\s?([\d,]+)",t); p90=re.search(r"90th Percentile[^£]{0,60}£\s?([\d,]+)",t)
    p25=re.search(r"25th Percentile[^£]{0,60}£\s?([\d,]+)",t); p75=re.search(r"75th Percentile[^£]{0,60}£\s?([\d,]+)",t)
    g=lambda m:int(m.group(1).replace(",","")) if m else None
    bands[title]={"median":g(med),"p10":g(p10),"p25":g(p25),"p75":g(p75),"p90":g(p90)}
    print(f"  {title:26s} median={g(med)} p10={g(p10)} p25={g(p25)} p75={g(p75)} p90={g(p90)}")

# ---- three-tier comp: posted > company-sourced override > ITJobsWatch market band ----
FALLBACK={"data scientist":90000,"senior data scientist":95000,"lead data scientist":100000,"principal data scientist":100000,"head of data science":125000}
def band_key(t):
    t=t.lower()
    if "head of" in t: return "head of data science"
    if re.search(r"principal|staff",t): return "principal data scientist"
    if "lead" in t or "manager" in t: return "lead data scientist"
    if re.search(r"senior|\bsr\b",t): return "senior data scientist"
    return "data scientist"
OUT=SRC.replace(".csv","_pay.csv")
with open(OUT,"w",newline="",encoding="utf-8") as f:
    w=csv.writer(f); first=rows[0]["_rec"] if rows else {}
    cols=list(first.keys()); cols.insert(3,"Approx London TC"); w.writerow(cols)
    for r in rows:
        p2=r.get("pay2"); comp=None
        if p2 and p2.get("lo") and p2.get("hi") and p2["lo"]!=p2["hi"]: comp=f"£{p2['lo']//1000}k–£{p2['hi']//1000}k (posted)"
        elif p2 and (p2.get("lo") or p2.get("hi")):
            v=(p2.get("lo") or p2.get("hi"))//1000; comp=(f"up to £{v}k" if "up to" in p2.get("how","") else f"from £{v}k")+" (posted)"
        if not comp:
            for o in OVR:
                if o["company"].lower()==r["company"].lower() and re.search(o["title_regex"],r["title"]):
                    comp=f"£{o['lo']}k–£{o['hi']}k ({o['label']})"; break
        if not comp:
            k=band_key(r["title"]); med=(bands.get(k) or {}).get("median") or FALLBACK[k]
            comp=f"£{int(med*0.85)//1000}k–£{int(med*1.25)//1000}k (market est.; ITJobsWatch London median £{med//1000}k for {k})"
        rec=dict(r["_rec"]); vals=[rec[c] if c!="Approx London TC" else comp for c in cols]; w.writerow(vals)
print(f"WROTE {OUT} with a three-tier Approx London TC column for {len(rows)} roles")

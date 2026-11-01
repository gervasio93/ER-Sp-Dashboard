"""Genera index.html a partir de template.html y los datos de data/.

Uso:
  python3 build.py           # actualiza divisas (fx.json) y regenera index.html
  python3 build.py --no-fx   # solo regenera index.html

Las divisas salen del paquete npm @fawazahmed0/currency-api (una versión por día).
El calendario deportivo está en data/eventos.json y se edita a mano o con la tarea diaria.
"""
import datetime, io, json, sys, tarfile, urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parent
FX = ROOT / "data" / "fx.json"
EV = ROOT / "data" / "eventos.json"
REG = "https://registry.npmjs.org/@fawazahmed0/currency-api"


def fetch_day(reg, tag):
    url = reg["versions"][reg["dist-tags"][tag]]["dist"]["tarball"]
    for _ in range(3):
        try:
            data = urllib.request.urlopen(url, timeout=60).read()
            tf = tarfile.open(fileobj=io.BytesIO(data))
            e = json.load(tf.extractfile("package/v1/currencies/eur.min.json"))["eur"]
            return tag, {"usd": e["usd"], "clp": e["clp"], "uyu": e["uyu"]}
        except Exception:
            pass
    return tag, None


def update_fx():
    fx = json.loads(FX.read_text()) if FX.exists() else {}
    reg = json.load(urllib.request.urlopen(REG, timeout=60))
    today = datetime.date.today()
    tags = [t for t in reg["dist-tags"] if t != "latest"]
    wanted = []
    for t in tags:
        d = datetime.date.fromisoformat(t)
        keep = (today - d).days <= 200 or d.weekday() == 0
        if keep and t not in fx:
            wanted.append(t)
    with ThreadPoolExecutor(8) as ex:
        for tag, val in ex.map(lambda t: fetch_day(reg, t), wanted):
            if val:
                fx[tag] = val
    # recorta: diario solo en los últimos 200 días, semanal (lunes) antes
    out = {}
    for t in sorted(fx):
        d = datetime.date.fromisoformat(t)
        if (today - d).days <= 200 or d.weekday() == 0:
            out[t] = fx[t]
    FX.write_text(json.dumps(out))
    print(f"fx: {len(wanted)} días nuevos, último {max(out)}")


def render():
    fx = json.loads(FX.read_text())
    k = sorted(fx)
    packed = {
        "dates": k,
        "usd": [round(fx[x]["usd"], 6) for x in k],
        "clp": [round(fx[x]["clp"], 3) for x in k],
        "uyu": [round(fx[x]["uyu"], 4) for x in k],
    }
    ev = json.loads(EV.read_text())
    html = (ROOT / "template.html").read_text()
    html = html.replace("__FX__", json.dumps(packed, separators=(",", ":")))
    html = html.replace("__SPORT__", json.dumps(ev, ensure_ascii=False, separators=(",", ":")))
    (ROOT / "index.html").write_text(html)
    print("index.html generado")


if __name__ == "__main__":
    if "--no-fx" not in sys.argv:
        update_fx()
    render()

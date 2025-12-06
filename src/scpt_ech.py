import datetime
import json
import os
from typing import Iterable, Tuple

# Third-party
import numpy as np
import pandas as pd

# import local files
import preprocessfns as fns


CLOUDFLARE_TOKEN = "cloudflare"


def _safe_parse_json(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    if isinstance(value, (dict, list)):
        return value
    if isinstance(value, str):
        text = value.strip()
        if not text or text == "{}":
            return None
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return None
    return None


def _safe_load_https_json(value):
    data = _safe_parse_json(value)
    return data if isinstance(data, dict) else {}


def _extract_https_ech(https_dict):
    if not isinstance(https_dict, dict):
        return np.nan
    if not fns.if_key_exists(https_dict, "HTTPS"):
        return np.nan
    try:
        return fns.get_https_fields(https_dict, "HTTPS", "svcb.ech")
    except Exception:
        return np.nan


def _base_domain(name: str, labels: int = 2) -> str | None:
    if not isinstance(name, str):
        return None
    stripped = name.strip().rstrip(".")
    if not stripped:
        return None
    parts = stripped.split(".")
    if len(parts) <= labels:
        return stripped.lower()
    return ".".join(parts[-labels:]).lower()


def _extract_ns_providers(ns_field) -> Tuple[str, ...]:
    data = _safe_parse_json(ns_field)
    ns_names: Iterable[str] = []

    if isinstance(data, dict):
        candidates = data.get("NS") or data.get("ns") or []
        if isinstance(candidates, str):
            ns_names = [candidates]
        else:
            ns_names = candidates
    elif isinstance(data, list):
        ns_names = data

    providers = {
        base for base in (_base_domain(name) for name in ns_names) if base
    }
    return tuple(sorted(providers))


def _classify_provider_group(providers: Tuple[str, ...]) -> str:
    if not providers:
        return "unknown"

    non_cf = [p for p in providers if CLOUDFLARE_TOKEN not in p]
    if not non_cf:
        return "cloudflare_only"
    if len(non_cf) == len(providers):
        return "non_cloudflare"
    return "mixed"


def _collect_non_cf_providers(ech_rows: pd.DataFrame) -> Tuple[str, ...]:
    non_cf: set[str] = set()
    for providers in ech_rows["ns.providers"]:
        non_cf.update(p for p in providers if CLOUDFLARE_TOKEN not in p)
    return tuple(sorted(non_cf))


def count_ech(date_l, datadir, dom_type):
    df_columns = [
        "date",
        "num_ech",
        "num_ech_dnssec",
        "pct_ech_dnssec",
        "num_ech_cf_only",
        "num_ech_non_cloudflare",
        "num_ech_ns_mixed",
        "num_ech_ns_unknown",
        "ech_ns_all_cloudflare",
        "ech_ns_non_cf_providers",
    ]
    df_ech = pd.DataFrame(columns=df_columns)

    for day in date_l:
        print("processing ", day, "...")
        date_str = day.strftime("%Y-%m-%d")
        month_str = day.strftime("%Y-%m")
        log_path = os.path.join(datadir, month_str, date_str, f"{dom_type}_https.csv")
        print("read logs:", log_path)
        try:
            df = pd.read_csv(log_path)
        except FileNotFoundError:
            print("warning: file not found, skipping", log_path)
            continue
        except pd.errors.EmptyDataError:
            print("warning: file empty, skipping", log_path)
            continue
        except Exception as exc:
            print("warning: failed reading", log_path, "error:", exc)
            continue

        if "https" not in df.columns:
            print("warning: 'https' column missing, skipping", log_path)
            continue

        df["https.dict"] = df["https"].apply(_safe_load_https_json)
        df["https.ech"] = df["https.dict"].apply(_extract_https_ech)
        df["https.rrsig"] = df["https.dict"].apply(
            lambda x: bool(fns.if_key_exists(x, "RRSIG")) if isinstance(x, dict) else False
        )

        if "ns" in df.columns:
            df["ns.providers"] = df["ns"].apply(_extract_ns_providers)
        else:
            df["ns.providers"] = [tuple()] * len(df)
        df["ns.provider_class"] = df["ns.providers"].apply(_classify_provider_group)

        ech_rows = df.loc[df["https.ech"].notna()].copy()
        num_ech = int(ech_rows.shape[0])

        num_ech_dnssec = int(ech_rows["https.rrsig"].sum()) if num_ech else 0
        pct_ech_dnssec = (
            float(num_ech_dnssec) / float(num_ech) * 100.0 if num_ech else np.nan
        )

        class_counts = ech_rows["ns.provider_class"].value_counts(dropna=False)
        num_cf_only = int(class_counts.get("cloudflare_only", 0))
        num_non_cf = int(class_counts.get("non_cloudflare", 0))
        num_mixed = int(class_counts.get("mixed", 0))
        num_unknown = int(class_counts.get("unknown", 0))

        non_cf_providers = (
            _collect_non_cf_providers(ech_rows) if num_ech else tuple()
        )

        if num_ech == 0:
            ech_ns_all_cloudflare = None
        elif num_non_cf or num_mixed:
            ech_ns_all_cloudflare = False
        elif num_unknown:
            ech_ns_all_cloudflare = None
        else:
            ech_ns_all_cloudflare = True

        tmp_dict = {
            "date": date_str,
            "num_ech": num_ech,
            "num_ech_dnssec": num_ech_dnssec,
            "pct_ech_dnssec": pct_ech_dnssec,
            "num_ech_cf_only": num_cf_only,
            "num_ech_non_cloudflare": num_non_cf,
            "num_ech_ns_mixed": num_mixed,
            "num_ech_ns_unknown": num_unknown,
            "ech_ns_all_cloudflare": ech_ns_all_cloudflare,
            "ech_ns_non_cf_providers": ";".join(non_cf_providers) if non_cf_providers else "none",
        }

        df_ech = pd.concat([df_ech, pd.DataFrame([tmp_dict])], ignore_index=True)
    return df_ech

if __name__ == "__main__":
    # set this to data directory
    DataRawDir = "../data/parsed"

    # Time range beginning to end
    start_d = datetime.datetime(2024,4,1)
    end_d = datetime.datetime(2025,7,31)
    ndays = (end_d - start_d).days
    date_l0 = [start_d + datetime.timedelta(days=i) for i in range(ndays)]
    print("first day:", date_l0[0], "last day:", date_l0[-1])

    ### compute httpsrr rrsig rate given the time range 
    apex_ech = count_ech(date_l0, DataRawDir, "apex")
    apex_https = pd.read_csv("../data/plotting/alldom/adoption_apex_httpsrr.csv")
    apex_ech_merge = apex_ech.merge(apex_https, how='inner', on='date')
    apex_ech_merge.to_csv("../data/plotting/alldom/ech_apex.csv", index=False)

    www_ech = count_ech(date_l0, DataRawDir, "www")
    www_https = pd.read_csv("../data/plotting/alldom/adoption_www_httpsrr.csv")
    www_ech_merge = www_ech.merge(www_https, how='inner', on='date')
    www_ech_merge.to_csv("../data/plotting/alldom/ech_www.csv", index=False)



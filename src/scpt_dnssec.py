import pandas as pd
import numpy as np
import os
import datetime
import json
# import local files
import preprocessfns as fns


def safe_load_https_json(value):
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return {}
    if isinstance(value, dict):
        return value
    if isinstance(value, str):
        if value.strip() == "" or value.strip() == "{}":
            return {}
        try:
            return json.loads(value)
        except Exception:
            return {}
    return {}


def count_rrsig(date_l, datadir, file_name="apex_https.csv"):
    adoptiondf = pd.DataFrame(columns=['date', 'num_rrsig'])
    for day in date_l:
        print ("processing ", day, "...")
        date_str = day.strftime("%Y-%m-%d")
        month_str = day.strftime("%Y-%m")
        log_path = os.path.join(datadir, month_str, date_str, file_name)
        try:
            df = pd.read_csv(log_path)
        except:
            pass
        df["https.dict"] = df["https"].apply(safe_load_https_json)
        df["rrsig.exist"] = df["https.dict"].apply(lambda x: fns.if_key_exists(x, "RRSIG"))
        tmp_dict = dict({'date': date_str, 'num_rrsig': df['rrsig.exist'].sum()})
        tmp_dict = {key:[value] for key, value in tmp_dict.items()}
        adoptiondf = pd.concat([adoptiondf, pd.DataFrame(tmp_dict)], ignore_index=True)
    return adoptiondf


def count_adbit(date_l, datadir, dom_type):
    df_adbit = pd.DataFrame(columns=['date', 'num_adbit'])
    for day in date_l:
        print ("processing ", day, "...")
        date_str = day.strftime("%Y-%m-%d")
        month_str = day.strftime("%Y-%m")
        log_pathapex = os.path.join(datadir, month_str, date_str, dom_type + "_https.csv")
        log_pathad = os.path.join(datadir, month_str, date_str, dom_type + "_flags.csv")
        
        try:
            dfapex = pd.read_csv(log_pathapex)
            dfad = pd.read_csv(log_pathad)
        except:
            pass

        df_merge = dfapex.merge(dfad, how='left', on='domain')
        df_merge['flags'] = df_merge['flags'].fillna("noflag")
        df_merge = df_merge.fillna(False)

        tmp_dict = dict({'date': date_str, \
                         'num_adbit': df_merge['AD'].sum()})
        tmp_dict = {key:[value] for key, value in tmp_dict.items()}
        df_adbit = pd.concat([df_adbit, pd.DataFrame(tmp_dict)], ignore_index=True)
        
    return df_adbit
    

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
    apex_rrsig = count_rrsig(date_l0, DataRawDir, "apex_https.csv")
    apex_https = pd.read_csv("../data/plotting/alldom/adoption_apex_httpsrr.csv")
    apex_rrsigmerge = apex_rrsig.merge(apex_https, how='inner', on='date')
    apex_rrsigmerge.to_csv("../data/plotting/alldom/rrsig_apex.csv", index=False)

    www_rrsig = count_rrsig(date_l0, DataRawDir, "www_https.csv")
    www_https = pd.read_csv("../data/plotting/alldom/adoption_www_httpsrr.csv")
    www_rrsigmerge = www_rrsig.merge(www_https, how='inner', on='date')
    www_rrsigmerge.to_csv("../data/plotting/alldom/rrsig_www.csv", index=False)

    ### compute adbit rate given the time range
    apex_ad = count_adbit(date_l0, DataRawDir, "apex")
    apex_ad.to_csv("../data/plotting/alldom/adbit_apex.csv", index=False)
    
    www_ad = count_adbit(date_l0, DataRawDir, "www")
    www_ad.to_csv("../data/plotting/alldom/adbit_www.csv", index=False)


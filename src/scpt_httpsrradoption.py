import pandas as pd
import numpy as np
import os
import datetime
#from preprocessfns import *


def count_httpsrr(date_l, datedir, file_name="apex_https.csv"):
    adoptiondf = pd.DataFrame(columns=['date', 'num_httpsrr'])
    for day in date_l:
        print ("processing ", day, "...")
        date_str = day.strftime("%Y-%m-%d")
        month_str = day.strftime("%Y-%m")
        log_path = os.path.join(datedir, month_str, date_str, file_name)
        
        try:
            df = pd.read_csv(log_path)
        except:
            pass

        tmp_dict = dict({'date': date_str, 'num_httpsrr': df.shape[0]})
        tmp_dict = {key:[value] for key, value in tmp_dict.items()}
        adoptiondf = pd.concat([adoptiondf, pd.DataFrame(tmp_dict)], ignore_index=True)
    return adoptiondf

if __name__ == "__main__":
    # set this to data directory
    DataRawDir = "../data/parsed"

    # Time range from beginning to end
    start_d = datetime.datetime(2024,4,1)
    end_d = datetime.datetime(2025,7,31)
    ndays = (end_d - start_d).days
    date_l = [start_d + datetime.timedelta(days=i) for i in range(ndays)]
    print("firstday:", date_l[0], "lastday:", date_l[-1])

    ### compute httpsrr adoption rate given the time range for 
    df_httpsrr = count_httpsrr(date_l, DataRawDir, "apex_https.csv")
    df_httpsrr.to_csv("../data/plotting/alldom/adoption_apex_httpsrr.csv", index=False)
    
    df_httpsrr_www = count_httpsrr(date_l, DataRawDir, "www_https.csv")
    df_httpsrr_www.to_csv("../data/plotting/alldom/adoption_www_httpsrr.csv", index=False)


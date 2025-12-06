import pandas as pd 
import json
from typing import Literal
import numpy as np
import dns.name


def if_field_exist(https_rec:dict, field:str):
    if field not in https_rec.keys():
        return False
    return True


def get_https_fields(https_dict: dict, dnstype: Literal["HTTPS", "RRSIG"], field: str):
    try:
        records = https_dict[dnstype]
        
        if len(records) == 1: # only one record
            if (if_field_exist(records[0], field)): # field exists
                ans = records[0][field]
                return ans
                #if "," in ans: # field has multiple values
                #    return ans.split(",") # return a list of value
                #else:
                #    return ans
            else:
                return None
        else: # multiple records
            tmp = []
            for rec in records:
                if (if_field_exist(rec, field)):
                    ans = rec[field]
                    tmp.append(ans)
                    #if "," in ans:
                    #    tmp += ans.split(",")
                    #else:
                    #    tmp.append(ans)
            #return ",".join(tmp)
            if len(tmp) == 0:
                tmp = None
            return tmp
    except Exception as err:
        raise err

        
def get_ip_fields(ip_dict: dict, dnstype: Literal["A", "AAAA"]):
    try:
        if ip_dict is None or pd.isna(ip_dict) or ip_dict == "{}":
            return None
        if ip_dict.__class__ == str:
            ip_dict = json.loads(ip_dict)
        return ip_dict[dnstype]
    except Exception as err:
        raise

        
def get_ns_fields(ns_dict: dict, dnstype: Literal["NS"]):
    try:
        if ns_dict is None or pd.isna(ns_dict):
            return None
        if ns_dict.__class__ == str:
            ns_dict = json.loads(ns_dict)
        return ns_dict[dnstype]
    except Exception as err:
        raise
        
        
def get_nsip_fields(nsip_dict: dict, dnstype: Literal["A", "AAAA"]):
    try:
        if nsip_dict is None or pd.isna(nsip_dict):
            return None
        if nsip_dict.__class__ == str:
            nsip_dict = json.loads(nsip_dict)
        return nsip_dict[dnstype]
    except Exception as err:
        raise
        
        
def if_key_exists(https_dict:dict, key:Literal["HTTPS","RRSIG"]):
    try:
        records = https_dict[key]
        return True
    except:
        return False
    
    
def iscloudflare_ns(asn_dscp):
    asn_dscplis = asn_dscp.split(";")
    cloudflare_cnt = 0
    
    for asn_info in asn_dscplis:
        if "cloudflare" in asn_info.lower():
            cloudflare_cnt += 1
    
    asn_len = len(asn_dscplis)
    empty_num = asn_dscplis.count("")
    
    if cloudflare_cnt == 0:
        return "none"
    elif empty_num == 0 and cloudflare_cnt == asn_len:
        return "full"
    elif empty_num == 0 and cloudflare_cnt < asn_len:
        return "partial"
    elif empty_num != 0 and cloudflare_cnt + empty_num == asn_len:
        return "full"
    elif empty_num != 0 and cloudflare_cnt + empty_num < asn_len:
        return "partial"
    elif empty_num == asn_len:
        return "missing_nsinfo"
    
    
def merge_nsinfo(ipv4_text, ipv6_text):
    if ipv4_text == "full" and ipv6_text == "full":
        return "full"
    elif ipv4_text == "none" and ipv6_text == "none":
        return "none"
    else:
        return "partial"
    
    
def finding_noncloudflarens(nstext):
    nslis = nstext.split(";")
    noncloudflarelis = []
    for ns in nslis:
        if "cloudflare" not in ns.lower() and ns != "":
            noncloudflarelis.append(ns)
    if noncloudflarelis:
        return ";".join(noncloudflarelis)
    else:
        return "none"
    
    
def iscloudflare_ns(asn_dscp):
    asn_dscplis = asn_dscp.split(";")
    cloudflare_cnt = 0
    
    for asn_info in asn_dscplis:
        if "cloudflare" in asn_info.lower():
            cloudflare_cnt += 1
    
    asn_len = len(asn_dscplis)
    empty_num = asn_dscplis.count("")
    
    if cloudflare_cnt == 0:
        return "none"
    elif empty_num == 0 and cloudflare_cnt == asn_len:
        return "full"
    elif empty_num == 0 and cloudflare_cnt < asn_len:
        return "partial"
    elif empty_num != 0 and cloudflare_cnt + empty_num == asn_len:
        return "full"
    elif empty_num != 0 and cloudflare_cnt + empty_num < asn_len:
        return "partial"
    elif empty_num == asn_len:
        return "missing_nsinfo"
    

def merge_nsinfo(ipv4_text, ipv6_text):
    if ipv4_text == "full" and ipv6_text == "full":
        return "full"
    elif ipv4_text == "none" and ipv6_text == "none":
        return "none"
    else:
        return "partial"
    
    
def finding_noncloudflarens(nstext):
    nslis = nstext.split(";")
    noncloudflarelis = []
    for ns in nslis:
        if "cloudflare" not in ns.lower() and ns != "":
            noncloudflarelis.append(ns)
    if noncloudflarelis:
        return ";".join(noncloudflarelis)
    else:
        return "none"
    
    
def ip_match(addr_l1, addr_l2):
    # if any ip list is empty
    if addr_l1 is None or addr_l2 is None:
        return None
    
    try:
        addr_l1 = addr_l1.split(',')
    except:
        pass
    
    try:
        addr_l2 = addr_l2.split(',')
    except:
        pass

    # If one of the ip list is empty, we do not care
    if len(addr_l1) == 0 or len(addr_l2) == 0:
        return None
    
    # If iphint is a subset of all ips
    if set(addr_l1) <= set(addr_l2):
        return True
    return False
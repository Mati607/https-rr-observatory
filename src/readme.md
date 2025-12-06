### Apex and www dynamic tranco list

Please check the available time range of the dataset and modify the `start_d` and `end_d` in each script, and run the scripts in following order:

1. `python scpt_httpsrradoption.py` This will compute the overall dns https rr adoption rate.
2. `python scpt_dnssec.py` This will compute the signed and authenticated dns https rr records.
3. `python scpt_ech.py` This will compute the ech configuration in dns https rr.


### Overlap domains
All  `*_overlap.py` script are used to generate results for domains that continously showed up from 2023-05-08 to 2024-03-31. 

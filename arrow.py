def download_tzdata_windows(
    base_dir=None,
    year=2022,
    name="tzdata"
):
    import os
    import tarfile
    import urllib3

    http = urllib3.PoolManager()
    folder = base_dir if base_dir else os.path.join(os.path.expanduser('~'), "Downloads")
    tz_path = os.path.join(folder, "tzdata.tar.gz")
    
    with open(tz_path, "wb") as f:
        f.write(http.request('GET', f'https://data.iana.org/time-zones/releases/tzdata{year}f.tar.gz').data)
    
    folder = os.path.join(folder, name)
    
    if not os.path.exists(folder):
        os.makedirs(folder)
    
    tarfile.open(tz_path).extractall(folder)
    
    with open(os.path.join(folder, "windowsZones.xml"), "wb") as f:
        f.write(http.request('GET', f'https://raw.githubusercontent.com/unicode-org/cldr/master/common/supplemental/windowsZones.xml').data)
download_tzdata_windows(year=2022)
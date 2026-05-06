import requests
from typing import List, Tuple
from urllib.parse import urlencode

def download_gfs_ensemble_mean(
    date: str,
    hour: int,
    forecast_hour: int,
    parameters: List[Tuple[str, str]],
    bbox: Tuple[float, float, float, float],
    out_path: str
):
    """
    Downloads GFS ensemble mean data from the NOMADS GRIB filter for a specific region and parameters.

    Args:
        date: The date of the model run in YYYYMMDD format.
        hour: The hour of the model run (e.g., 0, 6, 12, 18).
        forecast_hour: The forecast hour.
        parameters: A list of tuples, where each tuple contains a parameter and its level
                    (e.g., [('TMP', '2_m_above_ground'), ('PRMSL', 'mean_sea_level')]).
        bbox: A tuple defining the bounding box for the subregion:
              (leftlon, rightlon, toplat, bottomlat).
              Longitude is in degrees east (0 to 360).
        out_path: The path to save the downloaded GRIB file.
    """
    base_url = "https://nomads.ncep.noaa.gov/cgi-bin/filter_gefs_atmos_0p50a.pl"
    
    # Construct the directory and file parts of the query
    dir_param = f"/gefs.{date}/{hour:02d}/atmos/pgrb2ap5"
    file_param = f"geavg.t{hour:02d}z.pgrb2a.0p50.f{forecast_hour:03d}"

    # Prepare the query parameters
    query_params = {
        'dir': dir_param,
        'file': file_param,
        'subregion': '',
        'toplat': bbox[2],
        'leftlon': bbox[0],
        'rightlon': bbox[1],
        'bottomlat': bbox[3]
    }

    # Add variables and levels
    for var, level in parameters:
        query_params[f'var_{var}'] = 'on'
        if level:
            query_params[f'lev_{level}'] = 'on'
    
    # Final URL with query
    download_url = f"{base_url}?{urlencode(query_params)}"

    print(f"Downloading from: {download_url}")

    try:
        # Make the request to download the data
        response = requests.get(download_url, stream=True)
        response.raise_for_status()  # Raise an exception for bad status codes

        # Save the content to the output file
        with open(out_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print(f"Successfully downloaded data to {out_path}")

    except requests.exceptions.RequestException as e:
        print(f"Error downloading data: {e}")

if __name__ == '__main__':
    # Example usage: Download 2m temperature and mean sea level pressure for a region
    download_gfs_ensemble_mean(
        date="20260312",
        hour=0,
        forecast_hour=0,
        parameters=[('TMP', '2_m_above_ground'), ('PRMSL', 'mean_sea_level')],
        bbox=(0, 360, 90, -90), # Global
        out_path="/Users/heng/Downloads/gfs_ensemble_mean_test.grib"
    )

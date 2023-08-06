# climate-resilience

<a href="https://pypi.org/project/climate-resilience/"><img alt="PyPI" src="https://img.shields.io/pypi/v/black"></a>

---
## [Download Examples](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/scripts/download_example.py)
This file requires a [`download_params.yml`](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/scripts/download_params.yml) file to specify the download configurations.

We cannot directly download the data from the Google Earth Engine directly onto the local machine. So the best option is to download to the drive and then download that data to the local drive.

---
## [Preprocess Examples](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/scripts/preprocess_example.py)
The preprocessing functions will expect that the local data drive contains the downloaded data.

If the data is on drive, the drive needs to be mounted. 
This is easier to do in a google colab session. Once the drive is mounted, the path of the mounted drive can be used with the functions as normal.

#### Expected file and directory structure:
The input file and directory structure for functions `calculate_Nth_percentile()`, `calculate_pr_count_amount()`, and `calculate_temporal_mean()` in the [preprocessing code](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/src/climate_resilience/preprocess.py) should be as follows:
```
datadir
├── scenario1_variable1_ensemble
│   ├── name1_state1_scenario1_variable1.csv
│   └── name2_state2_scenario1_variable1.csv
├── scenario1_variable2_ensemble
│   ├── name1_state1_scenario1_variable2.csv
│   └── name2_state2_scenario1_variable2.csv
├── scenario2_variable1_ensemble
│   ├── name1_state1_scenario2_variable1.csv
│   └── name2_state2_scenario2_variable1.csv
└── scenario2_variable2_ensemble
    ├── name1_state1_scenario2_variable2.csv
    └── name2_state2_scenario2_variable2.csv
```

---
## [Visualization Examples](https://github.com/satyarth934/lbnl-climate-resilience/tree/main/examples/climate-resilience/notebooks)
The visualization code will be easier to be used in a notebook as inline visualizations can be used.



#### [Map visualization notebook](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/notebooks/visualize_example_1.ipynb)

Below is a screenshot of the interactive map with the sites marked.

![Map](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/notebooks/sample_map_screenshot.png?raw=true)

![Map Colorbar](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/notebooks/sample_map_colorbar.png?raw=true)



#### [Box plot visualization notebook](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/notebooks/visualize_example_3.ipynb)

Below is a screenshot of boxplot of annual precipitation in different regions of the United States.

![Boxplot](https://github.com/satyarth934/lbnl-climate-resilience/blob/main/examples/climate-resilience/notebooks/sample_boxplot.png?raw=true)



### Library Features:

#### Downloader
1. [Class SiteDownloader](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/downloader.py#L24) member functions: <br>  
  * [download_model_average_daily()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/downloader.py#L108)
  * [download_historical_daily()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/downloader.py#L159)
  * [download_historical_monthly()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/downloader.py#L211)
  * [download_samples()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/downloader.py#L348)

#### Preprocessing functions
1. [calculate_Nth_percentile()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/preprocess.py#L15)
2. [calculate_pr_count_amount()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/preprocess.py#L102)
3. [calculate_temporal_mean()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/preprocess.py#L204)
4. [get_climate_ensemble()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/preprocess.py#L301)
5. [get_per_year_stats()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/preprocess.py#L359)
6. [get_sub_period_stats()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/preprocess.py#L427)

#### Vizualization functions
1. [plot_map()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/visualize.py#L72)
2. [plot_histogram()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/visualize.py#L202)
3. [plot_boxplots()](https://github.com/ALTEMIS-DOE/climate-resilience/blob/main/src/climate_resilience/visualize.py#L262)


# Contributors
- [Satyarth Praveen](mailto:satyarth@lbl.gov)
- [Zexuan Xu](mailto:zexuanxu@lbl.gov)
- [Haruko Wainwright](mailto:hmwainwright@lbl.gov)

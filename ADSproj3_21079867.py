# -*- coding: utf-8 -*-
"""
Created on Fri May  5 16:28:34 2023

@author: Kisha
"""
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.optimize import curve_fit
from scipy.stats import linregress
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ds = pd.read_csv('D:\Projects\Project 3\API_19_DS2_en_csv_v2_5361599.csv',skiprows=4)

indi_codes_cluster = ["IQ.CPA.PUBS.XQ", "AG.LND.ARBL.ZS"]
years_cluster = ["2010", "2020"]


def extracted_data(indi_codes_cluster, years_cluster):
#This function takes two arguments, `cluster_indi_codes` and `cluster_years`, and extracts the data from the dataset for a given Indicator Code and given year. It then drops some columns from the dataset to create a new dataframe and returns a list of dataframes. 
    public_sector = ds[ds["Indicator Code"] == indi_codes_cluster[0]]
    arable_land = ds[ds["Indicator Code"] == indi_codes_cluster[1]]
    public_sector = public_sector.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")
    arable_land = arable_land.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")
    dfs = []
    for year in years_cluster:
        public_ = public_sector[year]
        arable_ = arable_land[year]
        data_frame = pd.DataFrame(
            {"CPIA public sector management ": public_, "Arable land": arable_})
        df = data_frame.dropna(axis=0)
        dfs.append(df)

    return dfs


dfs_cluster = extracted_data(indi_codes_cluster, years_cluster)


def data_clustering(data_frames):
#This function clusters a list of dataframes using k-means algorithm. The function first scales the data using standard scaling technique and then finds the optimum number of clusters using the elbow method. It then fits the k-means algorithm to the dataset and plots the clusters and their centroids on the original data. 
    year = "2010"
    for df in data_frames:
        x = df.values
        scaler = StandardScaler()
        x_scaled = scaler.fit_transform(x)

        # Finding the optimum number of clusters
        wcss = []
        for i in range(1, 11):
            kmeans = KMeans(n_clusters=i, init='k-means++',
                            max_iter=300, n_init=10, random_state=42)
            kmeans.fit(x_scaled)
            wcss.append(kmeans.inertia_)

      
        # Fitting kmeans to the dataset
        kmeans = KMeans(n_clusters=4, init='k-means++',
                        max_iter=300, n_init=10, random_state=0)
        y_kmeans = kmeans.fit_predict(x_scaled)

        # Plotting the clusters on original date
        plt.figure(figsize=(15, 10))
        plt.scatter(x_scaled[y_kmeans == 0, 0], x_scaled[y_kmeans ==
                    0, 1], s=50, c='brown', label='Cluster 1')
        plt.scatter(x_scaled[y_kmeans == 1, 0], x_scaled[y_kmeans ==
                    1, 1], s=50, c='red', label='Cluster 2')
        plt.scatter(x_scaled[y_kmeans == 2, 0], x_scaled[y_kmeans ==
                    2, 1], s=50, c='green', label='Cluster 3')
        plt.scatter(x_scaled[y_kmeans == 3, 0], x_scaled[y_kmeans ==
                    3, 1], s=50, c='blue', label="Cluster 4")

        # Plotting the centroids
        plt.scatter(kmeans.cluster_centers_[:, 0], kmeans.cluster_centers_[
                    :, 1], s=100, marker="*", c='black', label='Centroids')

        plt.title(f'All countries clusters {year}')
        plt.xlabel("Public sector management")
        plt.ylabel("Area of Arable land")

        plt.legend()
        plt.show()
        plt.savefig('cluster2015.png', dpi=300)
        plt.savefig('cluster2020.png', dpi=300)


        year = "2020"


data_clustering(dfs_cluster)


def predicted_fit():
#This function takes in a dataset and performs curve fitting and linear regression to predict CO2 emissions from liquid fuel consumption (kt) based on Urban population growth in selected countries. It also generates a plot to show the best fitting function, confidence range, and plots to show the predicted values in 10 and 20 years. 

    fit1 = ds[ds["Indicator Code"] == "SP.URB.GROW"]
    fit2 = ds[ds["Indicator Code"] == "EN.ATM.CO2E.LF.KT"]
    # fodata
    fit1 = fit1.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")
    fit2 = fit2.drop(
        ["Country Code", "Indicator Name", "Indicator Code"], axis=1).set_index("Country Name")

    fit1_sep = fit1["2012"]
    fit2_sep = fit2["2012"]

    total_fitdf = pd.DataFrame({
        "Urban_pop_grow": fit1_sep,
        "co2_con_liq": fit2_sep})
    total_fitdf = total_fitdf.dropna(axis=0)
    total_fitdf = total_fitdf.loc[["India", "Australia", "United Kingdom", "Pakistan", "Brazil",
                                         "Canada", "Russian Federation", "South Africa", "Austria", "Portugal", "Argentina", "Bangladesh",]]
    x_data = total_fitdf.iloc[:, 0].values
    y_data = total_fitdf.iloc[:, 1].values

    # Define the function to fit
    def func(x, a, b):
        return a*x + b

    # Fit the data
    fit_t, fit_s = curve_fit(func, x_data, y_data)

    # Generate a plot showing the best fitting function
    plt.figure(figsize=(15, 10))
    plt.plot(x_data, y_data, 'o', label='Data')
    plt.plot(x_data, func(x_data, *fit_t), 'r-',
             label='fit: x=%5.3f, y=%5.3f' % tuple(fit_t))
    plt.title("CO2 emission from liquid fuels vs Urban Population growth")
    plt.xlabel('Urban population growth (annual %)')
    plt.ylabel('CO2 emissions from liquid fuel consumption (kt)')
    plt.legend()
    plt.show()

    # Compute the confidence ranges
    def err_ranges(fit_t, fit_s):
        perr = np.sqrt(np.diag(fit_s))
        lower_fit = fit_t - perr
        upper_fit = fit_t + perr
        return lower_fit, upper_fit

    # Generate a plot showing the confidence range
    lower_fit, upper_fit = err_ranges(fit_t, fit_s)
    plt.figure(figsize=(15, 10))
    plt.plot(x_data, y_data, 'o', label='Data')
    plt.plot(x_data, func(x_data, *fit_t), 'r-',
             label='fit: x=%5.3f, y=%5.3f' % tuple(fit_t))
    plt.plot(x_data, func(x_data, *lower_fit), 'b--',
             label='lower_fit: x=%5.3f, y=%5.3f' % tuple(lower_fit))
    plt.plot(x_data, func(x_data, *upper_fit), 'g--',
             label='upper_fit: x=%5.3f, y=%5.3f' % tuple(upper_fit))
    plt.title("CO2 emissions from liquid fuels vs Urban Population growth")
    plt.xlabel('Urban population growth percentage')
    plt.ylabel('CO2 emissions from liquid fuel consumption (kt)')
    plt.legend()
    plt.bbox_to_anchor = (0.5, -0.5)
    plt.show()
    plt.savefig('fit1.png', dpi=300)
    plt.savefig('fit2.png', dpi=300)



    # Use the model for predictions
    slope, intercept, r_value, p_value, std_err = linregress(x_data, y_data)

    # Predict the values in 10 years
    x_yprediction = 15
    ypred = slope * x_yprediction + intercept
    print("CO2 emissions from liquid fuel consumption (kt) in 15 years: ", ypred)

    # Predict the values in 20 years
    x_yprediction = 30
    ypred = slope * x_yprediction + intercept
    print("CO2 emissions from liquid fuel consumption (kt) in 30 years: ", ypred)


predicted_fit()

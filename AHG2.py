#!/usr/bin/env python
# coding: utf-8

import streamlit as st
import geemap
import ee
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from rosetta import rosetta, SoilData

# 设置代理
import os
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:1080'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:1080'
geemap.set_proxy(port='1080')

# 初始化Earth Engine
ee.Initialize()
Map = geemap.Map(center=[39.7, 78.5], zoom=5)

# 添加一个标记，用于显示用户选择的坐标
Map.add_basemap('HYBRID')

# 显示地图
st.subheader("Interactive Map")
st.write("Click on the map to choose a location, or enter coordinates manually.")
Map.to_streamlit(height=500)
# 导入土壤数据 (每个深度层次)
clay_0 = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select('b0')
clay_10 = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select('b10')
clay_30 = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select('b30')
clay_60 = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select('b60')
clay_100 = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select('b100')
clay_200 = ee.Image("OpenLandMap/SOL/SOL_CLAY-WFRACTION_USDA-3A1A1A_M/v02").select('b200')

sand_0 = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select('b0')
sand_10 = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select('b10')
sand_30 = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select('b30')
sand_60 = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select('b60')
sand_100 = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select('b100')
sand_200 = ee.Image("OpenLandMap/SOL/SOL_SAND-WFRACTION_USDA-3A1A1A_M/v02").select('b200')

silt_0 = ee.Image(100).subtract(clay_0.add(sand_0))
silt_10 = ee.Image(100).subtract(clay_10.add(sand_10))
silt_30 = ee.Image(100).subtract(clay_30.add(sand_30))
silt_60 = ee.Image(100).subtract(clay_60.add(sand_60))
silt_100 = ee.Image(100).subtract(clay_100.add(sand_100))
silt_200 = ee.Image(100).subtract(clay_200.add(sand_200))

# 体积密度 (Bulk Density)
sbd_0 = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02").select('b0').divide(100)
sbd_10 = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02").select('b10').divide(100)
sbd_30 = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02").select('b30').divide(100)
sbd_60 = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02").select('b60').divide(100)
sbd_100 = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02").select('b100').divide(100)
sbd_200 = ee.Image("OpenLandMap/SOL/SOL_BULKDENS-FINEEARTH_USDA-4A1H_M/v02").select('b200').divide(100)

# 田间持水量 (Field Capacity)
fc_0 = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01").select('b0')
fc_10 = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01").select('b10')
fc_30 = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01").select('b30')
fc_60 = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01").select('b60')
fc_100 = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01").select('b100')
fc_200 = ee.Image("OpenLandMap/SOL/SOL_WATERCONTENT-33KPA_USDA-4B1C_M/v01").select('b200')

# 创建一个函数来提取土壤数据
def extract_soil_parameters(lat, lon):
    point = ee.Geometry.Point(lon, lat)
    
    # 获取每层数据的平均值
    def get_value(image):
        return image.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=point,
            scale=30
        ).getInfo()
    
    # 提取土壤参数
    clay_values = [get_value(clay_0)['b0'], get_value(clay_10)['b10'], get_value(clay_30)['b30'], 
                   get_value(clay_60)['b60'], get_value(clay_100)['b100'], get_value(clay_200)['b200']]
    sand_values = [get_value(sand_0)['b0'], get_value(sand_10)['b10'], get_value(sand_30)['b30'],
                   get_value(sand_60)['b60'], get_value(sand_100)['b100'], get_value(sand_200)['b200']]
    silt_values = [get_value(silt_0)['constant'], get_value(silt_10)['constant'], get_value(silt_30)['constant'],
                   get_value(silt_60)['constant'], get_value(silt_100)['constant'], get_value(silt_200)['constant']]
    sbd_values = [get_value(sbd_0)['b0'], get_value(sbd_10)['b10'], get_value(sbd_30)['b30'],
                  get_value(sbd_60)['b60'], get_value(sbd_100)['b100'], get_value(sbd_200)['b200']]
    fc_values = [get_value(fc_0)['b0'], get_value(fc_10)['b10'], get_value(fc_30)['b30'],
                 get_value(fc_60)['b60'], get_value(fc_100)['b100'], get_value(fc_200)['b200']]

    # 创建DataFrame来存储数据
    data = {
        'Layer (cm)': [0, 10, 30, 60, 100, 200],
        'Sand (%)': sand_values,
        'Silt (%)': silt_values,
        'Clay (%)': clay_values,
        'Bulk Density (g/cm³)': sbd_values,
        'Field Capacity (cm³/cm³)': fc_values
    }
    
    df = pd.DataFrame(data)
    return df

# Streamlit界面
st.title("Soil Parameters and Water Retention Curve")
st.sidebar.header("User Interaction")

coordinates = st.sidebar.text_area("Enter Coordinates (lat, lon)", value="{'lat': 39.7, 'lon': 78.5}", height=100)

# 坐标解析函数
def parse_coordinates(coords):
    try:
        coords_dict = eval(coords)
        return coords_dict['lat'], coords_dict['lon']
    except:
        st.error("Invalid coordinates format. Please enter as {'lat': value, 'lon': value}.")
        return None, None

# 用户点击按钮获取参数
if st.sidebar.button("Get Soil Parameters"):
    lat, lon = parse_coordinates(coordinates)

    if lat and lon:
        st.sidebar.text("Fetching soil parameters...")
        soil_data = extract_soil_parameters(lat, lon)
        
        # 显示土壤参数表格
        st.write("Soil Parameters (per layer):")
        st.dataframe(soil_data)

        # 使用Rosetta模型进行参数估算
        data = np.array([soil_data['Sand (%)'], soil_data['Silt (%)'], soil_data['Clay (%)'], 
                         soil_data['Bulk Density (g/cm³)'], soil_data['Field Capacity (cm³/cm³)'], np.repeat(0.1, 6)]).T
        
        mean, stdev, codes = rosetta(1, SoilData.from_array(data))
        
        # 提取推断的土壤水分参数
        theta_r = mean[:, 0]   # residual volumetric water content
        theta_s = mean[:, 1]   # saturated volumetric water content
        log10_alpha = mean[:, 2]  # log10(alpha)
        log10_n = mean[:, 3]    # log10(n)
        log10_Ksat = mean[:, 4] # log10(Ksat)
        
        # 创建推断参数的DataFrame
        inferred_data = {
            'Layer (cm)': [0, 10, 30, 60, 100, 200],
            'Residual Volumetric Water Content (theta_r)': theta_r,
            'Saturated Volumetric Water Content (theta_s)': theta_s,
            'Alpha (cm^-1)': 10**log10_alpha,
            'n (dimensionless)': 10**log10_n,
            'Log10(Ksat)': log10_Ksat
        }
        
        inferred_df = pd.DataFrame(inferred_data)
        
        # 显示推断参数表格
        st.write("Inferred Parameters (per layer):")
        st.dataframe(inferred_df)
        
        # 绘制每层的水分特征曲线 (交换X和Y)
        plt.figure(figsize=(10, 6))
        psi = np.logspace(-1, 4, 100)  # 水势范围

        for i in range(len(soil_data)):
            theta = theta_r[i] + (theta_s[i] - theta_r[i]) / (1 + (psi / 10**log10_alpha[i]) ** log10_n[i]) ** (1 - 1/log10_n[i])
            plt.plot(theta, np.log10(psi), label=f"Layer {soil_data['Layer (cm)'][i]}-{soil_data['Layer (cm)'][i+1] if i+1 < len(soil_data) else '200+'} cm")
        
        plt.ylabel('Log10(Pressure head (cm))')
        plt.xlabel('Volumetric water content (cm³/cm³)')
        plt.xlim(0,100)
        plt.title('Soil Water Retention Curves for Different Layers')
        plt.legend()
        st.pyplot(plt)

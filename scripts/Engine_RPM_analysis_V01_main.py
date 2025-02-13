#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：heat_map_inter.py 
@File    ：engine_RPM_analysis_streamlit_V01.py
@Author  ：Ray Gong
@Date    ：2024/10/25 21:20 
'''
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib as mpl
mpl.rcParams['font.sans-serif'] = ['SimHei'] # 设置中文
mpl.rcParams['axes.unicode_minus'] = False # 设置支持负号显示

@st.cache_data
def read_input_data(file):
    fname = file.name
    # 定义要尝试的编码列表
    df = None
    encodings_to_try = ['utf-8', 'gbk']
    try:
        df = pd.read_csv(file, encoding='gbk')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file, encoding='utf-8')
        except Exception as e:
            st.error(f'读取文件错误，原因：{e}')
    except Exception as err:
        st.error(f'读取文件错误，原因：{err}')
    #
    return df

# 将数据划分到不同区间
def get_bins(_max_value):
    """
        根据最大值生成区间列表
        :param max_value: 最大值
        :return: 区间列表
        """
    if _max_value<0:
        st.error(f'输入数据必须为正数！')
        _bin = None
    elif _max_value <= 100:
        _bins = list(range(0, _max_value+1, 10))
        _bins.insert(1, 0.01)
    else:
        ten_percent = _max_value*0.1
        nearest_ten = round(ten_percent/10)*10
        _bins = list(range(0, _max_value+1, nearest_ten))
        _bins.insert(1, 0.01)
    # print(_bins)
    return _bins

def convert_to_integer_intervals(intervals):
    """
        将区间转换为整数形式的区间
        :param intervals: 区间列表
        :return: 整数形式的区间列表
        """
    new_inter = []
    for interval in intervals:

        if interval.left > 1:
            _left = int(interval.left)
        else:
            _left = interval.left
        if interval.right > 1:
            _right = int(interval.right)
        else:
            _right = interval.right
        new_inter.append(pd.Interval(_left, _right, closed='right'))
    # st.write(new_inter)
    return new_inter

@st.cache_data
def get_cross_table(rpm_data, xdata, x_max = 100, sample_rate=1, extrapolate_ratio=1):
    '''
    获取时域数据xdata和ydata各自在特定bins里面的交叉表
    :param xdata: x数据组，可以是series，列表
    :param rpm_data: RPM数据组，可以是series，列表
    :param x_max: x数据bins时候的的最大值
    :param sample_rate: 采样率，用来将数据归一化到1s一次采样。
    :param extrapolate_ratio: 外推系数，交叉表数据直接乘以的倍数
    :return:
    '''
    bins_RPM = list(range(0, 7100, 100))
    bins_RPM.insert(1, 0.01)
    bins_ydata = pd.cut(rpm_data, bins_RPM, include_lowest=True)
    bins_xdata = pd.cut(xdata, get_bins(x_max), include_lowest=True)

    # print(bins_ydata)
    cross_table = pd.crosstab(bins_ydata, bins_xdata, normalize=False) # 获取时间T内每个bins（转速区间）内的数据点数量
    #
    # 外推
    # 计算原理：二阶激励的次数=每个转速bin区间内的数据点数量对应的时间*Middle of RPM bins / 30
    # 假设时间为T，T内的数据量多少随着采样率不同而不同，需要将数量除以采样率，获取时间，即将数据点数量的交叉表转为时间的交叉表
    cross_table = cross_table / sample_rate
    # 计算column2_bins的中间值
    # 首先确保bins_column2是排序的，并且是连续的或者指定了包括了右端点的bins
    bins_middle_rpm = [(bins_RPM[i] + bins_RPM[i + 1]) / 2 for i in range(len(bins_RPM) - 1)]
    # print(bins_middle_rpm)
    # 将中间值与cross_tab的index对齐并创建一个Series
    index_middle_values = pd.Series(bins_middle_rpm[:len(cross_table.index)], index=cross_table.index)
    # print(index_middle_values)
    # 乘以交叉表的值
    cross_table = cross_table.mul(index_middle_values, axis=0) / 30
    # print(cross_table)

    cross_table = cross_table * extrapolate_ratio

    # cross_table.columns = convert_to_integer_intervals(cross_table.columns)
    # cross_table.index = convert_to_integer_intervals(cross_table.index)
    # print(cross_table)
    return cross_table

def Heatmap_plot(_2dtable, xlabel=None, ylabel=None, datatype='Cycles'):
    # 绘制热力图
    st.subheader("2D Plot")

    # 根据用户选择的单元格大小计算 figsize
    figsize = (17, 3.5* _2dtable.shape[0]/_2dtable.shape[1])

    fig, ax = plt.subplots(figsize=figsize)
    max_2dtable = max(_2dtable.max())
    if datatype == 'Cycles':
        sns.heatmap(_2dtable, annot=True, fmt=".1e", cmap="Blues",
                    annot_kws={"size": 12, "weight": "normal"},
                    linewidths=0.5, linecolor='white',
                    ax=ax, square=False)
    else:
        # 计算每行的百分比
        # 如果你想计算每列的百分比，可以将 axis 参数改为 0
        _2dtable = _2dtable/(_2dtable.sum().sum())*100
        sns.heatmap(_2dtable, annot=True, fmt=".0f", cmap="Blues",
                    annot_kws={"size": 12, "weight": "normal"},
                    linewidths=0.5, linecolor='white',
                    ax=ax, square=False)

    ax.xaxis.tick_top()
    ax.xaxis.set_label_position('top')
    fontsize = 12
    ax.set_xticklabels(ax.get_xticklabels(), fontdict={'size': fontsize, 'weight': 'bold'})
    ax.set_yticklabels(ax.get_yticklabels(), fontdict={'size': fontsize, 'weight': 'bold'})
    ax.set_xlabel(xlabel, fontdict={'size': 14, 'weight': 'bold'})
    ax.set_ylabel(ylabel, fontdict={'size': 14, 'weight': 'bold'})
    st.pyplot(fig)
    return _2dtable

def hist_plot(data, xlabel='RPM'):
    bins_RPM = get_bins(int(max(data)))
    bins_RPM.insert(1, 0.01)
    counts, bin_edges = np.histogram(data, bins=bins_RPM)
    # 打印结果
    print("Bin edges: ", bin_edges)
    print("Counts in each bin: ", counts)
    # 绘制直方图
    fig = plt.figure(figsize=(12, 6))
    plt.bar(bin_edges[:-1], counts, width=np.diff(bin_edges)[-1], edgecolor='black')
    # plt.hist(data, bins=bins_RPM, edgecolor='black')
    plt.title('Histogram of RPM Distribution')
    plt.xlabel(xlabel)
    plt.ylabel('Counts')
    st.pyplot(fig)

def start_RPM_analysis():
    st.set_page_config(
        page_title="Engine Excitation calculation",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",
        # menu_items=None
        # menu_items={
        #     'Get Help': None,
        #     'Report a bug': None,
        #     'About': None
        # }
    )
    # 隐藏菜单栏
    # hide_streamlit_style = """
    # <style>
    # #MainMenu {visibility: hidden;}
    # footer {visibility: hidden;}
    # </style>
    #
    # """
    # st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    # 隐藏deploy和菜单栏
    st.markdown('''
        <style>
        .stApp [data-testid="stToolbar"]{
            display:none;
        }
        </style>
        ''', unsafe_allow_html=True)


    st.title('Engine RPM Distribution Analysis V01')
    st.text(
        '''
        An app to analysis the RPM data, and plot into a 3D view to show detail RPM distribution, 
        another axis can be loading rate, Torque....
        '''
    )
    uploaded_file = st.sidebar.file_uploader('Choose a file:', type=['csv', ])
    if uploaded_file is not None:
        df = read_input_data(uploaded_file)
        if df is not None:
            st.write(f'读取成功，数据总行数：{df.shape[0]}')
            st.write(df.head())
            columns = list(df.columns)
            columns.insert(0, None)
            ylabel = st.sidebar.selectbox('请选择RPM数据标签', columns)
            xlabel = st.sidebar.selectbox('请选择第二个轴数据标签（可选）', columns)
            if ylabel:
                if xlabel and xlabel != ylabel:
                    if max(df[xlabel]) > 100:
                        x_max = int(max(df[xlabel])) + 1
                    else:
                        x_max = 100
                    sample_rate = st.sidebar.number_input('Input sample rate of time series', min_value=0.001, value=1.0)
                    extrapolate_ratio = st.sidebar.number_input('Input extrapolate ratio', min_value=1.0)

                    cross_table = get_cross_table(df[ylabel], df[xlabel], x_max=x_max, sample_rate=sample_rate,
                                        extrapolate_ratio=extrapolate_ratio)
                    datatype = st.sidebar.radio('The data type you want', ('Cycles', 'Percent (%)'), )
                    if not cross_table.empty:
                        # 展示交叉表
                        # st.subheader("交叉表")
                        # st.write(cross_table)
                        _2d_plot = Heatmap_plot(cross_table, xlabel=xlabel, ylabel=ylabel, datatype=datatype)
                        st.subheader('Target RPM bin plot')
                        bin_select = st.selectbox('Select a RPM bin', _2d_plot.index)
                        # st.write(_2d_plot.loc[bin_select])
                        hist_plot(_2d_plot.loc[bin_select], xlabel=xlabel)

                else:
                    hist_plot(df[ylabel])


# start_RPM_analysis()


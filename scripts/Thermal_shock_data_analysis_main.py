#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：streamlit_project 
@File    ：thermal_shock_daata_analysis.py
@Author  ：Ray Gong
@Date    ：2024/4/3 22:31 
'''
import streamlit as st
import pandas as pd
import os
import time
# import base64
# import plotly.figure_factory as ff
# import traceback
import plotly.express as px
import plotly.io as pio
# from bs4 import BeautifulSoup
# pip install beautifulsoup4
# from subscript import read_csvs, Temperature_curve_plot_V02

time_column_candidates = ['Time', 'time', '时间'] # csv中可能的时间列名称

# def modify_html(html):
#     # 打开并读取HTML文件
#     file_path = html
#     with open(file_path, 'r', encoding='utf-8') as file:
#         soup = BeautifulSoup(file, 'html.parser')
#
#     scripts = soup.find_all('script')
#
#     url = 'https://plotly.com/'
#     for script in scripts:
#         # 假设我们知道URL是在一个明确的字符串中
#         if url in script.string:
#             new_url = 'http://bing.com'
#             # 使用replace()方法替换旧URL为新URL
#             updated_script = script.string.replace(url, new_url)
#             script.string.replace_with(updated_script)
#         elif 'Produced with ' in script.string:
#             updated_script = script.string.replace('Produced with ', ' ')
#             script.string.replace_with(updated_script)
#     # file_path = 'output1.html'
#     # 将修改后的HTML写回文件
#     with open(file_path, 'w', encoding='utf-8') as file:
#         file.write(str(soup.prettify()))

def plot_curve(df, interal, xcolumn_name, ycolumn_names, output_html):
    print('准备开始画曲线！')
    if interal:
        df1 = df.iloc[::interal]
    df1 = df1.reset_index()
    if xcolumn_name == None:
        xcolumn_name = '_Index'
        df1.loc[:, '_Index'] = df1.index
    # print(df.shape, xcolumn_name, ycolumn_names)
    # print(df.columns)
    fig = px.line(df1, x=xcolumn_name, y=ycolumn_names)
    # fig.update_xaxes(tickformat='%Y-%m-%d %H:%M:%S', type='date')
    # fig.update_layout(title=figure_title, xaxis_title=' ', yaxis_title=' ')

    # # 将图表导出为HTML文件
    # pio.write_html(fig, file='output.html', auto_open=True)
    # 如果不希望自动打开文件，可以这样调用：
    pio.write_html(fig, file=output_html, auto_open=False)
    # if os.path.exists(output_html):
    #     modify_html(output_html)

    # fig.show()
    print(f'画图完毕, 生成文件：{output_html}')


def duplicated_time(dup_df, time_colname):
    all_time = pd.Series()
    count_dupli = dup_df[time_colname].value_counts()
    # print(count_dupli)
    for idx, val in count_dupli.items():
        if val > 60:
            print('Error!时间列相同时间超过60行，无法重建时间列！对应的时间点为：', idx)
            break
        elif val == 1:
            series_of_seconds = pd.to_datetime(pd.Series([idx]))
            # all_time = pd.concat([all_time, series_of_seconds])
        else:
            # 设置起始时间
            start_time = pd.Timestamp(idx)

            # 结束时间是起始时间之后1分钟
            end_time = start_time + pd.Timedelta(minutes=1)

            # 使用date_range生成这一分钟内每秒的时间戳序列
            timestamps = pd.date_range(start=start_time, end=end_time - pd.Timedelta(seconds=1),
                                       freq='s')
            # print(timestamps)
            # 输出结果
            # for ts in timestamps:
            #     print(ts.strftime('%Y-%m-%d %H:%M:%S'))

            # 或者将它们转换成Series以便进一步操作
            series_of_seconds = pd.Series(timestamps)[:val]
        if len(all_time):
            all_time = pd.concat([all_time, series_of_seconds])
        else:
            all_time = series_of_seconds
    else:
        return None
            
    # print(all_time.dtypes)
    all_time = all_time.sort_values()
    return all_time.values()
    
    
def process_uploaded_file(file):
    filename = file.name
    st.write('正在处理csv文件：', filename)
    # detected_encoding = detect_encoding(file)
    # print('获取了编码规则：', detected_encoding)
    try:
        df_temp = pd.read_csv(file, encoding='gbk')
        na_rows = df_temp.isnull().any(axis=1)
        if na_rows.any():
            st.write('!!!发现存在NA行，将忽略这些行：')
            st.write(df_temp[na_rows])
            df_temp = df_temp[~na_rows]
        time_colname = None
        
        for candidate in time_column_candidates:
            if candidate in df_temp.columns:
                time_colname = candidate
                print('成功获取时间列名称，名称为：', time_colname)
                break
        if time_colname is None:
            # st.write('无法在CSV文件中检测到时间列，请确保至少包含以下列名之一：{}'.format(time_column_candidates))
            raise ValueError('无法在CSV文件中检测到时间列，请确保至少包含以下列名之一：{}'.format(time_column_candidates))
        else:
            df_temp[time_colname] = pd.to_datetime(df_temp[time_colname], errors='raise')
            print(f"将列: {time_colname}转换为时间成功")
            # print(df.dtypes)
            if df_temp.duplicated(subset=[time_colname]).any():
                print('！！！注意：时间列有重复，将对重复的时间尝试按照1Hz采样率进行重建。')
                new_time_index = duplicated_time(df_temp, time_colname)
                if new_time_index is not None:
                    print('new_time_index:', len(new_time_index))
                    print('df_temp.index:', len(df_temp.index))
                    df_temp.index = new_time_index
            else:
                df_temp = df_temp.sort_values(by=time_colname)
            
            # 将数据转为数值
            successful_numerical_columns = []
            for column in df_temp.columns:
                if column != time_colname:
                    df_temp[column] = pd.to_numeric(df_temp[column], errors='coerce')
                    if df_temp[column].dtype.kind in ('i', 'f'):
                        successful_numerical_columns.append(column)
            if len(successful_numerical_columns) >0:
                if len(successful_numerical_columns)+1 != len(df_temp.columns):
                    st.write('请注意！部分列未成功转换未数值类型，将忽略这些列！')
                df_temp = df_temp[[time_colname] + successful_numerical_columns]
                df_temp.rename(columns={time_colname:'time'}, inplace=True)
            else:
                raise ValueError('非时间列均无法完全转换为数值类型，请检查！')
    except Exception as e:
        st.write(f'处理文件"{filename}"时出错：{str(e)}')
        print(f"错误发生位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
        return None
    else:
        st.write(f'文件"{filename}"格式正确， 获取数据：{df_temp.shape[0]}行，{df_temp.shape[1]}列！')
        return df_temp

@st.cache_data(ttl=300)
def load_and_process_csvs(uploaded_files):
    all_data = pd.DataFrame()
    for uploaded_file in uploaded_files:
        processed_df = process_uploaded_file(uploaded_file) # 处理是时域数据，并且把时间列命名为 time
        if processed_df is not None:
            if all_data.shape[0] == 0:
                all_data = processed_df
            else:
                if list(all_data.columns) == list(all_data.columns):
                    times_in_all = set(all_data['time'])
                    common_times = processed_df[processed_df['time'].isin(times_in_all)]
                    if not common_times.empty:
                        st.write(f'!!!文件"{uploaded_file.name}"中的时间与其他文件有重复，将忽略该文件！重复数据如下：')
                        st.write(common_times)
                    else:
                        all_data = pd.concat([all_data, processed_df], ignore_index=True).sort_values(by='time')
                else:
                    st.write(f'文件"{uploaded_file.name}"列名与其他不同，将忽略该文件！')
    return all_data

def create_bins(target_temp, _lower, _upper):
    bins = [0, 150]
    for i in range(200, target_temp, 100):
        bins.append(i)
    # print(bins)

    bins.extend([_lower, target_temp, _upper, 10000])
    bins = list(dict.fromkeys(bins))
    bins.sort()

    print(bins)
    return bins

def create_data(data, col_name2cut, bins):
    # # 假设有一个DataFrame，其中一列是数值数据
    # data = pd.DataFrame({'Values': [1, 3, 6, 8, 10, 15, 17, 20, 22, 25]})
    # # 定义区间边界
    # bins = [0, 10, 20, 30]
    # 创建新的列，将数值划分到不同的区间
    data['Bins'] = pd.cut(data[col_name2cut], bins)
    # 计算各区间内数据的频数
    counts = data.groupby('Bins')[col_name2cut].size()
    # 计算各区间占比（百分比形式）
    percentages = counts / counts.sum() * 100
    # 输出占比结果
    print(percentages.values)
    # # 假设你已经有了之前计算出的百分比数据，这里直接使用示例数据
    # percentages = pd.Series([30, 40, 30], index=['[0, 10)', '[10, 20)', '[20, 30)'])
    # 绘制柱状图
    xi = [str(item) for item in percentages.index]

    return pd.DataFrame({'Intervals': xi, 'Percentage (%)': percentages.values})



def start_thermal_shock_analysis():
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


    st.title('Thermal Shock Data Visualization')
    # 输入密码验证
    # st.markdown("### 输入密码验证")
    # password = st.text_input("请输入6位数字密码")
    # if password != "123456":
    #     st.write("密码错误")
    #     st.stop()
    st.markdown('''
     注意：
         1. 将温度数据转为csv文件。
         2. 确保所有csv文件的列名一致，如果不一致，将会报错，需要手动更改。
         3. 确保存在时间列，且列名为['Time', 'time', '时间']之一。
         4. 如果时间列有重复，将按照1Hz进行重建。
    ''')
    st.markdown('## :blue[Input CSV read and preprocess]')
    # st.markdown('<font color=#0099ff size=12 face="黑体">黑体@@@@@@@@@</font>')
    
    uploaded_files = st.file_uploader('Choose the csv files:', accept_multiple_files=True, type='.csv', help=f'需要有{",".join(time_column_candidates)}之一作为时间列！')
    # if uploaded_files:
    with st.expander('Waiting for processs csv files, expand for detail.....'):
        all_data = load_and_process_csvs(uploaded_files)
        if all_data.shape[0]:
            st.write(f'共获取数据：{all_data.shape[0]}行，{all_data.shape[1]}列')
            st.write(all_data.head())
        else:
            st.write('No data have been read!')

    if all_data.shape[0]:
        st.markdown('## :blue[Time Series Plot]')
        interval = st.slider('Time series interval for plot(For better view):', 0, 120, 10)
        cols_no_time = list(all_data.columns)
        cols_no_time.remove('time')
        colums_choose = st.multiselect('Select the interested columns', cols_no_time)
        folder = os.getcwd()
        fname = f'Time_series_curves_{str(time.time()).replace(".", "-")}.html'
        if st.button('Plot Time Series Curve'):
            print('Ploting!')
            # st.line_chart(all_data[colums_choose], x='time', y=colums_choose)
            select_cols_with_time = colums_choose.copy()
            select_cols_with_time.append('time')
            if interval:
                fig = px.line(all_data[select_cols_with_time].iloc[::interval], x='time', y=colums_choose)
            else:
                fig = px.line(all_data[select_cols_with_time], x='time', y=colums_choose)
            st.plotly_chart(fig, theme=None)
            
            # temp_html_file = "temp_plot.html"
            # pio.write_html(fig, file=temp_html_file, auto_open=False)
            # with open(temp_html_file, 'r', encoding='utf-8') as f:
            #     html_content = f.read()
            # os.remove(temp_html_file)
            
            # # 将HTML内容转化为字节串
            # html_bytes = html_content.encode('utf-8')
            # # 在Streamlit界面添加下载按钮，直接提供数据和文件名
            # st.download_button(
            #     label="Download Time Series Curve File",
            #     data=html_bytes,
            #     file_name=temp_html_file,
            #     # mime_type="text/html"
            # )
            # # 使用Streamlit提供下载链接
            # b64 = base64.b64encode(html_content.encode()).decode()
            # href = f'<a href="data:text/html;base64,{b64}" download="interactive_plot.html">下载交互式图表 (HTML)</a>'
            # st.markdown(href, unsafe_allow_html=True)

        st.markdown('## :blue[Statistic Plot]')
        selected_col = st.selectbox('Select the column name for plot', [col for col in all_data.columns if col != 'time'])
        method_input_bins = st.radio('Choose the method for bins input', ['Auto', 'Manual Input'])
        if method_input_bins == 'Auto':
            col1, col2, col3 = st.columns(3)
            with col1:
                target_value = st.number_input('The target value', value=0)

            with col2:
                lower_boundary = st.number_input('The lower boundary', value=0)

            with col3:
                upper_boundary = st.number_input('The upper boundary', value=0)
        else:
            bins_str = st.text_input('Input bins (Comma separate)')
        if st.button('Statistic Plot'):
            if method_input_bins == 'Auto':
                if target_value > 0.01 and lower_boundary> 0.01 and upper_boundary > 0.01:
                    bins = create_bins(target_value, lower_boundary, upper_boundary)
                    chart_data = create_data(all_data, selected_col, bins)
                    st.bar_chart(chart_data, x="Intervals", y="Percentage (%)")
                else:
                    st.write('Some of input "data target_value" "lower_boundary" "upper_boundary" is not OK')
            elif method_input_bins == 'Manual Input':
                try:
                    bins = bins_str.split(',')
                    bins = [int(i) for i in bins]
                    if target_value > 0.01 and lower_boundary > 0.01 and upper_boundary > 0.01:
                        chart_data = create_data(all_data, selected_col, bins)
                        st.bar_chart(chart_data, x="Intervals", y="Percentage (%)")
                    else:
                        st.write('Some of input "data target_value" "lower_boundary" "upper_boundary" is not OK')
                except Exception as err:
                    st.write(f'输入的Bins有错误，请重新输入！具体原因：{err}')


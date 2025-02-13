

'''
@Project ：streamlit_project 
@File    ：thermal_shock_daata_analysis.py
@Author  ：Ray Gong
@Date    ：2024/4/3 22:31 
'''
import streamlit as _0bRQZptHwY
import pandas as _0ojDVEVlfmL
import os
import time



import plotly.express as _0oxwDxG
import plotly.io as _0oeQeyhrVBg




_0xWMHNLOPtwB = ['Time', 'time', '时间'] # csv中可能的时间列名称






















def plot_curve(_0xVgLlALLvcG, _0xeEacqaqFx, _0bCWRMJTZK, _0oqcFY, _0bgaLErpJT):
    print('准备开始画曲线！')
    if _0xeEacqaqFx:
        _0xCNVJGuafh = _0xVgLlALLvcG.iloc[::_0xeEacqaqFx]
    _0xCNVJGuafh = _0xCNVJGuafh.reset_index()
    if _0bCWRMJTZK == None:
        _0bCWRMJTZK = '_Index'
        _0xCNVJGuafh.loc[:, '_Index'] = _0xCNVJGuafh.index


    _0beRBxS = _0oxwDxG.line(_0xCNVJGuafh, x=_0bCWRMJTZK, y=_0oqcFY)





    _0oeQeyhrVBg.write_html(_0beRBxS, _0xYZjza=_0bgaLErpJT, auto_open=False)



    print(f'画图完毕, 生成文件：{_0bgaLErpJT}')


def duplicated_time(_0oDMftlaqk, _0bhtDlPUx):
    _0orPKShEzqvI = _0ojDVEVlfmL.Series()
    _0oTwGYGx = _0oDMftlaqk[_0bhtDlPUx].value_counts()

    for _0bttUI, _0xcCHGFe in _0oTwGYGx.items():
        if _0xcCHGFe > 60:
            print('Error!时间列相同时间超过60行，无法重建时间列！对应的时间点为：', _0bttUI)
            break
        elif _0xcCHGFe == 1:
            _0omCpIVLLb = _0ojDVEVlfmL.to_datetime(_0ojDVEVlfmL.Series([_0bttUI]))

        else:

            _0bQmtWI = _0ojDVEVlfmL.Timestamp(_0bttUI)

            _0xxrPP = _0bQmtWI + _0ojDVEVlfmL.Timedelta(minutes=1)

            _0oaWLHyETpJ = _0ojDVEVlfmL.date_range(start=_0bQmtWI, end=_0xxrPP - _0ojDVEVlfmL.Timedelta(seconds=1),
                                       freq='s')





            _0omCpIVLLb = _0ojDVEVlfmL.Series(_0oaWLHyETpJ)[:_0xcCHGFe]
        if len(_0orPKShEzqvI):
            _0orPKShEzqvI = _0ojDVEVlfmL.concat([_0orPKShEzqvI, _0omCpIVLLb])
        else:
            _0orPKShEzqvI = _0omCpIVLLb
    else:
        return None

    _0orPKShEzqvI = _0orPKShEzqvI.sort_values()
    return _0orPKShEzqvI.values()
    
    
def process_uploaded_file(_0xYZjza):
    _0oKeTXVUSZw = _0xYZjza.name
    _0bRQZptHwY.write('正在处理csv文件：', _0oKeTXVUSZw)


    try:
        _0bpBgkW = _0ojDVEVlfmL.read_csv(_0xYZjza, encoding='gbk')
        _0bwNGKulD = _0bpBgkW.isnull().any(axis=1)
        if _0bwNGKulD.any():
            _0bRQZptHwY.write('!!!发现存在NA行，将忽略这些行：')
            _0bRQZptHwY.write(_0bpBgkW[_0bwNGKulD])
            _0bpBgkW = _0bpBgkW[~_0bwNGKulD]
        _0bhtDlPUx = None
        
        for _0bnGqPIxU in _0xWMHNLOPtwB:
            if _0bnGqPIxU in _0bpBgkW.columns:
                _0bhtDlPUx = _0bnGqPIxU
                print('成功获取时间列名称，名称为：', _0bhtDlPUx)
                break
        if _0bhtDlPUx is None:

            raise ValueError('无法在CSV文件中检测到时间列，请确保至少包含以下列名之一：{}'.format(_0xWMHNLOPtwB))
        else:
            _0bpBgkW[_0bhtDlPUx] = _0ojDVEVlfmL.to_datetime(_0bpBgkW[_0bhtDlPUx], errors='raise')
            print(f"将列: {_0bhtDlPUx}转换为时间成功")

            if _0bpBgkW.duplicated(subset=[_0bhtDlPUx]).any():
                print('！！！注意：时间列有重复，将对重复的时间尝试按照1Hz采样率进行重建。')
                _0bZHYW = duplicated_time(_0bpBgkW, _0bhtDlPUx)
                if _0bZHYW is not None:
                    print('_0bZHYW:', len(_0bZHYW))
                    print('_0bpBgkW.index:', len(_0bpBgkW.index))
                    _0bpBgkW.index = _0bZHYW
            else:
                _0bpBgkW = _0bpBgkW.sort_values(by=_0bhtDlPUx)

            _0bWLPkoYJb = []
            for _0bncRz in _0bpBgkW.columns:
                if _0bncRz != _0bhtDlPUx:
                    _0bpBgkW[_0bncRz] = _0ojDVEVlfmL.to_numeric(_0bpBgkW[_0bncRz], errors='coerce')
                    if _0bpBgkW[_0bncRz].dtype.kind in ('_0oLYAYd', 'f'):
                        _0bWLPkoYJb.append(_0bncRz)
            if len(_0bWLPkoYJb) >0:
                if len(_0bWLPkoYJb)+1 != len(_0bpBgkW.columns):
                    _0bRQZptHwY.write('请注意！部分列未成功转换未数值类型，将忽略这些列！')
                _0bpBgkW = _0bpBgkW[[_0bhtDlPUx] + _0bWLPkoYJb]
                _0bpBgkW.rename(columns={_0bhtDlPUx:'time'}, inplace=True)
            else:
                raise ValueError('非时间列均无法完全转换为数值类型，请检查！')
    except Exception as _0xqLEbo:
        _0bRQZptHwY.write(f'处理文件"{_0oKeTXVUSZw}"时出错：{str(_0xqLEbo)}')
        print(f"错误发生位置: {_0xqLEbo.__traceback__.tb_frame.f_code.co_filename}:{_0xqLEbo.__traceback__.tb_lineno}")
        return None
    else:
        _0bRQZptHwY.write(f'文件"{_0oKeTXVUSZw}"格式正确， 获取数据：{_0bpBgkW.shape[0]}行，{_0bpBgkW.shape[1]}列！')
        return _0bpBgkW

@_0bRQZptHwY.cache_data(ttl=300)
def load_and_process_csvs(_0oJyrq):
    _0bGpZLcmvh = _0ojDVEVlfmL.DataFrame()
    for _0oeshjFXK in _0oJyrq:
        _0xXdVyfGQn = process_uploaded_file(_0oeshjFXK) # 处理是时域数据，并且把时间列命名为 time
        if _0xXdVyfGQn is not None:
            if _0bGpZLcmvh.shape[0] == 0:
                _0bGpZLcmvh = _0xXdVyfGQn
            else:
                if list(_0bGpZLcmvh.columns) == list(_0bGpZLcmvh.columns):
                    _0bopKGz = set(_0bGpZLcmvh['time'])
                    _0xFIbPi = _0xXdVyfGQn[_0xXdVyfGQn['time'].isin(_0bopKGz)]
                    if not _0xFIbPi.empty:
                        _0bRQZptHwY.write(f'!!!文件"{_0oeshjFXK.name}"中的时间与其他文件有重复，将忽略该文件！重复数据如下：')
                        _0bRQZptHwY.write(_0xFIbPi)
                    else:
                        _0bGpZLcmvh = _0ojDVEVlfmL.concat([_0bGpZLcmvh, _0xXdVyfGQn], ignore_index=True).sort_values(by='time')
                else:
                    _0bRQZptHwY.write(f'文件"{_0oeshjFXK.name}"列名与其他不同，将忽略该文件！')
    return _0bGpZLcmvh

def create_bins(_0bNrLTVrzUu, _0bQqkjqkxAN, _0xgNdyGWe):
    _0baGCGUHsqDc = [0, 150]
    for _0oLYAYd in range(200, _0bNrLTVrzUu, 100):
        _0baGCGUHsqDc.append(_0oLYAYd)


    _0baGCGUHsqDc.extend([_0bQqkjqkxAN, _0bNrLTVrzUu, _0xgNdyGWe, 10000])
    _0baGCGUHsqDc = list(dict.fromkeys(_0baGCGUHsqDc))
    _0baGCGUHsqDc.sort()

    print(_0baGCGUHsqDc)
    return _0baGCGUHsqDc

def create_data(_0xilOTadYvV, _0bjaxw, _0baGCGUHsqDc):





    _0xilOTadYvV['Bins'] = _0ojDVEVlfmL.cut(_0xilOTadYvV[_0bjaxw], _0baGCGUHsqDc)

    _0bPkuGZUFNpN = _0xilOTadYvV.groupby('Bins')[_0bjaxw].size()

    _0xTufRRD = _0bPkuGZUFNpN / _0bPkuGZUFNpN.sum() * 100

    print(_0xTufRRD.values)



    _0oeVMLIhMr = [str(_0oVBCkTaaLw) for _0oVBCkTaaLw in _0xTufRRD.index]

    return _0ojDVEVlfmL.DataFrame({'Intervals': _0oeVMLIhMr, 'Percentage (%)': _0xTufRRD.values})



def start_thermal_shock_analysis():
    _0bRQZptHwY.set_page_config(
        page_title="Engine Excitation calculation",
        page_icon="🧊",
        layout="wide",
        initial_sidebar_state="expanded",






    )









    _0bRQZptHwY.markdown('''
        <style>
        .stApp [_0xilOTadYvV-testid="stToolbar"]{
            display:none;
        }
        </style>
        ''', unsafe_allow_html=True)


    _0bRQZptHwY.title('Thermal Shock Data Visualization')






    _0bRQZptHwY.markdown('''
     注意：
         1. 将温度数据转为csv文件。
         2. 确保所有csv文件的列名一致，如果不一致，将会报错，需要手动更改。
         3. 确保存在时间列，且列名为['Time', 'time', '时间']之一。
         4. 如果时间列有重复，将按照1Hz进行重建。
    ''')
    _0bRQZptHwY.markdown('## :blue[Input CSV read and preprocess]')

    
    _0oJyrq = _0bRQZptHwY.file_uploader('Choose the csv files:', accept_multiple_files=True, type='.csv', help=f'需要有{",".join(_0xWMHNLOPtwB)}之一作为时间列！')

    with _0bRQZptHwY.expander('Waiting for processs csv files, expand for detail.....'):
        _0bGpZLcmvh = load_and_process_csvs(_0oJyrq)
        if _0bGpZLcmvh.shape[0]:
            _0bRQZptHwY.write(f'共获取数据：{_0bGpZLcmvh.shape[0]}行，{_0bGpZLcmvh.shape[1]}列')
            _0bRQZptHwY.write(_0bGpZLcmvh.head())
        else:
            _0bRQZptHwY.write('No _0xilOTadYvV have been read!')

    if _0bGpZLcmvh.shape[0]:
        _0bRQZptHwY.markdown('## :blue[Time Series Plot]')
        _0oLkXtHtWNo = _0bRQZptHwY.slider('Time series _0oLkXtHtWNo for plot(For better view):', 0, 120, 10)
        _0xUyUFAXwISM = list(_0bGpZLcmvh.columns)
        _0xUyUFAXwISM.remove('time')
        _0oZHAI = _0bRQZptHwY.multiselect('Select the interested columns', _0xUyUFAXwISM)
        _0bqHOlXzLs = os.getcwd()
        _0xEAPBzEC = f'Time_series_curves_{str(time.time()).replace(".", "-")}.html'
        if _0bRQZptHwY.button('Plot Time Series Curve'):
            print('Ploting!')

            _0oDBubFW = _0oZHAI.copy()
            _0oDBubFW.append('time')
            if _0oLkXtHtWNo:
                _0beRBxS = _0oxwDxG.line(_0bGpZLcmvh[_0oDBubFW].iloc[::_0oLkXtHtWNo], x='time', y=_0oZHAI)
            else:
                _0beRBxS = _0oxwDxG.line(_0bGpZLcmvh[_0oDBubFW], x='time', y=_0oZHAI)
            _0bRQZptHwY.plotly_chart(_0beRBxS, theme=None)



















        _0bRQZptHwY.markdown('## :blue[Statistic Plot]')
        _0xSceMJuwhq = _0bRQZptHwY.selectbox('Select the _0bncRz name for plot', [_0xGIptX for _0xGIptX in _0bGpZLcmvh.columns if _0xGIptX != 'time'])
        _0xmOmYtVUEqF = _0bRQZptHwY.radio('Choose the method for _0baGCGUHsqDc input', ['Auto', 'Manual Input'])
        if _0xmOmYtVUEqF == 'Auto':
            _0olysHS, _0bDLYN, _0ofrxNflBLr = _0bRQZptHwY.columns(3)
            with _0olysHS:
                _0bqEBO = _0bRQZptHwY.number_input('The target value', value=0)

            with _0bDLYN:
                _0bevoxT = _0bRQZptHwY.number_input('The lower boundary', value=0)

            with _0ofrxNflBLr:
                _0xuOXcNJmwXv = _0bRQZptHwY.number_input('The upper boundary', value=0)
        else:
            _0xAERq = _0bRQZptHwY.text_input('Input _0baGCGUHsqDc (Comma separate)')
        if _0bRQZptHwY.button('Statistic Plot'):
            if _0xmOmYtVUEqF == 'Auto':
                if _0bqEBO > 0.01 and _0bevoxT> 0.01 and _0xuOXcNJmwXv > 0.01:
                    _0baGCGUHsqDc = create_bins(_0bqEBO, _0bevoxT, _0xuOXcNJmwXv)
                    _0bmBQPipZH = create_data(_0bGpZLcmvh, _0xSceMJuwhq, _0baGCGUHsqDc)
                    _0bRQZptHwY.bar_chart(_0bmBQPipZH, x="Intervals", y="Percentage (%)")
                else:
                    _0bRQZptHwY.write('Some of input "_0xilOTadYvV _0bqEBO" "_0bevoxT" "_0xuOXcNJmwXv" is not OK')
            elif _0xmOmYtVUEqF == 'Manual Input':
                try:
                    _0baGCGUHsqDc = _0xAERq.split(',')
                    _0baGCGUHsqDc = [int(_0oLYAYd) for _0oLYAYd in _0baGCGUHsqDc]
                    if _0bqEBO > 0.01 and _0bevoxT > 0.01 and _0xuOXcNJmwXv > 0.01:
                        _0bmBQPipZH = create_data(_0bGpZLcmvh, _0xSceMJuwhq, _0baGCGUHsqDc)
                        _0bRQZptHwY.bar_chart(_0bmBQPipZH, x="Intervals", y="Percentage (%)")
                    else:
                        _0bRQZptHwY.write('Some of input "_0xilOTadYvV _0bqEBO" "_0bevoxT" "_0xuOXcNJmwXv" is not OK')
                except Exception as _0btPUbea:
                    _0bRQZptHwY.write(f'输入的Bins有错误，请重新输入！具体原因：{_0btPUbea}')


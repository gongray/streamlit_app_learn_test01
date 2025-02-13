import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 子图行列的数量
n_rows = 2
n_cols = 3
    
    
def process_uploaded_file(file):
    filename = file.name
    st.write('正在处理csv文件：', filename)
    try:
        df_temp = pd.read_csv(file, encoding='gbk')
        na_rows = df_temp.isnull().any(axis=1)
        if na_rows.any():
            st.write('!!!发现存在NA行，将忽略这些行：')
            st.write(df_temp[na_rows])
            df_temp = df_temp[~na_rows]
        return df_temp, filename[:-4]
    except Exception as e:
        st.write(f'处理文件"{filename}"时出错：{str(e)}')
        print(f"错误发生位置: {e.__traceback__.tb_frame.f_code.co_filename}:{e.__traceback__.tb_lineno}")
        return None, None


@st.cache_data(ttl=300)
def load_and_process_csvs(uploaded_files):
    all_data = []
    colnames = None
    for uploaded_file in uploaded_files:
        processed_df, fname = process_uploaded_file(uploaded_file) # 处理是时域数据，并且把时间列命名为 time
        if processed_df is not None:
            current_colnames = processed_df.columns.tolist()
            if colnames is None:
                colnames = current_colnames
            elif colnames != current_colnames:
                st.error('csv文件的列名不同，无法继续！')
                all_data = []
                return []
            all_data.append([fname, processed_df])
            
    return all_data


def plot_datas(datas, ylims, x_colname, x_title, colnames, legend_names):
    
   
    fig, axs = plt.subplots(nrows=n_rows, ncols=n_cols, figsize=(20, 10))
    for fname, processed_df in datas:
        total_subplots = len(processed_df.columns.tolist())
        for i, col in enumerate(colnames):

            row_i = i // n_cols
            col_i = i % n_cols
            # st.write('子图行：', row_i, '列：', col_i)
            if row_i<2 and col_i < 3:
                x_data= processed_df[x_colname] if x_colname else processed_df.index
                axs[row_i][col_i].plot(x_data, processed_df[col], label=legend_names[fname])
                
                # # 添加标题和标签
                axs[row_i][col_i].set_title(col)
                axs[row_i][col_i].set_xlabel(x_title)
                # axs[row][col].set_ylabel('Values')
                axs[row_i][col_i].set_ylim((ylims[col+ '_min'] , ylims[col+'_max']))
                
                axs[row_i][col_i].legend()
                    
    plt.tight_layout()
    st.pyplot(fig)
    


def start_plot_excitation():
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


    st.title('发动机激励数据可视化')
    st.markdown('''
                用于展示发动机转为一点后的激励数据，注意： 
                * csv输入文件的格式需要为Engine_Excitation_Points_to_One_V01.exe导出的文件。
                * 使用前请将csv文件名改为需要展示在legen中的名字。
                ''')
    st.sidebar.header("发动机激励数据可视化")
    uploaded_files = st.sidebar.file_uploader("Choose CSV files", type='csv', accept_multiple_files=True)
    
    if uploaded_files:
        datas = load_and_process_csvs(uploaded_files)
        
        if datas:
            colnames = datas[0][1].columns.tolist()
            x_colname = st.sidebar.selectbox('Select the X column for plot', ['']+colnames, index=1)
            x_title = st.sidebar.text_input('Input the X title', 'Frequency (Hz)')
            legend_names = {}
            for f_name, _ in datas:
                legend_names[f_name] = st.sidebar.text_input(f'Input the legend name of {f_name}', f_name)
                
            if x_colname:
                colnames.remove(x_colname)
            # 获取所有列的最大值，最小值
            max_values= pd.DataFrame(columns=colnames)
            min_values= pd.DataFrame(columns=colnames)
            for _, _df in datas:
                s = _df.max()
                temp_df = s.reset_index()
                temp_df = temp_df.T
                temp_df.columns = s.index
                temp_df.drop('index', axis=0, inplace=True)
                max_values = pd.concat([max_values, temp_df], ignore_index=True)
                
                s = _df.min()
                temp_df = s.reset_index()
                temp_df = temp_df.T
                temp_df.columns = s.index
                temp_df.drop('index', axis=0, inplace=True)
                min_values = pd.concat([max_values, temp_df], ignore_index=True)
            # st.write(max_values.max())
            ylims_max  = {}
            for key, value in (max_values.max().to_dict()).items():
                if value>0:
                    ylims_max[key] = value * 1.2
                else:
                    ylims_max[key] = value * 0.8
                    
            # ylims_max = (max_values.max()*1.2).to_dict()
            ylims_min  = {}
            for key, value in (min_values.min().to_dict()).items():
                if value>0:
                    ylims_min[key] = value * 0.8 
                else:
                    ylims_min[key] = value * 1.2 
            
            ylims = {}
            for _name in colnames:
                cols = st.columns(2)
                ylims[_name + '_min'] = cols[0].number_input(f'Y lower of {_name}', value=0.0, format='%0.5f')
                ylims[_name + '_max'] = cols[1].number_input(f'Y upper of {_name}', value=ylims_max[_name], format='%0.5f')
                
            # st.write(ylims)
            
            plot_datas(datas, ylims, x_colname, x_title, colnames, legend_names)
    
        
    




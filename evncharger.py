import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

font_path = "C:/Windows/Fonts/malgun.ttf" 
fontprop = fm.FontProperties(fname=font_path, size=12)

plt.rc('font', family=fontprop.get_name())
plt.rcParams['axes.unicode_minus'] = False  

ev_data = pd.read_csv('data/지역별 전기차 현황정보.csv', encoding='EUC-KR')  
charging_data = pd.read_csv('data/지역별 전기차 충전기 현황정보.csv', encoding='EUC-KR')  

ev_data.dropna(inplace=True)
charging_data.dropna(inplace=True)

long_format_ev_data = ev_data.set_index('연도').T.reset_index()
long_format_ev_data = long_format_ev_data.melt(id_vars=['index'], var_name='연도', value_name='전기차_등록대수')
long_format_ev_data = long_format_ev_data.rename(columns={'index': '지역명'})

long_format_charging_data = charging_data.set_index('연도').T.reset_index()
long_format_charging_data = long_format_charging_data.melt(id_vars=['index'], var_name='연도', value_name='충전기_수')
long_format_charging_data = long_format_charging_data.rename(columns={'index': '지역명'})

long_format_ev_data['연도'] = pd.to_numeric(long_format_ev_data['연도'])
long_format_charging_data['연도'] = pd.to_numeric(long_format_charging_data['연도'])

long_format_ev_data = long_format_ev_data[(long_format_ev_data['연도'] >= 2016) & (long_format_ev_data['연도'] <= 2024)]
long_format_charging_data = long_format_charging_data[(long_format_charging_data['연도'] >= 2020) & (long_format_charging_data['연도'] <= 2024)]

total_ev_by_year = long_format_ev_data.groupby('연도')['전기차_등록대수'].sum()
total_charging_by_year = long_format_charging_data.groupby('연도')['충전기_수'].sum()

ev_growth_rate = total_ev_by_year.pct_change() * 100
charging_growth_rate = total_charging_by_year.pct_change() * 100

growth_data = pd.DataFrame({
    '전기차_증가율(%)': ev_growth_rate,
    '충전기_증가율(%)': charging_growth_rate
}).dropna() 

# 표 3
plt.figure(figsize=(14, 8))
sns.lineplot(x='연도', y='전기차_등록대수', hue='지역명', data=long_format_ev_data, marker='o')
plt.title('지역별 전기차 등록 대수 증가 추이 (2016~2024)')
plt.xticks(rotation=45)
plt.ylabel('전기차 등록 대수')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.show()

# 표 2
plt.figure(figsize=(14, 8))
sns.lineplot(x='연도', y='충전기_수', hue='지역명', data=long_format_charging_data, marker='o')
plt.title('지역별 충전기 수 증가 추이 (2020~2024)')
plt.xticks(rotation=45)
plt.ylabel('충전기 수')
plt.legend(loc='upper left', bbox_to_anchor=(1, 1))
plt.show()

# 표 3
plt.figure(figsize=(10, 4))  
sns.heatmap(growth_data.T, 
            annot=True, 
            fmt='.1f', 
            cmap='RdYlBu_r',
            center=0,
            vmin=-20,
            vmax=120,
            cbar=False)  
plt.title('연도별 전기차 등록 대수와 충전기 수 증가율(%) 비교', pad=20)
plt.xlabel('연도', labelpad=10)
plt.ylabel('구분', labelpad=10)
plt.show()
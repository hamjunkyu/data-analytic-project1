import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

font_path = "C:/Windows/Fonts/malgun.ttf"
fontprop = fm.FontProperties(fname=font_path, size=12)

plt.rc('font', family=fontprop.get_name())
plt.rcParams['axes.unicode_minus'] = False

ev_data = pd.read_csv('data/지역별 전기차 현황정보.csv', encoding='EUC-KR')
car_data = pd.read_csv('data/자동차 등록 현황정보.csv', encoding='EUC-KR')

years_range = range(2016, 2025)

region_columns = ['강원특별자치도', '경기도', '경상도', '광주광역시', '대구광역시', 
                 '대전광역시', '부산광역시', '서울특별시', '세종특별자치시', 
                 '울산광역시', '인천광역시', '전라도', '제주특별자치도', '충청도']
ev_total = ev_data[ev_data['연도'].isin(years_range)].groupby('연도')[region_columns].sum().sum(axis=1)

car_data = car_data[car_data['연도'].isin(years_range)].copy()
car_data['등록대수'] = car_data['등록대수(만)'] * 10000

merged_data = pd.DataFrame({
    '연도': sorted(years_range),
    '전체차량': car_data['등록대수'].values,
    '전기차': ev_total.values
})

merged_data['전기차비율'] = (merged_data['전기차'] / merged_data['전체차량']) * 100

fig, ax1 = plt.subplots(figsize=(12, 6))

bars = ax1.bar(merged_data['연도'], merged_data['전기차비율'], 
               alpha=0.5, color='lightgreen')

ax1.plot(merged_data['연도'], merged_data['전기차비율'], 
         'o-', color='green', linewidth=2)

ax1.set_title('연도별 자동차 대수 대비 전기차 비율 추이 (2016-2024)', fontsize=14)
ax1.set_xlabel('연도', fontsize=12)
ax1.set_ylabel('전기차 비율 (%)', fontsize=12)

ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)

for bar in bars:
    height = bar.get_height()
    ax1.text(bar.get_x() + bar.get_width()/2., height,
             f'{height:.2f}%',
             ha='center', va='bottom')

plt.xticks(merged_data['연도'], rotation=45)

plt.tight_layout()
plt.show()
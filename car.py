import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

font_path = "C:/Windows/Fonts/malgun.ttf"
fontprop = fm.FontProperties(fname=font_path, size=12)

plt.rc('font', family=fontprop.get_name())
plt.rcParams['axes.unicode_minus'] = False

car_data = pd.read_csv('data/자동차 등록 현황정보.csv', encoding='EUC-KR')

car_data = car_data.dropna(subset=['연도'])

fig, ax = plt.subplots(figsize=(12, 6))

x = range(len(car_data['연도']))

ax.bar(x, car_data['등록대수(만)'], alpha=0.5, color='lightblue')
ax.plot(x, car_data['등록대수(만)'], 'o-', color='cornflowerblue', linewidth=2)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

plt.ylim(2000, 2700)
plt.title('연도별 자동차 등록대수 증가 추이 (2014-2024)')
plt.xlabel('연도')
plt.ylabel('등록대수(만)')

years = [str(int(year)) for year in car_data['연도']]
plt.xticks(x, years, rotation=45)

plt.show()
import indictor
import tushare as ts
df = ts.get_h_data("600519")
indictor.plot_all(df)
import time
import plotly.express as px
import plotly.graph_objects as go

data = [1,3,2,4,3,3,2,3]

fig = go.FigureWidget()
fig.add_scatter()

fig.write_html('first_figure.html', auto_open=True)

for i in range(len(data)):
    time.sleep(0.3)
    fig.data[0].y = data[:i] 


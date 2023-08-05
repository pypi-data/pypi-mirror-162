# System
import os

# External
import numpy
import matplotlib.pyplot as plt
from datetime import datetime

def show_raw_visualization(data,links):
    os.makedirs('data',exist_ok=True)
    date_time_key = "Month"
    colors = ["blue","orange","green","red","purple","brown","pink","gray"]
    plt.style.use('seaborn')
    time_data = data[date_time_key]
    fig, axes = plt.subplots(4,2,figsize=(15, 20),dpi=80,facecolor="w", edgecolor="k",sharex=True,sharey=True)
    for i in range(len(links)):
        key = links[i]
        c = colors[i % (len(colors))]
        t_data = data[key]
        t_data.index = time_data
        t_data.head()
        ax = t_data.plot(
            ax=axes[i // 2, i % 2],
            color=c,
            #title=key,
            rot=25,
        )
        ax.legend([key])
    plt.tight_layout()
    plt.savefig('data/visualization.pdf')
    plt.close()

def show_data(dataset):
    os.makedirs('data',exist_ok=True)
    plt.style.use('seaborn')
    groups = numpy.arange(len(dataset.values[0]))
    fig, ax = plt.subplots(len(groups),1,figsize=(10,10),dpi=200,sharex=True,sharey=True)
    for i,group in enumerate(groups):
        ax[i].plot(dataset.values[:, group], label=dataset.columns[group], lw=0.7)
        ax[i].legend(loc='upper left')
        ax[i].set_ylabel('Traffic')
    ax[i].set_xlabel('Time [hour]')
    plt.tight_layout()
    plt.savefig('data/data.pdf')
    plt.close()

def show_heatmap(data):
    os.makedirs('data',exist_ok=True)
    plt.style.use('seaborn')
    plt.figure(figsize=(10,9))
    plt.imshow(data.corr(),cmap='viridis',aspect='auto')
    plt.xticks(range(data.shape[1]), data.columns, fontsize=12, rotation=90)
    plt.gca().xaxis.tick_bottom()
    plt.yticks(range(data.shape[1]), data.columns, fontsize=12)
    cb = plt.colorbar()
    cb.ax.tick_params(labelsize=12)
    plt.title("Feature Correlation Heatmap", fontsize=12)
    plt.grid(False)
    plt.tight_layout()
    plt.savefig('data/heatmap.pdf')
    plt.close()

def show_acf(dataset):
    time = [datetime.strptime(str(x),'%Y-%m-%d') for x in dataset.index]
    data = dataset.values
    os.makedirs('data',exist_ok=True)
    plt.style.use('seaborn')
    fig, ax = plt.subplots(2,1,figsize=(12,6))
    # Plot time series
    ax[0].plot(time,data.ravel())
    ax[0].xaxis.tick_top()
    ax[0].set_xlabel('Year')
    ax[0].set_ylabel('Daily Minimum Temperature')
    ax[0].xaxis.set_label_position('top')
    # Plot autocorrelation
    norm_data = data.copy().ravel()
    norm_data -= numpy.median(norm_data)
    norm_data /= max(abs(norm_data))
    lags, xcorr, _, _ = ax[1].xcorr(norm_data,norm_data,maxlags=len(norm_data)-1)
    lags = lags/365
    ax[1].clear()
    ax[1].fill_between(lags,xcorr,color='black',lw=0)
    #ax[1].set_xlim(-500,500)
    ax[1].set_ylim(-1,1)
    ax[1].set_xlabel('Lags [year]')
    ax[1].set_ylabel('Auto-correlation')
    plt.tight_layout()
    plt.savefig('data/acf.pdf')
    plt.close()

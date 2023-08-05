# System
import re
import os
import ast
import glob

# Externals
import numpy
import plotly.graph_objects as go
import matplotlib as mpl
import matplotlib.pyplot as plt
import pickle5 as pickle
from scipy import signal
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from matplotlib import ticker, cm
from matplotlib.colors import LogNorm
from matplotlib.ticker import FormatStrFormatter
from mpl_toolkits.mplot3d import Axes3D
from plotly.subplots import make_subplots

# Locals
from .extract import *
from ..dnnmodels import training
from ..datasets import get_data
from ..hyperparams import set_hyperparams

def plot_convergence(results,isurr=None,ylim=[],xlim=[],save=None,dpi=100,**kwargs):
    loss, stdev = results
    x = numpy.arange(len(loss))+1
    plt.style.use('seaborn')
    plt.figure(figsize=(6,4),dpi=dpi)
    plt.plot(x,loss,color='black',lw=0.5,zorder=1,
             label='Surrogate Modeling',drawstyle='steps-post')
    plt.fill_between(x,loss-stdev/2,loss+stdev/2,
                     alpha=0.5,lw=0,color='tomato',step='post',
                     label='Standard Deviation')
    if isurr!=None:
        plt.axvline(isurr,color='black',lw=1,ls='dashed')
    if len(ylim)>0:
        plt.ylim(ylim)
    if len(xlim)>0:
        plt.xlim(xlim)
    else:
        plt.xlim(1,len(loss))
    plt.xlabel('Index of function evaluations')
    plt.ylabel('Loss')
    plt.legend(loc='upper right')
    plt.tight_layout()
    if save==None:
        plt.show()
    else:
        plt.savefig(save+'.pdf')
        plt.close()

def get_custom_data(results,sensitivity=False):
    hp_names = []
    customdata = results[['tot_prms','loss','stdev']].to_numpy().T
    text_coord = \
        '<b>Model Results:</b><br>' + \
        'Mean Loss of %{customdata[1]:.5f}<br>' + \
        'Uncertainty of %{customdata[2]:.5f}<br>' + \
        '%{customdata[0]:,} trainable parameters<br><br>' + \
        '<b>Hyperparameter Set:</b><br>'
    pass_col, hp_idx = True, 0
    for hp_name in results.columns:
        if hp_name=='tot_prms':
            pass_col = False
            continue
        elif pass_col or hp_name in ['nevals','time']:
            continue
        hp_fmt, hp_vals = 'i', results[hp_name].to_numpy()
        hp_idx+=1
        if '.' in str(hp_vals):
            hp_fmt = '.%if' % len(str(hp_vals).split('.')[-1])
        text_coord += (hp_name+' = %{customdata['+str(int(hp_idx)+2)+']:'+hp_fmt+'}<br>')
        customdata = numpy.vstack((customdata,hp_vals))
        hp_names.append(hp_name)
    text_coord += '<extra></extra>'
    return text_coord, customdata.T, hp_names

def plot_solutions(results,plotly=True,**kwargs):
    if plotly:
        dynamic_solutions(results,**kwargs)
    else:
        static_solutions(results,**kwargs)

def static_solutions(input_data,metric='tot_prms',ms=50,log=False,cmap='plasma',nbins=20,**kwargs):
    """
    Scatter plot of all evaluated HPO solutions. A top histogram is also displayed
    to show the distribution of losses found across all solutions. Multiple set of
    HPO solutions can be displayed next to each other, see examples.
    
    Parameters
    ----------
    input_data : :class:`list`
        Input extracted list of solutions.
    save : :class:`bool`
        Save the figure into a PDF with filename figure.pdf
    show : :class:`bool`
        Display figure.
        
    Examples
    --------
    A simple example of the ``input_data`` list can be as follows:
    
    >>> input_data = [solutions]
    
    where ``solutions`` is a set of solutions extracted from the saved log files
    using the :method:`hyppo.extract` function.
    
    
    More than one datasets can also be considered. For instance, let's consider two
    set of solutions, one, ``data1``, contains solutions obtained using Gaussian
    Process surrogate modeling, the other, ``data2``, are solutions obtained doing
    only random sampling, the ``input_data`` can be built as follows:
    
    >>> input_data = [[data1,'Gaussian Process'],[data2,'Random Sampling']]
    """
    color_metric = input_data[metric]
    plt.style.use('seaborn')
    fig, ax = plt.subplots(2,1,figsize=(10,5),gridspec_kw={'height_ratios': [1, 3]},dpi=200,sharex=True,sharey='row')
    plt.subplots_adjust(left=0.08,top=0.95,right=0.88,wspace=0.05,hspace=0.1)
    print('%i solutions displayed' % len(input_data))
    ax[0].hist(input_data.loss,range=[min(input_data.loss),max(input_data.loss)],rwidth=0.9,bins=nbins,histtype='bar')
    im = ax[1].scatter(input_data.loss,input_data.stdev,c=color_metric,lw=0.1,alpha=0.5,s=ms,cmap=cmap)
    ax[1].minorticks_off()
    ax[1].set_xlabel('Loss')
    ax[1].set_ylabel(r'1-$\mathrm{\sigma}$ Deviation')
    if log:
        ax[1].set_xscale('log')
        ax[1].set_yscale('log')
    ax[1].grid(which='minor', color='w', linestyle='dashed', lw=0.8)
    cax = plt.axes([0.89, 0.125, 0.02, 0.575])
    cbar = plt.colorbar(im,cax=cax,format='%.0e')
    cbar.set_alpha(1)
    cbar.draw_all()
    cbar.set_label('Number of trainable parameters' if metric=='tot_prms' else metric)
    plt.savefig('figure.pdf')
    plt.show()
    plt.close()
    
def dynamic_solutions(results,ms=20,edgewidth=2,log=True,metric='tot_prms',height=500,**kwargs):
    text_coord, custom_data, _ = get_custom_data(results)
    fig = go.Figure(
        data=go.Scatter(
            x=results.loss,
            y=results.stdev,
            mode='markers',
            customdata=custom_data,
            hovertemplate=text_coord,
            marker=dict(
                size=ms,
                opacity=0.5,
                color=results[metric],
                colorbar=dict(
                    thickness=20,
                    title='Number of trainable parameters' if metric=='tot_prms' else metric,
                    titleside='right'
                ),
                line=dict(
                    color='black',
                    width=edgewidth,
                ),
            ),
        )
    )
    if log:
        fig.update_xaxes(type='log')
        fig.update_yaxes(type='log')
    fig.update_layout(
        autosize=True,
        xaxis_title='Loss',
        yaxis_title='1-'+u'\u03C3'+' Deviation',
        font=dict(size=15),
        margin=dict(l=0, r=0, b=0, t=0),
    )
    fig.write_html('solutions.html')
    fig.update_layout(height=height)
    fig.show()

def plot_sensitivity(results,plotly=True,**kwargs):
    if plotly:
        dynamic_sensitivity(results,**kwargs)
    else:
        static_sensitivity(results,**kwargs)

def static_sensitivity(results,metric='stdev',ms=20,edgewidth=0.1,ncols=3,**kwargs):
    text_coord, custom_data, hp_names = get_custom_data(results,sensitivity=True)
    n_hps = custom_data.shape[1]-3
    nrows = int(numpy.ceil(n_hps/ncols))
    plt.style.use('seaborn')
    fig,ax = plt.subplots(nrows,ncols,figsize=(ncols*3+1,3*nrows),dpi=200,sharey=True)
    # ax = ax.flatten
    plt.subplots_adjust(top=0.97,wspace=0.07,hspace=0.3,right=0.9,left=0.07,bottom=0.08)
    for n,(irow,jcol) in enumerate([(i,j) for i in range(nrows) for j in range(ncols)]):
        if n+1>n_hps:
            break
        im = ax[irow][jcol].scatter(custom_data[:,3+n],results.loss,c=results[metric],lw=edgewidth,ec='black',alpha=0.5,s=ms,cmap='plasma')
        if n%ncols==0:
            ax[irow][jcol].set_ylabel('Loss')
        ax[irow][jcol].set_xlabel(hp_names[n])
    cax = plt.axes([0.92, 0.08, 0.02, 0.89])
    cbar = plt.colorbar(im,cax=cax)
    cbar.set_alpha(1)
    cbar.draw_all()
    if metric=='stdev':
        cbar.set_label(r'1-$\mathrm{\sigma}$ Deviation')
    else:
        cbar.set_label(metric)
    cbar.ax.xaxis.set_ticks_position('top')
    cbar.ax.xaxis.set_label_position('top')
    plt.savefig('figure.pdf')
    plt.show()
    plt.close()
    
def dynamic_sensitivity(results,metric='stdev',ms=20,edgewidth=2,ncols=3,log=False,height=200,**kwargs):
    """
    Parameters
    ----------
    results : :class:`pandas.core.frame.DataFrame`
      Extracted solutions from HYPPO log product files.
    ms : :class:`int`
      Marker size
    edgewidth : :class:`float`
      Marker edge line width
    ncols : :class:`int`
      Number of columns for multiplot figure
    log : :class:`bool`
      Display loss axes in logarithmic scale

    Examples
    --------
    >>> import hyppo
    >>> solutions = hyppo.extract('logs/*.log')
    >>> hyppo.hpo_sensitivity(solutions)
    
    .. raw:: html
       
       <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
       <embed type="text/html" src="../_static/plotly/sensitivity.html" width="100%" height="600">
    """
    text_coord, custom_data, hp_names = get_custom_data(results,sensitivity=True)
    n_hps = custom_data.shape[1]-3
    nrows = int(numpy.ceil(n_hps/ncols))
    fig = make_subplots(rows=nrows, cols=ncols, start_cell="top-left",
                        horizontal_spacing=0.03, vertical_spacing=0.08)
    for n,(irow,jcol) in enumerate([(i+1,j+1) for i in range(nrows) for j in range(ncols)]):
        if n+1>n_hps:
            break
        fig.add_trace(
            go.Scatter(
                x=custom_data[:,3+n],
                y=results.loss,
                mode='markers',
                customdata=custom_data,
                hovertemplate=text_coord,
                marker=dict(
                    size=ms,
                    opacity=0.5,
                    color=results[metric],
                    colorbar=dict(
                        thickness=20,
                        title='1-'+u'\u03C3'+' Deviation' if metric=='stdev' else metric,
                        titleside='right'
                    ),
                    line=dict(
                        color='black',
                        width=edgewidth,
                    ),
                ),
            ),row=irow, col=jcol)
        fig['layout']['xaxis%i' % (n+1)]['title'] = hp_names[n]
        if n%ncols==0:
            fig['layout']['yaxis%i' % (n+1)]['title'] = 'Loss'
    if log:
        fig.update_yaxes(type='log')
    fig.update_layout(
        autosize=True,
        margin=dict(l=0, r=0, b=0, t=0),
        showlegend=False,
    )
    fig.write_html('sensitivity.html')
    fig.update_layout(height=height*nrows)
    fig.show()

def focus_sensitivity(results,focus,up_bound=None,metric='stdev',ms=20,ew=0.1,cmap='jet',**kwargs):
    """
    Parameters
    ----------
    ew : float
      Edge width
    ms : float
      Marker size
    """
    if up_bound==None:
        up_bound = max(focus.loss)
    data1, hp_names = get_custom_data(results,sensitivity=True)[1:]
    data2 = get_custom_data(focus,sensitivity=True)[1]
    plt.style.use('seaborn')
    fig,ax = plt.subplots(2,6,figsize=(12,5),dpi=200,sharey='row',sharex='col')
    plt.draw()
    plt.subplots_adjust(top=0.97,wspace=0.05,hspace=0.05,right=0.92,left=0.07,bottom=0.15)
    for n in range(6):
        if n+1>data1.shape[1]-3:
            break
        im1 = ax[0][n-1].scatter(data1[:,n+3],results.loss,c=results[metric],lw=ew,ec='black',alpha=0.5,s=ms,cmap=cmap)
        im2 = ax[1][n-1].scatter(data2[:,n+3],focus.loss,c=focus[metric],lw=ew,ec='black',s=ms,cmap=cmap)
        ax[1][n-1].set_xlabel(hp_names[n])
        ax[1][n-1].tick_params(axis='x',labelrotation=45)
    ax[0][0].set_ylabel('Loss')
    ax[1][0].set_ylabel('Loss below %.2f' % up_bound)
    cax = plt.axes([0.93, 0.15, 0.02, 0.83])
    cbar = plt.colorbar(im1,cax=cax)
    cbar.set_alpha(1)
    cbar.draw_all()
    if metric=='stdev':
        cbar.set_label(r'1-$\mathrm{\sigma}$ Deviation')
    else:
        cbar.set_label(metric)
    cbar.ax.xaxis.set_ticks_position('top')
    cbar.ax.xaxis.set_label_position('top')
    plt.savefig('figure.pdf')
    plt.show()
    plt.close()
    
def model_visualization_1d(X,Y,path,evaluation,surrogate,imax=10,sigma=False,ylim=[-0.5,2.5]):
    scaler = round(1/(X[1]-X[0]))
    os.makedirs('%s/plots' % (path),exist_ok=True)
    plt.style.use('seaborn')
    for i,hp1s in enumerate(surrogate['hp1']):
        if i==imax:
            break
        model = pickle.load(open('%s/models/surrogate_%i/model.pkl' % (path,hp1s),'rb'))
        if sigma:
            Y_pred, Y_sigma = model.predict(X.reshape(-1, 1)*scaler,return_std=True)
        else:
            Y_pred = model.predict(X.reshape(-1, 1)*scaler,return_std=False)
        Y_pred = Y_pred.squeeze()
        fig,ax = plt.subplots(1,3,figsize=[12,4],dpi=200,sharex=True,sharey=True)
        fig.suptitle('Surrogate Modeling - Iteration %i / %i - Hyperparameters (%.2f)' % (i+1,imax,hp1s/scaler))
        ax[0].set_ylim(ylim)
        ax[0].plot(X,Y,'black')
        ax[1].plot(X,Y,'black',ls='dashed')
        ax[1].plot(X,Y_pred,'black')
        if sigma:
            ax[1].fill_between(X,Y_pred-Y_sigma/2,Y_pred+Y_sigma/2,alpha=0.2,lw=0,color='blue',step='post')
        ax[2].plot(X,Y-Y_pred,'black')
        for k in range(2):
            ax[k].set_xlabel('X')
            for hp,loss in zip(evaluation['hp1'],evaluation['loss']):
                ax[k].plot([hp/scaler], [loss], 'bx', mew=3)
            for n,(hp,loss) in enumerate(zip(surrogate['hp1'],surrogate['loss'])):
                if n>i: break
                ax[k].plot([hp/scaler], [loss], 'rx', mew=3)
        ax[0].set_ylabel('Y')
        plt.tight_layout()
        plt.savefig('%s/plots/iter_%02i' % (path,i+1))
        plt.close()
    
def model_visualization_2d(X,Y,path,evaluation,surrogate,imax=10,sigma=False):
    scaler = round(1/(X[1]-X[0]))
    X1, Y1 = numpy.meshgrid(X, Y)
    R = numpy.sqrt(X1**2 + Y1**2)
    Z = 0.4 - (1. / numpy.sqrt(2 * numpy.pi)) * numpy.exp(-.5*R**2)
    Z_scaler = round(Z.max(),1)
    os.makedirs('%s/plots' % (path),exist_ok=True)
    plt.style.use('seaborn')
    for i,(hp1s,hp2s) in enumerate(zip(surrogate['hp1'],surrogate['hp2'])):
        if i==imax:
            break
        model = pickle.load(open('%s/models/surrogate_%i_%i/model.pkl' % (path,hp1s,hp2s),'rb'))
        comb = numpy.array([(x,y) for y in Y for x in X]).reshape(-1, 2)*scaler
        Y_pred = model.predict(comb).reshape(len(X),len(Y))
        Y_pred[Y_pred<0], Y_pred[Y_pred>0.4] = 0.0, Z_scaler
        fig,ax = plt.subplots(1,3,figsize=[12,4],dpi=200,sharex=True,sharey=True)
        fig.suptitle('Surrogate Modeling - Iteration %i / %i - Hyperparameters (%.2f, %.2f)' % (i+1,imax,hp1s/scaler,hp2s/scaler))
        im0 = ax[0].contourf(X1,Y1,Z,levels=numpy.linspace(0,Z_scaler,scaler),cmap='viridis')
        im1 = ax[1].contourf(X1,Y1,Y_pred,levels=numpy.linspace(0,Z_scaler,scaler),cmap='viridis')
        im2 = ax[2].contourf(X1,Y1,Z-Y_pred,levels=numpy.linspace(-Z_scaler,Z_scaler,scaler),cmap='bwr')
        for k in range(3):
            ax[k].set_xlabel('X')
            for hp1,hp2 in zip(evaluation['hp1'],evaluation['hp2']):
                ax[k].plot(hp1/scaler, hp2/scaler, 'kx', mew=3)
            for n,(hp1,hp2) in enumerate(zip(surrogate['hp1'],surrogate['hp2'])):
                if n>i: break
                ax[k].plot(hp1/scaler, hp2/scaler, 'rx', mew=3)
            cbar = plt.colorbar(eval('im%i' % k), ax=ax[k],ticks=[0,Z_scaler/2,Z_scaler] if k<2 else [-Z_scaler,0,Z_scaler],
                                shrink=0.8, orientation='horizontal', location='top')
        ax[0].set_ylabel('Y')
        plt.tight_layout()
        plt.savefig('%s/plots/iter_%02i' % (path,i+1))
        plt.close()

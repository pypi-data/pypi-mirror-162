# -*- coding: utf-8 -*-
"""
Simulate Qantile Data
"""


import os
from tqdm import tqdm, trange
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

import scipy
from scipy import signal
from scipy.stats import norm

os.chdir('C:/Users/10200/Desktop/research/spectra_py/QuantileSpec')

import multiprocessing
from joblib import Parallel, delayed
import QuantSpecVI

#
## Function to calculate quantile DFT-statistic
#
def clipping(x, quant = [0.1, 0.5, 0.9]):
    # clip time series based on quantiles
    r = scipy.stats.mstats.rankdata(x, axis=0) / x.shape[0]
    clipped = [1*(r[:,i] <= j) for i in range(r.shape[1]) for j in quant]
    return np.stack(clipped, axis=1)

def freq_(x):
    n = x.shape[0]
    if np.mod(n, 2) == 0:
        # n is even
        fq_y = np.arange(1, int(n/2)+1) / n
    else:
        # n is odd
        fq_y = np.arange(1, int((n-1)/2)+1) / n     
    return fq_y
    
def sc_fft(clipped_ts):
    # x is a n-by-p matrix
    # unscaled fft
    x = clipped_ts
    y = np.apply_along_axis(np.fft.fft, 0, x)
    # scale it
    n = x.shape[0]
    y = y / np.sqrt(2*np.pi*n)
    # discard 0 freq
    y = y[1:]
    if np.mod(n, 2) == 0:
        # n is even
        y = y[0:int(n/2)]
        fq_y = np.arange(1, int(n/2)+1) / n
    else:
        # n is odd
        y = y[0:int((n-1)/2)]
        fq_y = np.arange(1, int((n-1)/2)+1) / n
    return y

#
# simulate data using numpy
#

# ar with white noise
def ar_sim(Phi, sigma, n=512):
    # Phi:   AR coefficient array. M0-by-p-by-p. i-th row imply lag (M-i), p is dim of time series.
    # n:     time stamps  
    # sigma: white noise variance
    dim = Phi.shape[1]
    lag = Phi.shape[0]
    
    Sigma = sigma
    x_init = np.array(np.zeros(shape = [lag+1, dim]))
    x = np.empty((n+101, dim))
    x[:] = np.NaN
    x[:lag+1, ] = x_init
    
    for i in np.arange(lag+1, x.shape[0]):
        if dim > 1:
            x[i,] = np.sum(np.matmul(Phi, x[i-1:i-lag-1:-1][...,np.newaxis]), axis=(0, -1)) + \
                    np.random.multivariate_normal(np.repeat(0., dim), Sigma)
        else:
            x[i,] = np.sum(np.matmul(Phi, x[i-1:i-lag-1:-1][...,np.newaxis]), axis=(0, -1)) + \
                    np.random.normal(np.repeat(0., dim), Sigma)
    x = x[101: ]
    return x
    # x = matrix(x[, 1], ncol = 1) | if need only 1-d time-series
    
def arch1_sim(n=512, sigma = 1.):
    # Phi:   AR coefficient array. M0-by-p-by-p. i-th row imply lag (M-i), p is dim of time series.
    # n:     time stamps  
    # sigma: white noise variance
    x_init = np.array(np.zeros(shape = [2, 1]))
    x = np.empty((n+101, 1))
    x[:] = np.NaN
    x[:2, ] = x_init
    for i in np.arange(2, x.shape[0]):
        x[i,] = (1/1.9 + 0.9*x[i-1]**2)**0.5 * \
                np.random.normal(0, sigma)
    x = x[101: ]
    return x

def qar1_sim(n=512):
    x_init = np.array(np.zeros(shape = [2, 1]))
    x = np.empty((n+101, 1))
    x[:] = np.NaN
    x[:2, ] = x_init
    for i in np.arange(2, x.shape[0]):
        v_t = np.random.uniform()
        x[i,] = 0.1*norm.ppf(v_t) + 1.9*(v_t - 0.5)*x[i-1]
    x = x[101: ]
    return x

def qvar1_sim(n=512):
    x_init = np.array(np.zeros(shape = [2, 2]))
    x = np.empty((n+101, 2))
    x[:] = np.NaN
    x[:2, ] = x_init
    Theta = lambda v: np.array([[1.9*(v[0]-0.5), 1.*(v[0]-0.5)], 
                                [1.*(v[1]-0.5), 0.4*(v[1]+0.2)]])
    for i in np.arange(2, x.shape[0]):
        v_t = np.random.uniform(size=[2])
        x[i,] = 0.1*norm.ppf(v_t) + np.matmul(Theta(v_t), x[i-1])
    x = x[101: ]
    return x

def plot_qspec(x):
    Spec_hs = QuantSpecVI.SpecFactorPrep(x)
    # clipping time series by quantile
    quant = [0.1, 0.5, 0.9]
    Spec_hs.clipping(quant=quant)
    Spec_hs.sc_fft()

    y_ft = Spec_hs.y_ft
    quant_spec = y_ft[...,np.newaxis]
    quant_perdgm_mat = np.matmul(quant_spec, np.conjugate(np.transpose(quant_spec, axes = [0,2,1])))

    f = Spec_hs.freq
    f_true = np.arange(1, int(512/2)+1) / 512
    fig, ax = plt.subplots(Spec_hs.p_dim,Spec_hs.p_dim, figsize = (13, 8), dpi=60)
    for idx in range(Spec_hs.p_dim):        
        ax[idx, idx].plot(f, np.real(quant_perdgm_mat[:,idx,idx]), marker = '.', markersize=2, linestyle = '-')
        #ax[idx, idx].tick_params(labelsize=20)
        ax[idx, idx].set_xlabel(r'$\nu$', fontsize=10)
        #ax.set_title(r'$f_{%d, %d}$'%(idx+1, idx+1), pad=20, fontsize=15)
        ax[idx, idx].set_ylabel(r'$f_{%d, %d}$'%(idx+1, idx+1), fontsize=10, labelpad=10, rotation=90)
        #ax.set_xlim([0, 0.5])
        ax[idx,idx].locator_params(axis='y', nbins=3)
        ax[idx,idx].tick_params(axis='y', labelrotation=90)

    for jj in np.arange(0, Spec_hs.p_dim):
        for ii in np.arange(jj+1, Spec_hs.p_dim):                
            ax[ii,jj].plot(f, np.real(quant_perdgm_mat[:,ii,jj]), marker = '.', markersize=2, linestyle = '-') 
            #ax[ii,jj].tick_params(labelsize=20)
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=10)
            #ax.set_title(r'$f_{%d, %d}$'%(idx+1, idx+1), pad=20, fontsize=15)
            ax[ii,jj].set_ylabel(r'$Re(f_{%d, %d})$'%(ii+1, jj+1), fontsize=10, labelpad=10, rotation=90)
            #ax.set_xlim([0, 0.5])
            plt.yticks(rotation=90, va="center")
            ax[ii,jj].locator_params(axis='y', nbins=3)
            ax[ii,jj].tick_params(axis='y', labelrotation=90)
        
    for ii in np.arange(0, Spec_hs.p_dim):
        for jj in np.arange(ii+1, Spec_hs.p_dim):            
            ax[ii,jj].plot(f, np.imag(quant_perdgm_mat[:,ii,jj]), marker = '.', markersize=2, linestyle = '-') 
            #ax[ii,jj].tick_params(labelsize=20)
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=10)
            #ax.set_title(r'$f_{%d, %d}$'%(idx+1, idx+1), pad=20, fontsize=15)
            ax[ii,jj].set_ylabel(r'$Im(f_{%d, %d})$'%(ii+1, jj+1), fontsize=10, labelpad=10, rotation=90)
            #ax.set_xlim([0, 0.5])
            ax[ii,jj].tick_params(axis='y', labelrotation=90)
            ax[ii,jj].locator_params(axis='y', nbins=3)
    plt.tight_layout()
    plt.show()
    

if __name__ == '__main__':
    num_cores = multiprocessing.cpu_count()
    ##
    ## ar2
    ##
    Phi_1 = np.array([[[0.]],[[-0.36]]])
    x = ar_sim(Phi_1, sigma=1., n=512*2)
    plot_qspec(x)
    plt.figure(figsize=(6,6))
    plt.plot(x, linewidth=0.5)
    plt.title('AR(2)',pad=20,fontsize=20)
    plt.xlabel("t", fontsize=20,labelpad=10)
    plt.show()
    #np.save('./Data/Zhang_ar2', x)
    
    quant = [0.1, 0.5, 0.9]
    f = freq_(x)
    
    def my_function(i):
        return sc_fft(clipping(ar_sim(Phi_1, sigma=1., n=512), quant=quant))
    if __name__ == "__main__":
        ar2_spec_ls = Parallel(n_jobs=num_cores)(delayed(my_function)(i) 
                                                            for i in trange(10000))
    
    
    quant_spec = np.stack(ar2_spec_ls, axis=0)[...,np.newaxis]
    quant_spec_mat = np.matmul(quant_spec, np.conjugate(np.transpose(quant_spec, axes = [0,1,3,2])))
    mean_qspec = np.mean(quant_spec_mat, axis=0)
    #np.save('./Data/Zhang_ar2_qspec_true', mean_qspec)
    
    
    for ii in range(mean_qspec.shape[1]):
        for jj in range(ii, mean_qspec.shape[1]):
            plt.plot(f, np.real(mean_qspec[...,ii, jj]), linewidth=3)
            plt.xlim([0,0.5])
            plt.title(r'$S_{%d,%d}$'%(ii+1,jj+1), fontsize = 30)
            plt.show()
    
    ## var2
    Phi = np.array([[[0.5, 0.], [0., -0.36]],[[0.1, -0.3], [0., 0.2]]])
    sigma = np.array([[1.,0.5], [0.5, 1.]])
    x = ar_sim(Phi, sigma, n=512)
    f = freq_(x)
    
    plt.plot(x)
    plt.show()
    plot_qspec(x)
    #np.save('./Data/var2', x)
    
    def my_function(i):
        return sc_fft(clipping(ar_sim(Phi, sigma, n=512), quant=quant))
    if __name__ == "__main__":
        var2_spec_ls = Parallel(n_jobs=num_cores)(delayed(my_function)(i) 
                                                            for i in trange(10000))
    quant_spec = np.stack(var2_spec_ls, axis=0)[...,np.newaxis]
    quant_spec_mat = np.matmul(quant_spec, np.conjugate(np.transpose(quant_spec, axes = [0,1,3,2])))
    mean_qspec = np.mean(quant_spec_mat, axis=0)
    #np.save('./Data/var2_qspec_true', mean_qspec)
    
    
    for ii in range(mean_qspec.shape[1]):
        for jj in range(ii, mean_qspec.shape[1]):
            plt.plot(f, np.real(mean_qspec[...,ii, jj]), linewidth=3)
            plt.xlim([0,0.5])
            plt.title(r'$S_{%d,%d}$'%(ii+1,jj+1), fontsize = 30)
            plt.show()
    
    ##
    ## qar1
    ##
    x = qar1_sim(n=512*2)
    plot_qspec(x)
    plt.plot(x)
    plt.show()
    #np.save('./Data/Zhang_qar1', x)
    
    
    def my_function(i):
        return sc_fft(clipping(qar1_sim(n=512), quant=quant))
    if __name__ == "__main__":
        qar1_spec_ls = Parallel(n_jobs=num_cores)(delayed(my_function)(i) 
                                                            for i in trange(10000))
                                                    
    qar1_spec = np.stack(qar1_spec_ls, axis=0)[...,np.newaxis]
    qar1_spec_mat = np.matmul(qar1_spec, np.conjugate(np.transpose(qar1_spec, axes = [0,1,3,2])))
    mean_qar1spec = np.mean(qar1_spec_mat, axis=0)
    #np.save('./Data/Zhang_qar1_qspec_true', mean_qar1spec)
    
    
    for ii in range(mean_qar1spec.shape[1]):
        for jj in range(ii, mean_qar1spec.shape[1]):
            plt.plot(f, np.real(mean_qar1spec[...,ii, jj]), linewidth=3)
            plt.xlim([0,0.5])
            plt.title(r'$S_{%d,%d}$'%(ii+1,jj+1), fontsize = 30)
            plt.show()                                               
    
    ## qvar1
    x = qvar1_sim(n=512)
    f = freq_(x)
    
    plot_qspec(x)
    plt.plot(x)
    plt.show()
    #np.save('./Data/qvar1', x)
    
    
    def my_function(i):
        return sc_fft(clipping(qvar1_sim(n=512), quant=quant))
    if __name__ == "__main__":
        qvar1_spec_ls = Parallel(n_jobs=num_cores)(delayed(my_function)(i) 
                                                            for i in trange(50000))
                                                    
    qvar1_spec = np.stack(qvar1_spec_ls, axis=0)[...,np.newaxis]
    qvar1_spec_mat = np.matmul(qvar1_spec, np.conjugate(np.transpose(qvar1_spec, axes = [0,1,3,2])))
    mean_qvar1spec = np.mean(qvar1_spec_mat, axis=0)
    #np.save('./Data/qvar1_qspec_true', mean_qvar1spec)
    
    
    for ii in range(mean_qvar1spec.shape[1]):
        for jj in range(ii, mean_qvar1spec.shape[1]):
            plt.plot(f, np.real(mean_qvar1spec[...,ii, jj]), linewidth=3)
            plt.xlim([0,0.5])
            plt.title(r'$S_{%d,%d}$'%(ii+1,jj+1), fontsize = 30)
            plt.show()                              
    
                                                    
    ##
    ## arch1
    ##
    x = arch1_sim(n=512*2)
    plot_qspec(x)
    plt.figure(figsize=(6,6))
    plt.plot(x, linewidth=0.5)
    plt.title('ARCH(1)',pad=20,fontsize=20)
    plt.xlabel("t", fontsize=20,labelpad=10)
    plt.show()
    #np.save('./Data/Zhang_arch1', x)
    
    
    def my_function(i):
        return sc_fft(clipping(arch1_sim(n=512), quant=quant))
    if __name__ == "__main__":
        arch1_spec_ls = Parallel(n_jobs=num_cores)(delayed(my_function)(i) 
                                                            for i in trange(10000))
                                                    
    arch1_spec = np.stack(arch1_spec_ls, axis=0)[...,np.newaxis]
    arch1_spec_mat = np.matmul(arch1_spec, np.conjugate(np.transpose(arch1_spec, axes = [0,1,3,2])))
    mean_arch1spec = np.mean(arch1_spec_mat, axis=0)
    #np.save('./Data/Zhang_arch1_qspec_true', mean_arch1spec)
    
    
    for ii in range(mean_arch1spec.shape[1]):
        for jj in range(ii, mean_arch1spec.shape[1]):
            plt.plot(f, np.real(mean_arch1spec[...,ii, jj]), linewidth=3)
            plt.xlim([0,0.5])
            plt.title(r'$S_{%d,%d}$'%(ii+1,jj+1), fontsize = 30)
            plt.show()                                                       
                                                    
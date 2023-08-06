'''
Load Packages
'''
import numpy as np
import matplotlib.pyplot as plt
import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
tfb = tfp.bijectors
from example_qspec import quant_spec_vi 


'''
Load Data

To load text files (such as .txt, .csv formats) use:
    x = np.loadtxt('YOUR_DATA.csv')
'''
dataset = "arch1"
if dataset == 'ar2':
    x = np.load('utils/ar2.npy')
    spec_mat_true = np.load('utils/ar2_qspec_true.npy')
elif dataset == 'arch1':
    x = np.load('utils/arch1.npy')
    spec_mat_true = np.load('utils/arch1_qspec_true.npy')
elif dataset == 'qar1':
    x = np.load('utils/qar1.npy')
    spec_mat_true = np.load('utils/qar1_qspec_true.npy')
freq = np.arange(1,np.floor_divide(256*2, 2)+1, 1) / (256*2) # frequency for true spectral matrix


'''
Fit Model
'''
quant = [0.1, 0.5, 0.9]
spec = quant_spec_vi.QuantSpecVI(x)
with tf.device('cpu:0'):
    spec.run_model(quantile=quant, rank=3, lr_map=1e-3, ntrain_map=8e3)
fq = np.arange(1,np.floor_divide(x.shape[0], 2)+1, 1) / (x.shape[0])



'''
Visualize Results
'''
fig, ax = plt.subplots(len(quant), len(quant), figsize = (13, 8))
for ii in np.arange(len(quant)):
    for jj in np.arange(len(quant)):
        if ii == jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')        
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj], spec.result_matrix[2,...,ii,jj],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.log(np.abs(spec_mat_true[:,ii,jj])), linewidth=3, color = 'red', linestyle="-", label = 'True')
            ax[ii,jj].set_title(r'$\tau_%d,\tau_%d={%.1f}, {%.1f}$'%(ii+1,jj+1,quant[ii],quant[jj]), fontsize=15, pad=10)
            if dataset == 'arch1':
                if ii == 1:
                    ax[ii,jj].set_ylim([-4,-2.5])
                else:
                    ax[ii,jj].set_ylim([-5.5,-2.5])
            if dataset == 'qar1':
                if ii == 1:
                    ax[ii,jj].set_ylim([-4,-2.5])    
                else:
                    ax[ii,jj].set_ylim([-5.2,-3.2])
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)
        if ii > jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj], spec.result_matrix[2,...,ii,jj],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.real(spec_mat_true[:, ii, jj]), linestyle='-', color = 'red', linewidth=3, label = 'Truth')
            ax[ii,jj].set_title(r'$(\Re) \,\, \tau_%d,\tau_%d={%.1f}, {%.1f}$'%(ii+1,jj+1,quant[ii],quant[jj]), fontsize=15, pad=10)
            if ii - jj == 1 and dataset == 'arch1':
                ax[ii,jj].set_ylim([-0.01,0.03])
            if dataset == 'qar1':
                if ii-jj==1:
                    ax[ii,jj].set_ylim([-0.006,0.024])
                else:
                    ax[ii,jj].set_ylim([-0.01,0.012])            
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)
        if ii < jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj], spec.result_matrix[2,...,ii,jj],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.imag(spec_mat_true[:, ii, jj]), linestyle='-', color = 'red', linewidth=3, label = 'Truth')
            ax[ii,jj].set_title(r'$(\Im) \,\, \tau_%d,\tau_%d={%.1f}, {%.1f}$'%(ii+1,jj+1,quant[ii],quant[jj]), fontsize=15, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)            
            if dataset == 'ar2' or dataset == 'arch1':
                ax[ii,jj].set_ylim([-0.02,0.02])
            if dataset == 'qar1':
                ax[ii,jj].set_ylim([-0.010,0.015])
            ax[ii,jj].grid(True)            
        if ii == len(quant)-1:
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=15)
        if ii == 0 and jj == 0:
            ax[ii,jj].legend(ncol=3, loc='lower right')
plt.tight_layout()
plt.show()
fig.savefig('simq_%s.png'%(dataset))
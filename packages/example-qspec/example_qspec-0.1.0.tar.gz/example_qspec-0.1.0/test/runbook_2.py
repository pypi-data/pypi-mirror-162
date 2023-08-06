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
x = np.load('utils/qvar1.npy')
spec_mat_true = np.load('utils/qvar1_qspec_true.npy')
freq = np.arange(1,np.floor_divide(256*2, 2)+1, 1) / (256*2) # frequency for true spectral matrix


'''
Fit Model
'''
quant = [0.1, 0.5, 0.9]
spec = quant_spec_vi.QuantSpecVI(x)
with tf.device('cpu:0'):
    spec.run_model(quantile=quant, rank=15, lr_map=1e-3, ntrain_map=8e3)
fq = np.arange(1,np.floor_divide(x.shape[0], 2)+1, 1) / (x.shape[0])


'''
Visualize Results
'''
fig, ax = plt.subplots(len(quant), len(quant), figsize = (13, 8), dpi=60)
plt.suptitle(r'f$^{1,1}_{\tau_i, \tau_j}$', fontsize=25, y=1)
for ii in np.arange(len(quant)):
    for jj in np.arange(len(quant)):
        if ii == jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')        
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj], spec.result_matrix[2,...,ii,jj],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.log(np.abs(spec_mat_true[:,ii,jj])), linewidth=2, color = 'red', linestyle="-", label = 'True')
            ax[ii,jj].set_title(r'$\tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii], quant[jj]), fontsize=20, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)
            if ii==1:
                ax[ii,jj].set_ylim([-3.7, -2.7])
        if ii > jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj], spec.result_matrix[2,...,ii,jj],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.real(spec_mat_true[:, ii, jj]), linestyle='-', color = 'red', linewidth=2, label = 'Truth')
            ax[ii,jj].set_title(r'$(\Re) \,\, \tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii], quant[jj]), fontsize=20, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)
        if ii < jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj], spec.result_matrix[2,...,ii,jj],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.imag(spec_mat_true[:, ii, jj]), linestyle='-', color = 'red', linewidth=2, label = 'Truth')
            ax[ii,jj].set_title(r'$(\Im) \,\, \tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii], quant[jj]), fontsize=20, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)            
        if ii == len(quant)-1:
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=20)
plt.tight_layout()
plt.show()
fig.savefig('simq_%s_f11.png'%('qvar1'))

fig, ax = plt.subplots(len(quant), len(quant), figsize = (13, 8), dpi=60)
plt.suptitle(r'$\Re($f$^{1,2}_{\tau_i, \tau_j})$', fontsize=25, y=1)
for ii in np.arange(len(quant)):
    for jj in np.arange(len(quant)):
        ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii+len(quant),jj], linewidth=3, color = 'k', linestyle="--", label = 'Est')
        ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii+len(quant),jj], spec.result_matrix[2,...,ii+len(quant),jj],
                        color = 'lightgray', alpha = 1, label = '95% CI')
        ax[ii,jj].plot(freq, np.real(spec_mat_true[:,ii+len(quant),jj]), linestyle='-', color = 'red', linewidth=2, label = 'Truth')
        ax[ii,jj].set_title(r'$\tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii],quant[jj]), fontsize=20, pad=10)
        ax[ii,jj].set_xlim([0,0.5])
        ax[ii,jj].grid(True)
        if ii == len(quant)-1:
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=20)
        if ii == 1 and jj == 1:
            ax[ii,jj].set_ylim([-0.007, 0.007])
        elif ii == 2 and jj == 0:
            ax[ii,jj].set_ylim([-0.006, 0.003])
        elif ii == 0 and jj == 2:
            ax[ii,jj].set_ylim([-0.005, 0.004])
plt.tight_layout()
plt.show()
fig.savefig('simq_%s_f12re.png'%('qvar1'))

fig, ax = plt.subplots(len(quant), len(quant), figsize = (13, 8), dpi=60)
plt.suptitle(r'$\Im($f$^{1,2}_{\tau_i, \tau_j})$', fontsize=25, y=1)
for ii in np.arange(len(quant)):
    for jj in np.arange(len(quant)):
        ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii,jj+len(quant)], linewidth=3, color = 'k', linestyle="--", label = 'Est')
        ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii,jj+len(quant)], spec.result_matrix[2,...,ii,jj+len(quant)],
                        color = 'lightgray', alpha = 1, label = '95% CI')
        ax[ii,jj].plot(freq, np.imag(spec_mat_true[:,ii+len(quant),jj]), linestyle='-', color = 'red', linewidth=2, label = 'Truth')
        ax[ii,jj].set_title(r'$\tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii],quant[jj]), fontsize=20, pad=10)
        ax[ii,jj].set_xlim([0,0.5])
        ax[ii,jj].grid(True)
        if ii == len(quant)-1:
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=20)
        
        if ii == 1 and jj == 1:
            ax[ii,jj].set_ylim([-0.008, 0.008])        
        elif ii == jj:
            ax[ii,jj].set_ylim([-0.005, 0.005])
        elif ii > jj:
            ax[ii,jj].set_ylim([-0.008, 0.003])
        elif ii < jj:
            ax[ii,jj].set_ylim([-0.004, 0.008])
plt.tight_layout()
plt.show()
fig.savefig('simq_%s_f12im.png'%('qvar1'))

fig, ax = plt.subplots(len(quant), len(quant), figsize = (13, 8), dpi=60)
plt.suptitle(r'f$^{2,2}_{\tau_i, \tau_j}$', fontsize=25, y=1)
for ii in np.arange(len(quant)):
    for jj in np.arange(len(quant)):
        if ii == jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii+len(quant),jj+len(quant)], linewidth=3, color = 'k', linestyle="--", label = 'Est')        
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii+len(quant),jj+len(quant)], spec.result_matrix[2,...,ii+len(quant),jj+len(quant)],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.log(np.abs(spec_mat_true[:,ii+len(quant),jj+len(quant)])), linewidth=2, color = 'red', linestyle="-", label = 'True')
            ax[ii,jj].set_title(r'$\tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii],quant[jj]), fontsize=20, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)
            if ii==0:
                ax[ii,jj].set_ylim([-5, -3.5])
        if ii > jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii+len(quant),jj+len(quant)], linewidth=3, color = 'k', linestyle="--", label = 'Est')
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii+len(quant),jj+len(quant)], spec.result_matrix[2,...,ii+len(quant),jj+len(quant)],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.real(spec_mat_true[:,ii+len(quant),jj+len(quant)]), linestyle='-', color = 'red', linewidth=2, label = 'Truth')
            ax[ii,jj].set_title(r'$(\Re) \,\, \tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii],quant[jj]), fontsize=20, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)
            if ii - jj == 2:
                ax[ii,jj].set_ylim([-0.004, 0.008])
        if ii < jj:
            ax[ii,jj].plot(fq, spec.result_matrix[1,...,ii+len(quant),jj+len(quant)], linewidth=3, color = 'k', linestyle="--", label = 'Est')
            ax[ii,jj].fill_between(fq, spec.result_matrix[0,...,ii+len(quant),jj+len(quant)], spec.result_matrix[2,...,ii+len(quant),jj+len(quant)],
                            color = 'lightgray', alpha = 1, label = '95% CI')
            ax[ii,jj].plot(freq, np.imag(spec_mat_true[:,ii+len(quant),jj+len(quant)]), linestyle='-', color = 'red', linewidth=2, label = 'Truth')
            ax[ii,jj].set_title(r'$(\Im) \,\, \tau_{%d},\tau_{%d}={%.1f}, {%.1f}$'%(ii+1, jj+1, quant[ii],quant[jj]), fontsize=20, pad=10)
            ax[ii,jj].set_xlim([0,0.5])
            ax[ii,jj].grid(True)       
            ax[ii,jj].set_ylim([-0.004, 0.006])
        if ii == len(quant)-1:
            ax[ii,jj].set_xlabel(r'$\nu$', fontsize=20)
plt.tight_layout()
plt.show()
fig.savefig('simq_%s_f22.png'%('qvar1'))

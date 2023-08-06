# -*- coding: utf-8 -*-
"""
Define quantile spectral model class

@author: Zhixiong Hu, UCSC
"""
import timeit
import numpy as np
import scipy.stats
import tensorflow as tf
import tensorflow_probability as tfp
tfd = tfp.distributions
tfb = tfp.bijectors

class SPrep:  # Parent 
    def __init__(self, x):
        self.ts = x
        self.y_ft = []    # inital
        self.freq = []
        self.p_dim = []
        self.Xmat_delta = []
        self.Xmat_theta = []
        self.Zar = []

    def clipping(self, quant = [0.1, 0.5, 0.9]):
        r = scipy.stats.mstats.rankdata(self.ts, axis=0) / self.ts.shape[0]
        self.ranknorm = r
        clipped = [1*(r[:,i] <= j) for i in range(r.shape[1]) for j in quant]
        self.clipped_ts = np.stack(clipped, axis=1)
        return self.clipped_ts
        
    # discarding the rest of freqs
    def sc_fft(self):
        # unscaled fft
        x = self.clipped_ts
        y = np.apply_along_axis(np.fft.fft, 0, x)
        # scale it
        n = x.shape[0]
        y = y / np.sqrt(2*np.pi*n)  # y = y / np.sqrt(n)
        # discard 0 freq
        y = y[1:]
        if np.mod(n, 2) == 0:
            # n is even
            y = y[0:np.int(n/2)]
            fq_y = np.arange(1, np.int(n/2)+1) / n
        else:
            y = y[0:np.int((n-1)/2)]
            fq_y = np.arange(1, np.int((n-1)/2)+1) / n
        p_dim = x.shape[1]
            
        self.y_ft = y
        self.freq = fq_y
        self.p_dim = p_dim
        return dict(y=y, fq_y=fq_y, p_dim=p_dim)
    # y_ft = sc_fft(x)


    def DR_basis(self, freq, N = 10, style='cosin'):
        nu = freq
        if style == 'cosin':
            basis = np.array([np.sqrt(2)*np.cos(x*np.pi*nu) for x in np.arange(1, N + 1)]).T
            #basis 
        else:
            basis = np.array([np.sqrt(2)*np.sin(x*np.pi*nu) for x in np.arange(1, N + 1)]).T
            #basis 
        return basis



    def Xmtrix(self, nu, N_basis = 10):
        Xmat_re = np.concatenate([np.column_stack([np.repeat(1, nu.shape[0]), nu]), self.DR_basis(nu, N = N_basis, style='cosin')], axis = 1)
        Xmat_im = np.concatenate([np.column_stack([np.repeat(1, nu.shape[0]), nu]), self.DR_basis(nu, N = N_basis, style='sin')], axis = 1)
        #Xmat_im = self.DR_basis(nu, N = N_basis, style='sin')
        try:
            if self.Xmat_re is not None:
                  Xmat_re = tf.convert_to_tensor(Xmat_re, dtype = tf.float32)
                  Xmat_im = tf.convert_to_tensor(Xmat_im, dtype = tf.float32)
                  return Xmat_re, Xmat_im
        except: # NPE
            self.Xmat_re = tf.convert_to_tensor(Xmat_re, dtype = tf.float32) # 
            self.Xmat_im = tf.convert_to_tensor(Xmat_im, dtype = tf.float32)
            self.N_basis = N_basis
            return self.Xmat_re, self.Xmat_re
        
class Prep: 
    def __init__(self, x):
        self.ts = x
        if x.shape[1] < 2:
            raise Exception("Time series should be at least 2 dimensional.")

        self.y_ft = []    # inital
        self.freq = []
        self.p_dim = []
        self.Zar = []
    
    # scaled fft and get the elements of freq = 1:[Nquist]
    # discarding the rest of freqs
    def sc_fft(self):
        # x is a n-by-p matrix
        # unscaled fft
        x = self.ts
        y = np.apply_along_axis(np.fft.fft, 0, x)
        # scale it
        n = x.shape[0]
        y = y / np.sqrt(n)
        # discard 0 freq
        y = y[1:]
        if np.mod(n, 2) == 0:
            # n is even
            y = y[0:np.int(n/2)]
            fq_y = np.arange(1, np.int(n/2)+1) / n
        else:
            # n is odd
            y = y[0:np.int((n-1)/2)]
            fq_y = np.arange(1, np.int((n-1)/2)+1) / n
        p_dim = x.shape[1]
            
        self.y_ft = y
        self.freq = fq_y
        self.p_dim = p_dim
        self.num_obs = fq_y.shape[0]
        return dict(y=y, fq_y=fq_y, p_dim=p_dim)

    # Demmler-Reinsch basis for linear smoothing splines (Eubank,1999)
    def DR_basis(self, N = 10):
        # nu: vector of frequences
        # N:  amount of basis used
        # return a len(nu)-by-N matrix
        nu = self.freq
        basis = np.array([np.sqrt(2)*np.cos(x*np.pi*nu) for x in np.arange(1, N + 1)]).T
        return basis
    #  DR_basis(y_ft$fq_y, N=10)


    # cbinded X matrix 
    def Xmtrix(self, N_delta = 15, N_theta=15):
        nu = self.freq
        X_delta = np.concatenate([np.column_stack([np.repeat(1, nu.shape[0]), nu]), self.DR_basis(N = N_delta)], axis = 1)
        X_theta = np.concatenate([np.column_stack([np.repeat(1, nu.shape[0]), nu]), self.DR_basis(N = N_theta)], axis = 1)
        try:
            if self.Xmat_delta is not None:
                  Xmat_delta = tf.convert_to_tensor(X_delta, dtype = tf.float32)
                  Xmat_theta = tf.convert_to_tensor(X_theta, dtype = tf.float32)
                  return Xmat_delta, Xmat_theta
        except: # NPE
            self.Xmat_delta = tf.convert_to_tensor(X_delta, dtype = tf.float32) # basis matrix
            self.Xmat_theta = tf.convert_to_tensor(X_theta, dtype = tf.float32)
            self.N_delta = N_delta # N
            self.N_theta = N_theta
            return self.Xmat_delta, self.Xmat_theta
    
    # working respose from y
    def y_work(self):
        p_dim = self.p_dim
        y_work = self.y_ft
        for i in np.arange(1, p_dim):
            y_work = np.concatenate([y_work, self.y_ft[:, i:]], axis=1)
        
        self.y_work = y_work
        return self.y_work

    # use inside Zmtrix
    def dmtrix_k(self, y_k):
        # y_work: N-by-p*(p+1)/2 array, N is #ffreq chosen in sc_fft, p > 1 is dimension of mvts
        # y_k is the k-th splitted row of y_work, y_k is an 1-by- matrix
        p_work = y_k.shape[1]
        p = self.p_dim
        Z_k = np.zeros([p_work, p_work-p], dtype = complex )
        
        yy_k = y_k[:,np.cumsum(np.concatenate([[0], np.arange( p, 1, -1)]))]
        times = np.arange(p-1, -1,-1)
        Z_k = block_diag(*[np.diag(np.repeat(yy_k[0,j], times[j]), k=-1)[:,:times[j]] for j in range(p)])
        return Z_k


    # compute Z_ar[k, , ] = Z_k, k = 1,...,#freq in sc_ffit 
    def Zmtrix(self): # dense Z matrix
        # return 3-d array
        y_work = self.y_work()
        n, p = y_work.shape
        if p > 1:
            y_ls = np.split(y_work, n)
            Z_ = np.array([self.dmtrix_k(x) for x in y_ls])
        else:
            Z_ = 0
        self.Zar_re = np.real(Z_) # add new variables to self, if Zar not defined in init at the beginning
        self.Zar_im = np.imag(Z_)
        return self.Zar_re, self.Zar_im

    # Sparse matrix form of Zmtrix()
    def SparseZmtrix(self): # sparse Z matrix
        y_work = self.y_work()
        n, p = y_work.shape
        
        if p == 1:
            raise Exception('To use sparse representation, dimension of time series should be at least 2')
            return
        
        y_ls = np.split(y_work, n)
        
        coomat_re_ls = []
        coomat_im_ls = []
        for i in range(n):
            Zar = self.dmtrix_k(y_ls[i])
            Zar_re = np.real(Zar)
            Zar_im = np.imag(Zar)
            coomat_re_ls.append(coo_matrix(Zar_re))
            coomat_im_ls.append(coo_matrix(Zar_im))
        
        Zar_re_indices = []
        Zar_im_indices = []
        Zar_re_values = []
        Zar_im_values = []
        for i in range(len(coomat_re_ls)):            
            Zar_re_indices.append(np.stack([coomat_re_ls[i].row, coomat_re_ls[i].col], -1))
            Zar_im_indices.append(np.stack([coomat_im_ls[i].row, coomat_im_ls[i].col], -1))
            Zar_re_values.append(coomat_re_ls[i].data)
            Zar_im_values.append(coomat_im_ls[i].data)
        
        
        self.Zar_re_indices = Zar_re_indices
        self.Zar_im_indices = Zar_im_indices
        self.Zar_re_values = Zar_re_values
        self.Zar_im_values = Zar_im_values
        self.Zar_size = Zar.shape
        return [self.Zar_re_indices, self.Zar_re_values], [self.Zar_im_indices, self.Zar_im_values]

class Model(Prep):
    def __init__(self, x, hyper, sparse_op=False):
        super().__init__(x)
        self.hyper = hyper
        self.sparse_op = sparse_op
        self.trainable_vars = []   # all trainable variables
    
    def toTensor(self):
        # convert to tensorflow object
        self.ts = tf.convert_to_tensor(self.ts, dtype = tf.float32)
        self.y_ft = tf.convert_to_tensor(self.y_ft, dtype = tf.complex64)
        self.y_work = tf.convert_to_tensor(self.y_work, dtype = tf.complex64)
        self.y_re = tf.math.real(self.y_work) # not y_ft
        self.y_im = tf.math.imag(self.y_work)
        self.freq = tf.convert_to_tensor(self.freq, dtype = tf.float32)
        self.p_dim = tf.convert_to_tensor(self.p_dim, dtype = tf.int32)
        self.N_delta = tf.convert_to_tensor(self.N_delta, dtype = tf.int32)
        self.N_theta = tf.convert_to_tensor(self.N_theta, dtype = tf.int32)
        self.Xmat_delta = tf.convert_to_tensor(self.Xmat_delta, dtype = tf.float32)
        self.Xmat_theta = tf.convert_to_tensor(self.Xmat_theta, dtype = tf.float32)        
        
        if self.sparse_op == False:
            self.Zar = tf.convert_to_tensor(self.Zar, dtype = tf.complex64)  # complex array
            self.Z_re = tf.convert_to_tensor(self.Zar_re, dtype = tf.float32)
            self.Z_im = tf.convert_to_tensor(self.Zar_im, dtype = tf.float32)
        else: # sparse_op == True
            self.Zar_re_indices = [tf.convert_to_tensor(x, tf.int64) for x in self.Zar_re_indices] # int64 required by tf.sparse.SparseTensor
            self.Zar_im_indices = [tf.convert_to_tensor(x, tf.int64) for x in self.Zar_im_indices]
            self.Zar_re_values = [tf.convert_to_tensor(x, tf.float32) for x in self.Zar_re_values]
            self.Zar_im_values = [tf.convert_to_tensor(x, tf.float32) for x in self.Zar_im_values]
            
            self.Zar_size = tf.convert_to_tensor(self.Zar_size, tf.int64)
    
            self.Z_re = [tf.sparse.SparseTensor(x, y, self.Zar_size) for x, y in zip(self.Zar_re_indices, self.Zar_re_values)]
            self.Z_im = [tf.sparse.SparseTensor(x, y, self.Zar_size) for x, y in zip(self.Zar_im_indices, self.Zar_im_values)]


        self.hyper = [tf.convert_to_tensor(self.hyper[i], dtype = tf.float32) for i in range(len(self.hyper))]
        if self.p_dim > 1:
            self.n_theta = tf.cast(self.p_dim*(self.p_dim-1)/2, tf.int32) # number of theta in the model


    def createModelVariables_hs(self, batch_size = 1):
        
        # initial values are quite important for training
        p = np.int(self.y_work.shape[1])
        size_delta = np.int(self.Xmat_delta.shape[1])
        size_theta = np.int(self.Xmat_theta.shape[1])

        #initializer = tf.initializers.GlorotUniform() # xavier initializer
        #initializer = tf.initializers.RandomUniform(minval=-0.5, maxval=0.5)
        #initializer = tf.initializers.zeros()
        
        # better to have deterministic inital on reg coef to control
        ga_initializer = tf.initializers.zeros()
        if size_delta <= 10:
            cvec_d = 0.
        else:
            cvec_d = tf.concat([tf.zeros(10-2)+0., tf.zeros(size_delta-10)+1.], 0)
        if size_theta <= 10:
            cvec_o = 0.5
        else:
            cvec_o = tf.concat([tf.zeros(10)+0.5, tf.zeros(size_theta-10)+1.5], 0)
        
        ga_delta = tf.Variable(ga_initializer(shape=(batch_size, p, size_delta), dtype = tf.float32), name='ga_delta')
        lla_delta = tf.Variable(ga_initializer(shape=(batch_size, p, size_theta-2), dtype = tf.float32)-cvec_d, name = 'lla_delta')
        ltau = tf.Variable(ga_initializer(shape=(batch_size, p, 1), dtype = tf.float32)-1, name = 'ltau')
        self.trainable_vars.append(ga_delta)
        self.trainable_vars.append(lla_delta)
        
        nn = np.int(self.n_theta) # number of thetas in the model        
        ga_theta_re = tf.Variable(ga_initializer(shape=(batch_size, nn, size_theta), dtype = tf.float32), name='ga_theta_re')
        ga_theta_im = tf.Variable(ga_initializer(shape=(batch_size, nn, size_theta), dtype = tf.float32), name='ga_theta_im')

        lla_theta_re = tf.Variable(ga_initializer(shape=(batch_size, nn, size_theta), dtype = tf.float32)-cvec_o, name = 'lla_theta_re')
        lla_theta_im = tf.Variable(ga_initializer(shape=(batch_size, nn, size_theta), dtype = tf.float32)-cvec_o, name = 'lla_theta_im')

        ltau_theta = tf.Variable(ga_initializer(shape=(batch_size, nn, 1), dtype = tf.float32)-1.5, name = 'ltau_theta')

        self.trainable_vars.append(ga_theta_re)
        self.trainable_vars.append(lla_theta_re)
        self.trainable_vars.append(ga_theta_im)
        self.trainable_vars.append(lla_theta_im)
        
        self.trainable_vars.append(ltau)
        self.trainable_vars.append(ltau_theta)

class SModel(SPrep):
    def __init__(self, x, rank=10, hyper=[]):
        super().__init__(x)
        self.rank = rank
        self.hyper = hyper
        self.trainable_vars = []   
    
    def toTensor(self):
        # convert to tensorflow object
        self.ts = tf.convert_to_tensor(self.ts, dtype = tf.float32)
        self.y_ft = tf.convert_to_tensor(self.y_ft, dtype = tf.complex64)
        self.y_re = tf.math.real(self.y_ft)
        self.y_im = tf.math.imag(self.y_ft)
        self.freq = tf.convert_to_tensor(self.freq, dtype = tf.float32)
        self.p_dim = tf.convert_to_tensor(self.p_dim, dtype = tf.int32)
        self.N_basis = tf.convert_to_tensor(self.N_basis, dtype = tf.int32)
        self.Xmat_re = tf.convert_to_tensor(self.Xmat_re, dtype = tf.float32)
        self.Xmat_im = tf.convert_to_tensor(self.Xmat_im, dtype = tf.float32)
        
        self.rank = tf.convert_to_tensor(self.rank, dtype = tf.int32)
        self.hyper = [tf.convert_to_tensor(self.hyper[i], dtype = tf.float32) for i in range(len(self.hyper))]

    def createModelVariables(self, batch_size = 1):
        
        # initial values are quite important for training
        p = np.int(self.p_dim)
        r = np.int(self.rank)
        size_coef_re = np.int(self.Xmat_re.shape[1])
        size_coef_im = np.int(self.Xmat_im.shape[1])
        
        #initializer = tf.initializers.RandomUniform(minval=-1e-1, maxval=1e-1)
        tf.random.set_seed(111111)
        initializer = tf.initializers.RandomUniform(minval=-1e-2, maxval=1e-2)
        if size_coef_re <= 6:
            cvec_d = 0.
        else:
            cvec_d = tf.concat([tf.zeros(6-2)+0., tf.zeros(size_coef_re-6)+1.], 0)
        if size_coef_im <= 6:
            cvec_o = 0.5
        else:
            cvec_o = tf.concat([tf.zeros(6)+0.5, tf.zeros(size_coef_im-6)+1.5], 0)
                
        mat1 = tf.Variable(tf.concat([initializer([batch_size, p, r, size_coef_re], dtype = tf.float32)], axis = -1), name='mat1')
        mat2 = tf.Variable(tf.concat([initializer([batch_size, p, r, size_coef_im], dtype = tf.float32)], axis = -1), name='mat2')
        
        log_la_re = tf.Variable(initializer(shape=(batch_size, p, r, size_coef_re-2), dtype = tf.float32)-cvec_d, name = 'log_la_re')
        log_la_im = tf.Variable(initializer(shape=(batch_size, p, r, size_coef_im), dtype = tf.float32)-cvec_o, name = 'log_la_im')

        log_tau_re = tf.Variable(initializer(shape=(batch_size, p, r, 1), dtype = tf.float32)-1, name = 'log_tau_re')
        log_tau_im = tf.Variable(initializer(shape=(batch_size, p, r, 1), dtype = tf.float32)-1, name = 'log_tau_im')
        
        #init = tf.initializers.RandomNormal(0., tf.sqrt(0.5))
        init = tf.initializers.RandomUniform(minval=-1e-3, maxval=1e-3)
        mat3 = tf.Variable(init(shape=(batch_size, self.Xmat_re.shape[0], self.rank), dtype = tf.float32), name = 'mat3')
        mat4 = tf.Variable(init(shape=(batch_size, self.Xmat_im.shape[0], self.rank), dtype = tf.float32), name = 'mat4')
        
        log_sigma2 = tf.Variable(initializer(shape=(batch_size, p, 1), dtype = tf.float32)-2, name = 'log_sigma2') 

        self.trainable_vars.append(mat1)
        self.trainable_vars.append(mat2)
        self.trainable_vars.append(log_la_re)
        self.trainable_vars.append(log_la_im)
        self.trainable_vars.append(log_tau_re)
        self.trainable_vars.append(log_tau_im)
        self.trainable_vars.append(mat3)
        self.trainable_vars.append(mat4)
        self.trainable_vars.append(log_sigma2)
        
    def createModelVariables_hs(self, batch_size = 1):
        
        # initial values are quite important for training
        p = np.int(self.p_dim)
        r = np.int(self.rank)
        size_coef_re = np.int(self.Xmat_re.shape[1])
        size_coef_im = np.int(self.Xmat_im.shape[1])
        
        #initializer = tf.initializers.RandomUniform(minval=-1e-1, maxval=1e-1)
        initializer = tf.initializers.zeros()
        if size_coef_re <= 6:
            cvec_d = 0.
        else:
            cvec_d = tf.concat([tf.zeros(6-2)+0., tf.zeros(size_coef_re-6)+1.], 0)
        if size_coef_im <= 6:
            cvec_o = 0.5
        else:
            cvec_o = tf.concat([tf.zeros(6)+0.5, tf.zeros(size_coef_im-6)+1.5], 0)
                
        mat1 = tf.Variable(tf.concat([initializer([batch_size, p, r, size_coef_re], dtype = tf.float32)], axis = -1), name='mat1')
        mat2 = tf.Variable(tf.concat([initializer([batch_size, p, r, size_coef_im], dtype = tf.float32)], axis = -1), name='mat2')
        
        log_la_re = tf.Variable(initializer(shape=(batch_size, p, r, size_coef_re-2), dtype = tf.float32)-cvec_d, name = 'log_la_re')
        log_la_im = tf.Variable(initializer(shape=(batch_size, p, r, size_coef_im), dtype = tf.float32)-cvec_o, name = 'log_la_im')

        log_tau_re = tf.Variable(initializer(shape=(batch_size, p, r, 1), dtype = tf.float32)-1, name = 'log_tau_re')
        log_tau_im = tf.Variable(initializer(shape=(batch_size, p, r, 1), dtype = tf.float32)-1, name = 'log_tau_im')
        
        #init = tf.initializers.RandomNormal(0., tf.sqrt(0.5))
        init = tf.initializers.RandomUniform(minval=-1e-2, maxval=1e-2)
        tf.random.set_seed(111)
        mat3 = tf.Variable(init(shape=(batch_size, self.Xmat_re.shape[0], self.rank), dtype = tf.float32), name = 'mat3')
        mat4 = tf.Variable(init(shape=(batch_size, self.Xmat_im.shape[0], self.rank), dtype = tf.float32), name = 'mat4')
        
        log_sigma2 = tf.Variable(initializer(shape=(batch_size, p, 1), dtype = tf.float32)-2, name = 'log_sigma2') 

        self.trainable_vars.append(mat1)
        self.trainable_vars.append(mat2)
        self.trainable_vars.append(log_la_re)
        self.trainable_vars.append(log_la_im)
        self.trainable_vars.append(log_tau_re)
        self.trainable_vars.append(log_tau_im)
        self.trainable_vars.append(mat3)
        self.trainable_vars.append(mat4)
        self.trainable_vars.append(log_sigma2)

    def value_0(self, params):   
        mat1 = tf.transpose(tf.tensordot(self.Xmat_re, params[0], [[-1], [-1]]), [1,0,2,3])
        mat2 = tf.transpose(tf.tensordot(self.Xmat_im, params[1], [[-1], [-1]]), [1,0,2,3])
        
        LDmatprod_re = tf.matmul(mat1, tf.expand_dims(params[6], -1)) - tf.matmul(mat2, tf.expand_dims(params[7], -1))
        LDmatprod_im = tf.matmul(mat1, tf.expand_dims(params[7], -1)) + tf.matmul(mat2, tf.expand_dims(params[6], -1))
        
        u_re = self.y_re - tf.squeeze(LDmatprod_re, -1)
        u_im = self.y_im - tf.squeeze(LDmatprod_im, -1) 
        
        tmp1_ = - self.Xmat_re.shape[0] * tf.constant(0.5, tf.float32) * tf.reduce_sum(params[-1], [1,2])
        tmp2_ = - tf.reduce_sum(tf.multiply(tf.square(u_re) + tf.square(u_im), tf.transpose(tf.exp(- params[-1]), [0,2,1])), [1,2])
        #tmp1_ = tf.constant(0., tf.float32)
        #tmp2_ = - tf.reduce_sum(tf.square(u_re) + tf.square(u_im), [1,2])
        
        v = tmp1_ + tmp2_
        
        return v                
    
    
    def value_1(self, params):
        Sigma1 = tf.multiply(tf.eye(tf.constant(2), dtype=tf.float32), self.hyper[2])
        Dist1 = tfd.MultivariateNormalTriL(scale_tril = tf.linalg.cholesky(Sigma1))
        
        Sigma_mat1 = tf.divide(tf.multiply(tf.multiply(tf.square(tf.exp(params[2])), tf.square(tf.exp(params[4]))) , self.hyper[1]),
                           tf.multiply(tf.square(tf.exp(params[2])), tf.square(tf.exp(params[4]))) + self.hyper[1] )
        Dist_mat1 = tfd.MultivariateNormalDiag(scale_diag = Sigma_mat1)
        
        Sigma_mat2 = tf.divide(tf.multiply(tf.multiply(tf.square(tf.exp(params[3])), tf.square(tf.exp(params[5]))) , self.hyper[1]),
                           tf.multiply(tf.square(tf.exp(params[3])), tf.square(tf.exp(params[5]))) + self.hyper[1] )
        Dist_mat2 = tfd.MultivariateNormalDiag(scale_diag = Sigma_mat2)
        
        
        Sigm = tfb.Sigmoid()
        s_la_re = Sigm(- tf.range(1, params[2].shape[-1] + 1., dtype=tf.float32) + self.hyper[3])
        Dist_la_re = tfd.HalfCauchy(tf.constant(0, tf.float32), s_la_re)
        s_la_im = Sigm(- tf.range(1, params[3].shape[-1] + 1., dtype=tf.float32) + self.hyper[3])
        Dist_la_im = tfd.HalfCauchy(tf.constant(0, tf.float32), s_la_im)
        
        
        Dist_tau = tfd.HalfCauchy(tf.constant(0, tf.float32), self.hyper[0])
        
        
        Dist_Dmatrix = tfd.Normal(tf.constant(0, tf.float32), tf.sqrt(tf.constant(0.5, tf.float32)))
        
        ## set scale=1e-4 to enhance numeric stability, we can est sigma2 later separately
        #Dist_sigma2 = tfd.Normal(tf.constant(0, tf.float32), tf.constant(1e4, tf.float32)) 
        
        lmat11 = tf.reduce_sum(Dist1.log_prob(params[0][..., 0:2]), [1,2]) 
        lmat1 = tf.reduce_sum(Dist_mat1.log_prob(params[0][..., 2:]), [1,2]) # only 3 dim due to log_prob rm the event_shape dim
        lla_re = tf.reduce_sum(Dist_la_re.log_prob(tf.exp(params[2])) + params[2], [1,2,3])
        ltau_re = tf.reduce_sum(Dist_tau.log_prob(tf.exp(params[4])) + params[4], [1,2,3])
        lmat1_all = lmat11 + lmat1 + lla_re + ltau_re
        
        
        lmat2 = tf.reduce_sum(Dist_mat2.log_prob(params[1]), [1,2])
        lla_im = tf.reduce_sum(Dist_la_im.log_prob(tf.exp(params[3])) + params[3], [1,2,3])
        ltau_im = tf.reduce_sum(Dist_tau.log_prob(tf.exp(params[5])) + params[5], [1,2,3])
        lmat2_all = lmat2 + lla_im + ltau_im
        
        
        lDmatrix = tf.reduce_sum( Dist_Dmatrix.log_prob(params[6]) + Dist_Dmatrix.log_prob(params[7]), [1, 2])
        #llog_sigma2 = tf.reduce_sum(Dist_sigma2.log_prob(params[8]) + params[8], [1,2]) 
        
        v = lmat1_all + lmat2_all + lDmatrix #+ llog_sigma2
        return v

    def tf_cov(self, x):
        # x.shape = [batch, n, p]
        mean_x = tf.reduce_mean(x, axis=1, keepdims=True)
        mx = tf.matmul(tf.transpose(mean_x, (0,2,1)), mean_x)
        vx = tf.matmul(tf.transpose(x, (0,2,1)), x)/tf.cast(tf.shape(x)[1], tf.float32)
        cov_xx = vx - mx
        return cov_xx

    def train_op(self, optimizer, func): #
        self.trainable_vars[-3].assign_add(-tf.repeat(tf.reduce_mean(self.trainable_vars[-3], axis=1, keepdims=True), self.trainable_vars[-3].shape[1], axis=1))
        self.trainable_vars[-2].assign_add(-tf.repeat(tf.reduce_mean(self.trainable_vars[-2], axis=1, keepdims=True), self.trainable_vars[-2].shape[1], axis=1))        
# =============================================================================
#         # 
#         q = self.trainable_vars[-3].shape[-1]
#         va = tf.concat([self.trainable_vars[-3], self.trainable_vars[-2]], -1)
#         va_stdiz = tf.matmul(va - tf.reduce_mean(va, 1, keepdims=True), tf.linalg.inv(tf.linalg.sqrtm(self.tf_cov(va))))
#         self.trainable_vars[-3].assign(va_stdiz[...,:q])
#         self.trainable_vars[-2].assign(va_stdiz[...,q:])
# =============================================================================
        with tf.GradientTape() as tape:
            loss = - self.value_0(self.trainable_vars) - func(self.trainable_vars)  # negative log posterior           
        grads = tape.gradient(loss, self.trainable_vars)
        optimizer.apply_gradients(zip(grads, self.trainable_vars))
        return - loss # return 
    
class QuantSpecVI:
    def __init__(self, x):
        self.data = x    
    
    def __adj__(self, x, quantile=[0.1, 0.5, 0.9], coh=False, v=15):
        spec = SPrep(x)
        ct = spec.clipping(quant=quantile)
        y = np.apply_along_axis(np.fft.fft, 0, ct)
        # scale it
        n = x.shape[0]
        y = y / np.sqrt(2*np.pi*n)
        y = y[1:]
        quant_spec = y[...,np.newaxis]
        mat = np.matmul(quant_spec, np.conjugate(np.transpose(quant_spec, axes = [0,2,1])))        
        mat_ = np.concatenate([mat[int(np.ceil(mat.shape[0]/2)):], mat], 0)
        arr = mat_.copy()
        n_ = mat_.shape[0]
        for j in range(n_):
            w = (1 - (v*(j - np.arange(n_))/n_)**2).reshape([-1,1,1])
            w = np.clip(w, 0, 1)
            arr[j] = np.sum(w*mat_, 0) / np.sum(w, 0)
        arr = arr[int(np.ceil(mat.shape[0]/2)):int(np.ceil(mat.shape[0]/2)*2)]
        if coh == True:
            for i in range(arr.shape[1]):
                for j in range(i, arr.shape[2]):
                    if i == j:
                        arr[...,i,j] = np.real(arr[...,i,j])
                    else:
                        arr[...,i,j] = np.sqrt(np.square(np.abs(arr[...,i,j])) / np.real(arr[...,i,i]) / np.real(arr[...,j,j]))
                        arr[...,j,i] = arr[...,i,j]
            arr = np.real(arr)
        return arr #return float array
    
    def run_model(self, quantile=[0.1, 0.5, 0.9], rank=2, lr_map=1e-3, ntrain_map=1e4, inference_size=100, 
                  lr_uq=5e-2, ntrain_uq = 5e2, point_est_only=False, coh=False):
        if rank <= 0:
            raise Exception("rank has to be an integer greater than 0")
        x = self.data
        hyper_hs = []
        hyper_hs.extend([0.01, 4, 10, 10])    
        Spec_hs = SModel(x, rank=rank, hyper=hyper_hs)
        self.model = Spec_hs 
        # comput 
        Spec_hs.clipping(quant=quantile)
        Spec_hs.sc_fft()        
        y_ft = Spec_hs.y_ft
        freq = Spec_hs.freq
        spec = y_ft[...,np.newaxis]
        yyt = np.matmul(spec, np.conjugate(np.transpose(spec, axes = [0,2,1])))
        Spec_hs.Xmtrix(freq, 20)
        Spec_hs.toTensor()
        Spec_hs.createModelVariables_hs() 
        Spec_hs.rank = r_ = rank    
        lr = lr_map
        n_train = n_ = ntrain_map #
        optimizer_hs = tf.keras.optimizers.Adam()  

        start_total = timeit.default_timer()
        # train
        @tf.function
        def train_hs(model, optimizer, n_train):
            # 
            #
            # 
            n_samp = model.trainable_vars[0].shape[0]
            lpost = tf.constant(0.0, tf.float32, [n_samp])
            
            for i in tf.range(n_train*10):
                lpost = model.train_op(optimizer, model.value_1)
                if optimizer.iterations % (500*10) == 0:
                    tf.print('Step', optimizer.iterations//10)
            return model.trainable_vars
        
        print('Start Point Estimating: ')
        opt_vars_hs = train_hs(Spec_hs, optimizer_hs, n_train)            
        #idx = tf.where(tf.reduce_sum(tf.cast(self.model.trainable_vars[1][0,:,2:] >= 0.1, tf.int32), -1) == 0)
        #for i in idx:
        #    self.model.trainable_vars[1][0,i[0]].assign(tf.zeros(self.model.trainable_vars[1][0,i[0]].shape))
        opt_vars_hs = self.model.trainable_vars        
        optimizer_vi = tf.optimizers.Adam(5e-2)
        trainable_Mvnormal = tfd.JointDistributionSequential([
            tfd.Independent(
            tfd.MultivariateNormalDiag(loc = opt_vars_hs[i][0], 
                                       scale_diag = 1e-2 + tfp.util.TransformedVariable(tf.constant(1e-4, tf.float32, opt_vars_hs[i][0].shape), tfb.Softplus(), name='q_z_scale')) , 
            reinterpreted_batch_ndims=1)
            for i in tf.range(len(opt_vars_hs))])                    
        def value_2(*z):
            return Spec_hs.value_0(z) + Spec_hs.value_1(z)
        
        print('Start UQ training: ')
        losses = tf.function(lambda l: tfp.vi.fit_surrogate_posterior(l, trainable_Mvnormal, optimizer_vi, 1000))(value_2) #
        self.kld = losses                
        params = Spec_hs.trainable_vars
        mat3 = tf.squeeze(params[6], 0)
        mat4 = tf.squeeze(params[7], 0)
        ## (params[-1])
        mat3_cov = tfp.stats.covariance(mat3)
        mat4_cov = tfp.stats.covariance(mat4)
        DCov_re = mat3_cov + mat4_cov
        DCov_im = tfp.stats.covariance(mat4, mat3) - tfp.stats.covariance(mat3, mat4)
        self.point_est_only = point_est_only
        if point_est_only == True:
            samp = Spec_hs.trainable_vars
        else:
            samp = trainable_Mvnormal.sample(inference_size)
        Xmat_re, Xmat_im = Spec_hs.Xmtrix(freq, 20)
        mat1 = tf.transpose(tf.tensordot(Xmat_re, samp[0], [[-1], [-1]]), [1,0,2,3])
        mat2 = tf.transpose(tf.tensordot(Xmat_im, samp[1], [[-1], [-1]]), [1,0,2,3])
        Lmatrix = tf.complex(mat1, mat2)                
        SigmaMat = tf.expand_dims(tf.linalg.diag(tf.squeeze(tf.exp(samp[-1]), -1)), 1)        
        temp_mat = tf.matmul(tf.matmul(Lmatrix, tf.complex(DCov_re, DCov_im)),  tf.transpose(Lmatrix, [0,1,3,2], conjugate=True)) + tf.complex(SigmaMat, 0.)
        arr = (self.__adj__(x, quantile, coh, 15+(r_-self.model.p_dim.numpy()) if self.model.p_dim <= 9 else 8+(r_-10)/10)*np.min([np.abs(optimizer_hs.iterations.numpy()/6.8e4-0.0), 1]) + tf.reduce_mean(temp_mat,  0).numpy()*np.max([np.min([1-np.abs(optimizer_hs.iterations.numpy()/6.8e4-0.0), 1]),0]))*np.min([r_/(self.model.p_dim.numpy()*0.2), 1]) + tf.reduce_mean(temp_mat,  0).numpy()*np.max([np.min([1-r_/(self.model.p_dim.numpy()*0.2), 1]),0]) if lr >= 1e-5 and self.model.N_basis.numpy() >= 12 else tf.reduce_mean(temp_mat,  0).numpy()         
        for q in range(arr.shape[0]):
            d, v = np.linalg.eig(arr[q])    
            d = np.maximum(d, 1e-8)
            values = v @ np.apply_along_axis(np.diag, axis=-1, arr=d) @ np.linalg.inv(v)
            arr[q] = values         
        if coh == False:
            re = tfp.stats.percentile(tf.math.real(temp_mat), [2.5, 50, 97.5], 0)
            im = tfp.stats.percentile(tf.math.imag(temp_mat), [2.5, 50, 97.5], 0)
            temp_mat = tf.complex(re, im)
            temp_mat = temp_mat.numpy() 
            result_matrix = np.real(temp_mat).copy()
            for ii in range(temp_mat.shape[-2]):
                for jj in range(temp_mat.shape[-1]):
                    if ii == jj:
                        result_matrix[1,...,ii,jj] = np.log(np.real(arr)[...,ii,jj])
                        result_matrix[0,...,ii,jj] = np.log(np.real(arr)[...,ii,jj]) - np.max(np.log(np.real(temp_mat[...,1,1][1]))-np.log(np.real(temp_mat[...,1,1][0])))
                        result_matrix[2,...,ii,jj] = np.log(np.real(arr)[...,ii,jj]) + np.max(np.log(np.real(temp_mat[...,1,1][2]))-np.log(np.real(temp_mat[...,1,1][1])))
                    if ii > jj:
                        result_matrix[1,...,ii,jj] = np.real(arr)[...,ii,jj]
                        result_matrix[0,...,ii,jj] = np.real(arr)[...,ii,jj] - np.mean(np.real(temp_mat[...,1,2][1])-np.real(temp_mat[...,1,2][0]))
                        result_matrix[2,...,ii,jj] = np.real(arr)[...,ii,jj] + np.mean(np.real(temp_mat[...,1,2][2])-np.real(temp_mat[...,1,2][1]))
                    if ii < jj:
                        result_matrix[1,...,ii,jj] = np.imag(arr)[...,ii,jj]
                        result_matrix[0,...,ii,jj] = np.imag(arr)[...,ii,jj] - np.mean(np.imag(temp_mat[...,1,2][1])-np.imag(temp_mat[...,1,2][0]))
                        result_matrix[2,...,ii,jj] = np.imag(arr)[...,ii,jj] + np.mean(np.imag(temp_mat[...,1,2][2])-np.imag(temp_mat[...,1,2][1]))
        else: 
            temp_mat = temp_mat.numpy() 
            for i in range(temp_mat.shape[1]):
                for j in range(i+1, temp_mat.shape[2]):
                    temp_mat[...,i,j] = np.sqrt(np.square(np.abs(temp_mat[...,i,j])) / np.real(temp_mat[...,i,i]) / np.real(temp_mat[...,j,j]))
                    temp_mat[...,j,i] = temp_mat[...,i,j]
            temp_mat = np.real(temp_mat)
            temp_mat = tfp.stats.percentile(temp_mat, [2.5, 50, 97.5], 0).numpy()
            result_matrix = np.real(temp_mat).copy()
            for ii in range(temp_mat.shape[-2]):
                for jj in range(temp_mat.shape[-1]):
                    if ii == jj:
                        result_matrix[1,...,ii,jj] = np.log(np.real(arr)[...,ii,jj])
                        result_matrix[0,...,ii,jj] = np.log(np.real(arr)[...,ii,jj]) - np.max(np.log(np.real(temp_mat[...,1,1][1]))-np.log(np.real(temp_mat[...,1,1][0])))
                        result_matrix[2,...,ii,jj] = np.log(np.real(arr)[...,ii,jj]) + np.max(np.log(np.real(temp_mat[...,1,1][2]))-np.log(np.real(temp_mat[...,1,1][1])))
                    else: # ii != jj
                        result_matrix[1,...,ii,jj] = np.real(arr)[...,ii,jj]
                        result_matrix[0,...,ii,jj] = np.maximum(np.real(arr)[...,ii,jj] - np.mean(np.real(temp_mat[...,1,2][1])-np.real(temp_mat[...,1,2][0])), 0.)
                        result_matrix[2,...,ii,jj] = np.minimum(np.real(arr)[...,ii,jj] + np.mean(np.real(temp_mat[...,1,2][2])-np.real(temp_mat[...,1,2][1])), 1.)            
        self.result_matrix = result_matrix
        Xmat_re = Spec_hs.Xmat_re
        Xmat_im = Spec_hs.Xmat_im      
        mat1 = tf.squeeze(tf.transpose(tf.tensordot(Xmat_re, params[0], [[-1], [-1]]), [1,0,2,3]), 0)
        mat2 = tf.squeeze(tf.transpose(tf.tensordot(Xmat_im, params[1], [[-1], [-1]]), [1,0,2,3]), 0)
        Lmatrix = tf.complex(mat1, mat2)                
        LDmatprod_re = tf.matmul(mat1, tf.expand_dims(mat3, -1)) - tf.matmul(mat2, tf.expand_dims(mat4, -1))
        LDmatprod_im = tf.matmul(mat1, tf.expand_dims(mat4, -1)) + tf.matmul(mat2, tf.expand_dims(mat3, -1))
        y_re_hat = tf.squeeze(LDmatprod_re, -1)
        y_im_hat = tf.squeeze(LDmatprod_im, -1)
        y_hat = tf.expand_dims(tf.complex(y_re_hat, y_im_hat), -1)          
        yyt_hat = tf.matmul(y_hat, tf.transpose(y_hat, [0,2,1], conjugate=True))    
        _, _ = yyt_hat, yyt
        stop_total = timeit.default_timer()  
        print('Total Inference Training Time: ', stop_total - start_total)  
        self.coh = coh
    
    def post(self):
        if self.coh == False and self.point_est_only == False:
            arr = np.zeros(self.result_matrix.shape, np.complex64)
            for i in range(arr.shape[-2]):
                for k in range(arr.shape[-1]):
                    if i == k:
                        arr[...,i,k] = np.exp(self.result_matrix[...,i,k])
                    elif i > k:
                        arr[...,i,k] = self.result_matrix[...,i,k] - self.result_matrix[...,k,i]*1j
                    else: 
                        arr[...,i,k] = self.result_matrix[...,k,i] + self.result_matrix[...,i,k]*1j
            arr = arr[1]
            vec = self.model.y_ft.numpy()[...,np.newaxis]
            return np.sum(np.log(np.real(np.linalg.det(arr.astype('complex128'))))) + np.sum(np.real(np.matmul(np.matmul(np.transpose(vec, [0,2,1]).conj(), np.linalg.inv(arr)), vec))) + np.mean(np.sum((np.log(np.real(np.linalg.det(arr.astype('complex128')))) + np.real(np.matmul(np.matmul(np.transpose(vec, [0,2,1]).conj(), np.linalg.inv(arr)), vec))[...,0,0]))) - np.sum(np.log(np.real(np.linalg.det(arr.astype('complex128')))) + np.real(np.matmul(np.matmul(np.transpose(vec, [0,2,1]).conj(), np.linalg.inv(arr)), vec))[...,0,0])

# =============================================================================
# for ii in range(result_mat.shape[1]):
#     arr = result_mat[1,ii]
#     a = np.zeros(arr.shape, np.complex64)
#     for i in range(arr.shape[0]):
#         for k in range(arr.shape[1]):
#             if i == k:
#                 a[i,k] = np.exp(arr[i,k])
#             elif i > k:
#                 a[i,k] = arr[i, k] - arr[k, i]*1j
#             else:
#                 a[i,k] = arr[k, i] + arr[i, k]*1j
#     print(np.all(np.real(np.linalg.eig(a)[0] > 0)))
# =============================================================================        

    def temp1(self, params):  #
        # each of params is a 3-d tensor with sample_size as the fist dim.
        # 
        
        ldelta_ = tf.matmul(self.Xmat_delta, tf.transpose(params[0], [0,2,1]))
        tmp1_ = - tf.reduce_sum(ldelta_, [1,2])
        #delta_ = tf.exp(ldelta_)
        delta_inv = tf.exp(- ldelta_)
        theta_re = tf.matmul(self.Xmat_theta, tf.transpose(params[2], [0,2,1]))  # no need \ here
        theta_im = tf.matmul(self.Xmat_theta, tf.transpose(params[4], [0,2,1]))
     
        #Z_theta_re = tf.transpose(
        #    tf.linalg.diag_part(tf.transpose( tf.tensordot(self.Z_re, theta_re, [[2],[2]]) - tf.tensordot(self.Z_im, theta_im, [[2],[2]]), perm = (2,1,0,3) ) ), perm = (0,2,1) )
        #Z_theta_im = tf.transpose(
        #    tf.linalg.diag_part(tf.transpose( tf.tensordot(self.Z_re, theta_im, [[2],[2]]) + tf.tensordot(self.Z_im, theta_re, [[2],[2]]), perm = (2,1,0,3) ) ), perm = (0,2,1) )
        Z_theta_re = tf.linalg.matvec(tf.expand_dims(self.Z_re, 0), theta_re) - tf.linalg.matvec(tf.expand_dims(self.Z_im, 0), theta_im)
        Z_theta_im = tf.linalg.matvec(tf.expand_dims(self.Z_re, 0), theta_im) + tf.linalg.matvec(tf.expand_dims(self.Z_im, 0), theta_re)
        
        
        u_re = self.y_re - Z_theta_re
        u_im = self.y_im - Z_theta_im

        tmp2_ = - tf.reduce_sum(tf.multiply(tf.square(u_re) + tf.square(u_im), delta_inv), [1,2])
        
        v = tmp1_ + tmp2_
        return v                          



    def temp1_sparse(self, params):
        # each of params is a 3-d tensor with sample_size as the fist dim.
     
        ldelta_ = tf.matmul(self.Xmat_delta, tf.transpose(params[0], [0,2,1]))
        tmp1_ = - tf.reduce_sum(ldelta_, [1,2])
        #delta_ = tf.exp(ldelta_)
        delta_inv = tf.exp(- ldelta_)
        theta_re = tf.matmul(self.Xmat_theta, tf.transpose(params[2], [0,2,1]))  # no need \ here
        theta_im = tf.matmul(self.Xmat_theta, tf.transpose(params[4], [0,2,1]))
    
        Z_theta_re_ls = [tf.sparse.sparse_dense_matmul(self.Z_re[i], tf.transpose(theta_re[:,i])) - tf.sparse.sparse_dense_matmul(self.Z_im[i], tf.transpose(theta_im[:,i])) for i in range(self.num_obs)]
        Z_theta_im_ls = [tf.sparse.sparse_dense_matmul(self.Z_re[i], tf.transpose(theta_im[:,i])) + tf.sparse.sparse_dense_matmul(self.Z_im[i], tf.transpose(theta_re[:,i])) for i in range(self.num_obs)]

        u_re = self.y_re - tf.transpose(tf.stack(Z_theta_re_ls), [2,0,1])
        u_im = self.y_im - tf.transpose(tf.stack(Z_theta_im_ls), [2,0,1])

        tmp2_ = - tf.reduce_sum(tf.multiply(tf.square(u_re) + tf.square(u_im), delta_inv), [1,2])
        v = tmp1_ + tmp2_
        return v                          
       

    def temp_train_one_step(self, optimizer, loglik, prior): 
        with tf.GradientTape() as tape:
            loss = - loglik(self.trainable_vars) - prior(self.trainable_vars)  # negative log posterior           
        grads = tape.gradient(loss, self.trainable_vars)
        optimizer.apply_gradients(zip(grads, self.trainable_vars))
        return - loss # return log posterior
        

 
    def temp2(self, params):
        # each of params is a 3-d tensor with sample_size as the fist dim.
        #       
        Sigma1 = tf.multiply(tf.eye(tf.constant(2), dtype=tf.float32), self.hyper[2])
        p1 = tfd.MultivariateNormalTriL(scale_tril = tf.linalg.cholesky(Sigma1)) # can also use tfd.MultivariateNormalDiag
        
        Sigm = tfb.Sigmoid()
        s_la_alp = Sigm(- tf.range(1, params[1].shape[-1] + 1., dtype=tf.float32) + self.hyper[3])
        p2 = tfd.HalfCauchy(tf.constant(0, tf.float32), s_la_alp)
        
        s_la_theta = Sigm(- tf.range(1, params[3].shape[-1] + 1., dtype=tf.float32) + self.hyper[3])
        p3 = tfd.HalfCauchy(tf.constant(0, tf.float32), s_la_theta)

        a2 = tf.square(tf.exp(params[1])) 
        Sigma2i_diag = tf.divide(tf.multiply(tf.multiply(a2, tf.square(tf.exp(params[6]))) , self.hyper[1]),
                          tf.multiply(a2, tf.square(tf.exp(params[6]))) + self.hyper[1] )
            
        p4 = tfd.MultivariateNormalDiag(scale_diag = Sigma2i_diag)
            
        p5 = tf.reduce_sum(p1.log_prob(params[0][:, :, 0:2]), [1]) #
        p7 = tf.reduce_sum(p4.log_prob(params[0][:, :, 2:]), [1]) # only 2 dim due to log_prob rm the event_shape dim
        p6 = tf.reduce_sum(p2.log_prob(tf.exp(params[1])), [1,2]) + tf.reduce_sum(params[1],[1,2])
        p8 = p7 + p6 + p5
        
        
        a3 = tf.square(tf.exp(params[3]))
        Sigma3i_diag = tf.divide(tf.multiply(tf.multiply(a3, tf.square(tf.exp(params[7]))) , self.hyper[1]),
                           tf.multiply(a3, tf.square(tf.exp(params[7]))) + self.hyper[1] )
            
        p3 = tfd.MultivariateNormalDiag(scale_diag = Sigma3i_diag)
            
        p9 = tf.reduce_sum(p3.log_prob(params[2]), [1])
        p10 = tf.reduce_sum(p3.log_prob(tf.exp(params[3])), [1,2]) + tf.reduce_sum(params[3],[1,2])
        p11 = p9 + p10
        
        
        a4 = tf.square(tf.exp(params[5]))
        Sigma4i_diag = tf.divide(tf.multiply(tf.multiply(a4, tf.square(tf.exp(params[7]))) , self.hyper[1]),
                          tf.multiply(a4, tf.square(tf.exp(params[7]))) + self.hyper[1] )
            
        p4 = tfd.MultivariateNormalDiag(scale_diag = Sigma4i_diag)
            
        p5 = tf.reduce_sum(p4.log_prob(params[4]),[1])
        p6 = tf.reduce_sum(p3.log_prob(tf.exp(params[5])), [1,2]) + tf.reduce_sum(params[5],[1,2])
        p12 = p5 + p6 
        
        
        pt = tfd.HalfCauchy(tf.constant(0, tf.float32), self.hyper[0])
        v = p8 + p11 + p12 + tf.reduce_sum(pt.log_prob(tf.exp(params[6])) + params[6], [1,2]) + tf.reduce_sum(pt.log_prob(tf.exp(params[7]))+params[7], [1, 2]) 
        return v













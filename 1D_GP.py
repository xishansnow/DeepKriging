r"""°°°
## First Simulation Study
°°°"""
# |%%--%%| <m12Y9BlcBB|7IytJP2FTZ>
r"""°°°
### Load Libraries
°°°"""
# |%%--%%| <7IytJP2FTZ|PQoeIYjdAw>

import numpy as np
import scipy.stats as stats

##Library neural nets
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization

# Library for Gaussian process
import GPy

##Library for visualization
import matplotlib as mpl
import matplotlib.pyplot as plt
plt.style.use("seaborn")
%matplotlib inline
%config InlineBackend.figure_format = 'svg'
import matplotlib;matplotlib.rcParams['figure.figsize'] = (8,6)
import pylab 
import re

# |%%--%%| <PQoeIYjdAw|WsjJVC8O6P>

# split into input (X) and output (Y) variables
N = 1000 ##Sample Size
P = 1 ##Covariates
M = 100 ##replicates
X = np.array([np.ones(N)]).T ##Design matrix

kernel = GPy.kern.Exponential(1,1,0.1) ##Covariance Function
noise_var = 0.01 ##Nugget variance

# 生成训练数据 1000 points evenly spaced over [0,1]
s = np.linspace(0,1,N).reshape(-1,1)
mu = np.ones(N).reshape(-1,1) # vector of the means
nugget = np.eye(N) * noise_var ##Nugget matrix
cov_mat = kernel.K(s) + nugget ##Covariance matrix

# Generate M sample path with mean mu and covariance C
np.random.seed(1)
y = np.random.multivariate_normal(mu[:,0],cov_mat,M).T

# |%%--%%| <WsjJVC8O6P|FBPKurHS5Y>

print(y.shape) ##check the dimension of y

# |%%--%%| <FBPKurHS5Y|4vK9d80dSC>
r"""°°°
### Visualize the Observation
°°°"""
# |%%--%%| <4vK9d80dSC|kPBILNH8Gy>

plt.plot(s,y[:,0],".",mew=1.5)
plt.show()### Create a neural network with three hidden layers
#plt.savefig("trueGP.pdf")

# |%%--%%| <kPBILNH8Gy|HBHohwRk28>
r"""°°°
### Create a neural network with seven hidden layers
°°°"""
# |%%--%%| <HBHohwRk28|8CvEq8gnkt>

def create_mlp_7(feature_dim):
    # create model
    model = Sequential()
    model.add(Dense(100, input_dim = feature_dim,  kernel_initializer='he_normal', activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(100, activation='relu'))
    model.add(Dense(1, activation='linear'))
    # Compile model
    model.compile(loss='mse', optimizer='adam', metrics=['mse','mae'])
    return model### Create a neural network with 7 hidden layers

# |%%--%%| <8CvEq8gnkt|LonWVahIUH>
r"""°°°
### Generate basis functions
°°°"""
# |%%--%%| <LonWVahIUH|6E0l5xsxnH>

num_basis = [10,19,37,73]
knots = [np.linspace(0,1,i) for i in num_basis]
##Wendland kernel
K = 0 ## basis size
phi = np.zeros((N, sum(num_basis)))
for res in range(len(num_basis)):
    theta = 1/num_basis[res]*2.5
    for i in range(num_basis[res]):
        d = np.absolute(s-knots[res][i])/theta
        for j in range(len(d)):
            if d[j] >= 0 and d[j] <= 1:
                phi[j,i + K] = (1-d[j])**6 * (35 * d[j]**2 + 18 * d[j] + 3)/3
            else:
                phi[j,i + K] = 0
    K = K + num_basis[res]

# |%%--%%| <6E0l5xsxnH|wZ99DeIqxq>
r"""°°°
Check the dimension of $s$, $X$, $y$ and $\phi$
°°°"""
# |%%--%%| <wZ99DeIqxq|AquZ2FPWTO>

print(s.shape)
print(X.shape)
print(y.shape)
print(phi.shape)

# |%%--%%| <AquZ2FPWTO|CZJZEMEXtp>
r"""°°°
### Split the data
°°°"""
# |%%--%%| <CZJZEMEXtp|yBDdu1d9Zo>

from sklearn.model_selection import train_test_split
indices = np.arange(N)
## Split the training and testing sets
s_train, s_test, X_train, X_test, phi_train, phi_test\
    , y_train, y_test, idx_train, idx_test \
    = train_test_split(s, X, phi, y, indices, test_size=0.2)
N_train = s_train.shape[0]
N_test = s_test.shape[0]

# |%%--%%| <yBDdu1d9Zo|mGnlTvtE4P>
r"""°°°
** Only with X=1 **
°°°"""
# |%%--%%| <mGnlTvtE4P|kY9MTIGhg7>

model_1 = create_mlp_7(feature_dim = P)
 
# train the model
print("[INFO] training model 1...")
model_1.fit(X_train, y_train[:,0], epochs = 200, batch_size = 32, verbose = 0)

# |%%--%%| <kY9MTIGhg7|3pIEmXo2Os>
r"""°°°
** With s and X **
°°°"""
# |%%--%%| <3pIEmXo2Os|7wTpnCkBQC>

model_2 = create_mlp_7(feature_dim = P + 1)
Xs_train = np.hstack((X_train,s_train)) 
# train the model
print("[INFO] training model 2...")
model_2.fit(Xs_train, y_train[:,0], epochs = 200, batch_size = 32, verbose = 0)

# |%%--%%| <7wTpnCkBQC|7QOxYTJtid>
r"""°°°
** With RBF and X **
°°°"""
# |%%--%%| <7QOxYTJtid|sbQ2pbITLH>

model_3 = create_mlp_7(feature_dim = P + K)
XRBF_train = np.hstack((X_train,phi_train)) 
# train the model
print("[INFO] training model 3...")
train_history = model_3.fit(XRBF_train, y_train[:,0], epochs = 200, batch_size = 32, verbose = 0)

# |%%--%%| <sbQ2pbITLH|Gsf5SWUf2Z>

Xs = np.hstack((X,s))
XRBF = np.hstack((X,phi))
y0_test_1 = model_1.predict(X)
y0_test_2 = model_2.predict(Xs)
y0_test_3 = model_3.predict(XRBF)

# |%%--%%| <Gsf5SWUf2Z|tVE2Wd2ypd>

print([y0_test_1.shape,y0_test_2.shape,y0_test_3.shape])

# |%%--%%| <tVE2Wd2ypd|umKhFZ26z2>
r"""°°°
### Truth from GP
°°°"""
# |%%--%%| <umKhFZ26z2|VrSxl3Rvmg>

##Warning: it is important to write 0:1 in GPRegression to get the size (Ntrain,1)
m = GPy.models.GPRegression(s_train,y_train[:,0:1] - mu[idx_train], kernel, noise_var = noise_var)
mu_GP,var_GP = m.predict(s)
lo95_GP,up95_GP = m.predict_quantiles(s)
y0_gp = mu_GP + mu

# |%%--%%| <VrSxl3Rvmg|XtkkrICeKo>

print(y0_gp.shape)

# |%%--%%| <XtkkrICeKo|jdmofPbOlP>

kernel2 = GPy.kern.Matern32(1,1,1)
m2 = GPy.models.GPRegression(s_train,y_train[:,0:1] - mu[idx_train],kernel2, noise_var = noise_var)
m2.optimize()
mu_GPE,var_GPE = m2.predict(s)
lo95_GPE,up95_GPE = m2.predict_quantiles(s)
y0_gpe = mu_GPE + mu

# |%%--%%| <jdmofPbOlP|F9KOg3LksP>

print(y0_gpe.shape)

# |%%--%%| <F9KOg3LksP|WA2Za9F14H>
r"""°°°
### Visualize results
°°°"""
# |%%--%%| <WA2Za9F14H|EYV047IzbB>

pylab.plot(s, y[:,0],".",label="Observation")
pylab.plot(s, y0_test_1,'blue',label="DNN with intercept")
pylab.plot(s, y0_test_2,'pink',label="DNN with intercept and coordinates")
pylab.plot(s, y0_test_3,'red',label="DeepKriging")
pylab.plot(s, y0_gpe,'black',label="Kriging with Matern covariance")
pylab.plot(s, y0_gp,'grey',label="Kriging with exponetial covariance")
pylab.legend(loc='upper right')
pylab.show()
#plt.savefig("1D_compare.pdf")

# |%%--%%| <EYV047IzbB|Zny49QLEHm>
r"""°°°
### MSE, MAE, and Nonlinearity
°°°"""
# |%%--%%| <Zny49QLEHm|jdFNo80EYV>

def rmse(y_true,y_pred):
    rmse = np.sqrt(np.mean((y_true-y_pred)**2))
    return float(rmse)
def mape(y_true,y_pred):
    mape = np.mean(np.absolute(y_true-y_pred)/np.absolute(y_true))
    return float(mape)

# |%%--%%| <jdFNo80EYV|tlBWWt0iDe>

rmse_train_combine = np.zeros((5,M))
mape_train_combine = np.zeros((5,M))
rmse_test_combine = np.zeros((5,M))
mape_test_combine = np.zeros((5,M))

for i in range(M):
    print("[INFO] training %s-th replicate..." % (i+1))
    ##Kriging with exponential covariance
    m = GPy.models.GPRegression(s_train,y_train[:,i:(i+1)], kernel, noise_var = noise_var)
    mu_GP_train,var_GP_train = m.predict(s_train)
    y_gp_train = mu_GP_train
    mu_GP_test,var_GP_test = m.predict(s_test)
    y_gp_test = mu_GP_test
    
    ##Kriging with Matern covariance
    kernel2 = GPy.kern.Matern32(1,1,1)
    m2 = GPy.models.GPRegression(s_train,y_train[:,i:(i+1)],kernel2, noise_var = noise_var)
    m2.optimize()
    mu_GPE_train,var_GPE_train = m2.predict(s_train)
    y_gpe_train = mu_GPE_train
    mu_GPE_test,var_GPE_test = m2.predict(s_test)
    y_gpe_test = mu_GPE_test
 
    ##DNN with intercept
    model_1.fit(X_train, y_train[:,i], epochs = 500, batch_size = 32, verbose = 0)
    y_dnn_train = model_1.predict(X[idx_train,:])
    y_dnn_test = model_1.predict(X[idx_test,:])
 
    ##DNN with intercept and coordinate
    model_2.fit(Xs_train, y_train[:,i], epochs = 500, batch_size = 32, verbose = 0)
    y_dnn2_train = model_2.predict(Xs[idx_train,:])
    y_dnn2_test = model_2.predict(Xs[idx_test,:])
    
    ##DeepKriging with seven hidden layers
    model_3.fit(XRBF_train, y_train[:,i], epochs = 200, batch_size = 32, verbose = 0)
    y_dk_train = model_3.predict(XRBF[idx_train,:])
    y_dk_test = model_3.predict(XRBF[idx_test,:])
    
   
    ##Save the results
    rmse_train_combine[:,i] = np.array([rmse(y_train[:,i],y_gp_train[:,0]),\
                                  rmse(y_train[:,i],y_gpe_train[:,0]),\
                                  rmse(y_train[:,i],y_dk_train[:,0]),\
                                  rmse(y_train[:,i],y_dnn_train[:,0]),\
                                  rmse(y_train[:,i],y_dnn2_train[:,0])])
    mape_train_combine[:,i] = np.array([mape(y_train[:,i],y_gp_train[:,0]),\
                                  mape(y_train[:,i],y_gpe_train[:,0]),\
                                  mape(y_train[:,i],y_dk_train[:,0]),\
                                  mape(y_train[:,i],y_dnn_train[:,0]),\
                                  mape(y_train[:,i],y_dnn2_train[:,0])])
    rmse_test_combine[:,i] = np.array([rmse(y_test[:,i],y_gp_test[:,0]),\
                                  rmse(y_test[:,i],y_gpe_test[:,0]),\
                                  rmse(y_test[:,i],y_dk_test[:,0]),\
                                  rmse(y_test[:,i],y_dnn_test[:,0]),\
                                  rmse(y_test[:,i],y_dnn2_test[:,0])])
    mape_test_combine[:,i] = np.array([mape(y_test[:,i],y_gp_test[:,0]),\
                                  mape(y_test[:,i],y_gpe_test[:,0]),\
                                  mape(y_test[:,i],y_dk_test[:,0]),\
                                  mape(y_test[:,i],y_dnn_test[:,0]),\
                                  mape(y_test[:,i],y_dnn2_test[:,0])])

    print(rmse_train_combine[:,i])
    print(mape_train_combine[:,i])
    
    print(rmse_test_combine[:,i])
    print(mape_test_combine[:,i])

# |%%--%%| <tlBWWt0iDe|HFf6flVdG4>

print(np.mean(rmse_train_combine,axis=1))
print(np.std(rmse_train_combine,axis=1))
print(np.mean(mape_train_combine,axis=1))
print(np.std(mape_train_combine,axis=1))

# |%%--%%| <HFf6flVdG4|PxnPxIUyhD>

print(np.mean(rmse_train_combine,axis=1))
print(np.std(rmse_train_combine,axis=1))
print(np.mean(mape_train_combine,axis=1))
print(np.std(mape_train_combine,axis=1))

# |%%--%%| <PxnPxIUyhD|TiRkNHneEC>

import numpy as np
from scipy.optimize import minimize
from sklearn.neighbors import kneighbors_graph
from scipy import sparse
from LAMDA_SSL.Base.InductiveEstimator import InductiveEstimator
from sklearn.base import ClassifierMixin
from sklearn.metrics.pairwise import rbf_kernel
import copy
import inspect
from torch.utils.data.dataset import Dataset
import LAMDA_SSL.Config.LapSVM as config

class LapSVM(InductiveEstimator,ClassifierMixin):
    # Binary
    def __init__(self,
           distance_function= config.distance_function,
           gamma_d=config.gamma_d,
           neighbor_mode =config.neighbor_mode,
           t=config.t,
           n_neighbor= config.n_neighbor,
           kernel_function= config.kernel_function,
           gamma_k=config.gamma_k,
           gamma_A= config.gamma_A,
           gamma_I= config.gamma_I,evaluation=config.evaluation,
           verbose=config.verbose,file=config.file):
        # >> Parameter:
        # >> - distance_function: The distance function for building the graph. This Pamater is valid when neighbor_mode is None.
        # >> - gamma_d: Kernel parameters related to distance_function.
        # >> - neighbor_mode: The edge weight after constructing the graph model by k-nearest neighbors. There are two options 'connectivity' and 'distance', 'connectivity' returns a 0-1 matrix, and 'distance' returns a distance matrix.
        # >> - n_neighbor: k value of k-nearest neighbors.
        # >> - kernel_function: The kernel function corresponding to SVM.
        # >> - gamma_k: The gamma parameter corresponding to kernel_function.
        # >> - gamma_A: Penalty weight for function complexity.
        # >> - gamma_I: Penalty weight for smoothness of data distribution.
        self.distance_function=distance_function
        self.neighbor_mode=neighbor_mode
        self.n_neighbor=n_neighbor
        self.t=t
        self.kernel_function=kernel_function
        self.gamma_k=gamma_k
        self.gamma_d=gamma_d
        self.gamma_A=gamma_A
        self.gamma_I=gamma_I
        self.evaluation = evaluation
        self.verbose=verbose
        self.file=file
        self.y_pred=None
        self.y_score=None
        self._estimator_type = ClassifierMixin._estimator_type


    def fit(self,X,y,unlabeled_X):
        classes, y_indices = np.unique(y, return_inverse=True)
        if len(classes)!=2:
            raise ValueError('TSVM can only be used in binary classification.')

        self.class_dict={classes[0]:-1,classes[1]:1}
        self.rev_class_dict = {-1:classes[0] ,  1:classes[1]}
        y=copy.copy(y)
        for _ in range(X.shape[0]):
            y[_]=self.class_dict[y[_]]


        # Construct Graph

        self.X=np.vstack([X,unlabeled_X])
        Y=np.diag(y)
        if self.distance_function == 'knn':
            if self.neighbor_mode=='connectivity':
                W = kneighbors_graph(self.X, self.n_neighbor, mode='connectivity',include_self=False)
                W = (((W + W.T) > 0) * 1)

            elif self.neighbor_mode=='distance':
                W = kneighbors_graph(self.X, self.n_neighbor, mode='distance',include_self=False)
                W = W.maximum(W.T)
                W = sparse.csr_matrix((np.exp(-W.data**2/4/self.t),W.indices,W.indptr),shape=(self.X.shape[0],self.X.shape[0]))

        elif self.distance_function =='rbf':
            W=rbf_kernel(self.X,self.X,self.gamma_d)
            W = sparse.csr_matrix(W)
        elif self.distance_function is not None:
            if self.gamma_d is not None:
                W=self.distance_function(self.X,self.X,self.gamma_d)
            else:
                W = self.distance_function(self.X, self.X)
            W=sparse.csr_matrix(W)
        else:
            raise Exception()

        L = sparse.diags(np.array(W.sum(0))[0]).tocsr() - W

        if self.kernel_function == 'rbf':
            K = rbf_kernel(self.X,self.X,self.gamma_k)
        elif self.kernel_function is not None:
            if self.gamma_k is not None:
                K = self.kernel_function(self.X,self.X,self.gamma_k)
            else:
                K = self.kernel_function(self.X, self.X)
        else:
            K = rbf_kernel(self.X, self.X, self.gamma_k)
        l=X.shape[0]
        u=unlabeled_X.shape[0]
        J = np.concatenate([np.identity(l), np.zeros(l * u).reshape(l, u)], axis=1)
        almost_alpha = np.linalg.inv(2 * self.gamma_A * np.identity(l + u) \
                                     + ((2 * self.gamma_I) / (l + u) ** 2) * L.dot(K)).dot(J.T).dot(Y)

        Q = Y.dot(J).dot(K).dot(almost_alpha)
        Q = (Q+Q.T)/2

        del W, L, K, J

        e = np.ones(l)
        q = -e

        def objective_func(beta):
            return (1 / 2) * beta.dot(Q).dot(beta) + q.dot(beta)

        def objective_grad(beta):
            return np.squeeze(np.array(beta.T.dot(Q) + q))

        bounds = [(0, 1 / l) for _ in range(l)]

        def constraint_func(beta):
            return beta.dot(np.diag(Y))

        def constraint_grad(beta):
            return np.diag(Y)

        cons = {'type': 'eq', 'fun': constraint_func, 'jac': constraint_grad}
        x0 = np.zeros(l)

        beta_hat = minimize(objective_func, x0, jac=objective_grad, constraints=cons, bounds=bounds)['x']
        self.alpha = almost_alpha.dot(beta_hat)

        del almost_alpha, Q
        if self.kernel_function == 'rbf':
            new_K = rbf_kernel(self.X,X,self.gamma_k)
        elif self.kernel_function is not None:
            if self.gamma_k is not None:
                new_K = self.kernel_function(self.X,X,self.gamma_k)
            else:
                new_K = self.kernel_function(self.X,X)
        else:
            new_K = rbf_kernel(self.X, X, self.gamma_k)
        f = np.squeeze(np.array(self.alpha)).dot(new_K)

        self.sv_ind=np.nonzero((beta_hat>1e-7)*(beta_hat<(1/l-1e-7)))[0]

        ind=self.sv_ind[0]
        self.b=np.diag(Y)[ind]-f[ind]
        return self


    def decision_function(self,X):
        if self.kernel_function == 'rbf':
            new_K = rbf_kernel(self.X,X,self.gamma_k)
        elif self.kernel_function is not None:
            if self.gamma_k is not None:
                new_K = self.kernel_function(self.X,X,self.gamma_k)
            else:
                new_K = self.kernel_function(self.X,X)
        else:
            new_K = rbf_kernel(self.X, X, self.gamma_k)
        f = np.squeeze(np.array(self.alpha)).dot(new_K)
        return f+self.b

    def predict_proba(self,X):
        Y_ = self.decision_function(X)
        y_proba = np.full((X.shape[0], 2), 0, np.float)
        y_proba[:,0]=1/(1+np.exp(Y_))
        y_proba[:, 1] =1- y_proba[:,0]
        return y_proba

    def predict(self,X):
        Y_ = self.decision_function(X)
        y_pred = np.ones(X.shape[0])
        y_pred[Y_ < 0] = -1
        for _ in range(X.shape[0]):
            y_pred[_]=self.rev_class_dict[y_pred[_]]
        return y_pred

    def evaluate(self,X,y=None):

        if isinstance(X,Dataset) and y is None:
            y=getattr(X,'y')

        self.y_score = self.predict_proba(X)
        self.y_pred=self.predict(X)


        if self.evaluation is None:
            return None
        elif isinstance(self.evaluation,(list,tuple)):
            performance=[]
            for eval in self.evaluation:
                score=eval.scoring(y,self.y_pred,self.y_score)
                if self.verbose:
                    print(score, file=self.file)
                performance.append(score)
            self.performance = performance
            return performance
        elif isinstance(self.evaluation,dict):
            performance={}
            for key,val in self.evaluation.items():

                performance[key]=val.scoring(y,self.y_pred,self.y_score)

                if self.verbose:
                    print(key,' ',performance[key],file=self.file)
                self.performance = performance
            return performance
        else:
            performance=self.evaluation.scoring(y,self.y_pred,self.y_score)
            if self.verbose:
                print(performance, file=self.file)
            self.performance=performance
            return performance
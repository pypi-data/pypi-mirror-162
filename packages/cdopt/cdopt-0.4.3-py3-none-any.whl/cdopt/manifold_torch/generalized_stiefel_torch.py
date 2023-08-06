import numpy as np
import torch

# from numpy.linalg import svd, eig
from .basic_manifold_torch import basic_manifold_torch
from torch.nn.parameter import Parameter
from torch import Tensor, DeviceObjType
from typing import List, Tuple, Optional, Callable

class generalized_stiefel_torch(basic_manifold_torch):
    def __init__(self, var_shape, B = lambda X:X , device = torch.device('cpu'), dtype = torch.float64) -> None:
        if len(var_shape) >= 2:
            self._n = var_shape[-2]
            self._p = var_shape[-1]
            self.dim = var_shape[:-2]
        else:
            print("The length of var_shape for generalized Stiefel manifold should be no less than 2.")
            raise TypeError
        self.var_shape = var_shape
        self.manifold_type = 'S'
        self.device = device
        self.dtype = dtype
        
        super().__init__('Generalized_Stiefel',var_shape, (*self.dim, self._p,self._p),   device= self.device ,dtype= self.dtype)
        if isinstance(B, Callable):
            self.B = B 
        elif isinstance(B, Tensor):
            self._parameters['B'] = B
            self.B = lambda X : torch.matmul(self._parameters['B'] , X)
        # Here we require B be a function since it could fully utilize the
        # low-rank structure of B
        #  when one wishes to input a matrix B_mat
        #  we recommand to use lambda X: B@X instead

        

        self._parameters['Ip'] = Parameter(torch.diag_embed(torch.ones((*self.dim, self._p), device=self.device, dtype=self.dtype)), False)
        self.Ip = self._parameters['Ip']


    def Phi(self, M):
        return (M + M.transpose(-2,-1))/2


    def A(self, X):
        XX = X.transpose(-2,-1) @ self.B(X)
        return 1.5 * X - X @ (XX /2)


    def JA(self, X, D):
        BX = self.B(X)
        return D @ ( 1.5 * self.Ip - 0.5 * X.transpose(-2,-1) @ BX  )  - BX @ self.Phi(X.transpose(-2,-1) @ D)


    def JA_transpose(self, X, D):
        BX = self.B(X)
        return D @ ( 1.5 * self.Ip - 0.5 * X.transpose(-2,-1) @ BX  ) - X @ self.Phi( D.transpose(-2,-1) @ BX )


    def hessA(self, X, gradf, D):
        BX = self.B(X)

        return - self.B(D) @ self.Phi( X.transpose(-2,-1) @ gradf  ) - BX @ self.Phi(D.transpose(-2,-1) @ gradf) - gradf @ self.Phi( D.transpose(-2,-1) @ BX )



    
    def C(self, X):
        return X.transpose(-2,-1) @ self.B(X) - self.Ip

    def C_quad_penalty(self, X):
        return torch.sum(self.C(X) ** 2)



    def JC(self, X, Lambda):
        return 2 * self.B(X) @ self.Phi( Lambda  )


    def hess_feas(self, X, D):
        BX = self.B(X)
        return 4*BX @ self.Phi( BX.transpose(-2,-1) @ D ) + 2*self.B(D) @ (X.transpose(-2,-1) @ BX- self.Ip)



    def Feas_eval(self, X):
        return torch.linalg.norm( self.C(X).flatten() )

    def Init_point(self, Xinit = None):
        if Xinit is None:
            Xinit = torch.randn(*self.var_shape).to(device = self.device, dtype = self.dtype)
        else:
            Xinit = Xinit.detach()
            
        XBX = torch.matmul(Xinit.transpose(-2,-1) , self.B(Xinit))
        S, V = torch.linalg.eigh(XBX)
        S_inv = 1/torch.sqrt(S)
        Xinit =  Xinit @ (V @ torch.diag_embed(S_inv) @ V.transpose(-2, -1) )

        Xinit.requires_grad = True

        
        return Xinit

    def Post_process(self,X):
        XBX = torch.matmul(X.transpose(-2,-1) , self.B(X))
        S, V = torch.linalg.eigh(XBX)
        S_inv = 1/torch.sqrt(S)
        X =  X @ (V @ torch.diag_embed(S_inv) @ V.transpose(-2, -1) )
        return X





    def generate_cdf_fun(self, obj_fun, beta):
        return  lambda X: obj_fun(self.A(X)) + (beta/2) * self.C_quad_penalty(X)
        



    def generate_cdf_grad(self, obj_grad, beta):
        def local_grad(X):
            BX= self.B(X)
            CX = X.transpose(-2,-1) @ BX - self.Ip
            AX = X - 0.5 * X@CX
            gradf = obj_grad(AX)
            XG = self.Phi(X.transpose(-2,-1) @ gradf)

            # local_JA_gradf = gradf @ (self.Ip - 0.5 * CX) - X @ XG 
            
            # local_JC_CX = 2 * X @(CX)

            return gradf @ (self.Ip - 0.5 * CX) +  BX @  ( 2* beta * CX - XG) 

        return local_grad  




    def generate_cdf_hess(self, obj_grad, obj_hess, beta):
        def local_hess(X, D):
            BX= self.B(X)
            CX = X.transpose(-2,-1) @ BX - self.Ip
            AX = X - 0.5 * X@CX
            gradf = obj_grad(AX)
            # XG = self.Phi(X.transpose(-2,-1) @ gradf)



            local_JAT_D =  D @ ( self.Ip - 0.5 * CX  ) - X @ self.Phi( D.transpose(-2,-1) @ BX )
            local_objhess_JAT_D = obj_hess(AX, local_JAT_D)
            # local_JA_objhess_JAT_D = local_objhess_JAT_D @ ( self.Ip - 0.5 * CX  )  - BX @ self.Phi(X.transpose(-2,-1) @ local_objhess_JAT_D)

            # local_hessA_objgrad_D = - self.B(D) @ self.Phi( X.transpose(-2,-1) @ gradf  ) - BX @ self.Phi(D.transpose(-2,-1) @ gradf) - gradf @ self.Phi( D.transpose(-2,-1) @ BX )

            # local_hess_feas = 4*BX @ self.Phi( BX.transpose(-2,-1) @ D ) + 2*self.B(D) @ CX



            return local_objhess_JAT_D @ ( self.Ip - 0.5 * CX  )  - BX @ (self.Phi(X.transpose(-2,-1) @ local_objhess_JAT_D) + self.Phi(D.transpose(-2,-1) @ gradf)  - 4* beta * self.Phi( BX.transpose(-2,-1) @ D )   ) - self.B(D) @ self.Phi( X.transpose(-2,-1) @ gradf -2*beta * CX ) - gradf @ self.Phi( D.transpose(-2,-1) @ BX )


        return local_hess



    def generate_cdf_hess_approx(self, obj_grad, obj_hess, beta):
        def local_hess(X, D):
            AX = self.A(X)
            gradf = obj_grad(AX)

            local_JAT_D = self.JA_transpose(X, D)
            local_objhess_JAT_D = obj_hess(AX, local_JAT_D)
            local_JA_objhess_JAT_D = self.JA(X, local_objhess_JAT_D)

            local_hessA_objgrad_D = self.hessA(X, gradf, D)

            local_hess_feas = self.hess_feas(X,D)


            return local_JA_objhess_JAT_D + local_hessA_objgrad_D + beta * local_hess_feas

        return local_hess

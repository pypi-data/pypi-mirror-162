import numpy as np
import torch
from .basic_manifold_torch import basic_manifold_torch
from torch.nn.parameter import Parameter
from torch import Tensor, DeviceObjType
from typing import List, Tuple, Optional, Callable

class hyperbolic_torch(basic_manifold_torch):
    def __init__(self, var_shape, B = None, device = torch.device('cpu'), dtype = torch.float64) -> None:
        if len(var_shape) >= 2:
            self._n = var_shape[-2]
            self._p = var_shape[-1]
            self.dim = var_shape[:-2]
        else:
            print("The length of var_shape should be no less than 2.")
            raise TypeError
        self.device = device
        self.dtype = dtype

        self.var_shape = var_shape

        self._half_n = int(self._n/2)



        super().__init__('Hyperbolic',var_shape, (*self.dim, self._p, self._p),   device= self.device ,dtype= self.dtype)
        if B is None:
            # idx =  list(range(int(n/2),n)) + list(range(int(n/2) )) 
            # def B(X):
            #     return X[idx,:]



            # In = np.eye(int(n/2))
            # Zero_n = np.zeros((int(n/2),int(n/2)))

            # Jn = np.block([[Zero_n,  In], [In, Zero_n]    ])




            # Jn = torch.tensor(Jn, dtype= self.dtype).to_sparse()
            # Jn = Jn.to(device = self.device, dtype = self.dtype)


            def B(X):
                return torch.cat( (X[...,self._half_n:, :], X[...,:self._half_n,:]), -2 )
                # return torch.matmul(Jn, X)


        if isinstance(B, Callable):
            self.B = B 
        elif isinstance(B, Tensor):
            self._parameters['B'] = B
            self.B = lambda X : torch.matmul(self._parameters['B'] , X)



        
        
        self._parameters['Ip'] = Parameter(torch.diag_embed(torch.ones((*self.dim, self._p), device=self.device, dtype=self.dtype)), False)
        self.Ip = self._parameters['Ip']
        # Here we require B be a function
        #  when one wishes to input a matrix B_mat
        #  we recommand to use lambda X: B@X instead

        

    def Phi(self, M):
        return (M + M.transpose(-2,-1))/2


    def A(self, X: Tensor):
        XX = torch.matmul(X.transpose(-2,-1) , self.B(X))
        return 1.5 * X - torch.matmul(X , (XX /2))


    def JA(self, X: Tensor, D: Tensor):
        BX = self.B(X)
        return torch.matmul(D , ( 1.5 * self.Ip - 0.5 * torch.matmul(X.transpose(-2,-1) , BX)  ))  - torch.matmul(BX , self.Phi( torch.matmul(X.transpose(-2,-1) , D) ) )


    def JA_transpose(self, X, D):
        BX = self.B(X)
        return torch.matmul(D , ( 1.5 * self.Ip - 0.5 * torch.matmul(X.transpose(-2,-1) , BX)  )) - torch.matmul(X , self.Phi( torch.matmul(D.transpose(-2,-1) , BX )) )


    def hessA(self, X, gradf, D):
        BX = self.B(X)

        return torch.matmul(- self.B(D) , self.Phi( torch.matmul(X.transpose(-2,-1) , gradf)  )) - torch.matmul(BX , self.Phi(torch.matmul(D.transpose(-2,-1) , gradf))) - torch.matmul(gradf , self.Phi( torch.matmul(D.transpose(-2,-1) , BX) ))




    
    def C(self, X):
        return torch.matmul(X.transpose(-2,-1) , self.B(X)) - self.Ip

    def C_quad_penalty(self, X):
        return torch.sum(self.C(X) ** 2)



    def JC(self, X:Tensor, Lambda:Tensor):
        return 2 * torch.matmul(self.B(X) , self.Phi( Lambda  ))


    def hess_feas(self, X:Tensor, D:Tensor):
        BX = self.B(X)
        return torch.matmul(4*BX , self.Phi( torch.matmul(BX.transpose(-2,-1), D) )) + 2*torch.matmul(self.B(D) , (torch.matmul(X.transpose(-2,-1) , BX)- self.Ip))



    def Feas_eval(self, X):
        return torch.linalg.norm( self.C(X).flatten() )

    def Init_point(self, Xinit = None):
        X = Xinit
        if X == None:
            X = torch.randn(*self.var_shape).to(device = self.device, dtype = self.dtype)
            UX, SX, VX = torch.svd(X)
            X = torch.matmul(UX, VX.transpose(-2,-1))
        else:
            X = X.detach().to(device = self.device, dtype = self.dtype)

            
        # X = X.to(device = self.device, dtype = self.dtype)
        

        for jl in range(30):
            # XX = torch.matmul(X.transpose(-2,-1) , self.B(X))
            feas = self.Feas_eval(X)
            # print(feas)
            if feas < 1e-1:
                X = self.A(X)
            else:
                X = X - 0.2* torch.matmul(self.B(X) , self.C(X))
                # X = np.linalg.solve(0.5 * XX + 0.5 * self.Ip, X.transpose(-2,-1) ).transpose(-2,-1)
                # X = X + 0.00001/self._n * np.random.randn(self._n, self._p)
            if feas < 1e-8:
                break

        X.requires_grad = True 
        return X

    def Post_process(self,X):
        XBX = torch.matmul(X.transpose(-2,-1) , self.B(X))
        S, V = torch.linalg.eigh(XBX)
        S_inv = 1/torch.sqrt(S)
        X =  X @ (V @ torch.diag_embed(S_inv) @ V.transpose(-2, -1) )
        return X





    def generate_cdf_fun(self, obj_fun, beta):
        return lambda X: obj_fun(self.A(X)) + (beta/2) * self.C_quad_penalty(X)
        




    def generate_cdf_grad(self, obj_grad, beta):
        def local_grad(X:Tensor):
            BX= self.B(X)
            CX = torch.matmul(X.transpose(-2,-1) , BX) - self.Ip
            AX = X - 0.5 * torch.matmul(X, CX)
            gradf = obj_grad(AX)
            XG = self.Phi(torch.matmul(X.transpose(-2,-1) , gradf))

            # local_JA_gradf = gradf @ (self.Ip - 0.5 * CX) - X @ XG 
            
            # local_JC_CX = 2 * X @(CX)

            return torch.matmul(gradf , (self.Ip - 0.5 * CX)) +  torch.matmul(BX ,  ( 2* beta * CX - XG) )

        return local_grad



    def generate_cdf_hess(self, obj_grad, obj_hess, beta):
        def local_hess(X:Tensor, D:Tensor):
            BX= self.B(X)
            CX = torch.matmul(X.transpose(-2,-1) , BX )- self.Ip
            AX = X - 0.5 * torch.matmul(X, CX)
            gradf = obj_grad(AX)
            # XG = self.Phi(X.transpose(-2,-1) @ gradf)



            local_JAT_D =  torch.matmul(D , ( self.Ip - 0.5 * CX  )) - torch.matmul(X , self.Phi( torch.matmul(D.transpose(-2,-1) , BX) ))
            local_objhess_JAT_D = obj_hess(AX, local_JAT_D)
            # local_JA_objhess_JAT_D = local_objhess_JAT_D @ ( self.Ip - 0.5 * CX  )  - BX @ self.Phi(X.transpose(-2,-1) @ local_objhess_JAT_D)

            # local_hessA_objgrad_D = - self.B(D) @ self.Phi( X.transpose(-2,-1) @ gradf  ) - BX @ self.Phi(D.transpose(-2,-1) @ gradf) - gradf @ self.Phi( D.transpose(-2,-1) @ BX )

            # local_hess_feas = 4*BX @ self.Phi( BX.transpose(-2,-1) @ D ) + 2*self.B(D) @ CX



            return torch.matmul(local_objhess_JAT_D , ( self.Ip - 0.5 * CX  ))  - torch.matmul(BX , (self.Phi(torch.matmul(X.transpose(-2,-1) , local_objhess_JAT_D)) + self.Phi(torch.matmul(D.transpose(-2,-1) , gradf))  - 4* beta * self.Phi( torch.matmul(BX.transpose(-2,-1) , D) )   )) - torch.matmul(self.B(D) , self.Phi( torch.matmul(X.transpose(-2,-1) , gradf) -2*beta * CX )) - torch.matmul(gradf , self.Phi( torch.matmul(D.transpose(-2,-1) , BX) ))


            # return local_JA_objhess_JAT_D + local_hessA_objgrad_D + beta * local_hess_feas

        return local_hess





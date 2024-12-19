# solving the household problem

import numpy as np
import numba as nb

from consav.linear_interp import interp_1d_vec

@nb.njit       
def solve_hh_backwards(par,z_trans,beta,ra,inc_TH,inc_NT,vbeg_a_plus,vbeg_a,a,c,uc_TH,uc_NT,c_TH,c_NT):
    """ solve backwards with vbeg_a from previous iteration (here vbeg_a_plus) """

    for i_fix in range(par.Nfix):
            for i_z in range(par.Nz):

                # a. solve step
                if par.sector_grid[i_fix] == 0:
                    inc = inc_TH/par.sT
                    c_endo = (par.delta_grid[i_fix]*beta*vbeg_a_plus[0,i_z])**(-1/par.sigma) #c endo for the tradeable sector and exponetial discounting
                else:
                    inc = inc_NT/(1-par.sT)
                    c_endo = (par.delta_grid[i_fix]*beta*vbeg_a_plus[2,i_z])**(-1/par.sigma)  #c endo for the Non-tradeable sector and exponetial discounting

                z = par.z_grid[i_z]

                # ii. EGM
                m_endo = c_endo + par.a_grid
            
                # iii. interpolation to fixed grid
                m = (1+ra)*par.a_grid + inc*z
                interp_1d_vec(m_endo,par.a_grid,m,a[i_fix,i_z])
                a[i_fix,i_z,:] = np.fmax(a[i_fix,i_z,:],0.0) # enforce borrowing constraint
                c[i_fix,i_z] = m-a[i_fix,i_z]

            # b. expectation step
            v_a = (1+ra)*c[i_fix]**(-par.sigma)
            vbeg_a[i_fix] = z_trans[i_fix]@v_a

    # extra output
    uc_TH[:] = 0.0
    uc_NT[:] = 0.0
    

    c_TH[:] = 0.0
    c_NT[:] = 0.0

    for i_z in range(par.Nz):
        uc_TH[0,i_z,:] = c[0,i_z,:]**(-par.sigma)*par.z_grid[i_z]
        uc_TH[1,i_z,:] = c[1,i_z,:]**(-par.sigma)*par.z_grid[i_z]
        uc_NT[2,i_z,:] = c[2,i_z,:]**(-par.sigma)*par.z_grid[i_z]
        uc_NT[3,i_z,:] = c[3,i_z,:]**(-par.sigma)*par.z_grid[i_z]

        c_TH[0,i_z,:] = c[0,i_z,:]
        c_TH[1,i_z,:] = c[1,i_z,:]
        c_NT[2,i_z,:] = c[2,i_z,:]
        c_NT[3,i_z,:] = c[3,i_z,:]

    uc_TH[:] /= par.sT
    uc_NT[:] /= (1-par.sT)

    c_TH[:] /= par.sT
    c_NT[:] /= (1-par.sT)

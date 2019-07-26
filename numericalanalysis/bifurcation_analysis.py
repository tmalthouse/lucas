
# coding: utf-8

# In[1]:


from params import params, π
import numpy as np
import math as m
from matplotlib import pyplot as plt
_=np.seterr('raise')


# In[2]:


def τ_of_s(params, s, φ, rc, τ_goal = 0):
    w_0 = params.w_0
    ξ = params.ξ
    
    hfact = 1 - rc * np.sin(φ - ξ * s + s)/np.sin(s)
    τ = s / (2*w_0**2) * (hfact * np.tan(s) + np.sqrt((hfact * np.tan(s))**2 + 4*w_0**2))
    ret = τ * w_0 / (2*π)
    err = τ - τ_goal
    return ret, err


# In[3]:


def g_of_s(params, s, φ, rc):
    ξ = params.ξ
    
    hfact = 1 - rc*np.cos(φ-ξ*s)
    
    g = hfact / np.cos(s)
    return g


# In[37]:


def bin_T_G(τ, dt, prev_idx, pls, nls):
    lt = τ - dt/2
    rt = τ + dt/2
    
    li = ri = prev_idx
    
    while (pls[ri[0], 0] <= rt):
        ri[0] += 1
        if (ri[0] > len(pls)):
            ri[0] = len(pls)
            break
    
    while (nls[ri[1], 0] <= rt):
        ri[1] += 1
        if (ri[1] > len(nls)):
            ri[1] = len(nls)
            break
    
    print('li={}, ri={}'.format(li,ri))
    retg = 0 if li == ri else min(
        min(
            pls[
                li[0] : ri[0],
                1
            ]
        ),
        min(
            rls[
                li[1] : ri[1],
                1
            ]
        )
    )
    
    new_idx = ri
    print(prev_idx, new_idx)
    return retg, new_idx
    


# In[33]:


def bin_T_G_z(τ, dt, prev_idx, zls):
    lt = τ - dt/2
    rt = τ + dt/2
    
    li = ri = prev_idx
    
    while (zls[ri[0], 0] <= rt):
        ri[0] += 1
        if (ri[0] > len(zls)):
            ri[0] = len(nls)
            break
    
    retg = 0 if li == ri else min(
        zls[li[0] : ri[0], 1]
    )
    newidx = ri
    return retg, newidx


# In[21]:


def cls(t_ub, width, pls, nls):
    catch = [1, [1,1]]
    
    out_list = []
    
    for τ in np.arange(0, t_ub, width):
        catch = bin_T_G(τ, width, catch[1], pls, nls)
        if (catch[0] == 0):
            continue
        else:
            out_list.append(np.array([τ, catch[0]]))
    return np.array(out_list)


# In[30]:


def bzls(t_ub, width, zls):
    catch = [1, [1,1]]
    
    out_list = []
    
    for τ in np.arange(0, t_ub, width):
        catch = bin_T_G_z(τ, width, catch[1], zls)
        if (catch[0] == 0):
            continue
        else:
            out_list.append(np.array([τ, catch[0]]))
    return np.array(out_list)


# In[8]:


def array_generate(params, φ, rc):
    arr_raw = []
    
    for s in np.arange(params.s_min, params.s_max, params.ds):
        try:
            if (
                τ_of_s(params, s, π/2, rc, 0)[0] <= params.τ_ub and
                g_of_s(params, s, π/2, rc) <= params.g_ub and
                g_of_s(params, s, π/2, rc) >= params.g_lb
            ):
                arr_raw.append(np.array([τ_of_s(params, s, π/2, rc)[0], g_of_s(params, s, π/2, rc)]))
        except (ZeroDivisionError, FloatingPointError):
            pass
    
    return np.array(
        sorted(arr_raw,
            key=lambda x: x[0]
        )
    )


# In[9]:


def generate_steps(params):
    
    pls = array_generate(params, π/2, params.r)
    
    nls = array_generate(params, -π/2, params.r)

    zls = array_generate(params, 0, 0)
    
    return (pls, nls, zls)


# In[35]:


pls, nls, zls = generate_steps(params)


# In[38]:


cls_out = cls(params.τ_ub, params.width, pls, nls)


# In[31]:


bzls = bzls(params.τ_ub, params.width, zls)


# In[32]:


bzls



#%%

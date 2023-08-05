#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on %(date)s

@author: %(username)s
"""

#%%%% imports
# %pylab inline
# %load_ext autoreload
# %autoreload 2
#%reload_ext autoreload
%pylab
import numpy
import matplotlib
from matplotlib import pylab, mlab, pyplot
np = numpy
plt = pyplot

from laspec import mpl
mpl.set_cham(15)

#%%%% 
from astropy import table
m9 = table.Table.read("/Users/cham/projects/sb2/sb2dc/data/pub/m9v1short.fits")

#%%
def auto_compress(col, eps=1e-3, reserved=("bjd", "ra", "dec")):
    """
    auto compress int and float type data    

    Parameters
    ----------
    col : astropy.table.Column or astropy.table.MaskedColumn
        the target column

    Returns
    -------
    auto compressed column

    """
    
    for _name in reserved:
        if _name in col.name.lower():
            return col
    
    if col.dtype.kind == "i":
        alm = col.dtype.alignment
        original_dtype = "i{}".format(alm)
        while alm > 1:
            this_dtype = "i{}".format(alm)
            next_dtype = "i{}".format(alm//2)
            if not np.all(col.astype(next_dtype) == col):
                break
            alm //= 2
    elif col.dtype.kind == "f":
        alm = col.dtype.alignment
        original_dtype = "f{}".format(alm)
        while alm > 1:
            this_dtype = "f{}".format(alm)
            next_dtype = "f{}".format(alm//2)
            if np.max(col.astype(next_dtype)) > eps:
                break
            alm //= 2
    else:
        return col
    
    ccol = col.astype(this_dtype)
    print("compressed column *{}* from {} to {}".format(col.name, original_dtype, this_dtype))
    return ccol
    

def modify_column(tbl, colname, name=None, description=None, remove_mask=False, fill_value=None, remove_directly=True, eps=1e-3, reserved=("bjd", "ra", "dec")):
    col = tbl[colname]
    
    if name is None:
        # change name if necessary
        name = col.name
        
    # if dtype is not None:
    #     # change data type if necessary
    #     col = col.astype(dtype)
    # dtype = col.dtype.name
    
    if description is None:
        # change description if necessary
        description = col.description
    
    if remove_directly:
        # remove mask directly
        data = col.data.data
        mcol = table.Column(data, name=name, dtype=dtype, description=description)
        
    elif isinstance(col, table.column.MaskedColumn):
        # for masked column
        data = col.data.data
        mask = col.data.mask
        
        # change dtype if necessary
        if fill_value is None:
            fill_value = col.data.fill_value
        data[mask] = fill_value
        
        if remove_mask:
            # remove mask
            mcol = table.Column(data, name=name, description=description)
        else:
            # keep masked
            mcol = table.MaskedColumn(data, mask=mask, name=name, fill_value=fill_value, description=description)
    else:
        # for normal Column
        data = col.data
        mcol = table.Column(data, name=name, description=description)
    # auto compress
    mcol = auto_compress(mcol, eps=eps, reserved=reserved)
    # replace the column
    tbl.replace_column(colname, mcol)
    return
            

# col = modify_column(m9, "obsid", remove_directly=True)

#%%

def compress_table(tbl, tbl_name="tbl"):
    from copy import deepcopy
    tbl_copy = deepcopy(tbl)

    infolist = []
    for colname in m9.colnames:
        infodict = dict()
        infodict["colname"] = colname
        
        infodict["dtype"] = m9[colname].dtype.str
        infodict["description"] = m9[colname].description
        
        # masked
        ismasked = isinstance(m9[colname], table.column.MaskedColumn)
        if ismasked:
            infodict["masked"] = ismasked
            infodict["n_masked"] = np.sum(m9[colname].mask)
            infodict["fill_value"] = m9[colname].fill_value
        else:
            infodict["masked"] = ismasked
            infodict["n_masked"] = 0
            infodict["fill_value"] = None
        
        infolist.append(infodict)
    tinfo = table.Table(infolist)
    print(tinfo)
    print()

    code = ""
    for i in range(len(tinfo)):
        code += "modify_column({}, ".format(tbl_name)
        code += "colname=\"{}\", ".format(tinfo[i]["colname"])
        code += "name=\"{}\", ".format(tinfo[i]["colname"])
        code += "description=\"\", ".format()
        # code += "dtype=\"{}\", ".format(tinfo[i]["dtype"]) 
        this_kwargs = dict(
            remove_mask=False,
            fill_value=None,
            remove_directly=False,
        )
        for k, v in this_kwargs.items():
            code += "{}={}, ".format(k, v)
        code += ")\n"
    print(code)
    
    return code

code = compress_table(m9, tbl_name="m9")
        
 #%%
modify_column(m9, colname="id", name="id", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="obsid", name="obsid", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="spid", name="spid", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="fiberid", name="fiberid", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="lmjm", name="lmjm", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="planid", name="planid", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="lmjd", name="lmjd", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="ra", name="ra", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="dec", name="dec", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="ra_obs", name="ra_obs", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="dec_obs", name="dec_obs", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="band_B", name="band_B", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="snr_B", name="snr_B", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="band_R", name="band_R", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="snr_R", name="snr_R", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="fibermask", name="fibermask", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="obsdate", name="obsdate", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="GroupID", name="GroupID", description="", remove_mask=False, fill_value=None, remove_directly=False, )
modify_column(m9, colname="GroupSize", name="GroupSize", description="", remove_mask=False, fill_value=None, remove_directly=False, )
#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2017
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#

# A trivial example
import numpy as np
import gzip, shutil

def output(arg:str, kw:str="Universe") -> str:
    return(f"Hello {arg} and {kw}")

def create_array(size:int) -> np.array:
    return np.array(size)

def gunzip(f_in:str, f_out:str) -> None:
    with gzip.open(f_in, 'rb') as f:
        with open(f_out, 'wb') as o:
            shutil.copyfileobj(f, o)
    return None

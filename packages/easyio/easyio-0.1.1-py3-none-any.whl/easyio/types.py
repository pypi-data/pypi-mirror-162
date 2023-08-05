'''
Helper functions that convert strings to other types.

This module contains helper functions that convert string 
values to a variety of types.
'''

# Copyright 2022 Casey Devet
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


def nat (value):
    '''
    Convert to a natural number.
    
    If the value is a natural number, the result will
    be an int object.  If the value has decimals, it
    will be truncated (rounded towards 0).  If the 
    value is not a natural number there will be an
    error.
    '''

    try:
        int_val = int(value)
    except ValueError:
        raise ValueError(f"Invalid natural number: {value}") from None

    if int_val < 1:
        raise ValueError(f"Invalid natural number (must be positive): {int_val}")

    return int_val


def number (value):
    '''
    Convert to a numerical value.

    Whole numbers will be returned as int objects and 
    decimal numbers will be returned as float objects.
    '''

    num = float(value)
    if num.is_integer():
        num = int(num)
    return num


__all__ = [
    "nat",
    "number"
]
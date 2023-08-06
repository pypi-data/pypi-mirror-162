# cABCanalysis
Nested computed ABC analysis (cABC): A method to reduce feature sets to their most relevant items. Implementation in Python.

## Author
Jorn Lotsch
Data Science | Clinical Pharmacology
Goethe - University
Frankfurt am Main
Germany

Alfred Ultsch
DataBionics Research Group
University of Marburg
Marburg
Germany

## Abstract
The **cABCanalysis** package is a Python package that provides a method for categorizing items or inventories, with the aim to reduce feature sets to the most important elements.

## Requirements
* numpy >= 1.19.2
* pandas >= 1.1.5
* seaborn >= 0.11.2
* scipy >= 1.7.3

## Reference
Publication in progress.

## Tutorial
The cABC analysis can be run with “ cABCanalysis(data, PlotIt=False, ax=None)”, where the data should be a one-dimensional numerical data set, “PlotIt” is self-explaining, and “ax” allows the inclusion of the resulting ABC plot as a subplot in a “seaborn” multipanel figure. The function returns a Python dictionary containing the following elements. "Aind", "Bind" and "Cind" are the data items assigned to the respective ABC subsets, "ABexchanged" (True/False) indicates whether in special cases the slope of the ABC curve has already reached the value of one before passing the point closest to the ideal "Pareto" point, which would be counterintuitive for the classification and is therefore corrected by exchanging points A and B, about which the user is informed. Other numbers returned include points "A" (Ax,Ay), i.e., the “Juran” or "BreakEven" point indicated by "ABexchanged", "B" (Bx,By), i.e., the "Juran" or "BreakEven" point indicated by "ABexchanged", and "C", a point at minimum distance from [Ax,1]. Also, "smallestAData" returns the AB limit defined by the point A or B with "ABexchanged", "smallestBData" returns the BC limit defined by the point C, "AlimitIndInInterpolation" returns the index of the AB limit in [p, ABC], the interpolation of the ABC curve, and "BlimitIndInInterpolation" is the index of the BC limit in [p, ABC], the interpolation of the ABC curve.

ABCres = cABCanalysis(data=data) ABCres["Aind"].index.tolist()
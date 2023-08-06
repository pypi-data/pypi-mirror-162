#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 17 11:22:35 2022

@author: joern
"""
# %% imports

from pandas.api.types import is_numeric_dtype
import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.interpolate import CubicSpline
from scipy.spatial import distance


def ABC_clean_data(data):

    # Create pandas dataframe with variable names and input values
    if isinstance(data, list):
        data = np.array(data)

    if not is_numeric_dtype(data):
        raise Warning("Data is not numeric")
        return

    dfItems = pd.DataFrame(data)
    dfItems.columns = ["value"]
    dfItems.replace([np.inf, -np.inf], np.nan, inplace=True)
    dfItems = dfItems[dfItems > 0]
    dfItems = dfItems.dropna()

    if len(dfItems) != len(data):
        print(str(len(dfItems)) + "rows of " + str(len(data)) +
              "items are positive and beeing used for further calculations.")

    return dfItems


def ABC_curve(CleanedData):

    # Create pandas dataframe with fitted ABC curve and local slopes

    CleanedData_sorted = CleanedData.sort_values(
        by="value", ascending=False, inplace=False)

    Contrib = CleanedData_sorted["value"].array
    y = np.cumsum(Contrib)
    y = y/y[-1]
    y = y[~np.isinf(y)]
    x = np.arange(1, len(y)+1)/len(y)
    if np.min(y) > 0:
        y = np.insert(y, 0, 0, axis=0)
        x = np.insert(x, 0, 0, axis=0)
    if np.max(y) < 1:
        y = np.append(y, 1)
        x = np.append(x, 1)

    f = CubicSpline(x, y)
    Effort = np.linspace(0, 1, num=100, endpoint=True)
    Yield = f(Effort)
    if max(Yield) > 1:
        inds = np.where(Yield > 1)[0].tolist()[0]
        if inds < len(Yield):
            Yield[inds:len(Yield)] = 1
    f = CubicSpline(Effort, Yield)
    dABC = f(Effort, 1)

    return pd.DataFrame({"effort": Effort, "yield": Yield, "dABC": dABC}, columns=["effort", "yield", "dABC"])


def ABC_calc(CleanedData, ABCcurveData):

    # Calculate set limits
    CleanedData_sorted = CleanedData.sort_values(
        by="value", ascending=False, inplace=False)

    curve = ABCcurveData[["effort", "yield"]]
    point = [[0.0, 1.0]]
    distPareto = distance.cdist(curve.to_numpy(), point, "euclidean")
    ParetoPointInd = np.where(distPareto == distPareto.min())[0].tolist()[0]
    ParetoPoint = curve.iloc[[ParetoPointInd]]
    ableitung = ABCcurveData["dABC"]
    ableitung = abs(ABCcurveData["dABC"] - 1)
    breakEvenInd = np.where(ableitung == ableitung.min())[0].tolist()[0]
    breakEvenPoint = curve.iloc[[breakEvenInd]]

    if curve["effort"][breakEvenInd] < curve["effort"][ParetoPointInd]:
        ABexchanged = True
        JurenInd = breakEvenInd
        Bx = curve["effort"][ParetoPointInd]
        A, B = breakEvenPoint, ParetoPoint
    else:
        ABexchanged = False
        JurenInd = ParetoPointInd
        Bx = curve["effort"][breakEvenInd]
        A, B = ParetoPoint, breakEvenPoint

    Juren = [[Bx, 1.0]]
    distBx = distance.cdist(curve.to_numpy(), Juren, "euclidean")

    B_limit = np.where(distBx == distBx.min())[0].tolist()[0]
    C = curve.iloc[[B_limit]]

    f = CubicSpline(np.linspace(1, 100, num=len(
        CleanedData_sorted["value"]), endpoint=True), CleanedData_sorted["value"])
    interpolatedInverseEcdf = f(np.linspace(1, 100, num=1000, endpoint=True))
    ABlimit = interpolatedInverseEcdf[round(
        A.values.tolist()[0][0] * 1000) + 1]
    BClimit = interpolatedInverseEcdf[round(
        C.values.tolist()[0][0] * 1000) + 1]

    Aind = CleanedData.loc[CleanedData['value'] > ABlimit]
    Bind = CleanedData.loc[CleanedData['value'].between(BClimit, ABlimit)]
    Cind = CleanedData.loc[CleanedData['value'] < BClimit]

    smallestAData = curve["yield"][JurenInd]
    smallestBData = curve["yield"][B_limit]

    return {"Aind": Aind, "Bind": Bind, "Cind": Cind, "ABexchanged": ABexchanged,
            "A": A, "B": B, "C": C, "smallestAData": smallestAData,
            "smallestBData": smallestBData, "AlimitIndInInterpolation": JurenInd,
            "BlimitIndInInterpolation": B_limit, "p": curve["effort"], "ABC": curve["yield"],
            "ABlimit": ABlimit, "BClimit": BClimit}


def ABC_plot(cABCresults, CleanedData, ax=None):
    CleanedData_sorted = CleanedData.sort_values(
        by="value", ascending=False, inplace=False)

    Contrib = CleanedData_sorted["value"].array
    y = np.cumsum(Contrib)
    y = y/y[-1]
    y = y[~np.isinf(y)]
    x = np.arange(1, len(y)+1)/len(y)
    pIdent = np.linspace(0, 1, 100)
    A = CleanedData_sorted["value"].min()
    MaxX = CleanedData_sorted["value"].max()
    if A == MaxX:
        A = 0
        MaxX = 1
    B = MaxX - A
    ABCuniform = (-0.5 * B * pIdent**2 + MaxX * pIdent)/(A + 0.5 * B)

    ax = ax or plt.gca()
    sns.scatterplot(ax=ax, x=x, y=y, color="none", edgecolor="blue")
    sns.lineplot(ax=ax, x=cABCresults["p"],
                 y=cABCresults["ABC"], color="dodgerblue", label="ABC")
    sns.lineplot(ax=ax, x=[cABCresults["A"].values.tolist()[0][0], cABCresults["A"].values.tolist()[0][0]],
                 y=[0, cABCresults["A"].values.tolist()[0][1]], color="salmon", linewidth=2)
    sns.lineplot(ax=ax, x=[0, cABCresults["A"].values.tolist()[0][0]],
                 y=[cABCresults["A"].values.tolist()[0][1], cABCresults["A"].values.tolist()[0][1]], color="salmon", linewidth=2)
    sns.lineplot(ax=ax, x=[cABCresults["C"].values.tolist()[0][0], cABCresults["C"].values.tolist()[0][0]],
                 y=[0, cABCresults["C"].values.tolist()[0][1]], color="salmon", linewidth=2)
    sns.lineplot(ax=ax, x=[0, cABCresults["C"].values.tolist()[0][0]],
                 y=[cABCresults["C"].values.tolist()[0][1], cABCresults["C"].values.tolist()[0][1]], color="salmon", linewidth=2)
    sns.lineplot(ax=ax, x=pIdent, y=pIdent, color="magenta",
                 linestyle="dashed", label="Identity")
    sns.lineplot(ax=ax, x=pIdent, y=ABCuniform,
                 color="green", linestyle="dotted", label="Uniform")
    ax.text(0.5 * cABCresults["A"].values.tolist()[0][0], .1,
            "Set A:\nn = " + str(len(cABCresults["Aind"])),
            ha='center', size='large', color='blue', weight='bold')
    ax.text(0.5 * (cABCresults["C"].values.tolist()[0][0] + cABCresults["A"].values.tolist()[0][0]), .1,
            "Set B:\nn = " + str(len(cABCresults["Bind"])),
            ha='center', size='medium', weight='semibold')
    ax.text(0.5 * (1 + cABCresults["C"].values.tolist()[0][0]), .1,
            "Set C:\nn = " + str(len(cABCresults["Cind"])),
            ha='center', size='medium', weight='semibold')

    return


def  cABCanalysis(data, PlotIt=False, ax=None):
    cABCresults = None
    CleanedData = ABC_clean_data(data)
    if CleanedData.shape[0] > 0:
        ABCcurveData = ABC_curve(CleanedData=CleanedData)
        cABCresults = ABC_calc(CleanedData=CleanedData,
                              ABCcurveData=ABCcurveData)
        if PlotIt:
            if ax == None:
                fig, ax = plt.subplots(figsize=(10, 10))
            ABC_plot(cABCresults=cABCresults, CleanedData=CleanedData, ax=ax)

    return cABCresults

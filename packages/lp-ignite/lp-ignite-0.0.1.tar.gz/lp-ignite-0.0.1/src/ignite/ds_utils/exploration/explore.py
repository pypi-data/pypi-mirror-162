import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from sklearn.model_selection import train_test_split
import warnings
from scipy.stats import norm
from typing import Optional, Union, Callable, List
import numpy
import pandas
import seaborn
from matplotlib import axes, pyplot, dates, ticker
from scipy.cluster import hierarchy



def _print_header(var, target):
    print(f"{var} vs {target}")
    print("-------------------------------")


def explore_bivariate_categorical(target, cat_vars, train):
    """
    Takes in a target and plots it against categorial variables. Outputs boxplots and barplots and gives the mean of the target
    by each categorical variable.
    """
    for var in cat_vars:
        _print_header(var, target)

        sns.boxplot(x=var, y=target, data=train)
        plt.show()

        print()

        sns.barplot(x=var, y=target, data=train)
        plt.show()
        
        print("-------------------------------")
        print(f"Mean {target} by {var}:  ")
        print(train.groupby(var)[target].mean())
        print()

def _freq_table(train, cat_var):
    '''
    for a given categorical variable, compute the frequency count and percent split
    and return a dataframe of those values along with the different classes. 
    '''
    class_labels = list(train[cat_var].unique())

    frequency_table = (
        pd.DataFrame({cat_var: class_labels,
                      'Count': train[cat_var].value_counts(normalize=False), 
                      'Percent': round(train[cat_var].value_counts(normalize=True)*100,2)}
                    )
    )
    return frequency_table


def _explore_univariate_categorical(train, cat_var):
    '''
    takes in a dataframe and a categorical variable and returns
    a frequency table and barplot of the frequencies. 
    '''
    frequency_table = _freq_table(train, cat_var)
    plt.figure(figsize=(2,2))
    sns.barplot(x=cat_var, y='Count', data=frequency_table, color='lightseagreen')
    plt.title(cat_var)
    plt.show()
    print(frequency_table)

def explore_univariate(train, cat_vars, quant_vars):
    for var in cat_vars:
        _explore_univariate_categorical(train, var)
        print('_________________________________________________________________')
    for col in quant_vars:
        p, descriptive_stats = _explore_univariate_quant(train, col)
        plt.show(p)
        print(descriptive_stats)

def _explore_univariate_quant(train, quant_var):
    '''
    takes in a dataframe and a quantitative variable and returns
    descriptive stats table, histogram, and boxplot of the distributions. 
    '''
    descriptive_stats = train[quant_var].describe()
    plt.figure(figsize=(8,2))

    p = plt.subplot(1, 2, 1)
    p = plt.hist(train[quant_var], color='lightseagreen')
    p = plt.title(quant_var)

    # second plot: box plot
    p = plt.subplot(1, 2, 2)
    p = plt.boxplot(train[quant_var])
    p = plt.title(quant_var)
    return p, descriptive_stats
    

def visualize_feature(series: pandas.Series, remove_na: bool = False, *, ax: Optional[axes.Axes] = None,
                      **kwargs) -> axes.Axes:
    """
    Visualize a feature series:
    * If the feature is float then the method plots the distribution plot.
    * If the feature is datetime then the method plots a line plot of progression of amount thought time.
    * If the feature is object, categorical, boolean or integer then the method plots count plot (histogram).
    :param series: the data series.
    :param remove_na: True to ignore NA values when plotting; False otherwise.
    :param ax: Axes in which to draw the plot, otherwise use the currently-active Axes.
    :param kwargs: other keyword arguments
                   All other keyword arguments are passed to ``matplotlib.axes.Axes.pcolormesh()``.
    :return: Returns the Axes object with the plot drawn onto it.
    """
    if ax is None:
        pyplot.figure()
        ax = pyplot.gca()

    if remove_na:
        feature_series = series.dropna()
    else:
        feature_series = series

    if str(feature_series.dtype).startswith("float"):
        seaborn.histplot(feature_series, ax=ax, kde=True, **kwargs)
        labels = ax.get_xticks()
    elif str(feature_series.dtype).startswith("datetime"):
        feature_series.value_counts().plot(kind="line", ax=ax, **kwargs)
        labels = ax.get_xticks()
    else:
        seaborn.countplot(x=_copy_series_or_keep_top_10(feature_series), ax=ax, **kwargs)
        labels = ax.get_xticklabels()

    if not ax.get_title():
        ax.set_title(f"{feature_series.name} ({feature_series.dtype})")
        ax.set_xlabel("")

    ticks_loc = ax.get_xticks().tolist()
    ax.xaxis.set_major_locator(ticker.FixedLocator(ticks_loc))
    ax.set_xticklabels(labels, rotation=45, horizontalalignment='right')

    if str(feature_series.dtype).startswith("datetime"):
        ax.xaxis.set_major_formatter(_convert_numbers_to_dates)

    return ax
    

def get_correlated_features(data_frame: pandas.DataFrame, features: List[str], target_feature: str,
                            threshold: float = 0.95, method: Union[str, Callable] = 'pearson',
                            min_periods: Optional[int] = 1) -> pandas.DataFrame:
    """
    Calculate which features correlated above a threshold and extract a data frame with the correlations and correlation
    to the target feature.
    :param data_frame: the data frame.
    :param features: list of features names.
    :param target_feature: name of target feature.
    :param threshold: the threshold (default 0.95).
    :param method: {‘pearson’, ‘kendall’, ‘spearman’} or callable
                   Method of correlation:
                   * pearson : standard correlation coefficient
                   * kendall : Kendall Tau correlation coefficient
                   * spearman : Spearman rank correlation
                   * callable: callable with input two 1d ndarrays and returning a float. Note that the returned matrix from corr will have 1 along the diagonals and will be symmetric regardless of the callable’s behavior.
    :param min_periods: Minimum number of observations required per pair of columns to have a valid result. Currently only available for Pearson and Spearman correlation.
    :return: data frame with the correlations and correlation to the target feature.
    """
    correlations = _calc_corrections(data_frame[features + [target_feature]], method, min_periods)
    target_corr = correlations[target_feature].transpose()
    features_corr = correlations.loc[features, features]
    corr_matrix = features_corr.where(numpy.triu(numpy.ones(features_corr.shape), k=1).astype(numpy.bool_))
    corr_matrix = corr_matrix[(~numpy.isnan(corr_matrix))].stack().reset_index()
    corr_matrix = corr_matrix[corr_matrix[0].abs() >= threshold]
    if corr_matrix.shape[0] > 0:
        corr_matrix["level_0_target_corr"] = target_corr[corr_matrix["level_0"]].values.tolist()[0]
        corr_matrix["level_1_target_corr"] = target_corr[corr_matrix["level_1"]].values.tolist()[0]
        corr_matrix = corr_matrix.rename({0: "level_0_level_1_corr"}, axis=1).reset_index(drop=True)
        return corr_matrix
    else:
        warnings.warn(f"Correlation threshold {threshold} was too high. An empty frame was returned", UserWarning)
        return pandas.DataFrame(
            columns=['level_0', 'level_1', 'level_0_level_1_corr', 'level_0_target_corr', 'level_1_target_corr'])


def visualize_correlations(data: pandas.DataFrame, method: Union[str, Callable] = 'pearson',
                           min_periods: Optional[int] = 1, *, ax: Optional[axes.Axes] = None,
                           **kwargs) -> axes.Axes:
    """
    Compute pairwise correlation of columns, excluding NA/null values, and visualize it with heat map.
    `Original code <https://seaborn.pydata.org/examples/many_pairwise_correlations.html>`_
    :param data: the data frame, were each feature is a column.
    :param method: {‘pearson’, ‘kendall’, ‘spearman’} or callable
                   Method of correlation:
                   * pearson : standard correlation coefficient
                   * kendall : Kendall Tau correlation coefficient
                   * spearman : Spearman rank correlation
                   * callable: callable with input two 1d ndarrays and returning a float. Note that the returned matrix from corr will have 1 along the diagonals and will be symmetric regardless of the callable’s behavior.
    :param min_periods: Minimum number of observations required per pair of columns to have a valid result. Currently only available for Pearson and Spearman correlation.
    :param ax: Axes in which to draw the plot, otherwise use the currently-active Axes.
    :param kwargs: other keyword arguments
                   All other keyword arguments are passed to ``matplotlib.axes.Axes.pcolormesh()``.
    :return: Returns the Axes object with the plot drawn onto it.
    """
    if ax is None:
        pyplot.figure()
        ax = pyplot.gca()

    corr = _calc_corrections(data, method, min_periods)
    mask = numpy.triu(numpy.ones_like(corr, dtype=numpy.bool_))
    seaborn.heatmap(corr, mask=mask, annot=True, fmt=".3f", ax=ax, **kwargs)
    return 


def plot_correlation_dendrogram(data: pandas.DataFrame, correlation_method: Union[str, Callable] = 'pearson',
                                min_periods: Optional[int] = 1,
                                cluster_distance_method: Union[str, Callable] = "average", *,
                                ax: Optional[axes.Axes] = None,
                                **kwargs) -> axes.Axes:
    """
    Plot dendrogram of a correlation matrix. This consists of a chart that that shows hierarchically the variables that
    are most correlated by the connecting trees. The closer to the right that the connection is, the more correlated the features are.
    :param data: the data frame, were each feature is a column.
    :param correlation_method: {‘pearson’, ‘kendall’, ‘spearman’} or callable
                   Method of correlation:
                   * pearson : standard correlation coefficient
                   * kendall : Kendall Tau correlation coefficient
                   * spearman : Spearman rank correlation
                   * callable: callable with input two 1d ndarrays and returning a float. Note that the returned matrix from corr will have 1 along the diagonals and will be symmetric regardless of the callable’s behavior.
    :param min_periods: Minimum number of observations required per pair of columns to have a valid result. Currently only available for Pearson and Spearman correlation.
    :param cluster_distance_method: The following are methods for calculating the distance between the newly formed cluster.
            Methods of linkage:
            * single: This is also known as the Nearest Point Algorithm.
            * complete: This is also known by the Farthest Point Algorithm or Voor Hees Algorithm.
            * average:
            .. math:: d(u,v) = \\sum_{ij} \\frac{d(u[i], v[j])}{(|u|*|v|)}
            This is also called the UPGMA algorithm.
            * weighted:
            .. math:: d(u,v) = (dist(s,v) + dist(t,v))/2
            where cluster u was formed with cluster s and t and v
            is a remaining cluster in the forest. (also called WPGMA)
            * centroid: Euclidean distance between the centroids
            * median: This is also known as the WPGMC algorithm.
            * ward: uses the Ward variance minimization algorithm.
            see `scipy.cluster.hierarchy.linkage <https://docs.scipy.org/doc/scipy/reference/generated/scipy.cluster.hierarchy.linkage.html>`_ for more information.
    :param ax: Axes in which to draw the plot, otherwise use the currently-active Axes.
    :param kwargs: other keyword arguments
                   All other keyword arguments are passed to ``matplotlib.axes.Axes.pcolormesh()``.
    :return: Returns the Axes object with the plot drawn onto it.
    """

    if ax is None:
        pyplot.figure()
        ax = pyplot.gca()

    corr = _calc_corrections(data, correlation_method, min_periods)
    # reverse the distance
    corr_condensed = hierarchy.distance.squareform(1 - corr)
    z = hierarchy.linkage(corr_condensed, method=cluster_distance_method)
    ax.set(**kwargs)
    hierarchy.dendrogram(z, labels=numpy.asarray(data.columns.tolist()), orientation="left", ax=ax)
    return ax

def _calc_corrections(data, method, min_periods):
    return data.apply(lambda x: x.factorize()[0]).corr(method=method, min_periods=min_periods)


def plot_features_interaction(feature_1: str, feature_2: str, data: pandas.DataFrame, *,
                              ax: Optional[axes.Axes] = None, **kwargs) -> axes.Axes:
    """
    Plots the joint distribution between two features:
    * If both features are either categorical, boolean or object then the method plots the shared histogram.
    * If one feature is either categorical, boolean or object and the other is numeric then the method plots a boxplot chart.
    * If one feature is datetime and the other is numeric or datetime then the method plots a line plot graph.
    * If one feature is datetime and the other is either categorical, boolean or object the method plots a violin plot (combination of boxplot and kernel density estimate).
    * If both features are numeric then the method plots scatter graph.
    :param feature_1: the name of the first feature.
    :param feature_2: the name of the second feature.
    :param data: the data frame, were each feature is a column.
    :param ax: Axes in which to draw the plot, otherwise use the currently-active Axes.
    :param kwargs: other keyword arguments
                   All other keyword arguments are passed to ``matplotlib.axes.Axes.pcolormesh()``.
    :return: Returns the Axes object with the plot drawn onto it.
    """
    if ax is None:
        pyplot.figure()
        ax = pyplot.gca()

    dup_df = pandas.DataFrame()
    if str(data[feature_1].dtype) in ["object", "category", "bool"]:
        dup_df[feature_1] = _copy_series_or_keep_top_10(data[feature_1])
        if str(data[feature_2].dtype) in ["object", "category", "bool"]:
            # both features are categorical
            dup_df[feature_2] = _copy_series_or_keep_top_10(data[feature_2])
            group_feature_1 = dup_df[feature_1].unique().tolist()
            ax.hist([dup_df.loc[dup_df[feature_1] == value, feature_2] for value in group_feature_1],
                    label=group_feature_1, **kwargs)
            ax.set_xlabel(feature_1)
            ax.legend(title=feature_2)
        elif str(data[feature_2].dtype).startswith("datetime"):
            # first feature is categorical and the second is datetime
            dup_df[feature_2] = data[feature_2].apply(dates.date2num)
            chart = seaborn.violinplot(x=feature_2, y=feature_1, data=dup_df, ax=ax)
            ticks_loc = chart.get_xticks().tolist()
            chart.xaxis.set_major_locator(ticker.FixedLocator(ticks_loc))
            chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
            ax.xaxis.set_major_formatter(_convert_numbers_to_dates)
        else:
            # first feature is categorical and the second is numeric
            dup_df[feature_2] = data[feature_2]
            chart = seaborn.boxplot(x=feature_1, y=feature_2, data=dup_df, ax=ax, **kwargs)
            chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
    elif str(data[feature_1].dtype).startswith("datetime"):
        if str(data[feature_2].dtype) in ["object", "category", "bool"]:
            # first feature is datetime and the second is categorical
            dup_df[feature_1] = data[feature_1].apply(dates.date2num)
            dup_df[feature_2] = _copy_series_or_keep_top_10(data[feature_2])
            chart = seaborn.violinplot(x=feature_1, y=feature_2, data=dup_df, ax=ax)
            ticks_loc = chart.get_xticks().tolist()
            chart.xaxis.set_major_locator(ticker.FixedLocator(ticks_loc))
            chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
            ax.xaxis.set_major_formatter(_convert_numbers_to_dates)
        else:
            # first feature is datetime and the second is numeric or datetime
            ax.plot(data[feature_1], data[feature_2], **kwargs)
            ax.set_xlabel(feature_1)
            ax.set_ylabel(feature_2)
    elif str(data[feature_2].dtype) in ["object", "category", "bool"]:
        # first feature is numeric and the second is categorical
        dup_df[feature_2] = _copy_series_or_keep_top_10(data[feature_2])
        dup_df[feature_1] = data[feature_1]
        chart = seaborn.boxplot(x=feature_2, y=feature_1, data=dup_df, ax=ax, **kwargs)
        chart.set_xticklabels(chart.get_xticklabels(), rotation=45, horizontalalignment='right')
    elif str(data[feature_2].dtype).startswith("datetime"):
        # first feature is numeric and the second is datetime
        ax.plot(data[feature_2], data[feature_1], **kwargs)
        ax.set_xlabel(feature_2)
        ax.set_ylabel(feature_1)
    else:
        # both features are numeric
        ax.scatter(data[feature_1], data[feature_2], **kwargs)
        ax.set_xlabel(feature_1)
        ax.set_ylabel(feature_2)

    return ax
    
def _copy_series_or_keep_top_10(series: pandas.Series) -> pandas.Series:
    if str(series.dtype) == "bool":
        # avoiding RuntimeWarning from numpy (Converting input from bool to <class 'numpy.uint8'> for compatibility.)
        return series.apply(lambda val: "True" if val else "False")
    if len(series.unique().tolist()) > 10:
        top10 = series.value_counts()[:10].index.tolist()
        return series.apply(lambda val: val if val in top10 else "Other values")
    return series


@pyplot.FuncFormatter
def _convert_numbers_to_dates(x, pos):
    return dates.num2date(x).strftime('%Y-%m-%d %H:%M')


def missing_data_stats(data:pandas.DataFrame):
    """Check remaining missing value and print out if any.
    Arguments:
        data (pd.DataFrame): The dataframe need to check
    Returns:
        The missing dataframe
    Usage:
        from data_science_utilities import data_science_utilities
        # make statistic
        missing_data = data_science_utilities.missing_data_stats(df)
        # display missing data
        missing_data
    """
    nan_df = (data.isnull().sum() / len(data)) * 100
    nan_df = nan_df.drop(nan_df[nan_df == 0].index).sort_values(ascending=False)
    missing_data = pd.DataFrame({'Missing Ratio': nan_df})

    return missing_data


def plot_corelation_matrix(data:pandas.DataFrame):
    """
    Plotting the co-relation matrix on the dataset
    using the numeric columns only.
    """
    corr = data.select_dtypes(include=['float64', 'int64']).iloc[:, 1:].corr()

    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(22, 22))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    sns.heatmap(
        corr, mask=mask, cmap=cmap, center=0.0,
        vmax=1, square=True, linewidths=.5, ax=ax
    )

    return corr

def plot_dist_norm(dist, title):
    """Plotting normal distribution.
    Args:
        dist (pd.DataFrame): The distribution dataframe
        title (str): The title of chart
    Usage:
        from src.visualization.visualize import plot_dist_norm
    """
    sns.distplot(dist, fit=norm)
    (mu, sigma) = norm.fit(dist)
    plt.legend(['Normal dist. ($\mu=$ {:.2f} and $\sigma=$ {:.2f} )'.format(mu, sigma)], loc='best')
    plt.ylabel('Frequency')
    plt.title(title)
    plt.figure()
    stats.probplot(dist, plot=plt)
    plt.show()


def plot_top_corelation_matrix(data: pandas.DataFrame, target, k=10, cmap='YlGnBu'):
    """
    Plotting top k features with highest co-relation matrix.
    """
    corr = data.select_dtypes(include=['float64', 'int64']).iloc[:, 1:].corr()
    cols = corr.nlargest(k, target)

    # Drop columns that not in the top co-relation.
    excludes = corr.index.map(lambda x: x if x not in cols.index else None)
    excludes = excludes.dropna()

    cols_index = cols[target].index
    cols.drop(excludes, axis=1, inplace=True)

    # Generate a mask for the upper triangle
    mask = np.zeros_like(cols, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(11, 11))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    sns.heatmap(
        cols, mask=mask, cmap=cmap, center=0.0,
        vmax=1, square=True, linewidths=.5, ax=ax,
        yticklabels=cols_index.values, xticklabels=cols_index.values,
    )

    return cols_index
    
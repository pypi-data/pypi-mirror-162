import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from statsmodels.formula.api import ols
from sklearn.metrics import mean_squared_error, classification_report, accuracy_score
from math import sqrt 


def _compare_sum_squared_errors(model_sse2, baseline_sse2):
    delta = model_sse2 - baseline_sse2
    
    if (model_sse2 < baseline_sse2):
        print(f"The MODEL performs better than the baseline with an SSE value of {model_sse2} and delta of {delta}")
        return True
    else:
        print(f"The BASELINE performs better than the model with an SSE value of {baseline_sse2} and delta of {delta}")
        return False


def plot_residuals(y, yhat):
    sns.scatterplot(x=y, y=yhat - y)
    plt.title("Residuals")
    plt.ylabel("yhat - y")
    plt.show()
    
def plot_residuals_against_x(x, y, yhat, df):
    sns.scatterplot(x=x, y=(yhat - y), data=df)
    plt.title("Residuals")
    plt.ylabel("yhat - y")
    plt.show()

def regression_errors(y, yhat):
    sse2 = mean_squared_error(y, yhat) * len(y)
    ess = sum((yhat - y.mean()) ** 2)
    tss = ess + sse2
    mse = mean_squared_error(y, yhat)
    rmse = sqrt(mse)
    
    return sse2, ess, tss, mse, 


def baseline_mean_errors(y):
    index = []
    
    for i in range(1, len(y) + 1):
        index.append(i)
        
    y_mean = pd.Series(y.mean(), index=index)

    sse2_baseline = mean_squared_error(y, y_mean) * len(y)
    mse_baseline = mean_squared_error(y, y_mean)
    rmse_baseline = sqrt(mse_baseline)
    
    return sse2_baseline, mse_baseline, 


def better_than_baseline(y, yhat):
    sse2, ess, tss, mse, rmse = regression_errors(y, yhat)
    sse2_baseline, mse_baseline, rmse_baseline = baseline_mean_errors(y)
    
    model_errors = {'sse' : sse2, 'ess' : ess, 'tss' : tss, 'mse' : mse, 'rmse' : rmse}
    baseline_errors = {'sse' : sse2_baseline, 'mse' : mse_baseline, 'rmse' : rmse_baseline}

    _print_comparison(model_errors, baseline_errors)
    
    return _compare_sum_squared_errors(sse2, sse2_baseline)


def model_signficance(ols_model):
    r2 = ols_model.rsquared
    p_value = ols_model.f_pvalue
    alpha = .05

    print(f"variance:  {r2}, p:  {p_value}, a: {alpha},  signficant:  {p_value < alpha}")
    return r2, p_value, p_value < alpha


def _print_comparison(model_errors, baseline_errors):
    print("----------------------------------------------")
    print(pd.DataFrame(index=model_errors.keys(), columns=["model"], data=model_errors.values()))
    print("----------------------------------------------")
    print(pd.DataFrame(index=baseline_errors.keys(), columns=["baseline"], data=baseline_errors.values()))
    print("----------------------------------------------")


def print_model_evaluation(sample_df, prediction_key):
    print('Accuracy: {:.2%}'.format(accuracy_score(sample_df.actual, sample_df[prediction_key])))
    print('---')
    print('Confusion Matrix')
    print(pd.crosstab(sample_df[prediction_key], sample_df.actual))
    print('---')
    print(classification_report(sample_df.actual, sample_df[prediction_key]))


def mape(y_true, y_pred):
    """"
    Calculates the mape

    Args:
        y_true: An array with the realized y values
        y_pred: An array with the predicted y values by the model

    Returns:
        Mape
    """
    import numpy as np

    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


def overall_error(y_true, y_pred):
    """
    Calculates the overall error

    Args:
        y_true: An array with the realized y values
        y_pred: An array with the predicted y values by the model

    Returns:
        Overall error
    """ 
    import numpy as np

    length = len(y_true)
    y_true, y_pred = sum(np.array(y_true)), sum(np.array(y_pred))
    return (y_pred - y_true) / length


def overall_error_percentage(y_true, y_pred): 
    """
    Calculates the overal error as a percentage

    Args:
        y_true: An array with the realized y values
        y_pred: An array with the predicted y values by the model

    Returns:
        Overal error percentage
    """
    import numpy as np

    y_true, y_pred = sum(np.array(y_true)), sum(np.array(y_pred))
    return ((y_pred - y_true) / y_true) * 100


def evaluate_per_intersection_bounds(data, y_test, y_pred_test, intersection=[], only_top_X=0):
    """
    Evaluates a model per intersection on the test set including upper and lower bounds from bootstrapping.

    Args:
        data: A dataframe containing the X_test values
        y_test: series/array containing the dependent variable and data used in the test set
        y_pred_test: predictions by the model made on the test set data
        intersection: a list of intersections the evalution should be split on
        only_top_X: only the top x amount of rows that should be returned in the table, ordered by descending count. 0 returns all rows.

    Returns:
        Dataframe containing the evaluation per intersection
    """
    import pandas as pd
    from tabulate import tabulate

    # hp.print_title('Model Evaluation per Intersection: ' + ' / '.join(intersection))

    # Join the data as a start for the evaluation
    results = pd.DataFrame()
    results['real_value'] = y_test
    results['pred_value'] = y_pred_test
    
    data = results.merge(data, left_index=True, right_index=True)
    
    # Create intersection column to deal with multiple intersections
    data['intersection'] = data[intersection].astype(str).apply(lambda x: ' / '.join(x), axis=1)

    # Create output dataframe
    df = pd.DataFrame(columns=['intersection', 'avg_real', 'avg_pred', 'overall_error', 'mape', 'count', 'avg_catalog', 'lower_bound', 'upper_bound', 'bandwidth', 'bandwidth_%_catalog'])
    
    index = 1

    row = pd.DataFrame(columns=['intersection', 'avg_real', 'avg_pred', 'overall_error', 'mape', 'count', 'avg_catalog', 'lower_bound', 'upper_bound', 'bandwidth', 'bandwidth_%_catalog'], index=[index])

    # Create totals
    row['intersection'] = 'Total'
    row['avg_real'] = int(round(data['real_value'].mean(), 0))
    row['avg_pred'] = int(round(data['pred_value'].mean(), 0))
    row['overall_error'] = int(round(row['avg_real'] - row['avg_pred'], 0))
    row['mape'] = round(mape(data['real_value'], data['pred_value']), 2)
    row['count'] = data['real_value'].count()
    row['avg_catalog'] = int(round(data['catalog_price_car_options'].mean(), 0))
    row['lower_bound'] = int(round(data['quantile_10%'].mean(), 0))
    row['upper_bound'] = int(round(data['quantile_90%'].mean(), 0))
    row['bandwidth'] = row['upper_bound'] - row['lower_bound']
    row['bandwidth_%_catalog'] = round(row['bandwidth'] / row['avg_catalog'] * 100, 2)

    df = df.append(row, sort=False)

    for value in data['intersection'].unique():

        index += 1

        data_sub = data[data['intersection'] == value]

        row = pd.DataFrame(columns=['intersection', 'avg_real', 'avg_pred', 'overall_error', 'mape', 'count', 'avg_catalog', 'lower_bound', 'upper_bound', 'bandwidth', 'bandwidth_%_catalog'], index=[index])

        row['intersection'] = value
        row['avg_real'] = int(round(data_sub['real_value'].mean(), 0))
        row['avg_pred'] = int(round(data_sub['pred_value'].mean()))
        row['overall_error'] = int(round(row['avg_real'] - row['avg_pred'], 0))
        row['mape'] = round(mape(data_sub['real_value'], data_sub['pred_value']), 2)
        row['count'] = data_sub['real_value'].count()
        row['avg_catalog'] = int(round(data_sub['catalog_price_car_options'].mean(), 0))
        row['lower_bound'] = int(round(data_sub['quantile_10%'].mean(), 0))
        row['upper_bound'] = int(round(data_sub['quantile_90%'].mean(), 0))
        row['bandwidth'] = row['upper_bound'] - row['lower_bound']
        row['bandwidth_%_catalog'] = round(row['bandwidth'] / row['avg_catalog'] * 100, 2)

        df = df.append(row, sort=False)

    df.sort_values(by='count', axis=0, ascending=False, inplace=True)

    # Rename intersection column to chosen intersections
    df.rename(columns={'intersection': ' / '.join(intersection)}, inplace=True)

    # Only return top X rows
    if only_top_X > 0:
        df = df.head(only_top_X + 1)

    # Do not print the index
    blankIndex=[''] * len(df)
    df.index=blankIndex

    print(tabulate(df, headers='keys', tablefmt='psql'))

    return df


def mean_absolute_error(y_true, y_pred):
    """"
    Calculates the MAE

    Args:
        y_true: An array with the realized y values
        y_pred: An array with the predicted y values by the model

    Returns:
        MAE
    """
    import numpy as np

    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs(y_true - y_pred))

def r2_score(y_true, y_pred):
    """"
    Calculates the R2

    Args:
        y_true: An array with the realized y values
        y_pred: An array with the predicted y values by the model
        sample_weight : array-like of shape = (n_samples), optional sample weights.
        multioutput : string in ['raw_values', 'uniform_average', 
        \'variance_weighted'] or None or array-like of shape (n_outputs)

    Returns:
        R2
    """
    import numpy as np

    y_true, y_pred = np.array(y_true), np.array(y_pred)

    numerator = sum((y_true - y_pred) ** 2)
    denominator = sum((y_true - np.average(y_true, axis=0)) ** 2)
    R2 = 1 - (numerator / denominator)
    return R2

def mean_squared_error(y_true, y_pred):
    """"
    Calculates the MSE

    Args:
        y_true: An array with the realized y values
        y_pred: An array with the predicted y values by the model

    Returns:
        MSE
    """
    import numpy as np

    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean((y_true - y_pred)**2)
    
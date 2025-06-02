# -*- coding: utf-8 -*-
"""
Created on Mon Jun  2 19:22:02 2025

@author: dozzi
"""

# --------------------------------------
# ECONOMIC-FINANCIAL RELATIONSHIP ANALYSIS
# --------------------------------------

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statsmodels.tsa.vector_ar.vecm import coint_johansen
from statsmodels.tsa.stattools import grangercausalitytests, coint
from statsmodels.tsa.api import VAR
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import mutual_info_regression

# Set seed for reproducibility
np.random.seed(42)

# --------------------------------------
# STEP 1: SIMULATE ECONOMIC AND FINANCIAL DATA
# --------------------------------------

def simulate_monthly_data():
    print("[INFO] Simulating Monthly Data")
    # Generate monthly date index
    dates = pd.date_range(start="2020-01-01", periods=36, freq='M')
    df = pd.DataFrame(index=dates)

    # Simulate macroeconomic variables
    df['CPI_YoY'] = np.random.normal(2.0, 0.5, len(dates))
    df['Unemployment_Rate'] = np.random.normal(5.0, 1.0, len(dates))
    df['ISM_Manufacturing'] = np.random.normal(50, 3, len(dates))

    # Simulate financial variables as functions of macro inputs + noise
    df['S&P500_Return'] = (
        -0.2 * (df['Unemployment_Rate'] - 5) +
        0.1 * (df['CPI_YoY'] - 2) +
        np.random.normal(0, 1, len(dates))
    )
    df['Treasury10Y_Yield'] = (
        0.3 * df['CPI_YoY'] +
        0.05 * (df['ISM_Manufacturing'] - 50) +
        np.random.normal(0, 0.3, len(dates)) + 2
    )
    return df

# --------------------------------------
# STEP 2: ADD MIXED FREQUENCY VARIABLES
# --------------------------------------

def add_mixed_frequency_data(df):
    # Simulate quarterly GDP and forward-fill to monthly
    quarterly = pd.date_range(start="2020-03-31", periods=12, freq='Q')
    gdp = pd.Series(np.random.normal(2.0, 0.8, len(quarterly)), index=quarterly)
    df['GDP_Growth_QoQ'] = gdp.resample('M').ffill()

    # Simulate daily VIX and average to monthly
    daily = pd.date_range(start="2020-01-01", periods=750, freq='B')
    vix = np.clip(np.random.normal(20, 5, len(daily)), 10, None)
    df['VIX_Monthly_Avg'] = pd.Series(vix, index=daily).resample('M').mean()

    return df.dropna()

# --------------------------------------
# STEP 3: CORRELATION ANALYSIS
# --------------------------------------

def plot_correlation_matrix(df, method='pearson'):
    print("[INFO] Calculating Pairwise Correlation")
    # Display heatmap of correlation matrix using the specified method
    plt.figure(figsize=(10, 6))
    sns.heatmap(df.corr(method=method), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(f"{method.title()} Correlation Matrix")
    plt.tight_layout()
    plt.show()

# --------------------------------------
# STEP 4: ROLLING CORRELATION ANALYSIS
# --------------------------------------
"""
def find_optimal_rolling_correlation_window(df, min_window=3, max_window=12):
    print("[INFO] Cacluating Rolling Pairwise Correlation")
    # Loop through each variable pair to find the best rolling window based on average correlation
    cols = df.select_dtypes(include=np.number).columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            var1, var2 = cols[i], cols[j]
            best_window, best_corr = None, -np.inf
            for window in range(min_window, max_window + 1):
                roll_corr = df[var1].rolling(window).corr(df[var2])
                avg_corr = roll_corr.mean()
                if avg_corr > best_corr:
                    best_corr, best_window = avg_corr, window
                    best_series = roll_corr
            print(f"Best rolling window for {var1} vs {var2}: {best_window} months (Avg Corr = {best_corr:.2f})")
            plt.plot(df.index, best_series, label=f'{var1} vs {var2}')
            plt.axhline(0, linestyle='--', color='gray')
            plt.title(f'Rolling Correlation ({best_window}-month): {var1} vs {var2}')
            plt.legend()
            plt.tight_layout()
            plt.show()"""
            

def find_optimal_rolling_correlation_window(df, min_window=3, max_window=12):
    print("[INFO] Calculating Rolling Pairwise Correlation")
    results = []
    cols = df.select_dtypes(include=np.number).columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            var1, var2 = cols[i], cols[j]
            best_window, best_corr = None, -np.inf
            for window in range(min_window, max_window + 1):
                roll_corr = df[var1].rolling(window).corr(df[var2])
                avg_corr = roll_corr.mean()
                if avg_corr > best_corr:
                    best_corr, best_window = avg_corr, window
            results.append({
                'Variable 1': var1,
                'Variable 2': var2,
                'Best Window (months)': best_window,
                'Avg Rolling Corr': round(best_corr, 3)
            })
    result_df = pd.DataFrame(results)
    print("\nOptimal Rolling Window Correlation Results:")
    print(result_df.sort_values(by='Avg Rolling Corr', ascending=False))

# --------------------------------------
# STEP 5: LEAD-LAG CORRELATION ANALYSIS
# --------------------------------------

def find_optimal_lead_lag(df, max_lag=6):
    print("[INFO] Optimizing Lead/Lag for Rolling Pairwise Correlation")
    # Shift one variable backward and forward to find the highest absolute correlation
    cols = df.select_dtypes(include=np.number).columns
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            var1, var2 = cols[i], cols[j]
            best_corr, best_lag = -np.inf, 0
            lags = list(range(-max_lag, max_lag + 1))
            correlations = []
            for lag in lags:
                shifted = df[var2].shift(-lag)
                corr = df[var1].corr(shifted)
                correlations.append(corr)
                if pd.notnull(corr) and abs(corr) > abs(best_corr):
                    best_corr, best_lag = corr, lag
            print(f"Best lag for {var1} vs {var2}: {best_lag} months (Corr = {best_corr:.2f})")
            plt.plot(lags, correlations, marker='o')
            plt.axhline(0, linestyle='--', color='gray')
            plt.title(f'Lead-Lag Correlation: {var1} vs {var2}')
            plt.xlabel('Lag (months)')
            plt.ylabel('Correlation')
            plt.tight_layout()
            plt.show()

# --------------------------------------
# STEP 4: NONLINEAR RELATIONSHIP DETECTION
# --------------------------------------

def compute_mutual_information(df):
    print("[INFO] Calculating Mutual Information")
    # Detect nonlinear relationships using mutual information scores
    numeric_df = df.select_dtypes(include=np.number).dropna()
    cols = numeric_df.columns
    print("\nMutual Information Scores (nonlinear associations):")
    mi_matrix = pd.DataFrame(index=cols, columns=cols)

    for i in range(len(cols)):
        for j in range(len(cols)):
            if i != j:
                x = numeric_df[[cols[i]]].values
                y = numeric_df[cols[j]].values
                score = mutual_info_regression(x, y, discrete_features=False)[0]
                mi_matrix.iloc[i, j] = round(score, 3)
            else:
                mi_matrix.iloc[i, j] = np.nan

    # Print the matrix
    print(mi_matrix)

    # Plot heatmap of MI scores
    plt.figure(figsize=(10, 6))
    sns.heatmap(mi_matrix.astype(float), annot=True, cmap="YlGnBu")
    plt.title("Mutual Information Matrix (Nonlinear Dependency)")
    plt.tight_layout()
    plt.show()

# --------------------------------------
# STEP 5: COINTEGRATION ANALYSIS
# --------------------------------------

def test_cointegration(df):
    # Test for long-term equilibrium relationships between variable sets using Johansen Test
    print("[INFO] Performing Johansen Cointegration Test")
    numeric_df = df.select_dtypes(include=np.number).dropna()
    cols = numeric_df.columns

    # Run Johansen test
    johansen_result = coint_johansen(numeric_df, det_order=0, k_ar_diff=1)

    print("\nTrace Statistic:")
    for i, col in enumerate(cols):
        print(f"{col}: Trace Stat = {johansen_result.lr1[i]:.2f}, Crit 5% = {johansen_result.cvt[i, 1]:.2f}")

    print("\nEigen Statistic:")
    for i, col in enumerate(cols):
        print(f"{col}: Eigen Stat = {johansen_result.lr2[i]:.2f}, Crit 5% = {johansen_result.cvm[i, 1]:.2f}")

    # Interpretation
    print("\n[INFO] Johansen Test complete. Check if trace/eigen stats > critical value for significance.")

# --------------------------------------
# STEP 6: PRINCIPAL COMPONENT ANALYSIS (PCA)
# --------------------------------------

def run_pca(df, n_components=2):
    print("[INFO] Implementing PCA")
    # Use PCA to find dominant patterns in multivariate time series
    data = df.select_dtypes(include=np.number).dropna()
    scaled = StandardScaler().fit_transform(data)
    pca = PCA(n_components=n_components)
    pca.fit(scaled)
    print("Explained Variance Ratio:", pca.explained_variance_ratio_)
    plt.plot(range(1, n_components + 1), pca.explained_variance_ratio_, marker='o')
    plt.title("PCA: Variance Explained")
    plt.xlabel("Component")
    plt.ylabel("Proportion of Variance")
    plt.tight_layout()
    plt.show()

# --------------------------------------
# STEP 7: GRANGER CAUSALITY TESTING
# --------------------------------------

def run_granger_tests(df, max_lag=3):
    print("[INFO] Implementing GRANGER CAUSALITY TESTING")
    # Check whether lagged values of one variable help predict another
    econ_vars = ['CPI_YoY', 'Unemployment_Rate', 'ISM_Manufacturing', 'GDP_Growth_QoQ']
    fin_vars = ['S&P500_Return', 'Treasury10Y_Yield', 'VIX_Monthly_Avg']
    for econ in econ_vars:
        for fin in fin_vars:
            subset = df[[fin, econ]].dropna()
            print(f"Granger Test: Does {econ} → {fin}?")
            try:
                grangercausalitytests(subset, maxlag=max_lag, verbose=False)  # Suppress deprecated verbose output
            except Exception as e:
                print(f"Failed: {e}")


# --------------------------------------
# STEP 8: VECTOR AUTOREGRESSION (VAR)
# --------------------------------------

def run_var_model(df, variables, lags=3):
    print("[INFO] Implementing VECTOR AUTOREGRESSION")
    # Fit VAR model to examine interdependence between multiple time series
    model_data = df[variables].dropna()
    model = VAR(model_data)
    results = model.fit(lags)
    print(results.summary())

    # Plot impulse response functions (IRFs)
    irf = results.irf(10)
    irf.plot(orth=True)
    plt.suptitle("Impulse Response Functions")
    plt.tight_layout()
    plt.show()

    # Plot forecast error variance decomposition (FEVD)
    fevd = results.fevd(10)
    fevd.plot()
    plt.suptitle("Forecast Error Variance Decomposition")
    plt.tight_layout()
    plt.show()

    # Print correlation matrix of residuals
    print("\n[INFO] Residual Correlation Matrix:")
    print(results.resid.corr())
# --------------------------------------
# MAIN EXECUTION FLOW
# --------------------------------------

data = simulate_monthly_data()
data = add_mixed_frequency_data(data)

# Correlation matrix heatmaps
plot_correlation_matrix(data, 'pearson')
plot_correlation_matrix(data, 'spearman')

# Rolling correlation window optimization
find_optimal_rolling_correlation_window(data)

# Lead-lag correlation analysis
find_optimal_lead_lag(data)

# Nonlinear mutual information analysis
compute_mutual_information(data)

# Cointegration testing
cointegration_results = test_cointegration(data)

# Principal components from macro-financial signals
run_pca(data)

# Test directional predictability
run_granger_tests(data)

# Estimate dynamic responses in multivariate systems
run_var_model(data, ['CPI_YoY', 'Treasury10Y_Yield', 'S&P500_Return'])

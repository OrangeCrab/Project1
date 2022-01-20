'''
___process data and forecasting___
'''
import warnings
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import statsmodels.api as sm
# from scipy import stats
from plotly import graph_objs as go
from plotly.offline import plot
from statsmodels.tsa.stattools import adfuller
# import logging
from prophet import Prophet
from prophet.plot import plot_plotly, plot_components_plotly

changepoint_prior_scale_ = 0.5

class ForecastingProcess:
    def __init__(self):
        self.processFunction = {"Prophet": self.ProphetFunction}  # add other function with input and output similar ProphetFunction

    def ProphetFunction(self, df, prediction_size_, freq_df_, field_, seasonality_mode):
        '''
            forecasting dataframe using prophet model
            input: 
                df: dataframe for forecasting
                prediction_size_: prediction size
                freq_df_: freqence of dataframe get from step 3 (front-end)
                field_: field of original data (for -title- parameter in this function)
            output: 
                forecasting chart and forecasting component chart (plotly.offline.plot object) for embedded in html
        '''
        # print(df)
        df['ds'] = pd.to_datetime(df['ds'])
        train_df = df.copy()

        size = len(train_df)
        demo_df = df.copy()

        numDiff = 0
        tmp_y = train_df['y']
        check1 = adfuller(tmp_y)
        adf = []
        adf.append(check1)
        root = []
        while check1[1] > 0.05:                     # differencing
            root.append(tmp_y[size-1])              # append base value for inverse
            tmp_y = tmp_y.diff().dropna()
            numDiff = numDiff + 1
            check1 = adfuller(tmp_y)
            adf.append(check1)
        train_df['y'] = tmp_y

        m = Prophet(changepoint_range=0.95, changepoint_prior_scale=0.5, seasonality_mode=seasonality_mode)
        m.fit(train_df)
        future = m.make_future_dataframe(periods=prediction_size_, freq=freq_df_)
        forecast = m.predict(future)

        # fit for plot component
        m1 = Prophet(changepoint_range=0.95, changepoint_prior_scale=0.5, seasonality_mode=seasonality_mode) 
        m1.fit(demo_df)

        # inverse yhat
        if numDiff:                 
            series_inverted = self.inverse_differencing(root, forecast['yhat'], prediction_size_, size)
            for i in range(len(forecast)):
                forecast['yhat'][i] = series_inverted[i]

        cmp = self.make_comparison_dataframe(df, forecast) 

        err = []    # number 0 is mape, 1 is mae
        for err_name, err_value in self.calculate_forecast_errors(cmp, size).items():
            err.append(err_value)

        # from MAE & MAPE, calc yhat_lower & yhat_upper
        if numDiff:
            for i in range(len(forecast)):
                prd = forecast['yhat'][i]
                # print (prd)
                if prd != 0:
                    forecast['yhat_lower'][i] = prd - err[0] / 100 * abs(prd)
                    forecast['yhat_upper'][i] = prd + err[0] / 100 * abs(prd)
                else:
                    forecast['yhat_lower'][i] = prd - err[1]
                    forecast['yhat_upper'][i] = prd + err[1]
        
        # inverse trend
        if numDiff:
            for col in ['trend', 'trend_upper', 'trend_lower']:
                series_inverted = self.inverse_differencing(root, forecast[col], prediction_size_, size)
                for i in range(len(forecast)):
                    forecast[col][i] = series_inverted[i]
        
        cmp = self.make_comparison_dataframe(df, forecast)
        # print(cmp)
        # return [plot(plot_plotly(m1, forecast_demo), output_type = 'div'), plot(plot_components_plotly(m1,forecast_demo), output_type = 'div')]
        title = "Forecasting Visualize {} {}".format(field_, prediction_size_)
        return [self.show_forecast(cmp, len(forecast), len(forecast), title=title), 
                plot(plot_components_plotly(m1,forecast), output_type = 'div'),
                adf, err, numDiff]

    def calculate_forecast_errors(self, df, size):
        """Calculate MAPE and MAE of the forecast.
        Args:
            df: joined dataset with 'y' and 'yhat' columns.
            prediction_size: number of days at the end to predict.
        """
        df = df[:size].copy()

        # Calculate the values of e_i and p_i according to the formulas given in the article above.
        df["e"] = df["y"] - df["yhat"]
        df["p"] = 100 * df["e"] / df["y"]

        # Now cut out the part of the data which we made our prediction for.
        predicted_part = df[:size]

        # Define the function that averages absolute error values over the predicted part.
        error_mean = lambda error_name: np.mean(np.abs(predicted_part[error_name]))

        # Now we can calculate MAPE and MAE and return the resulting dictionary of errors.
        return {"MAPE %": error_mean("p"), "MAE": error_mean("e")}

    def inverse_differencing(self, root, df, prediction_size, size):
        '''
            inverse differencing list
            input:
                root: list of base value for inverse (len(root) = number of differencing)
                tg: list data for inverse
            output:
                list data after inverse
        '''
        series_inverted = []
        tg = df[-prediction_size:].copy()
        for i in range(len(root)-1, -1,-1):
            series_inverted = np.r_[root[i], tg].cumsum().astype(float)
            tg = series_inverted.copy()
        
        series_inverted1 = df[:size].copy()
        tg1 = df[:size].copy()
        for i in range(len(root)-1, -1,-1):
            series_inverted1[size-1] = root[i]
            for j in range(size-1, i, -1):
                series_inverted1[j-1] = series_inverted1[j] - tg1[j]
            tg1 = series_inverted1.copy()
        res = []
        for i in series_inverted1:
            res.append(i)
        series_inverted = np.delete(series_inverted,0)
        for i in series_inverted:
            res.append(i)
            
        return res

    def show_forecast(self, cmp_df, num_predictions, num_values, title):
        """Visualize the forecast.
            input: 
                cmp_df: compare dataframe for visualize
                num_prediction: prediction size
                numvalue: number of value of history data for visualize
                title: title of visualize
            output:
                chart ((plotly.offline.plot object)) for embedded in html
        """
        def create_go(name, column, num, **kwargs):
            # print(num)
            points = cmp_df.tail(num)
            args = dict(name=name, x=points.index, y=points[column], mode="lines")
            args.update(kwargs)
            return go.Scatter(**args)

        lower_bound = create_go(
            "Lower Bound",
            "yhat_lower",
            num_predictions,
            line=dict(width=0),
            marker=dict(color="gray"),
        )
        upper_bound = create_go(
            "Upper Bound",
            "yhat_upper",
            num_predictions,
            line=dict(width=0),
            marker=dict(color="gray"),
            fillcolor="rgba(68, 68, 68, 0.3)",
            fill="tonexty",
        )
        forecast = create_go(
            "Forecast", "yhat", num_predictions, line=dict(color="rgb(31, 119, 180)")
        )
        actual = create_go("History", "y", num_values, marker=dict(color="black"))

        # In this case the order of the series is important because of the filling
        data = [lower_bound, upper_bound, forecast, actual]

        layout = go.Layout(yaxis=dict(title="Posts"), title=title, showlegend=True)
        fig = go.Figure(data=data, layout=layout)
        return plot(fig, output_type = "div")

    def percentile(a, *args, **kwargs):
        """
        We rely on np.nanpercentile in the rare instances where there
        are a small number of bad samples with MCMC that contain NaNs.
        However, since np.nanpercentile is far slower than np.percentile,
        we only fall back to it if the array contains NaNs. See
        https://github.com/facebook/prophet/issues/1310 for more details.
        """
        fn =  np.nanpercentile if np.isnan(a).any() else np.percentile
        return fn(a, *args, **kwargs)

    def make_comparison_dataframe(self, historical, forecast):
        """Join the history with the forecast.
        The resulting dataset will contain columns 'yhat', 'yhat_lower', 'yhat_upper' and 'y'.
        """
        return forecast.set_index("ds")[["yhat", "yhat_lower", "yhat_upper"]].join(
            historical.set_index("ds")
        )

def plotly_df(df, ds_col, title=""):
        """Visualize all the dataframe columns as line plots.
            input:  df: dataframe for plot
                    ds_col: datetime column in df
                    title: title of Figure

            output: plot object for embedded in html
        """
        common_kw = dict(x=df[ds_col], mode="lines")
        data = []
        for c in df.columns:
            if (c != ds_col):
                data.append(go.Scatter(y=df[c], name=c, **common_kw))
        layout = dict(title=title)
        fig = dict(data=data, layout=layout)
        return plot(fig, output_type = "div")
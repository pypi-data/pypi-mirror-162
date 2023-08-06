import logging

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import KBinsDiscretizer

from .entity_summary_generator import EntitySummaryGenerator
from superwise.resources.superwise_enums import NumericSecondaryType

logger = logging.getLogger(__name__)


class NumericalSummaryGenerator(EntitySummaryGenerator):
    def __init__(self, entity):
        super(NumericalSummaryGenerator, self).__init__(entity)

    def _get_linear_percentile(self, quantile_deviation=0.03):
        # upper limit
        q_values = self._entity.astype(float).quantile(q=[0.98, 0.985, 0.99, 0.995])
        lr = LinearRegression().fit(q_values.reset_index()[["index"]].values, q_values.values)
        q_predict = 1 + quantile_deviation
        upper_limit = float(lr.predict(np.array(q_predict).reshape(-1, 1))[0])
        # Lower limit
        q_values = self._entity.astype(float).quantile(q=[0.005, 0.01, 0.015, 0.02])
        lr = LinearRegression().fit(q_values.reset_index()[["index"]].values, q_values.values)
        q_predict = 0 - quantile_deviation
        lower_limit = float(lr.predict(np.array(q_predict).reshape(-1, 1))[0])
        return lower_limit, upper_limit

    def calc_range(self):
        logger.debug("Calc range for".format(self._entity.name))
        lower_limit, upper_limit = self._get_linear_percentile()
        entities_count = self._entity.notna().sum()
        if entities_count:
            is_outlier_mask = (lower_limit > self._entity) | (self._entity > upper_limit)
            outliers_count = (is_outlier_mask & self._entity.notna()).sum()
            outliers = outliers_count / entities_count
        else:
            outliers = 0
        return {"range": {"from": lower_limit, "to": upper_limit}, "statistics": {"outliers": outliers}}

    def calc_min_value(self):
        logger.debug(f"Calc min value for {self._entity.name}")
        min_value = self._entity.min()
        min_value = None if pd.isna(min_value) else float(min_value)
        return {"statistics": {"min": min_value}}

    def calc_max_value(self):
        logger.debug(f"Calc max value for {self._entity.name}")
        max_value = self._entity.max()
        max_value = None if pd.isna(max_value) else float(max_value)
        return {"statistics": {"max": max_value}}

    def calc_std(self):
        logger.debug(f"Calc std value for {self._entity.name}")
        stdev = self._entity.std(ddof=1)
        logger.debug("calculated std {}".format(stdev))
        stdev = None if pd.isna(stdev) else float(stdev)
        return {"statistics": {"std": stdev}}

    def calc_mean_value(self):
        logger.debug(f"Calc mean value for {self._entity.name}")
        mean_value = self._entity.mean()
        mean_value = None if pd.isna(mean_value) else float(mean_value)
        return {"statistics": {"mean": mean_value}}

    def _numeric_bins(self, n_bins=30, strategy="kmeans", pad_bins=2):
        nunique = self._entity.nunique()
        if nunique == 1:
            return [self._entity.dropna().iloc[0]]
        n_bins = min(nunique, n_bins)
        discretizer = KBinsDiscretizer(n_bins=n_bins, encode="ordinal", strategy=strategy)
        bins = discretizer.fit(self._entity.dropna().to_frame()).bin_edges_[0]

        if pad_bins:
            lower_bin_width = bins[1] - bins[0]
            lower_bins_padding = [bins[-1] + lower_bin_width * (i + 1) for i in range(pad_bins)]
            upper_bin_width = bins[-1] - bins[-2]
            upper_bins_padding = [bins[0] - upper_bin_width * (i + 1) for i in range(pad_bins)]
            bins = np.append(bins, lower_bins_padding + upper_bins_padding)
            bins.sort()
        return bins

    def calc_numeric_distribution(self):
        logger.debug(f"Calc numeric distribution for {self._entity.name}")
        bins = self._numeric_bins()
        return self._calc_distribution(bins)

    def _calc_distribution(self, bins):
        bins = np.append(bins, [-np.Inf, np.Inf])
        bins.sort()
        buckets = pd.cut(self._entity, bins, right=False)
        buckets = buckets.value_counts(normalize=True, dropna=True).sort_index()
        buckets = pd.DataFrame(buckets).reset_index().reset_index().sort_values(by="index")
        buckets.columns = ["id", "name", "frequency"]
        buckets["lower"] = buckets["name"].values.categories.left
        buckets["upper"] = buckets["name"].values.categories.right

        mid_bin = list()
        bin_width = list()
        for idx, row in buckets.dropna().iterrows():
            if not {row["name"].right, row["name"].left}.intersection({np.Inf, -np.Inf}):
                mid_bin.append(row["name"].mid)
                bin_width.append(row["name"].length)

        if len(bin_width) == 0:
            bins_without_inf = bins[(bins < bins.max()) & (bins > bins.min())]
            mid_bin = [bins_without_inf[0] - 1, bins_without_inf[0] + 1]
            bin_width = [1, 1]
        else:
            bin_width.insert(0, bin_width[0])
            mid_bin.insert(0, buckets.iloc[0]["name"].right - bin_width[0] / 2)
            bin_width.append(bin_width[-1])
            mid_bin.append(buckets.dropna().iloc[-1]["name"].left + bin_width[-1] / 2)

        buckets["name"] = buckets["name"].astype(str)
        buckets["mid_bin"] = mid_bin
        buckets["bin_width"] = bin_width

        # remove -Inf & Inf
        bins = bins[1:-1]
        return {"distribution": {"bins": bins, "buckets": buckets.to_dict(orient="records")}}

    def generate_summary(self, secondary_type):
        secondary_type_to_metrics = {
            NumericSecondaryType.NUM_RIGHT_TAIL.value: [
                self.calc_missing_values,
                self.calc_range,
                self.calc_min_value,
                self.calc_max_value,
                self.calc_mean_value,
                self.calc_numeric_distribution,
                self.calc_std,
            ],
            NumericSecondaryType.NUM_LEFT_TAIL.value: [
                self.calc_missing_values,
                self.calc_range,
                self.calc_min_value,
                self.calc_max_value,
                self.calc_mean_value,
                self.calc_std,
                self.calc_numeric_distribution,
            ],
            NumericSecondaryType.NUM_CENTERED.value: [
                self.calc_missing_values,
                self.calc_range,
                self.calc_min_value,
                self.calc_max_value,
                self.calc_mean_value,
                self.calc_std,
                self.calc_numeric_distribution,
            ],
        }
        logger.debug(f"Generate summary for Numerical ({secondary_type}) feature {self._entity.name}")
        summary = {}
        for metric in secondary_type_to_metrics[secondary_type]:
            summary = self._update(summary, metric())
        return summary

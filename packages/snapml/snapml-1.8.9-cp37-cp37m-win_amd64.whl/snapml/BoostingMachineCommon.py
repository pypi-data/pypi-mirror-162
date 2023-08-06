# *****************************************************************
#
# Licensed Materials - Property of IBM
#
# (C) Copyright IBM Corp. 2017, 2021. All Rights Reserved.
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
#
# ******************************************************************

from sklearn.base import BaseEstimator

## @ingroup pythonclasses
class BoostingMachineCommon(BaseEstimator):
    """! This class implements common parts of the regressor and the classifier."""

    ## Documentation of the method
    #  @brief This method converts a parameter list
    def make_boosting_params(self):
        params = {
            "boosting_params": {
                "num_threads": self.n_jobs,
                "num_round": self.num_round,
                "objective": self.objective,
                "min_max_depth": self.min_max_depth
                if self.max_depth is None
                else self.max_depth,
                "max_max_depth": self.max_max_depth
                if self.max_depth is None
                else self.max_depth,
                "early_stopping_rounds": self.early_stopping_rounds,
                "random_state": self.random_state,
                "base_score": self.base_score,
                "learning_rate": self.learning_rate,
                "verbose": self.verbose,
                "compress_trees": self.compress_trees,
            },
            "tree_params": {
                "use_histograms": self.use_histograms,
                "hist_nbins": self.hist_nbins,
                "use_gpu": self.use_gpu,
                "gpu_ids": self.gpu_ids if hasattr(self, "gpu_ids") else [self.gpu_id],
                "colsample_bytree": self.colsample_bytree,
                "subsample": self.subsample,
                "lambda_l2": self.lambda_l2,
                "select_probability": self.tree_select_probability,
            },
            "ridge_params": {
                "regularizer": self.regularizer,
                "fit_intercept": self.fit_intercept,
            },
            "kernel_params": {
                "gamma": self.gamma,
                "n_components": self.n_components,
            },
        }
        return params

    def set_params(self, **params):

        """
        Set the parameters of this model.

        Valid parameter keys can be listed with ``get_params()``.

        Returns
        -------
        self

        """

        params_copy = self.get_params()
        super().set_params(**params)
        """
        If self.booster_ has not been created a parameter check is performed
        when fit() is called and self.booster_ is created.
        If self.booster_ exists a parameter change is happening after the fit()
        call and therefore a paramter check is required.
        """
        if hasattr(self, "booster_"):
            try:
                self.booster_.set_param(self.make_boosting_params())
            except:
                super().set_params(**params_copy)
                raise

        return self

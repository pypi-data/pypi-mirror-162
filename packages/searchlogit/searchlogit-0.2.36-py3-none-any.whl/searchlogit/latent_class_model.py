"""Implements Latent Class Model."""

from .multinomial_logit import MultinomialLogit
import numpy as np
from scipy.optimize import minimize
import copy  # TODO: TESTING
import logging

# define the computation boundary values not to be exceeded
min_exp_val = -700
max_exp_val = 700

max_comp_val = 1e+300
min_comp_val = 1e-300

logger = logging.getLogger(__name__)


class LatentClassModel(MultinomialLogit):
    """Class for estimation of Latent Class Models."""
    def __init__(self):
        super(LatentClassModel, self).__init__()

    def fit(self, X, y, varnames=None, alts=None, isvars=None, num_classes=2,
            class_params_spec=None, member_params_spec=None,
            ids=None, weights=None, avail=None,
            avail_latent=None,  # TODO?: separate param needed?
            transvars=None,
            transformation=None, base_alt=None, fit_intercept=False,
            intercept_opts=None,
            init_coeff=None, init_class_betas=None, init_class_thetas=None,
            maxiter=2000, random_state=None, ftol=1e-5,
            gtol=1e-5, gtol_membership_func=1e-5, grad=True, hess=True,
            panels=None, verbose=1,
            method="bfgs", scipy_optimisation=False):
        """Fit multinomial and/or conditional logit models.

        Parameters
        ----------
        X : array-like, shape (n_samples, n_variables)
            Input data for explanatory variables in long format

        y : array-like, shape (n_samples,)
            Choices in long format

        varnames : list, shape (n_variables,)
            Names of explanatory variables that must match the number and
            order of columns in ``X``

        alts : array-like, shape (n_samples,)
            Alternative indexes in long format or list of alternative names

        isvars : list
            Names of individual-specific variables in ``varnames``

        num_classes: int
            Number of latent classes

        class_params_spec: array-like, shape (n_samples,)
            Array of lists containing names of variables for latent class

        member_params_spec: array-like, shape (n_samples,)
            Array of lists containing names of variables for class membership

        transvars: list, default=None
            Names of variables to apply transformation on

        ids : array-like, shape (n_samples,)
            Identifiers for choice situations in long format.

        weights : array-like, shape (n_variables,), default=None
            Weights for the choice situations in long format.

        avail : array-like, shape (n_samples,)
            Availability of alternatives for the choice situations. One when
            available or zero otherwise.

        avail : array-like, shape (n_classes,)
            List of avails for each class.

        transvars: list, default=None
            Names of variables to apply transformation on

        transformation: string, default=None
            Name of transformation to apply on transvars

        base_alt : int, float or str, default=None
            Base alternative

        fit_intercept : bool, default=False
            Whether to include an intercept in the model.

        intercept_opts : dict, default=None
            Options for intercept. Allows specific alts for various intercepts.

        init_coeff : numpy array, shape (n_variables,), default=None
            Initial coefficients for estimation.

        init_class_betas : numpy array, shape (n_classes,), default=None
            Array of lists for initial coefficients for estimation for
            each class.

        init_class_thetas : numpy array, shape (n_classes-1,), default=None
            Array of lists for initial coefficients for estimations for
            the membership function.

        maxiter : int, default=200
            Maximum number of iterations

        random_state : int, default=None
            Random seed for numpy random generator

        ftol : int, float, default=1e-5
            Sets the tol parameter in scipy.optimize.minimize - Tolerance for
            termination.

        gtol: int, float, default=1e-5
            Sets the gtol parameter in scipy.optimize.minimize(method="bfgs) -
            Gradient norm must be less than gtol before successful termination.

        gtol_membership_func : int, float, default=1e-5
            Same as gtol, but for the membership function,

        grad : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        hess : bool, default=True
            Calculate and return the gradient in _loglik_and_gradient

        panels : array-like, shape (n_samples,), default=None
            Identifiers in long format to create panels in combination with
            ``ids``.

        verbose : int, default=1
            Verbosity of messages to show during estimation. 0: No messages,
            1: Some messages, 2: All messages

        method: string, default="bfgs"
            specify optimisation method passed into scipy.optimize.minimize

        scipy_optimisation : bool, default=False
            Use scipy_optimisation for minimisation. When false uses own
            bfgs method.

        Returns
        -------
        None.
        """

        self.ftol = ftol
        self.gtol = gtol
        self.gtol_membership_func = gtol_membership_func
        self.num_classes = num_classes

        # default to using all varnames in each latent class if not specified
        if class_params_spec is None:
            if isvars is not None:
                class_vars = [var for var in varnames if var not in isvars]
            else:
                class_vars = varnames
            class_params_spec = np.array([])
            class_params_spec = np.vstack([class_vars for i in range(num_classes)])
        self.class_params_spec = class_params_spec

        self.membership_as_probability = True if member_params_spec is True else False
        if self.membership_as_probability:
            member_params_spec = np.vstack(['dummy' for i in range(num_classes-1)])
        if member_params_spec is None:
            if isvars is not None:
                member_vars = isvars
            else:
                member_vars = varnames
            member_params_spec = np.vstack([member_vars for i in range(num_classes-1)])

        self.member_params_spec = member_params_spec

        self.panels = panels
        self.init_df = X
        self.init_y = y
        self.ids = ids

        # For predicted probabilities of alternative need to inc. all classes
        self.pred_prob = None
        self.pred_prob_all = None

        if '_inter' in np.concatenate(class_params_spec) or '_inter' in np.concatenate(member_params_spec):
            fit_intercept = True

        # TODO?: assumes alts are nums 1...J
        if intercept_opts is None:
            intercept_opts = {}
        else:
            if 'class_intercept_alts' in intercept_opts:
                if len(intercept_opts['class_intercept_alts']) != num_classes:
                    raise ValueError("The key class_intercept_alts in "
                                     "intercept_opts must be the same length "
                                     "as num_classes")
        self.intercept_opts = intercept_opts

        if avail_latent is None:
            avail_latent = np.repeat(None, num_classes)
        self.avail_latent = avail_latent

        self.init_class_betas = init_class_betas
        self.init_class_thetas = init_class_thetas

        super(LatentClassModel, self).fit(X, y, varnames, alts, isvars,
                                          transvars, transformation, ids,
                                          weights, avail, base_alt,
                                          fit_intercept, init_coeff, maxiter,
                                          random_state, ftol, gtol, grad, hess,
                                          verbose, method, scipy_optimisation)

    # TODO: DECIDE KEEP THIS FUNCTION OR NOT
    def optimal_class_fit(self, X, y, varnames=None, alts=None, isvars=None,
                          num_classes=1, class_params_spec=None,
                          member_params_spec=None, ids=None, weights=None,
                          avail=None, transvars=None, transformation=None,
                          base_alt=None, fit_intercept=False, init_coeff=None,
                          maxiter=2000, random_state=None, ftol=1e-5,
                          gtol=1e-5, grad=True, hess=True, panels=None,
                          verbose=1, method="placeholder",
                          scipy_optimisation=False):
        """Determines optimal number of latent classes based on BIC.
           Note current implementation only considers latent classes with
           the same variables."""
        self.num_classes = num_classes
        self.panels = panels
        self.init_df = X
        self.init_y = y
        self.ids = ids

        curr_bic = -1
        prev_bic = 0
        model = copy.copy(self)
        num_classes = self.num_classes
        prev_model = None
        curr_model = None
        while curr_bic < prev_bic and num_classes > 1:  # lowest BIC
            class_params_spec = np.vstack([varnames for i in range(num_classes)])
            model.class_params_spec = class_params_spec

            member_params_spec = np.vstack([varnames for i in range(num_classes-1)])
            model.member_params_spec = member_params_spec

            model.fit(X, y, varnames, alts, isvars, num_classes,
                      class_params_spec, member_params_spec, ids, weights,
                      avail, transvars, transformation, base_alt,
                      fit_intercept, init_coeff, maxiter, random_state, ftol,
                      gtol, grad, hess, panels, verbose, method,
                      scipy_optimisation)
            prev_bic = curr_bic
            prev_model = curr_model
            curr_model = model
            curr_bic = model.bic
            num_classes -= 1

        if num_classes == 1:
            # TODO: compare against multinomial?
            pass

        # check cause of termination
        optimal_num = -1
        if curr_bic > prev_bic:
            optimal_num = num_classes+2
            model = prev_model
        else:
            optimal_num = num_classes+1
            model = curr_model

        print('Optimal number of classes', optimal_num)
        return (optimal_num, model)

    def _post_fit(self, optimization_res, coeff_names, sample_size,
                  hess_inv=None, verbose=1):
        super(LatentClassModel, self)._post_fit(optimization_res,
                                                coeff_names,
                                                sample_size)

    def _compute_probabilities_latent(self, betas, X, y, avail):
        p, _ = self._compute_probabilities(betas, X, avail)
        p = y*p

        # collapse on alts
        pch = np.sum(p, axis=1)

        # if hasattr(self, 'panel_info'):
        #     pch_new = np.zeros(self.N)
        #     # pch = self._prob_product_across_panels(pch, self.panel_info)
        #     counter = 0
        #     for ii, row in enumerate(self.panel_info):
        #         row_sum = int(np.sum(row))
        #         pch_new[counter:counter+row_sum] = np.mean(pch[counter:counter+row_sum])
        #         counter += row_sum
        #     pch = pch_new
        return pch.flatten()

    def _prob_product_across_panels(self, pch, panel_info):
        if not np.all(panel_info):  # If panels unbalanced. Not all ones
            idx = panel_info == .0
            pch[:, :][idx] = 1  # Multiply by one when unbalanced
        pch = pch.prod(axis=1, dtype=np.float64)  # (N,R)
        pch[pch < min_comp_val] = min_comp_val
        return pch  # (N,R)

    # copied from mixed_logit class
    def _balance_panels(self, X, y, panels):
        """Balance panels if necessary and produce a new version of X and y.

        If panels are already balanced, the same X and y are returned. This
        also returns panel_info, which keeps track of the panels that needed
        balancing.
        """
        _, J, K = X.shape
        _, p_obs = np.unique(panels, return_counts=True)
        p_obs = (p_obs/J).astype(int)
        N = len(p_obs)  # This is the new N after accounting for panels
        P = np.max(p_obs)  # panels length for all records
        if not np.all(p_obs[0] == p_obs):  # Balancing needed
            y = y.reshape(X.shape[0], J, 1)
            Xbal, ybal = np.zeros((N*P, J, K)), np.zeros((N*P, J, 1))
            panel_info = np.zeros((N, P))
            cum_p = 0  # Cumulative sum of n_obs at every iteration
            for n, p in enumerate(p_obs):
                # Copy data from original to balanced version
                Xbal[n*P:n*P + p, :, :] = X[cum_p:cum_p + p, :, :]
                ybal[n*P:n*P + p, :, :] = y[cum_p:cum_p + p, :, :]
                panel_info[n, :p] = np.ones(p)
                cum_p += p
        else:  # No balancing needed
            Xbal, ybal = X, y
            panel_info = np.ones((N, P))

        return Xbal, ybal, panel_info

    def _posterior_est_latent_class_probability(self, class_thetas):
        """Get the prior estimates of the latent class probabilities.

        Args:
            class_thetas (array-like): (number of latent classes) - 1 array of
                                       latent class vectors
            X (array-like): Input data for explanatory variables in wide format

        Returns:
            H [array-like]: Prior estimates of the class probabilities

        """
        class_thetas_original = class_thetas
        if class_thetas.ndim == 1:
            new_class_thetas = np.array(np.repeat('tmp', self.num_classes-1),
                                        dtype='object')
            j = 0
            for ii, member_params in enumerate(self.member_params_spec):
                num_params = len(member_params)
                tmp = class_thetas[j:j+num_params]
                j += num_params
                new_class_thetas[ii] = tmp

            class_thetas = new_class_thetas

        class_thetas_base = np.zeros(len(class_thetas[0]))
        base_X_idx = self._get_member_X_idx(0)
        member_df = np.transpose(self.short_df[:, base_X_idx])

        member_N = member_df.shape[1]

        eZB = np.zeros((self.num_classes, member_N))

        if '_inter' in np.concatenate(self.member_params_spec):
            member_df = np.vstack((np.ones((1, member_N)),
                                   np.transpose(self.short_df[:, base_X_idx])))

        if self.membership_as_probability:
            H = np.tile(np.concatenate([1 - np.sum(class_thetas), class_thetas_original]), (member_N, 1))
            H = np.transpose(H)
        else:
            zB_q = np.dot(class_thetas_base[None, :],
                          member_df)

            eZB[0, :] = np.exp(zB_q)

            for i in range(0, self.num_classes-1):
                class_X_idx = self._get_member_X_idx(i)
                member_df = np.transpose(self.short_df[:, class_X_idx])
                # add in columns of ones for class-specific const (_inter)
                if '_inter' in np.concatenate(self.member_params_spec):
                    member_df = np.vstack((np.ones((1, member_N)),
                                           np.transpose(self.short_df[:, base_X_idx])))

                zB_q = np.dot(class_thetas[i].reshape((1, -1)),
                              member_df)
                zB_q[np.where(max_exp_val < zB_q)] = max_exp_val
                eZB[i+1, :] = np.exp(zB_q)

            H = eZB/np.sum(eZB, axis=0, keepdims=True)

        # store to display in summary
        self.class_freq = np.mean(H, axis=1)

        if hasattr(self, 'panel_info') and self.panel_info is not None:
            # convert H to num choice situations
            new_H = np.zeros((self.num_classes, self.N))
            counter = 0

            for ii, row in enumerate(self.panel_info):
                row_sum = int(np.sum(row))
                new_H[:, counter:counter+row_sum] = np.repeat(H[:, ii], row_sum).reshape((self.num_classes, row_sum))
                counter += row_sum
            H = new_H

        return H

    def _class_member_func(self, class_thetas, weights, X):
        """Find latent class params that minimise negative loglik.

           Used in Maximisaion step. Used to find latent class vectors that
           minimise the negative loglik where there is no observed dependent
           variable (H replaces y).

        Args:
            class_thetas (array-like): (number of latent classes) - 1 array of
                                       latent class vectors
            weights (array-like): weights is prior probability of class by the
                                  probability of y given the class.
            X (array-like): Input data for explanatory variables in wide format
        Returns:
            ll [np.float64]: Loglik
        """
        H = self._posterior_est_latent_class_probability(class_thetas)

        H[np.where(H < 1e-30)] = 1e-30
        weight_post = np.multiply(np.log(H), weights)
        ll = -np.sum(weight_post)

        # TODO: gradient
        # tgr = np.multiply(weights, H)
        # tgr = np.hstack(tgr).reshape((-1, 1))
        # X_tmp = np.mean(X, axis=1)
        # X_tmp = np.concatenate((X_tmp, X_tmp))
        # gr = np.dot(np.transpose(X_tmp), tgr)

        return ll  # , gr.flatten()

    def _get_class_X_idx(self, class_num, coeff_names=None, **kwargs):
        """Get indices for X dataset for class parameters.

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class
        """
        #  below line: return indices of that class params in Xnames
        #  pattern matching for isvars

        tmp_varnames = None
        if coeff_names is None:
            tmp_varnames = self.varnames.copy()
        else:
            tmp_varnames = coeff_names.copy()

        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]

        X_class_idx = np.array([], dtype='int32')
        for var in self.class_params_spec[class_num]:
            for ii, var2 in enumerate(tmp_varnames):
                if 'inter' in var and coeff_names is not None:  # only want to use summary func
                    if 'inter' in var2:
                        if 'class_intercept_alts' in self.intercept_opts:
                            alt_num = int(var2.split('.')[-1])
                            if alt_num not in self.intercept_opts['class_intercept_alts'][class_num]:
                                continue
                if var in var2:
                    X_class_idx = np.append(X_class_idx, ii)

        # isvars handled if pass in full coeff names
        X_class_idx = np.unique(X_class_idx)
        X_class_idx = np.sort(X_class_idx)
        X_class_idx_tmp = np.array([], dtype='int')
        counter = 0

        # TODO? better approach than replicating Xname creation?
        if coeff_names is not None:
            return X_class_idx
        for idx_pos in range(len(self.varnames)):
            if idx_pos in self.ispos:
                # fix bug of not all alts checked intercept
                for i in range(self.J - 1):
                    if idx_pos in X_class_idx:
                        # TODO? check
                        if self.varnames[idx_pos] == '_inter' and 'class_intercept_alts' in self.intercept_opts:
                            if i+2 not in self.intercept_opts['class_intercept_alts'][class_num]:
                                counter += 1
                                continue
                        X_class_idx_tmp = np.append(X_class_idx_tmp, int(counter))
                    counter += 1
            else:
                if idx_pos in X_class_idx:
                    X_class_idx_tmp = np.append(X_class_idx_tmp, counter)
                counter += 1

        X_class_idx = X_class_idx_tmp

        return X_class_idx

    def _get_member_X_idx(self, class_num, coeff_names=None):
        """Get indices for X dataset based for class parameters.

        Args:
            class_num (int): latent class number

        Returns:
            X_class_idx [np.ndarray]: indices to retrieve relevant
                                        explantory params of specified
                                        latent class

        """
        if coeff_names is None:
            tmp_varnames = self.varnames.copy()
        else:
            tmp_varnames = coeff_names.copy()

        # factor in isvars

        # tmp_varnames = coeff_names.copy()
        for ii, varname in enumerate(tmp_varnames):
            # remove lambda so can get indices correctly
            if varname.startswith('lambda.'):
                tmp_varnames[ii] = varname[7:]

        X_class_idx = np.array([], dtype='int32')
        for var in self.member_params_spec[class_num]:
            for ii, var2 in enumerate(tmp_varnames):
                if var in var2 and var != '_inter':
                    X_class_idx = np.append(X_class_idx, ii)

        X_class_idx = np.sort(X_class_idx)

        return X_class_idx

    def _get_betas_length(self, class_num):
        """Get betas length (parameter vectors) for the specified latent class.

        Args:
            class_num (int): latent class number

        Returns:
            betas_length (int): number of betas for latent class
        """
        class_params_spec = self.class_params_spec[class_num]

        betas_length = 0
        if 'class_intercept_alts' in self.intercept_opts and '_inter' in class_params_spec:
            # separate logic for intercept
            class_isvars = [isvar for isvar in self.isvars if isvar != '_inter']
            betas_length +=  len(self.intercept_opts['class_intercept_alts'][class_num])
        else:
            class_isvars = [x for x in class_params_spec if x in self.isvars]
        betas_length += (len(self.alternatives)-1)*(len(class_isvars))
        class_asvars = [x for x in class_params_spec if x in self.asvars]
        class_transvars = [x for x in class_params_spec if x in self.transvars]

        betas_length += len(class_asvars)
        betas_length += len(class_transvars)*2

        return betas_length

    def _expectation_maximisation_algorithm(self, X, y, avail=None, weights=None,
                                            class_betas=None, class_thetas=None,
                                            validation=False):
        """Runs expectation-maximisation algorithm.

           Run the EM algorithm by iterating between computing the
           posterior class probabilities and re-estimating the model parameters
           in each class by using a probability weighted loglik function

        Args:
            X (array-like): Input data for explanatory variables in wide format
            y (array-like):  Choices (outcome) in wide format
            weights (array-like): weights is prior probability of class by the
                                  probability of y given the class.
            avail (array-like): Availability of alternatives for the
                                choice situations. One when available or
                                zero otherwise.

        Returns:
            optimisation_result (dict): Dictionary mimicking the optimisation
                                        result in scipy.optimize.minimize
        """
        converged = False
        # TODO? better structure - revert N
        if self.panels is not None:
            N = X.shape[0]
            self.N = N

        if self.membership_as_probability:
            class_thetas = np.array([1/(self.num_classes) for i in range(0, self.num_classes-1)])

        if class_betas is None and self.init_class_betas is not None:
            class_betas = self.init_class_betas

        if class_thetas is None and self.init_class_thetas is not None:
            class_thetas = self.init_class_thetas

        if class_betas is None:
            class_betas = [np.random.normal(0, .1, self._get_betas_length(i))
                           for i in range(self.num_classes)]
        if class_thetas is None:
            # class membership probability
            len_class_thetas = [len(self._get_member_X_idx(i)) for i in range(0, self.num_classes-1)]
            if '_inter' in np.concatenate(self.member_params_spec):
                len_class_thetas = [len_i + 1 for len_i in len_class_thetas]
            class_thetas = np.concatenate([
                np.random.normal(0, .1, len_class_thetas[i])
                for i in range(0, self.num_classes-1)], axis=0)

        # used for _get_class_X_idx
        self.trans_pos = [ii for ii, var in enumerate(self.varnames) if var in self.transvars]

        log_lik_old = 0

        # TODO! check dims... summing over panel or alts here?
        short_df = np.mean(X, axis=1)

        if hasattr(self, 'panel_info') and self.panel_info is not None:
            counter = 0
            new_short_df = np.zeros((self.panel_info.shape[0], short_df.shape[1]))
            for ii, row in enumerate(self.panel_info):
                row_sum = int(np.sum(row))
                new_short_df[ii, :] = np.mean(short_df[counter:counter+row_sum, :], axis=0)
                counter += row_sum
            short_df = new_short_df

        # Remove intercept columns
        if self.fit_intercept:
            short_df = short_df[:, (self.J-2):]
            short_df[:, 0] = 1
        self.short_df = short_df

        max_iter = 2000
        iter_num = 0
        class_betas_sd = [np.repeat(.99, len(betas))
                          for betas in class_betas]
        class_thetas_sd = np.repeat(.01, class_thetas.size)
        class_idxs = []
        class_fxidxs = []
        class_fxtransidxs = []
        global_fxidx = self.fxidx
        global_fxtransidx = self.fxtransidx
        global_varnames = self.varnames  # ? Code smell
        for class_num in range(self.num_classes):
            X_class_idx = self._get_class_X_idx(class_num)
            class_idxs.append(X_class_idx)
            class_fx_idx = [fxidx for ii, fxidx in enumerate(global_fxidx)
                            if ii in X_class_idx]

            class_fxtransidx = [not fxidx for fxidx in class_fx_idx]
            class_fxidxs.append(class_fx_idx)
            class_fxtransidxs.append(class_fxtransidx)

        while not converged and iter_num < max_iter:
            # Expectation step
            X_class0_idx = self._get_class_X_idx(0)
            # Set fxidx for base class when calling multinomial loglik
            self.fxidx = class_fxidxs[0]
            self.fxtransidx = class_fxtransidxs[0]
            self.Kf = sum(class_fxidxs[0])
            self.Kftrans = sum(class_fxtransidxs[0])
            self.varnames = np.array(self.class_params_spec[0])

            # TODO? revist
            # if self.panels is not None:
                # p = self._compute_probabilities_latent_panels(
                                                # class_betas[0],
                                                # X[:, :, X_class0_idx],
                                                # y,
                                                # self.panel_info,
                                                # self.avail_latent[0]
                                                # )
            # else:
            p = self._compute_probabilities_latent(
                                            class_betas[0],
                                            X[:, :, X_class0_idx],
                                            y,
                                            self.avail_latent[0]
                                            )

            self.varnames = global_varnames

            H = self._posterior_est_latent_class_probability(class_thetas)
            for class_i in range(1, self.num_classes):
                X_class_idx = class_idxs[class_i]
                self.fxidx = class_fxidxs[class_i]
                self.fxtransidx = class_fxtransidxs[class_i]
                self.Kf = sum(class_fxidxs[class_i])
                self.Kftrans = sum(class_fxtransidxs[class_i])
                self.varnames = np.array(self.class_params_spec[class_i])

                # TODO? revist
                # if self.panels is not None:
                #     new_p = self._compute_probabilities_latent_panels(class_betas[class_i],
                #                 X[:, :, X_class_idx],
                #                 y,
                #                 self.panel_info,
                #                  self.avail_latent[class_i])
                # else:
                new_p = self._compute_probabilities_latent(class_betas[class_i],
                                                           X[:, :, X_class_idx],
                                                           y,
                                                           self.avail_latent[class_i])
                p = np.vstack((p, new_p))

            self.varnames = global_varnames
            weights = np.multiply(p, H)
            weights[weights == 0] = min_comp_val

            lik = np.sum(weights, axis=0)
            lik[np.where(lik < min_comp_val)] = min_comp_val
            log_lik = np.log(np.sum(weights, axis=0))  # sum over classes

            log_lik_new = np.sum(log_lik)
            if validation:
                return log_lik_new

            weights = np.divide(weights,
                                np.tile(np.sum(weights, axis=0),
                                        (self.num_classes, 1)))
            # Maximisation (minimisation) step
            # if any minimisations don't converge set to False
            optimsation_convergences = True
            opt_res = minimize(self._class_member_func,
                               class_thetas,
                               args=(weights, X),
                               # jac=True,
                               method='BFGS',
                               tol=self.ftol,
                               options={'gtol': self.gtol_membership_func}
                               )

            if opt_res['success']:
                class_thetas = opt_res['x']
                tmp_thetas_sd = np.sqrt(np.diag(opt_res['hess_inv']))
                # in scipy.optimse if "initial guess" is close to optimal
                # solution it will not build up a guess at the Hessian inverse
                # this if statement prevents this case
                # TODO? inc. atol=1e-3? investigate
                if not np.allclose(tmp_thetas_sd,
                                   np.ones(len(tmp_thetas_sd))):
                    class_thetas_sd = tmp_thetas_sd

            self.pred_prob_all = np.array([])
            global_transvars = self.transvars.copy()
            for s in range(0, self.num_classes):
                X_class_idx = class_idxs[s]
                self.fxidx = class_fxidxs[s]
                self.fxtransidx = class_fxtransidxs[s]
                self.Kf = sum(class_fxidxs[s])
                self.Kftrans = sum(class_fxtransidxs[s])

                self.varnames = np.array(self.class_params_spec[s])

                # remove transvars which are not included in class params
                self.transvars = [transvar for transvar in
                                  global_transvars if transvar in
                                  self.class_params_spec[s]]

                jac = True if self.grad else False
                opt_res = minimize(self._loglik_and_gradient,
                                   class_betas[s],
                                   jac=jac,
                                   args=(
                                       X[:, :, X_class_idx],
                                       y,
                                       weights[s, :].reshape(-1, 1),
                                       self.avail_latent[s]),
                                   method="BFGS",
                                   tol=self.ftol,
                                   options={'gtol': self.gtol}
                                   )
                self.varnames = global_varnames
                self.transvars = global_transvars
                self.pred_prob_all = np.append(self.pred_prob_all,
                                               self.pred_prob)
                if opt_res['success']:
                    class_betas[s] = opt_res['x']
                    tmp_calc = np.sqrt(np.diag(opt_res['hess_inv']))
                    if not np.all(np.diag(tmp_calc ==
                                  np.eye(len(class_betas[s])))):
                        class_betas_sd[s] = tmp_calc
                    else:
                        optimsation_convergences = False   # todo? check
                else:
                    optimsation_convergences = False
            converged = np.abs(log_lik_new - log_lik_old) < self.ftol
            logger.debug("Class betas: {}".format(class_betas))
            logger.debug("Class thetas: {}".format(class_thetas))
            logger.debug("Log-lik: {}".format(log_lik_new))
            log_lik_old = log_lik_new
            logger.debug("Latent class iteration: {}".format(iter_num))
            iter_num += 1

        x = np.array([])
        for betas in class_betas:
            betas = np.array(betas)
            x = np.concatenate((x, betas))

        stderr = np.concatenate(class_betas_sd)

        optimisation_result = {'x': x,
                               'success': optimsation_convergences,  # TODO? valid?
                               'fun': -log_lik_new, 'nit': iter_num,
                               'stderr': stderr, 'is_latent_class': True,
                               'class_x': class_thetas.flatten(),
                               'class_x_stderr': class_thetas_sd}

        # reset here when rerun
        self.fxidx = global_fxidx
        self.fxtransidx = global_fxtransidx
        self.Kf = sum(global_fxidx)
        self.Kftrans = sum(global_fxidx)

        p_class = np.mean(H, axis=1)
        pred_prob_tmp = np.zeros(self.J)
        for i in range(self.num_classes):
            pred_prob_tmp += p_class[i] * self.pred_prob_all[i*self.J:(i*self.J)+self.J]
        self.pred_prob = pred_prob_tmp
        return optimisation_result

    def validation_loglik(self, validation_X, validation_Y, avail=None, avail_latent=None,
                          weights=None, betas=None, panels=None):
        """Compute the log-likelihood on the validation set."""
        validation_X, _ = self._setup_design_matrix(validation_X)
        N = validation_X.shape[0]
        # self.N = N
        validation_Y = validation_Y.reshape(N, -1)
        if panels is not None:
            ind_N = len(np.unique(panels))
            self.N = ind_N
        self.avail_latent = avail_latent
        if avail_latent is None:
            avail_latent = np.repeat(None, self.num_classes)
            self.avail_latent = avail_latent

        if panels is not None:  # If panels
            _, _, panel_info = self._balance_panels(validation_X, validation_Y, panels)
            self.panel_info = panel_info
        self.panels = panels

        class_betas = []
        counter = 0
        for ii, param_spec in enumerate(self.class_params_spec):
            idx = counter + self._get_betas_length(ii)
            class_betas.append(self.coeff_[counter:idx])
            counter = idx

        loglik = self._expectation_maximisation_algorithm(validation_X,
                                                          validation_Y,
                                                          avail=avail,
                                                          weights=weights,
                                                          class_betas=class_betas,
                                                          class_thetas=self.class_x,
                                                          validation=True
                                                          )
        logger.info('Validation loglik: {}'.format(loglik))
        return loglik

    def _bfgs_optimization(self, betas, X, y, weights, avail, maxiter):
        """Override bfgs function in multinomial logit to use EM."""
        opt_res = self._expectation_maximisation_algorithm(X, y, avail)
        return opt_res

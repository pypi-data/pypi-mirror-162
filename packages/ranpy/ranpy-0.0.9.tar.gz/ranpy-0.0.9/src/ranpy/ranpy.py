from scipy.stats import truncnorm
from scipy.stats import lognorm
from scipy.stats import gamma
from scipy.stats import expon
from scipy.stats import weibull_min
from scipy.stats import invgauss
from scipy.stats import uniform
from scipy.stats import poisson
from scipy.stats import beta
from scipy.optimize import minimize, root_scalar, minimize_scalar
import numpy as np

class Ranpy(object):
    def __init__(self, seed):
        np.random.seed(seed)
        self.unif = uniform()

    def rand(self, n=1):
        if n==1:
            return self.unif.rvs(1)[0]
        else:
            return self.unif.rvs(n)


    def get_uniform(self, params):
        """
        Parameters: a, b 

        Is uniform on [a, b]
        """
        return uniform(loc=params['a'], scale=(params['b']-params['a']))
        

    def get_exponential(self, dist_pars):
        """
        Parameters: rate

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html
        https://en.wikipedia.org/wiki/Exponential_distribution
        """
        loc = 0
        scale = 1/dist_pars['rate']
        return expon(loc, scale)


    def get_truncnorm(self, dist_pars):
        """
        Parameters: mu, sigma, a, b 

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.truncnorm.html
        Not explicitly provided by NumPy, can be obtained by using acceptance-rejection
        on normal distribution https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.normal.html
        https://en.wikipedia.org/wiki/Truncated_normal_distribution
        """
        mu = dist_pars['mu']
        s = dist_pars['sigma']
        lo = dist_pars['a']
        hi = dist_pars['b']
        a, b = (lo - mu) / s, (hi - mu) / s
        return truncnorm(a, b, mu, s)


    def get_lognorm(self, dist_pars):
        """
        Parameters: mu, sigma (these are the mean and standard deviation of the corresponding normal distribution)

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.lognormal.html
        https://en.wikipedia.org/wiki/Log-normal_distribution
        """
        scale = np.exp(dist_pars['mu'])
        s = dist_pars['sigma']
        loc = 0
        return lognorm(s, loc, scale)


    def get_gamma(self, dist_pars):
        """
        Parameters: shape, rate

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.gamma.html
        https://en.wikipedia.org/wiki/Gamma_distribution
        """
        a = dist_pars['shape']
        loc = 0
        scale = 1/dist_pars['rate']
        return gamma(a, loc, scale)

    def get_beta(self, dist_pars):
        """
        Parameters: shape, rate

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html
        https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.gamma.html
        https://en.wikipedia.org/wiki/Gamma_distribution
        """
        a = dist_pars['alpha']
        b = dist_pars['beta']
        return beta(a, b)


    def get_weibull(self, dist_pars):
        """
        Parameters: shape, scale

        https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.weibull.html#numpy.random.Generator.weibull
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.weibull_min.html
        https://en.wikipedia.org/wiki/Weibull_distribution
        """
        c = dist_pars['shape']
        loc = 0
        scale = dist_pars['scale']
        return weibull_min(c, loc, scale)


    def get_invgauss(self, dist_pars):
        """
        Parameters: mu

        https://numpy.org/doc/stable/reference/random/generated/numpy.random.Generator.wald.html
        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.invgauss.html
        https://en.wikipedia.org/wiki/Inverse_Gaussian_distribution
        """
        mu = dist_pars['mu']
        loc = 0
        scale = 1
        return invgauss(mu, loc, scale)


    def get_poisson(self, dist_pars):
        """
        Parameters: mu

        """
        mu = dist_pars['mu']
        return poisson(mu)


    def get_pareto(self, params):
        """
        Parameters: minimum, rate

        https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pareto.html
        https://en.wikipedia.org/wiki/Pareto_distribution
        """
        exp_dist = self.get_exponential({'rate': params['rate']})
        class dist(object):
            def rvs(self, n):
                if n == 1:
                    return params['minimum']*np.exp(exp_dist.rvs(n))[0]
                else:
                    return params['minimum']*np.exp(exp_dist.rvs(n))
                
        return dist()


    def get_dist(self, dist, dist_pars):
        """
        Wrapper function to utilise above functions using the 
        strings 'truncnorm', 'gamma', 'lognorm', 'weibull', 'invgauss'. 
        """
        match dist:
            case 'truncnorm':
                return self.get_truncnorm(dist_pars)
            case 'gamma':
                return self.get_gamma(dist_pars)
            case 'lognorm':
                return self.get_lognorm(dist_pars)
            case 'weibull':
                return self.get_weibull(dist_pars)
            case 'invgauss':
                return self.get_invgauss(dist_pars)
            case 'poisson':
                return self.get_poisson(dist_pars)
            case 'pareto':
                return self.get_pareto(dist_pars)
            case 'beta':
                return self.get_beta(dist_pars)
            case 'exponential':
                return self.get_exponential(dist_pars)


    def est_truncnorm(self, data, x0=None, bounds=None):
        """
        Parameters
        ----------
        data : list
            List containing observations.
            
        x0 : list
            Initial guess of parameters. 

        bounds : list
            Bounds on parameters. Should be specified as a sequence of
            ``(min, max)`` pairs for each unknown parameter. ``None`` is used to specify no bound. 
            
        Returns
        -------
        
        est: dictionary
            Dictionary containing params (list containing parameter estimates) and 
            log_likelihood (scalar representing log-likelihood of data at estimated
            parameters). 
        
        """
        def neg_ll(params):
            temp_dist = self.get_truncnorm({'mu': params[0], 'sigma': params[1], 'a': params[2], 'b': params[3]})
            val = np.sum(-temp_dist.logpdf(data))
            return val
        
        if x0 is None:
            x0 = [np.mean(data), np.std(data), max(0, np.min(data)-np.std(data)), np.max(data)+np.std(data)]
            
        if bounds is None:
            bounds = [(None, None), (None, None), (0, max(0, np.min(data)-0.0001)), (np.max(data), None)]
            
        res = minimize(neg_ll, x0=x0, bounds=bounds)

        return {'estimate': {'mu': res.x[0], 'sigma': res.x[1], 'a': res.x[2], 'b': res.x[3]}, 'log_likelihood': -res.fun} 


    def est_lognorm(self, data):
        """
        Parameters
        ----------
        data : list
            List containing observations.
            
        Returns
        -------
        
        est: dictionary
            Dictionary containing params (list containing parameter estimates) and 
            log_likelihood (scalar representing log-likelihood of data at estimated
            parameters). 
        
        """
        
        mu = np.mean(np.log(data))
        
        sigma = np.sqrt(np.sum(np.square(np.log(data)-mu))/(len(data)-1))
        
        est = self.get_lognorm({'mu': mu, 'sigma': sigma})
        log_likelihood = np.sum(est.logpdf(data))

        return {'estimate': {'mu': mu, 'sigma': sigma}, 'log_likelihood': log_likelihood}


    def est_gamma(self, data, x0=None, bounds=None):
        """
        Parameters
        ----------
        data : list
            List containing observations.
            
        x0 : list
            Initial guess of parameters. 

        bounds : list
            Bounds on parameters. Should be specified as a sequence of
            ``(min, max)`` pairs for each unknown parameter. ``None`` is used to specify no bound. 
            
        Returns
        -------
        
        est: dictionary
            Dictionary containing params (dict containing parameter estimates) and 
            log_likelihood (scalar representing log-likelihood of data at estimated
            parameters). 
        
        """
        def neg_ll(params):
            temp_dist = self.get_gamma({'shape': params[0], 'rate': params[1]})
            val = np.sum(-temp_dist.logpdf(data))
            return val

        if x0 is None:
            n = len(data)
            data_sum = np.sum(data)
            data_log_sum = np.sum(np.log(data))
            data_log_multiply_sum = np.sum(np.multiply(data, np.log(data)))
            shape_0 = n*data_sum/(n*data_log_multiply_sum - data_log_sum*data_sum)
            
            scale_0 = (n*data_log_multiply_sum - data_log_sum*data_sum)/(n**2)
            
            rate_0 = 1/scale_0
            
            x0 = [shape_0, rate_0]
            
        if bounds is None:
            bounds = [(0, None), (1e-10, None)]
            
        res = minimize(neg_ll, x0=x0, bounds=bounds)

        return {'estimate': {'shape': res.x[0], 'rate': res.x[1]}, 'log_likelihood': -res.fun} 


    def est_weibull(self, data, shape_0=None, bracket=None):
        """
        Parameters
        ----------
        data : list
            List containing observations.
            
        shape_0 : scalar
            Initial guess of shape parameter. 

        bracket : tuple
            Bracket containing shape parameter. Should be specified as a 
            ``[min, max]`` pair. ``None`` is used to specify no bound. 
            
        Returns
        -------
        
        est: dictionary
            Dictionary containing params (list containing parameter estimates) and 
            log_likelihood (scalar representing log-likelihood of data at estimated
            parameters). 
        
        """

        if shape_0 is None:
            shape_0 = 1 # This is an exponential distribution
        
        n = len(data)
        
        part1 = lambda shape_prop: np.sum(np.multiply(np.power(data, shape_prop), np.log(data)))
        
        part2 = lambda shape_prop: np.sum(np.power(data, shape_prop))
        
        part3 = lambda shape_prop: np.sum(np.log(data))
        
        def fun(shape_prop):
            return part1(shape_prop)/part2(shape_prop) - 1/shape_prop - part3(shape_prop)/n
            
        if bracket is None:
            sol = root_scalar(fun, x0=shape_0, x1=(shape_0+1))
        else:
            sol = root_scalar(fun, x0=shape_0, x1=(shape_0+1), bracket=bracket) 
        
        shape = sol.root
        
        scale = np.power(np.sum(np.power(data, shape))/n, 1/shape)

        est = self.get_weibull({'shape': shape, 'scale': scale})
        log_likelihood = np.sum(est.logpdf(data))    
        
        return {'estimate': {'shape': shape, 'scale': scale}, 'log_likelihood': log_likelihood}


    def est_invgauss(self, data, bound=None):
        """
        Parameters
        ----------
        data : list
            List containing observations.

        bound : list
            Bound on mu. Should be specified as a
            ``(min, max)`` pair. ``None`` is used to specify no bound. 
            
        Returns
        -------
        
        est: dictionary
            Dictionary containing params (list containing parameter estimates) and 
            log_likelihood (scalar representing log-likelihood of data at estimated
            parameters). 
        
        """
        def neg_ll(params):
            temp_dist = self.get_invgauss({'mu': params})
            val = np.sum(-temp_dist.logpdf(data))
            return val
            
        if bound is None:
            res = minimize_scalar(neg_ll)
        else:
            res = minimize_scalar(neg_ll, bounds=bound)

        return {'estimate': {'mu': res.x}, 'log_likelihood': -res.fun}


    def est_pareto(self, data):
        """
        Parameters
        ----------
        data : list
            List containing observations.
            
        Returns
        -------
        
        est: dictionary
            Dictionary containing params (list containing parameter estimates) and 
            log_likelihood (scalar representing log-likelihood of data at estimated
            parameters). 
        
        """
        
        m = min(data)
        
        rate = len(data)/np.sum(np.log(np.divide(data, m)))
        
        log_likelihood = np.sum(np.log(np.divide(rate*(m**rate), np.power(data, rate+1))))

        return {'estimate': {'minimum': m, 'rate': rate}, 'log_likelihood': log_likelihood}


    def est_ensemble(self, data):

        log_likelihoods = [-np.inf]

        # est0 = self.est_truncnorm(data)
        # log_likelihoods.append(est0['log_likelihood'])
        # param_estimates.append(est0['estimate'])

        # print(est0)

        est1 = self.est_lognorm(data)
        log_likelihoods.append(est1['log_likelihood'])

        # print(est1)

        est2 = self.est_gamma(data)
        log_likelihoods.append(est2['log_likelihood'])

        # print(est2)

        est3 = self.est_weibull(data)
        log_likelihoods.append(est3['log_likelihood'])

        # print(est3)

        est4 = self.est_invgauss(data)
        log_likelihoods.append(est4['log_likelihood'])

        # print(est4)

        est5 = self.est_pareto(data)
        log_likelihoods.append(est5['log_likelihood'])

        idx_max = np.argmax(log_likelihoods)

        match idx_max:
            case 0:
                est0['distribution'] = 'truncnorm'
                return est0
            case 1:
                est1['distribution'] = 'lognorm'
                return est1
            case 2:
                est2['distribution'] = 'gamma'
                return est2
            case 3:
                est3['distribution'] = 'weibull'
                return est3
            case 4:
                est4['distribution'] = 'invgauss'
                return est4
            case 5:
                est5['distribution'] = 'pareto'
                return est5

    def fit_CI(self, lb, ub, alpha, dist):
        """Fit parameters for a chosen distribution with specified alpha/2 and
        1-alpha/2 inverse cumulative distribution function values. 
        
        Parameters
        ----------
        lb : scalar
            Value of inverse cumulative distribution function at alpha/2.
        ub : scalar
            Value of inverse cumulative distribution function at 1-alpha/2.
        alpha : scalar
            Value between 0 and 1 giving the distribution mass outside of [lb, ub]. 
        dist : str
            Distribution being fitted. Must be one of 'beta', 'gamma', 'truncnorm', 
            'lognorm', 'uniform' or 'fixed'. 

        Return
        -------
        params : dict
            A dictionary of the parameters distribution found to best fit the
            desired settings. 

        """
        if dist == 'fixed':
            return {'value': (lb + ub) / 2}
        elif dist == 'uniform':
            return {'a':lb + 0.05*(ub-lb), 'b': lb + 0.95*(ub-lb)}

        bds = np.array([lb, ub])
        loss_measure = lambda x: np.sum(np.square(np.subtract(x, bds)))

        f1 = (ub - lb) / 4
        f2 = (lb + ub) / 2

        if dist == 'beta':
            params_mapper = lambda params: {'alpha': params[0], 'beta': params[1]}
            params0 = [2*f2/(1-f2), 2]
        elif dist == 'gamma':
            params_mapper = lambda params: {'shape': params[0], 'rate': params[1]}
            params0 = [(f2 / f1)**2, f2 / f1**2]
        elif dist == 'truncnorm':
            params_mapper = lambda params: {'a':0, 'b':np.inf, 'mu': params[0], 'sigma': params[1]}
            params0 = [f2, f1]
        elif dist == 'lognorm':
            params_mapper = lambda params: {'mu': params[0], 'sigma': params[1]}
            sigma0 = np.sqrt(np.log((f1/f2)**2 + 1))
            params0 = [np.log(f2)-sigma0**2/2, sigma0]
        else:
            raise TypeError("Argument of 'dist' is unknown, it must be one of 'beta', 'gamma', 'truncnorm', 'lognorm', 'uniform' or 'fixed'. ")

        loss_fun = lambda params: loss_measure([self.get_dist(dist, params_mapper(params)).ppf(alpha/2),
                                                self.get_dist(dist, params_mapper(params)).ppf(1-alpha/2)])

        sol = minimize(loss_fun, 
                       params0, 
                       bounds=[(1e-10, np.inf), (1e-10, np.inf)])

        return params_mapper(sol.x)
                    
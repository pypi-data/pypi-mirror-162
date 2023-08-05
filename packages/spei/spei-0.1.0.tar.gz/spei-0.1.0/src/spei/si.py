from pandas import Series
from numpy import linspace
from scipy.stats import norm, gamma, fisk
from .utils import check_series


def get_si_ppf(series, dist, sgi=False):

    check_series(series)

    si = Series(index=series.index, dtype='float')
    for month in range(1, 13):
        data = series[series.index.month == month].sort_values()
        if sgi:
            pmin = 1 / (2 * data.size)
            pmax = 1 - pmin
            cdf = linspace(pmin, pmax, data.size)
        else:
            *pars, loc, scale = dist.fit(data, scale=data.std())
            cdf = dist.cdf(data, pars, loc=loc, scale=scale)
        ppf = norm.ppf(cdf)
        si.loc[data.index] = ppf

    return si


def sgi(series):
    """Method to compute the Standardized Groundwater Index [sgi_2013]_.
    Same method as in Pastas.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the groundwater levels. Time series index
        should be a pandas DatetimeIndex.

    Returns
    -------
    pandas.Series

    References
    ----------
    .. [sgi_2013] Bloomfield, J. P. and Marchant, B. P.: Analysis of
       groundwater drought building on the standardised precipitation index
       approach. Hydrol. Earth Syst. Sci., 17, 4769–4787, 2013.
    """

    return get_si_ppf(series, None, sgi=True)


def spi(series, dist=None):
    """Method to compute the Standardized Precipitation Index [spi_2002]_.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats._continuous_distns
        Can be any continuous distribution from the scipy.stats library.
        However, for the SPI generally the Gamma probability density
        function is recommended. Other appropriate choices could be the
        lognormal, log-logistic or PearsonIII distribution.

    Returns
    -------
    pandas.Series

    References
    ----------
    .. [spi_2002] LLoyd-Hughes, B. and Saunders, M.A.: A drought
       climatology for Europe. International Journal of Climatology,
       22, 1571-1592, 2002.
    """

    if dist == None:
        dist = gamma

    return get_si_ppf(series, dist)


def spei(series, dist=None):
    """Method to compute the Standardized Precipitation Evaporation Index [spei_2010]_.

    Parameters
    ----------
    series: pandas.Series
        Pandas time series of the precipitation. Time series index
        should be a pandas DatetimeIndex.
    dist: scipy.stats._continuous_distns
        Can be any continuous distribution from the scipy.stats library.
        However, for the SPEI generally the log-logistic (fisk) probability
        density function is recommended. Other appropriate choices could be
        the lognormal or PearsonIII distribution.

    Returns
    -------
    pandas.Series

    References
    ----------
    .. [spei_2010] Vicente-Serrano S.M., Beguería S., López-Moreno J.I.:
       A Multi-scalar drought index sensitive to global warming: The
       Standardized Precipitation Evapotranspiration Index.
       Journal of Climate, 23, 1696-1718, 2010.
    """

    if dist == None:
        dist = fisk  # log-logistic

    return get_si_ppf(series, dist)

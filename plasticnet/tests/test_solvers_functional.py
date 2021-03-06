import numpy as np

from sklearn import linear_model
from sklearn.preprocessing import scale
from sklearn.datasets import make_regression

from plasticnet.solvers.functional import (
    ordinary_least_squares,
    ridge,
    lasso,
    elastic_net,
    general_plastic_net,
    plastic_ridge,
    plastic_lasso,
    hard_plastic_net,
    soft_plastic_net,
    unified_plastic_net,
)


def test_ordinary_least_squares_explicit(N=1500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test explicitly coded special case OLS numba code in :meth:`plasticnet.solvers.functional.ordinary_least_squares` against sklearn LinearRegression."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N, coef=True
    )
    X, y = scale(X), scale(y)

    lm = linear_model.LinearRegression()
    lm.fit(X, y)

    beta = ordinary_least_squares(X, y, tol=tol, max_iter=max_iter)

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_ridge_explicit(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test explicitly coded special case ridge numba code in :meth:`plasticnet.solvers.functional.ridge` against sklearn elastic net with l1_ratio=0."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()

    lm = linear_model.Ridge(alpha=lambda_total * N, tol=tol, max_iter=max_iter)
    lm.fit(X, y)

    beta = ridge(X, y, lambda_total=lambda_total, tol=tol, max_iter=max_iter)

    np.testing.assert_almost_equal(beta, lm.coef_, decimal=4)


def test_lasso_explicit(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test explicitly coded special case lasso numba code in :meth:`plasticnet.solvers.functional.lasso` against sklearn elastic net with `l1_ratio=1`."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=1.0, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)

    beta = lasso(X, y, lambda_total=lambda_total, tol=tol, max_iter=max_iter)

    np.testing.assert_almost_equal(beta, lm.coef_, decimal=4)


def test_elastic_net_explicit_ordinary_least_squares(
    N=1500, D=1000, tol=1e-12, max_iter=10000
):
    r"""Test explicitly coded special case elastic net with :math:`\lambda=0` in :meth:`plasticnet.solvers.functional.elastic_net` against sklearn LinearRegression."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N, coef=True
    )
    X, y = scale(X), scale(y)

    lm = linear_model.LinearRegression()
    lm.fit(X, y)

    beta = elastic_net(X, y, lambda_total=0.0, alpha=0.0, tol=tol, max_iter=max_iter)

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_elastic_net_explicit(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test explicitly coded elastic net in :meth:`plasticnet.solvers.functional.elastic_net` against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    alpha = np.random.rand()

    elastic_net_lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    elastic_net_lm.fit(X, y)

    beta = elastic_net(
        X, y, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(elastic_net_lm.coef_, beta, decimal=4)


def test_ordinary_least_squares_general(N=1500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test OLS (:math:`\lambda=0` in :meth:`plasticnet.solvers.functional.general_plastic_net`) against sklearn LinearRegression."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = 0.0
    alpha = 0.0
    xi = np.zeros(D, dtype=np.float64)
    zeta = np.zeros(D, dtype=np.float64)

    lm = linear_model.LinearRegression()
    lm.fit(X, y)

    beta = general_plastic_net(
        X,
        y,
        xi,
        zeta,
        lambda_total=lambda_total,
        alpha=alpha,
        tol=tol,
        max_iter=max_iter,
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_elastic_net_general(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test elastic net (:math:`\xi=0` and :math:`\zeta=0` in :meth:`plasticnet.solvers.functional.general_plastic_net`) against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    alpha = np.random.rand()
    xi = np.zeros(D, dtype=np.float64)
    zeta = np.zeros(D, dtype=np.float64)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)

    beta = general_plastic_net(
        X,
        y,
        xi,
        zeta,
        lambda_total=lambda_total,
        alpha=alpha,
        tol=tol,
        max_iter=max_iter,
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_plastic_ridge_trivial(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test plastic ridge(:math:`\zeta=0` in :meth:`plasticnet.solvers.functional.plastic_ridge`) against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    zeta = np.zeros(D, dtype=np.float64)

    lm = linear_model.Ridge(alpha=lambda_total * N, tol=tol, max_iter=max_iter)
    lm.fit(X, y)

    beta = plastic_ridge(
        X, y, zeta, lambda_total=lambda_total, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_plastic_ridge_real(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test :meth:`plasticnet.solvers.functional.plastic_ridge` against sklearn ElasticNet with transformed variables."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    zeta = np.random.randn(D).astype(np.float64)

    X_prime = X
    y_prime = y - np.dot(X, zeta)

    lm = linear_model.Ridge(alpha=lambda_total * N, tol=tol, max_iter=max_iter)
    lm.fit(X_prime, y_prime)
    beta_lm = lm.coef_ + zeta

    beta = plastic_ridge(
        X, y, zeta, lambda_total=lambda_total, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)


def test_plastic_lasso_trivial(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test plastic lasso (:math:`\xi=0` in :meth:`plasticnet.solvers.functional.plastic_lasso`) against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    xi = np.zeros(D, dtype=np.float64)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=1, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)

    beta = plastic_lasso(
        X, y, xi, lambda_total=lambda_total, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_plastic_lasso_real(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test :meth:`plasticnet.solvers.functional.plastic_lasso` against sklearn ElasticNet with transformed variables."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    xi = np.random.randn(D).astype(np.float64)

    X_prime = X
    y_prime = y - np.dot(X, xi)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=1, tol=tol, max_iter=max_iter
    )
    lm.fit(X_prime, y_prime)
    beta_lm = lm.coef_ + xi

    beta = plastic_lasso(
        X, y, xi, lambda_total=lambda_total, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)


def test_hard_plastic_net_trivial(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test hard plastic net (:math:`\xi=0` and in :meth:`plasticnet.solvers.functional.hard_plastic_net`) against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    alpha = np.random.rand()
    xi = np.zeros(D, dtype=np.float64)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)

    beta = hard_plastic_net(
        X, y, xi, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_hard_plastic_net_limiting_cases(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test hard plastic net :meth:`plasticnet.solvers.functional.hard_plastic_net` against sklearn ElasticNet in limiting cases."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    xi = np.random.randn(D).astype(np.float64)

    X_prime = X
    y_prime = y - np.dot(X, xi)

    alpha = 1.0

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X_prime, y_prime)
    beta_lm = lm.coef_ + xi

    beta = hard_plastic_net(
        X, y, xi, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)

    alpha = 0.0

    lm = linear_model.Ridge(alpha=lambda_total * N, tol=tol, max_iter=max_iter)
    lm.fit(X, y)

    beta_lm = lm.coef_

    beta = hard_plastic_net(
        X, y, xi, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)


def test_soft_plastic_net_trivial(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test soft plastic net (:math:`\zeta=0` in :meth:`plasticnet.solvers.functional.soft_plastic_net`) against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    alpha = np.random.rand()
    zeta = np.zeros(D, dtype=np.float64)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)

    beta = soft_plastic_net(
        X, y, zeta, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_soft_plastic_net_limiting_cases(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test :meth:`plasticnet.solvers.functional.soft_plastic_net` against sklearn ElasticNet in limiting cases."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    zeta = np.random.randn(D).astype(np.float64)

    alpha = 1.0

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)
    beta_lm = lm.coef_

    beta = soft_plastic_net(
        X, y, zeta, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)

    alpha = 0.0

    X_prime = X
    y_prime = y - np.dot(X, zeta)

    lm = linear_model.Ridge(alpha=lambda_total * N, tol=tol, max_iter=max_iter)
    lm.fit(X_prime, y_prime)

    beta_lm = lm.coef_ + zeta

    beta = soft_plastic_net(
        X, y, zeta, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)


def test_unified_plastic_net_trivial(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test unified plastic net (:math:`\xi=0` in :meth:`plasticnet.solvers.functional.unified_plastic_net`) against sklearn ElasticNet."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    alpha = np.random.rand()
    xi = np.zeros(D, dtype=np.float64)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X, y)

    beta = unified_plastic_net(
        X, y, xi, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(lm.coef_, beta, decimal=4)


def test_unified_plastic_net_real(N=500, D=1000, tol=1e-12, max_iter=10000):
    r"""Test :meth:`plasticnet.solvers.functional.unified_plastic_net` against sklearn ElasticNet with transformed variables."""

    X, y, beta_true = make_regression(
        n_samples=N, n_features=D, n_informative=N // 10, coef=True
    )
    X, y = scale(X), scale(y)

    lambda_total = np.random.exponential()
    alpha = np.random.rand()
    xi = np.random.randn(D).astype(np.float64)

    X_prime = X
    y_prime = y - np.dot(X, xi)

    lm = linear_model.ElasticNet(
        alpha=lambda_total, l1_ratio=alpha, tol=tol, max_iter=max_iter
    )
    lm.fit(X_prime, y_prime)
    beta_lm = lm.coef_ + xi

    beta = unified_plastic_net(
        X, y, xi, lambda_total=lambda_total, alpha=alpha, tol=tol, max_iter=max_iter
    )

    np.testing.assert_almost_equal(beta_lm, beta, decimal=4)

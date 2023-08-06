"""Long double precision"""
from __future__ import annotations
import _alpaqa_d.longdouble
import typing

__all__ = [
    "ALMParams",
    "ALMSolver",
    "Box",
    "CountedProblem",
    "FunctionalProblem",
    "InnerSolver",
    "LBFGS",
    "LipschitzEstimateParams",
    "PANOCDirection",
    "PANOCParams",
    "PANOCProgressInfo",
    "PANOCSolver",
    "Problem",
    "ProblemBase",
    "StructuredPANOCLBFGSParams",
    "StructuredPANOCLBFGSProgressInfo",
    "StructuredPANOCLBFGSSolver",
    "with_counters"
]


class ALMParams():
    """
    C++ documentation: :cpp:class:`alpaqa::ALMParams`
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, **kwargs) -> None: ...
    def to_dict(self) -> dict: ...
    @property
    def M(self) -> float:
        """
        :type: float
        """
    @M.setter
    def M(self, arg0: float) -> None:
        pass
    @property
    def max_iter(self) -> int:
        """
        :type: int
        """
    @max_iter.setter
    def max_iter(self, arg0: int) -> None:
        pass
    @property
    def max_num_initial_retries(self) -> int:
        """
        :type: int
        """
    @max_num_initial_retries.setter
    def max_num_initial_retries(self, arg0: int) -> None:
        pass
    @property
    def max_num_retries(self) -> int:
        """
        :type: int
        """
    @max_num_retries.setter
    def max_num_retries(self, arg0: int) -> None:
        pass
    @property
    def max_time(self) -> datetime.timedelta:
        """
        :type: datetime.timedelta
        """
    @max_time.setter
    def max_time(self, arg0: datetime.timedelta) -> None:
        pass
    @property
    def max_total_num_retries(self) -> int:
        """
        :type: int
        """
    @max_total_num_retries.setter
    def max_total_num_retries(self, arg0: int) -> None:
        pass
    @property
    def print_interval(self) -> int:
        """
        :type: int
        """
    @print_interval.setter
    def print_interval(self, arg0: int) -> None:
        pass
    @property
    def single_penalty_factor(self) -> bool:
        """
        :type: bool
        """
    @single_penalty_factor.setter
    def single_penalty_factor(self, arg0: bool) -> None:
        pass
    @property
    def Δ(self) -> float:
        """
        :type: float
        """
    @Δ.setter
    def Δ(self, arg0: float) -> None:
        pass
    @property
    def Δ_lower(self) -> float:
        """
        :type: float
        """
    @Δ_lower.setter
    def Δ_lower(self, arg0: float) -> None:
        pass
    @property
    def Δ_min(self) -> float:
        """
        :type: float
        """
    @Δ_min.setter
    def Δ_min(self, arg0: float) -> None:
        pass
    @property
    def Σ_0(self) -> float:
        """
        :type: float
        """
    @Σ_0.setter
    def Σ_0(self, arg0: float) -> None:
        pass
    @property
    def Σ_0_lower(self) -> float:
        """
        :type: float
        """
    @Σ_0_lower.setter
    def Σ_0_lower(self, arg0: float) -> None:
        pass
    @property
    def Σ_max(self) -> float:
        """
        :type: float
        """
    @Σ_max.setter
    def Σ_max(self, arg0: float) -> None:
        pass
    @property
    def Σ_min(self) -> float:
        """
        :type: float
        """
    @Σ_min.setter
    def Σ_min(self, arg0: float) -> None:
        pass
    @property
    def δ(self) -> float:
        """
        :type: float
        """
    @δ.setter
    def δ(self, arg0: float) -> None:
        pass
    @property
    def ε(self) -> float:
        """
        :type: float
        """
    @ε.setter
    def ε(self, arg0: float) -> None:
        pass
    @property
    def ε_0(self) -> float:
        """
        :type: float
        """
    @ε_0.setter
    def ε_0(self, arg0: float) -> None:
        pass
    @property
    def ε_0_increase(self) -> float:
        """
        :type: float
        """
    @ε_0_increase.setter
    def ε_0_increase(self, arg0: float) -> None:
        pass
    @property
    def θ(self) -> float:
        """
        :type: float
        """
    @θ.setter
    def θ(self, arg0: float) -> None:
        pass
    @property
    def ρ(self) -> float:
        """
        :type: float
        """
    @ρ.setter
    def ρ(self, arg0: float) -> None:
        pass
    @property
    def ρ_increase(self) -> float:
        """
        :type: float
        """
    @ρ_increase.setter
    def ρ_increase(self, arg0: float) -> None:
        pass
    @property
    def ρ_max(self) -> float:
        """
        :type: float
        """
    @ρ_max.setter
    def ρ_max(self, arg0: float) -> None:
        pass
    @property
    def σ_0(self) -> float:
        """
        :type: float
        """
    @σ_0.setter
    def σ_0(self, arg0: float) -> None:
        pass
    pass
class ALMSolver():
    """
    Main augmented Lagrangian solver.

    C++ documentation: :cpp:class:`alpaqa::ALMSolver`
    """
    def __call__(self, problem: ProblemBase, x: typing.Optional[numpy.ndarray] = None, y: typing.Optional[numpy.ndarray] = None) -> typing.Tuple[numpy.ndarray, numpy.ndarray, dict]: 
        """
        Solve.

        :param problem: Problem to solve.
        :param x: Initial guess for decision variables :math:`x`

        :param y: Initial guess for Lagrange multipliers :math:`y`
        :return: * Solution :math:`x`
                 * Lagrange multipliers :math:`y` at the solution
                 * Statistics
        """
    @typing.overload
    def __init__(self) -> None: 
        """
        Build an ALM solver using Structured PANOC as inner solver.

        Build an ALM solver using PANOC as inner solver.

        Build an ALM solver using Structured PANOC as inner solver.

        Build an ALM solver using PANOC as inner solver.

        Build an ALM solver using Structured PANOC as inner solver.
        """
    @typing.overload
    def __init__(self, alm_params: typing.Union[ALMParams, dict], inner_solver: PANOCSolver) -> None: ...
    @typing.overload
    def __init__(self, alm_params: typing.Union[ALMParams, dict], inner_solver: StructuredPANOCLBFGSSolver) -> None: ...
    @typing.overload
    def __init__(self, inner_solver: PANOCSolver) -> None: ...
    @typing.overload
    def __init__(self, inner_solver: StructuredPANOCLBFGSSolver) -> None: ...
    def __str__(self) -> str: ...
    @property
    def inner_solver(self) -> InnerSolver:
        """
        :type: InnerSolver
        """
    @property
    def params(self) -> ALMParams:
        """
        :type: ALMParams
        """
    pass
class Box():
    """
    C++ documentation: :cpp:class:`alpaqa::Box`
    """
    @typing.overload
    def __init__(self, n: int) -> None: 
        """
        Create an :math:`n`-dimensional box at with bounds at :math:`\pm\infty` (no constraints).

        Create a box with the given bounds.
        """
    @typing.overload
    def __init__(self, ub: numpy.ndarray, lb: numpy.ndarray) -> None: ...
    @property
    def lowerbound(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @lowerbound.setter
    def lowerbound(self, arg0: numpy.ndarray) -> None:
        pass
    @property
    def upperbound(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @upperbound.setter
    def upperbound(self, arg0: numpy.ndarray) -> None:
        pass
    pass
class ProblemBase():
    def __copy__(self) -> ProblemBase: ...
    def __deepcopy__(self, arg0: dict) -> ProblemBase: ...
    def eval_f(self, x: numpy.ndarray) -> float: ...
    @typing.overload
    def eval_g(self, x: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def eval_g(self, x: numpy.ndarray, gx: numpy.ndarray) -> None: ...
    @typing.overload
    def eval_grad_f(self, x: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def eval_grad_f(self, x: numpy.ndarray, grad_fx: numpy.ndarray) -> None: ...
    @typing.overload
    def eval_grad_g_prod(self, x: numpy.ndarray, y: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def eval_grad_g_prod(self, x: numpy.ndarray, y: numpy.ndarray, grad_gxy: numpy.ndarray) -> None: ...
    @typing.overload
    def eval_grad_ψ(self, x: numpy.ndarray, y: numpy.ndarray, Σ: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def eval_grad_ψ(self, x: numpy.ndarray, y: numpy.ndarray, Σ: numpy.ndarray, grad_ψ: numpy.ndarray, work_n: numpy.ndarray, work_m: numpy.ndarray) -> None: ...
    @typing.overload
    def eval_grad_ψ_from_ŷ(self, x: numpy.ndarray, ŷ: numpy.ndarray) -> numpy.ndarray: ...
    @typing.overload
    def eval_grad_ψ_from_ŷ(self, x: numpy.ndarray, ŷ: numpy.ndarray, grad_ψ: numpy.ndarray, work_n: numpy.ndarray) -> None: ...
    @typing.overload
    def eval_ψ_grad_ψ(self, x: numpy.ndarray, y: numpy.ndarray, Σ: numpy.ndarray) -> typing.Tuple[float, numpy.ndarray]: ...
    @typing.overload
    def eval_ψ_grad_ψ(self, x: numpy.ndarray, y: numpy.ndarray, Σ: numpy.ndarray, grad_ψ: numpy.ndarray, work_n: numpy.ndarray, work_m: numpy.ndarray) -> float: ...
    @typing.overload
    def eval_ψ_ŷ(self, x: numpy.ndarray, y: numpy.ndarray, Σ: numpy.ndarray) -> typing.Tuple[float, numpy.ndarray]: ...
    @typing.overload
    def eval_ψ_ŷ(self, x: numpy.ndarray, y: numpy.ndarray, Σ: numpy.ndarray, ŷ: numpy.ndarray) -> float: ...
    @property
    def m(self) -> int:
        """
        Number of general constraints, dimension of :math:`g(x)`

        :type: int
        """
    @m.setter
    def m(self, arg0: int) -> None:
        """
        Number of general constraints, dimension of :math:`g(x)`
        """
    @property
    def n(self) -> int:
        """
        Number of unknowns, dimension of :math:`x`

        :type: int
        """
    @n.setter
    def n(self, arg0: int) -> None:
        """
        Number of unknowns, dimension of :math:`x`
        """
    pass
class Problem(ProblemBase):
    """
    C++ documentation: :cpp:class:`alpaqa::Problem`
    """
    def __init__(self, n: int, m: int, p: int = 0) -> None: 
        """
        :param n: Number of unknowns
        :param m: Number of constraints
        :param p: Number of parameters
        """
    @property
    def C(self) -> Box:
        """
        Box constraints on :math:`x`

        :type: Box
        """
    @C.setter
    def C(self, arg0: Box) -> None:
        """
        Box constraints on :math:`x`
        """
    @property
    def D(self) -> Box:
        """
        Box constraints on :math:`g(x)`

        :type: Box
        """
    @D.setter
    def D(self, arg0: Box) -> None:
        """
        Box constraints on :math:`g(x)`
        """
    @property
    def param(self) -> numpy.ndarray:
        """
        Parameter vector :math:`p` of the problem

        :type: numpy.ndarray
        """
    @param.setter
    def param(self, arg1: numpy.ndarray) -> None:
        """
        Parameter vector :math:`p` of the problem
        """
    pass
class InnerSolver():
    def __call__(self, arg0: ProblemBase, arg1: numpy.ndarray, arg2: float, arg3: bool, arg4: numpy.ndarray, arg5: numpy.ndarray, arg6: numpy.ndarray) -> dict: ...
    def __init__(self, arg0: PANOCSolver) -> None: ...
    @property
    def name(self) -> str:
        """
        :type: str
        """
    pass
class LBFGS():
    """
    C++ documentation :cpp:class:`alpaqa::LBFGS`
    """
    class Params():
        """
        C++ documentation :cpp:class:`alpaqa::LBFGSParams`
        """
        class CBFGS():
            """
            C++ documentation :cpp:class:`alpaqa::CBFGSParams`
            """
            @typing.overload
            def __init__(self) -> None: ...
            @typing.overload
            def __init__(self, **kwargs) -> None: ...
            def to_dict(self) -> dict: ...
            @property
            def α(self) -> float:
                """
                :type: float
                """
            @α.setter
            def α(self, arg0: float) -> None:
                pass
            @property
            def ϵ(self) -> float:
                """
                :type: float
                """
            @ϵ.setter
            def ϵ(self, arg0: float) -> None:
                pass
            pass
        @typing.overload
        def __init__(self) -> None: ...
        @typing.overload
        def __init__(self, **kwargs) -> None: ...
        def to_dict(self) -> dict: ...
        @property
        def cbfgs(self) -> LBFGS.Params.CBFGS:
            """
            :type: LBFGS.Params.CBFGS
            """
        @cbfgs.setter
        def cbfgs(self, arg0: LBFGS.Params.CBFGS) -> None:
            pass
        @property
        def memory(self) -> int:
            """
            :type: int
            """
        @memory.setter
        def memory(self, arg0: int) -> None:
            pass
        pass
    class Sign():
        """
        C++ documentation :cpp:enum:`alpaqa::LBFGS::Sign`

        Members:

          Positive

          Negative
        """
        def __eq__(self, other: object) -> bool: ...
        def __getstate__(self) -> int: ...
        def __hash__(self) -> int: ...
        def __index__(self) -> int: ...
        def __init__(self, value: int) -> None: ...
        def __int__(self) -> int: ...
        def __ne__(self, other: object) -> bool: ...
        def __repr__(self) -> str: ...
        def __setstate__(self, state: int) -> None: ...
        @property
        def name(self) -> str:
            """
            :type: str
            """
        @property
        def value(self) -> int:
            """
            :type: int
            """
        Negative: _alpaqa_d.longdouble.LBFGS.Sign # value = <Sign.Negative: 1>
        Positive: _alpaqa_d.longdouble.LBFGS.Sign # value = <Sign.Positive: 0>
        __members__: dict # value = {'Positive': <Sign.Positive: 0>, 'Negative': <Sign.Negative: 1>}
        pass
    @typing.overload
    def __init__(self, params: typing.Union[LBFGS.Params, dict]) -> None: ...
    @typing.overload
    def __init__(self, params: typing.Union[LBFGS.Params, dict], n: int) -> None: ...
    def __str__(self) -> str: ...
    def apply(self, q: numpy.ndarray, γ: float) -> bool: ...
    def apply_masked(self, q: numpy.ndarray, γ: float, J: typing.List[int]) -> bool: ...
    def current_history(self) -> int: ...
    def reset(self) -> None: ...
    def resize(self, n: int) -> None: ...
    def s(self, i: int) -> numpy.ndarray: ...
    def scale_y(self, factor: float) -> None: ...
    def update(self, xk: numpy.ndarray, xkp1: numpy.ndarray, pk: numpy.ndarray, pkp1: numpy.ndarray, sign: LBFGS.Sign = Sign.Positive, forced: bool = False) -> bool: ...
    def update_sy(self, sk: numpy.ndarray, yk: numpy.ndarray, pkp1Tpkp1: float, forced: bool = False) -> bool: ...
    @staticmethod
    def update_valid(params: LBFGS.Params, yᵀs: float, sᵀs: float, pᵀp: float) -> bool: ...
    def y(self, i: int) -> numpy.ndarray: ...
    def α(self, i: int) -> float: ...
    def ρ(self, i: int) -> float: ...
    @property
    def n(self) -> int:
        """
        :type: int
        """
    @property
    def params(self) -> LBFGS.Params:
        """
        :type: LBFGS.Params
        """
    Negative: _alpaqa_d.longdouble.LBFGS.Sign # value = <Sign.Negative: 1>
    Positive: _alpaqa_d.longdouble.LBFGS.Sign # value = <Sign.Positive: 0>
    pass
class LipschitzEstimateParams():
    """
    C++ documentation: :cpp:class:`alpaqa::LipschitzEstimateParams`
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, **kwargs) -> None: ...
    def to_dict(self) -> dict: ...
    @property
    def L_0(self) -> float:
        """
        :type: float
        """
    @L_0.setter
    def L_0(self, arg0: float) -> None:
        pass
    @property
    def Lγ_factor(self) -> float:
        """
        :type: float
        """
    @Lγ_factor.setter
    def Lγ_factor(self, arg0: float) -> None:
        pass
    @property
    def δ(self) -> float:
        """
        :type: float
        """
    @δ.setter
    def δ(self, arg0: float) -> None:
        pass
    @property
    def ε(self) -> float:
        """
        :type: float
        """
    @ε.setter
    def ε(self, arg0: float) -> None:
        pass
    pass
class PANOCDirection():
    def __str__(self) -> str: ...
    pass
class PANOCParams():
    """
    C++ documentation: :cpp:class:`alpaqa::PANOCParams`
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, **kwargs) -> None: ...
    def to_dict(self) -> dict: ...
    @property
    def L_max(self) -> float:
        """
        :type: float
        """
    @L_max.setter
    def L_max(self, arg0: float) -> None:
        pass
    @property
    def L_min(self) -> float:
        """
        :type: float
        """
    @L_min.setter
    def L_min(self, arg0: float) -> None:
        pass
    @property
    def Lipschitz(self) -> LipschitzEstimateParams:
        """
        :type: LipschitzEstimateParams
        """
    @Lipschitz.setter
    def Lipschitz(self, arg0: LipschitzEstimateParams) -> None:
        pass
    @property
    def alternative_linesearch_cond(self) -> bool:
        """
        :type: bool
        """
    @alternative_linesearch_cond.setter
    def alternative_linesearch_cond(self, arg0: bool) -> None:
        pass
    @property
    def lbfgs_stepsize(self) -> _alpaqa_d.LBFGSStepsize:
        """
        :type: _alpaqa_d.LBFGSStepsize
        """
    @lbfgs_stepsize.setter
    def lbfgs_stepsize(self, arg0: _alpaqa_d.LBFGSStepsize) -> None:
        pass
    @property
    def max_iter(self) -> int:
        """
        :type: int
        """
    @max_iter.setter
    def max_iter(self, arg0: int) -> None:
        pass
    @property
    def max_no_progress(self) -> int:
        """
        :type: int
        """
    @max_no_progress.setter
    def max_no_progress(self, arg0: int) -> None:
        pass
    @property
    def max_time(self) -> std::__1::chrono::duration<long long, std::__1::ratio<1l, 1000000l> >:
        """
        :type: std::__1::chrono::duration<long long, std::__1::ratio<1l, 1000000l> >
        """
    @max_time.setter
    def max_time(self, arg0: std::__1::chrono::duration<long long, std::__1::ratio<1l, 1000000l> >) -> None:
        pass
    @property
    def print_interval(self) -> int:
        """
        :type: int
        """
    @print_interval.setter
    def print_interval(self, arg0: int) -> None:
        pass
    @property
    def print_precision(self) -> int:
        """
        :type: int
        """
    @print_precision.setter
    def print_precision(self, arg0: int) -> None:
        pass
    @property
    def quadratic_upperbound_tolerance_factor(self) -> float:
        """
        :type: float
        """
    @quadratic_upperbound_tolerance_factor.setter
    def quadratic_upperbound_tolerance_factor(self, arg0: float) -> None:
        pass
    @property
    def stop_crit(self) -> _alpaqa_d.PANOCStopCrit:
        """
        :type: _alpaqa_d.PANOCStopCrit
        """
    @stop_crit.setter
    def stop_crit(self, arg0: _alpaqa_d.PANOCStopCrit) -> None:
        pass
    @property
    def update_lipschitz_in_linesearch(self) -> bool:
        """
        :type: bool
        """
    @update_lipschitz_in_linesearch.setter
    def update_lipschitz_in_linesearch(self, arg0: bool) -> None:
        pass
    @property
    def τ_min(self) -> float:
        """
        :type: float
        """
    @τ_min.setter
    def τ_min(self, arg0: float) -> None:
        pass
    pass
class PANOCProgressInfo():
    """
    Data passed to the PANOC progress callback.

    C++ documentation: :cpp:class:`alpaqa::PANOCProgressInfo`
    """
    @property
    def L(self) -> float:
        """
        Estimate of Lipschitz constant of objective :math:`L`

        :type: float
        """
    @property
    def fpr(self) -> float:
        """
        Fixed-point residual :math:`\left\|p\right\| / \gamma`

        :type: float
        """
    @property
    def grad_ψ(self) -> numpy.ndarray:
        """
        Gradient of objective :math:`\nabla\psi(x)`

        :type: numpy.ndarray
        """
    @property
    def grad_ψ_hat(self) -> numpy.ndarray:
        """
        Gradient of objective at x̂ :math:`\nabla\psi(\hat x)`

        :type: numpy.ndarray
        """
    @property
    def k(self) -> int:
        """
        Iteration

        :type: int
        """
    @property
    def norm_sq_p(self) -> float:
        """
        :math:`\left\|p\right\|^2`

        :type: float
        """
    @property
    def p(self) -> numpy.ndarray:
        """
        Projected gradient step :math:`p`

        :type: numpy.ndarray
        """
    @property
    def params(self) -> PANOCParams:
        """
        Solver parameters

        :type: PANOCParams
        """
    @property
    def problem(self) -> ProblemBase:
        """
        Problem being solved

        :type: ProblemBase
        """
    @property
    def x(self) -> numpy.ndarray:
        """
        Decision variable :math:`x`

        :type: numpy.ndarray
        """
    @property
    def x̂(self) -> numpy.ndarray:
        """
        Decision variable after projected gradient step :math:`\hat x`

        :type: numpy.ndarray
        """
    @property
    def y(self) -> numpy.ndarray:
        """
        Lagrange multipliers :math:`y`

        :type: numpy.ndarray
        """
    @property
    def Σ(self) -> numpy.ndarray:
        """
        Penalty factor :math:`\Sigma`

        :type: numpy.ndarray
        """
    @property
    def γ(self) -> float:
        """
        Step size :math:`\gamma`

        :type: float
        """
    @property
    def ε(self) -> float:
        """
        Tolerance reached :math:`\varepsilon_k`

        :type: float
        """
    @property
    def τ(self) -> float:
        """
        Line search parameter :math:`\tau`

        :type: float
        """
    @property
    def φγ(self) -> float:
        """
        Forward-backward envelope :math:`\varphi_\gamma(x)`

        :type: float
        """
    @property
    def ψ(self) -> float:
        """
        Objective value :math:`\psi(x)`

        :type: float
        """
    @property
    def ψ_hat(self) -> float:
        """
        Objective at x̂ :math:`\psi(\hat x)`

        :type: float
        """
    pass
class PANOCSolver():
    """
    C++ documentation: :cpp:class:`alpaqa::PANOCSolver`
    """
    @typing.overload
    def __init__(self, panoc_params: typing.Union[PANOCParams, dict] = {}, lbfgs_params: typing.Union[LBFGS.Params, dict] = {}) -> None: 
        """
        Create a PANOC solver using L-BFGS directions.

        Create a PANOC solver using L-BFGS directions.
        """
    @typing.overload
    def __init__(self, panoc_params: typing.Union[PANOCParams, dict], LBFGS: LBFGS) -> None: ...
    def set_progress_callback(self, callback: typing.Callable[[PANOCProgressInfo], None]) -> PANOCSolver: 
        """
        Specify a callable that is invoked with some intermediate results on each iteration of the algorithm.
        """
    pass
class FunctionalProblem(Problem, ProblemBase):
    """
    C++ documentation: :cpp:class:`alpaqa::FunctionalProblem`
    """
    def __init__(self, n: int, m: int, p: int = 0) -> None: 
        """
        :param n: Number of unknowns
        :param m: Number of constraints
        :param p: Number of parameters
        """
    @property
    def f(self) -> object:
        """
        :type: object
        """
    @f.setter
    def f(self, arg1: typing.Optional[object]) -> None:
        pass
    @property
    def g(self) -> object:
        """
        :type: object
        """
    @g.setter
    def g(self, arg1: typing.Optional[object]) -> None:
        pass
    @property
    def grad_f(self) -> object:
        """
        :type: object
        """
    @grad_f.setter
    def grad_f(self, arg1: typing.Optional[object]) -> None:
        pass
    @property
    def grad_g_prod(self) -> object:
        """
        :type: object
        """
    @grad_g_prod.setter
    def grad_g_prod(self, arg1: typing.Optional[object]) -> None:
        pass
    @property
    def grad_gi(self) -> object:
        """
        :type: object
        """
    @grad_gi.setter
    def grad_gi(self, arg1: typing.Optional[object]) -> None:
        pass
    @property
    def hess_L(self) -> object:
        """
        :type: object
        """
    @hess_L.setter
    def hess_L(self, arg1: typing.Optional[object]) -> None:
        pass
    @property
    def hess_L_prod(self) -> object:
        """
        :type: object
        """
    @hess_L_prod.setter
    def hess_L_prod(self, arg1: typing.Optional[object]) -> None:
        pass
    pass
class CountedProblem(ProblemBase):
    """
    C++ documentation: :cpp:class:`alpaqa::WrappedProblemWithCounters`
    """
    @property
    def evaluations(self) -> _alpaqa_d.EvalCounter:
        """
        :type: _alpaqa_d.EvalCounter
        """
    @evaluations.setter
    def evaluations(self, arg0: _alpaqa_d.EvalCounter) -> None:
        pass
    pass
class StructuredPANOCLBFGSParams():
    """
    C++ documentation: :cpp:class:`alpaqa::StructuredPANOCLBFGSParams`
    """
    @typing.overload
    def __init__(self) -> None: ...
    @typing.overload
    def __init__(self, **kwargs) -> None: ...
    def to_dict(self) -> dict: ...
    @property
    def L_max(self) -> float:
        """
        :type: float
        """
    @L_max.setter
    def L_max(self, arg0: float) -> None:
        pass
    @property
    def L_min(self) -> float:
        """
        :type: float
        """
    @L_min.setter
    def L_min(self, arg0: float) -> None:
        pass
    @property
    def Lipschitz(self) -> LipschitzEstimateParams:
        """
        :type: LipschitzEstimateParams
        """
    @Lipschitz.setter
    def Lipschitz(self, arg0: LipschitzEstimateParams) -> None:
        pass
    @property
    def alternative_linesearch_cond(self) -> bool:
        """
        :type: bool
        """
    @alternative_linesearch_cond.setter
    def alternative_linesearch_cond(self, arg0: bool) -> None:
        pass
    @property
    def fpr_shortcut_accept_factor(self) -> float:
        """
        :type: float
        """
    @fpr_shortcut_accept_factor.setter
    def fpr_shortcut_accept_factor(self, arg0: float) -> None:
        pass
    @property
    def fpr_shortcut_history(self) -> int:
        """
        :type: int
        """
    @fpr_shortcut_history.setter
    def fpr_shortcut_history(self, arg0: int) -> None:
        pass
    @property
    def full_augmented_hessian(self) -> bool:
        """
        :type: bool
        """
    @full_augmented_hessian.setter
    def full_augmented_hessian(self, arg0: bool) -> None:
        pass
    @property
    def hessian_vec(self) -> bool:
        """
        :type: bool
        """
    @hessian_vec.setter
    def hessian_vec(self, arg0: bool) -> None:
        pass
    @property
    def hessian_vec_finite_differences(self) -> bool:
        """
        :type: bool
        """
    @hessian_vec_finite_differences.setter
    def hessian_vec_finite_differences(self, arg0: bool) -> None:
        pass
    @property
    def lbfgs_stepsize(self) -> _alpaqa_d.LBFGSStepsize:
        """
        :type: _alpaqa_d.LBFGSStepsize
        """
    @lbfgs_stepsize.setter
    def lbfgs_stepsize(self, arg0: _alpaqa_d.LBFGSStepsize) -> None:
        pass
    @property
    def max_iter(self) -> int:
        """
        :type: int
        """
    @max_iter.setter
    def max_iter(self, arg0: int) -> None:
        pass
    @property
    def max_no_progress(self) -> int:
        """
        :type: int
        """
    @max_no_progress.setter
    def max_no_progress(self, arg0: int) -> None:
        pass
    @property
    def max_time(self) -> std::__1::chrono::duration<long long, std::__1::ratio<1l, 1000000l> >:
        """
        :type: std::__1::chrono::duration<long long, std::__1::ratio<1l, 1000000l> >
        """
    @max_time.setter
    def max_time(self, arg0: std::__1::chrono::duration<long long, std::__1::ratio<1l, 1000000l> >) -> None:
        pass
    @property
    def nonmonotone_linesearch(self) -> float:
        """
        :type: float
        """
    @nonmonotone_linesearch.setter
    def nonmonotone_linesearch(self, arg0: float) -> None:
        pass
    @property
    def print_interval(self) -> int:
        """
        :type: int
        """
    @print_interval.setter
    def print_interval(self, arg0: int) -> None:
        pass
    @property
    def print_precision(self) -> int:
        """
        :type: int
        """
    @print_precision.setter
    def print_precision(self, arg0: int) -> None:
        pass
    @property
    def quadratic_upperbound_tolerance_factor(self) -> float:
        """
        :type: float
        """
    @quadratic_upperbound_tolerance_factor.setter
    def quadratic_upperbound_tolerance_factor(self, arg0: float) -> None:
        pass
    @property
    def stop_crit(self) -> _alpaqa_d.PANOCStopCrit:
        """
        :type: _alpaqa_d.PANOCStopCrit
        """
    @stop_crit.setter
    def stop_crit(self, arg0: _alpaqa_d.PANOCStopCrit) -> None:
        pass
    @property
    def update_lipschitz_in_linesearch(self) -> bool:
        """
        :type: bool
        """
    @update_lipschitz_in_linesearch.setter
    def update_lipschitz_in_linesearch(self, arg0: bool) -> None:
        pass
    @property
    def τ_min(self) -> float:
        """
        :type: float
        """
    @τ_min.setter
    def τ_min(self, arg0: float) -> None:
        pass
    pass
class StructuredPANOCLBFGSProgressInfo():
    """
    Data passed to the PANOC progress callback.

    C++ documentation: :cpp:class:`alpaqa::StructuredPANOCLBFGSProgressInfo`
    """
    @property
    def J(self) -> numpy.ndarray:
        """
        Index set :math:`\mathcal J`

        :type: numpy.ndarray
        """
    @property
    def L(self) -> float:
        """
        Estimate of Lipschitz constant of objective :math:`L`

        :type: float
        """
    @property
    def fpr(self) -> float:
        """
        Fixed-point residual :math:`\left\|p\right\| / \gamma`

        :type: float
        """
    @property
    def grad_ψ(self) -> numpy.ndarray:
        """
        Gradient of objective :math:`\nabla\psi(x)`

        :type: numpy.ndarray
        """
    @property
    def grad_ψ_hat(self) -> numpy.ndarray:
        """
        :type: numpy.ndarray
        """
    @property
    def k(self) -> int:
        """
        Iteration

        :type: int
        """
    @property
    def norm_sq_p(self) -> float:
        """
        :math:`\left\|p\right\|^2`

        :type: float
        """
    @property
    def p(self) -> numpy.ndarray:
        """
        Projected gradient step :math:`p`

        :type: numpy.ndarray
        """
    @property
    def params(self) -> StructuredPANOCLBFGSParams:
        """
        Solver parameters

        :type: StructuredPANOCLBFGSParams
        """
    @property
    def problem(self) -> ProblemBase:
        """
        Problem being solved

        :type: ProblemBase
        """
    @property
    def q(self) -> numpy.ndarray:
        """
        Previous quasi-Newton step :math:`q`

        :type: numpy.ndarray
        """
    @property
    def x(self) -> numpy.ndarray:
        """
        Decision variable :math:`x`

        :type: numpy.ndarray
        """
    @property
    def x̂(self) -> numpy.ndarray:
        """
        Decision variable after projected gradient step :math:`\hat x`

        :type: numpy.ndarray
        """
    @property
    def y(self) -> numpy.ndarray:
        """
        Lagrange multipliers :math:`y`

        :type: numpy.ndarray
        """
    @property
    def Σ(self) -> numpy.ndarray:
        """
        Penalty factor :math:`\Sigma`

        :type: numpy.ndarray
        """
    @property
    def γ(self) -> float:
        """
        Step size :math:`\gamma`

        :type: float
        """
    @property
    def ε(self) -> float:
        """
        Tolerance reached :math:`\varepsilon_k`

        :type: float
        """
    @property
    def τ(self) -> float:
        """
        Line search parameter :math:`\tau`

        :type: float
        """
    @property
    def φγ(self) -> float:
        """
        Forward-backward envelope :math:`\varphi_\gamma(x)`

        :type: float
        """
    @property
    def ψ(self) -> float:
        """
        Objective value :math:`\psi(x)`

        :type: float
        """
    @property
    def ψ_hat(self) -> float:
        """
        :type: float
        """
    pass
class StructuredPANOCLBFGSSolver():
    """
    C++ documentation: :cpp:class:`alpaqa::StructuredPANOCLBFGSSolver`
    """
    def __init__(self, panoc_params: typing.Union[StructuredPANOCLBFGSParams, dict] = {}, lbfgs_params: typing.Union[LBFGS.Params, dict] = {}) -> None: 
        """
        Create a PANOC solver using L-BFGS directions.
        """
    def set_progress_callback(self, callback: typing.Callable[[StructuredPANOCLBFGSProgressInfo], None]) -> StructuredPANOCLBFGSSolver: 
        """
        Specify a callable that is invoked with some intermediate results on each iteration of the algorithm.
        """
    pass
def with_counters(prob: ProblemBase) -> CountedProblem:
    """
    Return a counted version of the given problem.
    """

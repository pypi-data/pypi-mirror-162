"""Python interface to alpaqa's C++ implementation."""
from __future__ import annotations
import _alpaqa_d
import typing

__all__ = [
    "ApproxKKT",
    "ApproxKKT2",
    "BasedOnCurvature",
    "BasedOnGradientStepSize",
    "Busy",
    "Converged",
    "EvalCounter",
    "FPRNorm",
    "FPRNorm2",
    "Interrupted",
    "Ipopt",
    "LBFGSBpp",
    "LBFGSStepsize",
    "MaxIter",
    "MaxTime",
    "NoProgress",
    "NotFinite",
    "PANOCStopCrit",
    "ProjGradNorm",
    "ProjGradNorm2",
    "ProjGradUnitNorm",
    "ProjGradUnitNorm2",
    "SolverStatus",
    "float32",
    "float64",
    "longdouble",
    "not_implemented_error",
    "with_casadi"
]


class EvalCounter():
    """
    C++ documentation: :cpp:class:`alpaqa::EvalCounter`
    """
    class EvalTimer():
        """
        C++ documentation: :cpp:class:`alpaqa::EvalCounter::EvalTimer`
        """
        def __getstate__(self) -> tuple: ...
        def __setstate__(self, arg0: tuple) -> None: ...
        @property
        def f(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @f.setter
        def f(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def f_g(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @f_g.setter
        def f_g(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def f_grad_f(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @f_grad_f.setter
        def f_grad_f(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def f_grad_f_g(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @f_grad_f_g.setter
        def f_grad_f_g(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def g(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @g.setter
        def g(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_L(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_L.setter
        def grad_L(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_f(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_f.setter
        def grad_f(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_f_grad_g_prod(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_f_grad_g_prod.setter
        def grad_f_grad_g_prod(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_g_prod(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_g_prod.setter
        def grad_g_prod(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_gi(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_gi.setter
        def grad_gi(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_ψ(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_ψ.setter
        def grad_ψ(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def grad_ψ_from_ŷ(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @grad_ψ_from_ŷ.setter
        def grad_ψ_from_ŷ(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def hess_L(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @hess_L.setter
        def hess_L(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def hess_L_prod(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @hess_L_prod.setter
        def hess_L_prod(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def ψ(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @ψ.setter
        def ψ(self, arg0: datetime.timedelta) -> None:
            pass
        @property
        def ψ_grad_ψ(self) -> datetime.timedelta:
            """
            :type: datetime.timedelta
            """
        @ψ_grad_ψ.setter
        def ψ_grad_ψ(self, arg0: datetime.timedelta) -> None:
            pass
        pass
    def __getstate__(self) -> tuple: ...
    def __setstate__(self, arg0: tuple) -> None: ...
    def __str__(self) -> str: ...
    @property
    def f(self) -> int:
        """
        :type: int
        """
    @f.setter
    def f(self, arg0: int) -> None:
        pass
    @property
    def f_g(self) -> int:
        """
        :type: int
        """
    @f_g.setter
    def f_g(self, arg0: int) -> None:
        pass
    @property
    def f_grad_f(self) -> int:
        """
        :type: int
        """
    @f_grad_f.setter
    def f_grad_f(self, arg0: int) -> None:
        pass
    @property
    def f_grad_f_g(self) -> int:
        """
        :type: int
        """
    @f_grad_f_g.setter
    def f_grad_f_g(self, arg0: int) -> None:
        pass
    @property
    def g(self) -> int:
        """
        :type: int
        """
    @g.setter
    def g(self, arg0: int) -> None:
        pass
    @property
    def grad_L(self) -> int:
        """
        :type: int
        """
    @grad_L.setter
    def grad_L(self, arg0: int) -> None:
        pass
    @property
    def grad_f(self) -> int:
        """
        :type: int
        """
    @grad_f.setter
    def grad_f(self, arg0: int) -> None:
        pass
    @property
    def grad_f_grad_g_prod(self) -> int:
        """
        :type: int
        """
    @grad_f_grad_g_prod.setter
    def grad_f_grad_g_prod(self, arg0: int) -> None:
        pass
    @property
    def grad_g_prod(self) -> int:
        """
        :type: int
        """
    @grad_g_prod.setter
    def grad_g_prod(self, arg0: int) -> None:
        pass
    @property
    def grad_gi(self) -> int:
        """
        :type: int
        """
    @grad_gi.setter
    def grad_gi(self, arg0: int) -> None:
        pass
    @property
    def grad_ψ(self) -> int:
        """
        :type: int
        """
    @grad_ψ.setter
    def grad_ψ(self, arg0: int) -> None:
        pass
    @property
    def grad_ψ_from_ŷ(self) -> int:
        """
        :type: int
        """
    @grad_ψ_from_ŷ.setter
    def grad_ψ_from_ŷ(self, arg0: int) -> None:
        pass
    @property
    def hess_L(self) -> int:
        """
        :type: int
        """
    @hess_L.setter
    def hess_L(self, arg0: int) -> None:
        pass
    @property
    def hess_L_prod(self) -> int:
        """
        :type: int
        """
    @hess_L_prod.setter
    def hess_L_prod(self, arg0: int) -> None:
        pass
    @property
    def time(self) -> EvalCounter.EvalTimer:
        """
        :type: EvalCounter.EvalTimer
        """
    @time.setter
    def time(self, arg0: EvalCounter.EvalTimer) -> None:
        pass
    @property
    def ψ(self) -> int:
        """
        :type: int
        """
    @ψ.setter
    def ψ(self, arg0: int) -> None:
        pass
    @property
    def ψ_grad_ψ(self) -> int:
        """
        :type: int
        """
    @ψ_grad_ψ.setter
    def ψ_grad_ψ(self, arg0: int) -> None:
        pass
    pass
class LBFGSStepsize():
    """
    C++ documentation: :cpp:enum:`alpaqa::LBFGSStepSize`

    Members:

      BasedOnGradientStepSize

      BasedOnCurvature
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
    BasedOnCurvature: _alpaqa_d.LBFGSStepsize # value = <LBFGSStepsize.BasedOnCurvature: 1>
    BasedOnGradientStepSize: _alpaqa_d.LBFGSStepsize # value = <LBFGSStepsize.BasedOnGradientStepSize: 0>
    __members__: dict # value = {'BasedOnGradientStepSize': <LBFGSStepsize.BasedOnGradientStepSize: 0>, 'BasedOnCurvature': <LBFGSStepsize.BasedOnCurvature: 1>}
    pass
class PANOCStopCrit():
    """
    C++ documentation: :cpp:enum:`alpaqa::PANOCStopCrit`

    Members:

      ApproxKKT

      ApproxKKT2

      ProjGradNorm

      ProjGradNorm2

      ProjGradUnitNorm

      ProjGradUnitNorm2

      FPRNorm

      FPRNorm2

      Ipopt

      LBFGSBpp
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
    ApproxKKT: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ApproxKKT: 0>
    ApproxKKT2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ApproxKKT2: 1>
    FPRNorm: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.FPRNorm: 6>
    FPRNorm2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.FPRNorm2: 7>
    Ipopt: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.Ipopt: 8>
    LBFGSBpp: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.LBFGSBpp: 9>
    ProjGradNorm: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradNorm: 2>
    ProjGradNorm2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradNorm2: 3>
    ProjGradUnitNorm: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradUnitNorm: 4>
    ProjGradUnitNorm2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradUnitNorm2: 5>
    __members__: dict # value = {'ApproxKKT': <PANOCStopCrit.ApproxKKT: 0>, 'ApproxKKT2': <PANOCStopCrit.ApproxKKT2: 1>, 'ProjGradNorm': <PANOCStopCrit.ProjGradNorm: 2>, 'ProjGradNorm2': <PANOCStopCrit.ProjGradNorm2: 3>, 'ProjGradUnitNorm': <PANOCStopCrit.ProjGradUnitNorm: 4>, 'ProjGradUnitNorm2': <PANOCStopCrit.ProjGradUnitNorm2: 5>, 'FPRNorm': <PANOCStopCrit.FPRNorm: 6>, 'FPRNorm2': <PANOCStopCrit.FPRNorm2: 7>, 'Ipopt': <PANOCStopCrit.Ipopt: 8>, 'LBFGSBpp': <PANOCStopCrit.LBFGSBpp: 9>}
    pass
class SolverStatus():
    """
    C++ documentation: :cpp:enum:`alpaqa::SolverStatus`

    Members:

      Busy : In progress.

      Converged : Converged and reached given tolerance

      MaxTime : Maximum allowed execution time exceeded

      MaxIter : Maximum number of iterations exceeded

      NotFinite : Intermediate results were infinite or NaN

      NoProgress : No progress was made in the last iteration

      Interrupted : Solver was interrupted by the user
    """
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: object) -> bool: ...
    def __getstate__(self) -> int: ...
    def __gt__(self, other: object) -> bool: ...
    def __hash__(self) -> int: ...
    def __index__(self) -> int: ...
    def __init__(self, value: int) -> None: ...
    def __int__(self) -> int: ...
    def __le__(self, other: object) -> bool: ...
    def __lt__(self, other: object) -> bool: ...
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
    Busy: _alpaqa_d.SolverStatus # value = <SolverStatus.Busy: 0>
    Converged: _alpaqa_d.SolverStatus # value = <SolverStatus.Converged: 1>
    Interrupted: _alpaqa_d.SolverStatus # value = <SolverStatus.Interrupted: 6>
    MaxIter: _alpaqa_d.SolverStatus # value = <SolverStatus.MaxIter: 3>
    MaxTime: _alpaqa_d.SolverStatus # value = <SolverStatus.MaxTime: 2>
    NoProgress: _alpaqa_d.SolverStatus # value = <SolverStatus.NoProgress: 5>
    NotFinite: _alpaqa_d.SolverStatus # value = <SolverStatus.NotFinite: 4>
    __members__: dict # value = {'Busy': <SolverStatus.Busy: 0>, 'Converged': <SolverStatus.Converged: 1>, 'MaxTime': <SolverStatus.MaxTime: 2>, 'MaxIter': <SolverStatus.MaxIter: 3>, 'NotFinite': <SolverStatus.NotFinite: 4>, 'NoProgress': <SolverStatus.NoProgress: 5>, 'Interrupted': <SolverStatus.Interrupted: 6>}
    pass
class not_implemented_error(NotImplementedError, RuntimeError, Exception, BaseException):
    pass
ApproxKKT: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ApproxKKT: 0>
ApproxKKT2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ApproxKKT2: 1>
BasedOnCurvature: _alpaqa_d.LBFGSStepsize # value = <LBFGSStepsize.BasedOnCurvature: 1>
BasedOnGradientStepSize: _alpaqa_d.LBFGSStepsize # value = <LBFGSStepsize.BasedOnGradientStepSize: 0>
Busy: _alpaqa_d.SolverStatus # value = <SolverStatus.Busy: 0>
Converged: _alpaqa_d.SolverStatus # value = <SolverStatus.Converged: 1>
FPRNorm: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.FPRNorm: 6>
FPRNorm2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.FPRNorm2: 7>
Interrupted: _alpaqa_d.SolverStatus # value = <SolverStatus.Interrupted: 6>
Ipopt: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.Ipopt: 8>
LBFGSBpp: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.LBFGSBpp: 9>
MaxIter: _alpaqa_d.SolverStatus # value = <SolverStatus.MaxIter: 3>
MaxTime: _alpaqa_d.SolverStatus # value = <SolverStatus.MaxTime: 2>
NoProgress: _alpaqa_d.SolverStatus # value = <SolverStatus.NoProgress: 5>
NotFinite: _alpaqa_d.SolverStatus # value = <SolverStatus.NotFinite: 4>
ProjGradNorm: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradNorm: 2>
ProjGradNorm2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradNorm2: 3>
ProjGradUnitNorm: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradUnitNorm: 4>
ProjGradUnitNorm2: _alpaqa_d.PANOCStopCrit # value = <PANOCStopCrit.ProjGradUnitNorm2: 5>
__version__ = '1.0.0a1'
with_casadi = True

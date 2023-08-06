from SciDataTool.Functions import AxisError
from SciDataTool.Classes.Norm_vector import Norm_vector


def get_axis_periodic(self, Nper, is_aper=False):
    """Returns the vector 'axis' taking symmetries into account.

    Parameters
    ----------
    self: Data1D
        a Data1D object
    Nper: int
        number of periods
    is_aper: bool
        return values on a semi period (only for antiperiodic signals)

    Returns
    -------
    New_axis: Data1D
        Axis with requested (anti-)periodicities
    """

    # Dynamic import to avoid loop
    module = __import__("SciDataTool.Classes.Data1D", fromlist=["Data1D"])
    Data1D = getattr(module, "Data1D")

    try:
        # Reduce axis to the given periodicity
        Nper = Nper * 2 if is_aper else Nper
        values = self.values
        N = self.get_length()

        if N % Nper != 0:
            raise AxisError("length of axis is not divisible by the number of periods")
        values_per = values[: int(N / Nper)]
        for norm in self.normalizations.values():
            if isinstance(norm, Norm_vector):
                norm.vector = norm.vector[: int(N / Nper)]

        if is_aper:
            sym = "antiperiod"
        else:
            sym = "period"

        if Nper == 1 and sym == "period":
            symmetries = dict()
        else:
            symmetries = {sym: Nper}

        New_axis = Data1D(
            values=values_per,
            name=self.name,
            unit=self.unit,
            symmetries=symmetries,
            normalizations=self.normalizations,
            is_components=self.is_components,
            symbol=self.symbol,
        )

    except AxisError:
        # Periodicity cannot be applied, return full axis
        New_axis = self.copy()

    return New_axis

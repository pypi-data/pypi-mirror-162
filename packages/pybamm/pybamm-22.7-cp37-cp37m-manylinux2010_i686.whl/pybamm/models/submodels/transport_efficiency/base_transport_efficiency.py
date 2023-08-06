#
# Base class for transport_efficiency
#
import pybamm


class BaseModel(pybamm.BaseSubModel):
    """Base class for transport_efficiency

    Parameters
    ----------
    param : parameter class
        The parameters to use for this submodel
    phase : str
        The material for the model ('electrolyte' or 'electrode').
    options : dict, optional
        A dictionary of options to be passed to the model.

    **Extends:** :class:`pybamm.BaseSubModel`
    """

    def __init__(self, param, phase, options=None):
        super().__init__(param, options=options)
        self.phase = phase

    def _get_standard_transport_efficiency_variables(
        self, tor_n, tor_s, tor_p, set_leading_order=False
    ):
        tor = pybamm.concatenation(tor_n, tor_s, tor_p)

        variables = {
            self.phase + " transport efficiency": tor,
            "Positive " + self.phase.lower() + " transport efficiency": tor_p,
            "X-averaged positive "
            + self.phase.lower()
            + " transport efficiency": pybamm.x_average(tor_p),
        }

        if not self.half_cell:
            variables.update(
                {
                    "Negative " + self.phase.lower() + " transport efficiency": tor_n,
                    "X-averaged negative "
                    + self.phase.lower()
                    + " transport efficiency": pybamm.x_average(tor_n),
                }
            )

        if self.phase == "Electrolyte":
            variables.update(
                {
                    "Separator transport efficiency": tor_s,
                    "X-averaged separator transport efficiency": pybamm.x_average(
                        tor_s
                    ),
                }
            )

        if set_leading_order is True:
            leading_order_variables = {
                "Leading-order " + name.lower(): var for name, var in variables.items()
            }
            variables.update(leading_order_variables)

        # Override print_name
        tor.print_name = r"\epsilon^{b_e}"

        return variables

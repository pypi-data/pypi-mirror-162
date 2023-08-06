from typing import List

import numpy as np
from ase import Atoms
from .fastatomstruct import *


def static_structure_factor(atoms: List[Atoms], q: np.ndarray, r_max: float,
                            n_bins: int, filter: Filter = None) -> np.ndarray:
    """Static structure factor, as calculated from the RDF.
    
    For isotropic systems, the static structure factor can be calculated using

    .. math::

        S(q) = q + 4 \pi \\rho \int_0^\infty r (g(r) - 1) \\frac{\sin{qr}}{q} dr,
    
    with :math:`q` the absolute value of the reciprocal vector and :math:`g(r)`
    the radial distribution function.

    Arguments:
        atoms (ase.Atoms or List[ase.Atoms]): Atoms object(s) from ASE
        q (np.ndarray): Array with values of :math:`q`
        r_max (float): Cutoff radius for calculating the radial distribution function
        n_bins (int): Number of bins for calculating the radial distribution function
        filter (fastatomstruct.Filter): Filter applied to the atoms

    Returns:
        np.ndarray of floats with values of :math:`S(q)`
    """
    if isinstance(atoms, list):
        rdf = []
        for a in atoms:
            r, rdf_i = radial_distribution_function(a, r_max, n_bins, filter)
            rdf.append(rdf_i)
        rdf = np.mean(rdf, axis=0)
        rho = len(atoms[0]) / atoms[0].get_volume()
    else:
        r, rdf = radial_distribution_function(atoms, r_max, n_bins)
        rho = len(atoms) / atoms.get_volume()

    integral = np.zeros(len(q))
    for i, qi in enumerate(q):
        integrand = r[1:] * np.sin(qi * r[1:]) * (rdf[1:] - 1)
        integral[i] = np.trapz(integrand, r[1:])
    return 1 + 4 * np.pi * rho / q * integral

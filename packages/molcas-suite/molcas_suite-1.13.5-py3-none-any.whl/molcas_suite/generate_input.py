"""
This module contains functions for generating molcas input files
"""

import numpy as np
import numpy.linalg as la
import xyz_py as xyzp
import xyz_py.atomic as atomic
import scipy.special as sps
import copy
import sys
from textwrap import dedent


class MolcasInput:

    def __init__(self, *sections, title=None):
        self.sections = sections
        self.title = title

    def write(self, f_name):

        with open(f_name, "w") as f:

            if self.title is not None:
                f.write(str(MolcasComm(self.title, num_char=3)))
                f.write('\n')

            f.write('\n'.join(str(sec) for sec in self.sections))


class MolcasComm:
    def __init__(self, text, num_char=1):
        self.num_char = num_char
        self.text = text

    def __str__(self):
        return "{} {}\n".format('*' * self.num_char, self.text)


class MolcasEmil:
    def __init__(self, cmd, *args, num_char=2):
        self.cmd = cmd.upper()
        self.args = args
        self.num_char = num_char

    def __str__(self):
        return '>' * self.num_char + " " + \
            "{} {}\n".format(self.cmd, " ".join(self.args))


class MolcasProg:
    def __init__(self, name, *args, num_indent=2, **kwargs):
        self.name = name.upper()
        self.args = args
        self.kwargs = kwargs
        self.num_indent = num_indent

    def __str__(self):
        indent = self.num_indent * ' '
        return '\n'.join(
            ["&{}".format(self.name)] +
            [indent + str(val) for val in self.args if val is not None] +
            [indent + ("{}= {}".format(key, val) if val else str(key))
             for key, val in self.kwargs.items() if key is not None]) + '\n'


class Gateway(MolcasProg):
    def __init__(self, *args, **kwargs):
        super().__init__('Gateway', *args, **kwargs)


class Alaska(MolcasProg):
    def __init__(self, *args, **kwargs):
        super().__init__('Alaska', *args, **kwargs)


class Mclr(MolcasProg):
    def __init__(self, *args, **kwargs):
        super().__init__('Mclr', *args, **kwargs)


def generate_input(labels, coords, central_atom, charge, n_active_elec,
                   n_active_orb, n_coord_atoms, f_name,
                   xfield=[], xfield_ext="", xyz_out="", xyz_ext="",
                   seward_decomp="High Cholesky", seward_extra=[],
                   basis_set_central="ANO-RCC-VTZP",
                   basis_set_coord="ANO-RCC-VDZP",
                   basis_set_remaining="ANO-RCC-VDZ", casscf_extra=[],
                   high_S_only=False, initial_orb="", max_orb=None,
                   caspt2=False, rassi=True, rassi_extra=[],
                   single_aniso=True, single_aniso_extra=[], quax=[],
                   skip_magneto=False, coord_hydrogens=False,
                   ang_central=False, extract_orbs=True):
    """
    Generates OpenMolcas input file for a CASSCF-RASSI-SO calculation on a
        coordination complex

    Parameters
    ----------
    labels : list
        Atomic labels
    coords : list
        list of lists of xyz coordinates of each atom
    central_atom : str
        Atomic label of central atom
    charge : int
        Charge of entire system
    n_active_elec : int
        Number of active electrons
    n_active_orb : int
        Number of active orbitals
    n_coord_atoms : int
        Number of atoms coordinates to central atom
    f_name : str
        Filename of final input file including extension
    xfield : list, optional
        list of lists of x, y, z, charge, dipole
    xfield_ext : str, optional
        Name of external charge file
    xyz_out : str, optional
        Name of output coordinates file
    xyz_ext : str, optional
        Name of external coordinates file
    seward_decomp : str, default "High Cholesky"
        Keyword(s) to use for SEWARD 2 electron integral decompositon
    seward_extra : list, optional
        Extra keywords/commands for SEWARD section
    basis_set_central : str, default ANO-RCC-VTZP
        Basis set for central atom
    basis_set_coord : str, default ANO-RCC-VDZP
        Basis set for coordinated atoms
    basis_set_remaining : str, default ANO-RCC-VDZ
        Basis set for all other atoms
    casscf_extra : list, optional
        Extra keywords/commands for CASSCF section(s)
    high_S_only : bool, default False
        If True, only consider the highest spin state
    initial_orb : str, optional
        Path to a custom input guess orbital file used in the initial
        RASSCF call
    max_orb : int, default None (all roots)
        Maximum number of RasOrb files to produce,
        one for each root up to the specified maximum. By default this is
        the number of roots per spin state
    caspt2 : bool, default False
        If True, include a CASPT2 section
    rassi : bool, default True
        If True, include a RASSI section
    rassi_extra : list, optional
        Extra keywords/commands for RASSI section
    extract_orbs : bool, default True
        If True, extract SA orbs with molcas_suite orbs to give human
        readable file for first spin
    single_aniso : bool, default True
        If True, include a SINGLE_ANISO section
    single_aniso_extra : list, optional
        Extra keywords/commands for SINGLE_ANISO
    quax : np.ndarray, optional
        (3,3) array containing rotation matrix for CFP reference frame
    skip_magneto : bool, default False
        If True, skip calculation of magnetic data section
    coord_hydrogens : bool, default False
        If True, hydrogens will be treated as coordinating atoms
    ang_central : bool, default False
        If True, Angular momentum will match the central metal coordinates
        which will not be shifted
    Returns
    -------
    None
    """

    # Create file handle for input file
    if f_name and f_name != "-":
        f = open(f_name, "w")
    else:
        f = sys.stdout

    # Write seward section
    write_seward(
        f, labels, coords, central_atom, n_coord_atoms, decomp=seward_decomp,
        basis_set_central=basis_set_central, basis_set_coord=basis_set_coord,
        basis_set_remaining=basis_set_remaining, extra=seward_extra,
        xfield=xfield, xfield_ext=xfield_ext, xyz_out=xyz_out,
        xyz_ext=xyz_ext, coord_hydrogens=coord_hydrogens,
        ang_central=ang_central
    )

    # Get information on electronic states
    # spins, roots etc
    spin_states, roots, trunc_roots = get_spin_and_roots(
        central_atom,
        n_active_elec,
        n_active_orb,
        high_S_only
    )

    # Write casscf section
    write_casscf(
        f, central_atom, charge, n_active_elec, n_active_orb, spin_states,
        roots, casscf_extra, verbose=True, initial_orb=initial_orb,
        extract_orbs=extract_orbs, max_orb=max_orb
    )

    # Write rassi section
    if rassi:
        write_rassi(f, trunc_roots, rassi_extra)

    # Write single_aniso section
    if single_aniso:
        write_single_aniso(
            f, central_atom, n_active_orb, quax=quax,
            skip_magneto=skip_magneto, verbose=True, extra=single_aniso_extra
        )

    if f_name and f_name != "-":
        f.close()

    return


def write_seward(f, labels, coords, central_atom, n_coord_atoms, decomp,
                 basis_set_central, basis_set_coord, basis_set_remaining,
                 extra=[], xfield=[], xfield_ext="", xyz_out="", xyz_ext="",
                 coord_hydrogens=False, ang_central=False):
    """

    Writes seward section of molcas input file to specified file object

    Parameters
    ----------
    f : file object
        File object corresponding to final input file
    labels : list
        Atomic labels
    coords : list
        list of lists of xyz coordinates of each atom
    central_atom : str
        Atomic label of central atom
    n_coord_atoms : int
        Number of atoms coordinates to central atom
    decomp : str
        Keyword(s) to use for SEWARD 2 electron integral decompositon
    extra : list, optional
        Extra keywords/commands for SEWARD section
    xfield : list, optional
        list of lists with dimensions (npoints, 7) arranged as:
            x,y,z,charge,dipolex,dipoley,dipolez
            for each point charge/dipole
    xfield_ext : str, optional
        Name of external charge file
    xyz_out : str, optional
        Name of output coordinates file
    xyz_ext : str, optional
        Name of external coordinates file
    coord_hydrogens : bool, default False
        If True, hydrogens will be treated as coordinating atoms
    ang_central : bool, default False
        If True, Angular momentum origin will match the central metal
        coordinates which will not be shifted
    Returns
    -------
    None
    """

    # Remove numbers from list of labels
    _labels_nn = xyzp.remove_label_indices(labels)

    # Capitalise labels
    _labels_nn = [la.capitalize() for la in _labels_nn]

    # Store hydrogen coordinates in separate array
    _coords_h = [
        co for lab, co in zip(_labels_nn, coords) if lab == 'H'
    ]

    # and remove from main list if H is not allowed to coordinate
    if not coord_hydrogens:
        _coords = [co for lab, co in zip(_labels_nn, coords)
                   if lab.capitalize() != 'H']
        _labels_nn = [lab for lab in _labels_nn if lab.capitalize() != 'H']
        is_h = [True if lab == 'H' else False for lab in _labels_nn]
    else:
        _coords = np.copy(coords)
        is_h = [False for lab in _labels_nn]

    # Re add numbers to labels
    _labels = xyzp.add_label_indices(_labels_nn)

    # Check if central_atom contains numbers
    need_numbers = False
    for letter in central_atom:
        # If it does, then the labels must be numbered
        if letter.isdigit():
            need_numbers = True

    # Get index of specified central atom
    if need_numbers:
        c_index = [
            it for it, lab in enumerate(_labels)
            if lab == central_atom.capitalize()
        ]
    else:
        c_index = [
            it for it, lab in enumerate(_labels_nn)
            if lab == central_atom.capitalize()
        ]

    # If no match for central atom error out
    if len(c_index) == 0:
        exit(
            dedent(
                "\u001b[31m Error: No instances of central atom {} found\033[0m".format( # noqa
                    central_atom
                )
            )
        )
    # If more than one match for central atom error out
    if len(c_index) > 1:
        exit(
            dedent(
                "\u001b[31m Error: Multiple instances of central atom {} found\033[0m".format( # noqa
                    central_atom
                )
            )
        )

    # Shift coordinates so origin is central atom
    center_shift = _coords[c_index[0]]
    _coords -= center_shift
    if len(_coords_h):
        _coords_h -= center_shift

    # Calculate distances to central atom

    if xyz_ext:
        # restore labels (incl H)
        _labels_nn = xyzp.remove_label_indices(labels)
        _labels = xyzp.add_label_indices(_labels_nn)
        # Get index of specified central atom
        if need_numbers:
            c_index = [
                it for it, lab in enumerate(_labels)
                if lab == central_atom.capitalize()
            ]
        else:
            c_index = [
                it for it, lab in enumerate(_labels_nn)
                if lab == central_atom.capitalize()
            ]
        is_h = [True if lab == 'H' else False for lab in _labels_nn]
        _labels = xyzp.add_label_indices(_labels_nn)
        _coords_all = coords - center_shift
        distances = [la.norm(co) for co in _coords_all]
        order = np.argsort(distances)
        coord_count = 0
        is_coord = [False for i in _labels]

        for o in order:

            if not is_h[o] and o not in c_index:
                coord_count = coord_count + 1

            if coord_count <= n_coord_atoms and not is_h[o] and o != c_index:
                is_coord[o] = True

        bs_labels = [
            basis_set_central
            if i in c_index
            else (basis_set_coord if c else basis_set_remaining)
            for i, c in enumerate(is_coord)
        ]

        xyz_labels = [
            "{}.{}".format(lab, bs_labels[i]) for i, lab in enumerate(_labels)
        ]

    else:
        distances = [la.norm(co) for co in _coords]
        order = np.argsort(distances)
        # Central metal ion is now first atom
        c_index = 0

        # Use distances to sort coordinates and labels
        distances = [distances[o] for o in order]
        _labels_nn = [_labels_nn[o] for o in order]
        _coords = [_coords[o] for o in order]

        # Replace atom numbering to follow new order
        _labels = xyzp.add_label_indices(_labels_nn)

    # ANGMOM defined to central atom so remove origin shift
    if ang_central:
        _coords += center_shift
        if len(_coords_h):
            _coords_h += center_shift

    # Get dictionaries of element indices
    # Shift indices in dictionaries to match original indexing
    coord_element_types = xyzp.index_elements(
        _labels_nn[1:n_coord_atoms+1],
        shift=1
    )
    other_element_types = xyzp.index_elements(
        _labels_nn[n_coord_atoms+1:],
        shift=n_coord_atoms+1
    )

    # Write header
    f.write("&SEWARD\n")
    f.write("AMFI\n")
    if not ang_central:
        f.write("ANGMOM=0.0 0.0 0.0 ANGSTROM\n")
    else:
        f.write(
            "ANGMOM={: 12.8f} {: 12.8f} {: 12.8f} ANGSTROM\n".format(
                *center_shift
            )
        )
    if decomp == 'RICD_acCD':
        f.write("RICD\nacCD")
    else:
        f.write("{}\n".format(decomp))

    # Additional arguments
    if len(extra):
        for e in extra:
            f.write("{}\n".format(e))

    # Section gap
    f.write("\n")

    if xyz_ext:
        xyzp.save_xyz(xyz_out, xyz_labels, _coords_all, verbose=False)
        f.write("Coords={}\n".format(xyz_ext))

    else:
        # Central ion basis set
        f.write("Basis Set\n")
        f.write(
            "{}.{}\n".format(
                _labels_nn[c_index].capitalize(),
                basis_set_central
            )
        )
        f.write(
            "{:4}  {: 12.8f} {: 12.8f} {: 12.8f}  Angstrom\n".format(
                _labels[c_index],
                *_coords[c_index]
            )
        )
        f.write("End of Basis Set")

        # Section gap
        f.write("\n\n")

        # Basis set(s) for coordinated atom(s)

        # Write basis set section for each element, where atom labels include
        # numerical index
        for label in coord_element_types.keys():
            f.write("Basis Set\n")
            f.write("{}.{}\n".format(label.capitalize(), basis_set_coord))
            for index in coord_element_types[label]:
                f.write(
                    "{:4}  {: 12.8f} {: 12.8f} {: 12.8f}   Angstrom\n".format(
                        _labels[index].capitalize(),
                        *_coords[index]
                    )
                )
            f.write("End of Basis Set\n\n")

        # Basis set(s) for remaining ligand atom(s)

        # Write basis set section for each element, where atom labels include
        # numerical index
        for label in other_element_types.keys():
            f.write("Basis Set\n")
            f.write("{}.{}\n".format(label.capitalize(), basis_set_remaining))
            for index in other_element_types[label]:
                f.write(
                    "{:4}  {: 12.8f} {: 12.8f} {: 12.8f}   Angstrom\n".format(
                        _labels[index].capitalize(), *_coords[index]
                    )
                )
            f.write("End of Basis Set\n\n")

        # Basis set(s) for Hydrogens if assumed to not coordinate

        # Write basis set section for each element, where atom labels include
        # numerical index
        if not coord_hydrogens and len(_coords_h):
            f.write("Basis Set\n")
            f.write("H.{}\n".format(basis_set_remaining))
            for it, co in enumerate(_coords_h):
                f.write(
                    "H{:d}  {: 12.8f} {: 12.8f} {: 12.8f}   Angstrom\n".format(
                        it+1,
                        *co
                    )
                )
            f.write("End of Basis Set\n\n")

    # Point charge locations
    if len(xfield):
        f.write("XField\n")
        f.write("{:d} ANGSTROM\n".format(len(xfield)))
        fmt = "{: 12.8f} " * 3 + "{:^12.8f} " + "{: 12.8f} " * 3 + "\n"
        for entity in xfield:
            # x, y, z, charge, dipolex, dipoley, dipolez
            f.write(fmt.format(*entity))
        f.write("\n\n")
    elif xfield_ext:
        f.write("XField\n")
        f.write("{}\n".format(xfield_ext))
        f.write("\n")

    return


def get_spin_and_roots(central_atom, n_active_elec, n_active_orb,
                       high_S_only=False):

    """
    Generates list of spin states and roots given a number of orbitals and
    electrons

    Parameters
    ----------
    central_atom : str
        Atomic label of central atom
    n_active_elec : int
        Number of active electrons
    n_active_orb : int
        Number of active orbitals
    high_S_only : bool, default False
        If True, only consider the highest spin state

    Returns
    -------
    list
        2S values for each spin state
    list
        Number of roots for each spin state
    list
        Reduced number of roots for each spin state
    """

    # Calculate high and low spin states
    if (n_active_elec <= n_active_orb):
        high_spin = n_active_elec + 1
    else:
        high_spin = 2*n_active_orb - n_active_elec + 1

    low_spin = n_active_elec % 2 + 1

    # Calculate total number of spin states
    if (high_S_only):
        lim = copy.copy(high_spin)
    else:
        lim = copy.copy(low_spin)

    n_spin_states = len(range(high_spin, lim-2, -2))

    # Array of spin values for each spin states
    spin_states = [int(high_spin - 2*i) for i in range(0, n_spin_states)]

    # Calculate the roots of each spin

    # Calculate number of roots in each spin state, and
    # truncated number of roots used in RASSI

    # Dictionary of roots and truncated roots for Lanthanide ions
    # Key is number of active electrons
    # Value is [roots, trunc_roots]
    # Where roots and trunc_roots are lists
    ln_roots_dict = {
        1: [[7], [7]],
        2: [[21, 28], [21, 28]],
        3: [[35, 112], [35, 112]],
        4: [[35, 210, 196], [35, 159, 156]],
        5: [[21, 224, 490], [21, 128, 130]],
        6: [[7, 140, 588, 490], [7, 140, 195, 197]],
        7: [[1, 48, 392, 784], [1, 48, 119, 113]],
        8: [[7, 140, 588, 490], [7, 140, 195, 197]],
        9: [[21, 224, 490], [21, 128, 130]],
        10: [[35, 210, 196], [35, 159, 156]],
        11: [[35, 112], [35, 112]],
        12: [[21, 28], [21, 28]],
        13: [[7], [7]]
    }
    # Defining small list of roots for spin-phonon calculations on Ln3+ ions
    # Ce = 2F
    # Pr = 3H + 3F
    # Nd = 4I
    # Pm = 5I
    # Sm = 6H + 6F
    # Eu = 7F
    # Gd = 8S
    # Tb = 7F
    # Dy = 6H + 6F
    # Ho = 5I
    # Er = 4I
    # Tm = 3H
    # Yb = 2F
    small_ln_roots_dict = {
        1: [[7], [7]],
        2: [[18], [18]],
        3: [[13], [13]],
        4: [[13], [13]],
        5: [[18], [18]],
        6: [[7], [7]],
        7: [[1], [1]],
        8: [[7], [7]],
        9: [[18], [18]],
        10: [[13], [13]],
        11: [[13], [13]],
        12: [[11], [11]],
        13: [[7], [7]]
    }

    _central_atom = xyzp.remove_label_indices([central_atom])[0].capitalize()

    # Check if Lanthanide n in 7 calculation
    if 57 <= atomic.lab_num[_central_atom] <= 71 and n_active_orb == 7:
        ln_calc = True
    else:
        ln_calc = False

    # If n in 7 for Ln: use above dictionary
    if ln_calc:
        roots, trunc_roots = ln_roots_dict[n_active_elec]
    # All other elements calculate the number of roots with Weyl's formula
    else:
        roots = []
        for spin in spin_states:
            k = spin/float(n_active_orb+1)
            k *= sps.binom(
                n_active_orb + 1,
                0.5*n_active_elec - (spin - 1.) * 0.5
                )
            k *= sps.binom(
                n_active_orb + 1,
                0.5*n_active_elec + (spin - 1.) * 0.5+1.
                )
            if (k <= 500):
                roots.append(int(k))
            else:
                roots.append(-1)
            # In this case trunc_roots is equal to roots
        trunc_roots = copy.copy(roots)

    if high_S_only:
        if ln_calc:
            roots, trunc_roots = small_ln_roots_dict[n_active_elec]
        else:
            roots = [roots[0]]
            trunc_roots = [trunc_roots[0]]

    return spin_states, roots, trunc_roots


def write_casscf(f, central_atom, charge, n_active_elec, n_active_orb,
                 spin_states, roots, extra=[], verbose=False, initial_orb="",
                 extract_orbs=True, max_orb=None):
    """
        Writes RASSCF section of molcas input file to specified file object

    Parameters
    ----------
    f : file_object
        File object corresponding to final input file
    central_atom : str
        Atomic label of central atom
    charge : int
        Charge of entire system
    n_active_elec : int
        Number of active electrons
    n_active_orb : int
        Number of active orbitals
    spin_states : list
        List of 2S values for each spin state
    roots : list
        List of # of roots for each spin state
    extra : list, optional
        Extra string keywords/commands for CASSCF section(s)
    verbose : bool, default False
        If True, print information to screen
    initial_orb : str, optional
        Path to a custom input guess orbital file used in the initial
        RASSCF call
    extract_orbs : bool, default True
        If True, extract SA orbs with molcas_suite orbs to give human
        readable file for first spin
    max_orb : int, default None (all roots)
        Maximum number of RasOrb files to produce,
        one for each root up to the specified maximum. By default this is
        the number of roots per spin state

    Returns
    -------
    None
    """

    _central_atom = xyzp.remove_label_indices([central_atom])[0].capitalize()

    # Loop over each spin state and write CASSCF section
    for it, spin in enumerate(spin_states):

        # Write blank line to separate sections
        if it != 0:
            f.write("\n")

        # Write section header
        f.write("&RASSCF\n")

        # Write name of previous orbital file to use as initial guess
        # If not looking at first spin-state
        if it != 0:
            f.write("FILEORB={:d}.RasOrb\n".format(it))
        elif initial_orb:
            f.write("FILEORB= {}\n".format(initial_orb))

        # Write spin for current state
        f.write("Spin= {:d}\n".format(int(spin)))

        # Write number of active electrons in current state
        f.write("Nactel= {:d} 0 0\n".format(n_active_elec))

        # Write number of active orbitals in current state
        f.write("Ras2= {:d}\n".format(n_active_orb))

        # Write number of inactive electrons in current state
        f.write("Charge= {:d}\n".format(charge))

        # Write number of CI roots for this spin state
        # Input is (number of roots, number of roots to use in averaging,
        # number 1 which indicates all roots weighted equally in averaging)
        # See the MOLCAS manual for this bonkers input

        # If n in 7 for Ln
        if 57 <= atomic.lab_num[_central_atom] <= 71 and n_active_orb == 7:
            if n_active_elec == 7 and spin == 2:
                f.write("CiRoot= x x 1\n")
                if verbose:
                    print(
                        dedent(
                            """ \n \
                              \033[93m ****  Large number of roots for spin 2 ****
                            Modify CiRoot= x x 1 in input, x is number of roots \
                            \033[0m """ # noqa
                        )
                    )
            else:
                f.write("CiRoot= {:d} {:d} 1\n".format(roots[it], roots[it]))

        else:
            # If not a lanthanide then truncate at 500 roots
            if (roots[it] <= 500):
                f.write("CiRoot= {:d} {:d} 1\n".format(roots[it], roots[it]))
            else:
                f.write("CiRoot= x x 1\n")
                if verbose:
                    print(
                        dedent(
                            """ \n \
                            \033[93m ****  Large number of roots ****
                                Modify CiRoot= x x 1 in input, x is number of roots \
                            \033[0m """ # noqa
                        )
                    )

        # Write additional commands
        # Set orbital output to include all contributions no matter how small
        f.write('ORBA=FULL\n')

        # Set maximum number of RASORB.XX files if not given to function
        if max_orb is None:
            c_max_orb = roots[it]
        else:
            c_max_orb = copy.copy(max_orb)

        if verbose:
            if c_max_orb > 100:
                print(
                    dedent(
                        """ \n \
                        \033[93m ****  Large number of RasOrb files for spin {:d}  ****
                                        Check/modify input file!   \
                        \033[0m """.format(spin) # noqa
                    )
                )

        f.write('MAXORB={:d}\n'.format(c_max_orb))

        if len(extra):
            for e in extra:
                f.write("{}\n".format(e))

        # Write molcas commands to copy current IPH and average RasOrb files
        # to new locations as molcas overwrites these by default
        f.write('>> COPY $Project.JobIph {:d}_IPH\n'.format(it+1))
        f.write('>> COPY $Project.RasOrb {:d}.RasOrb\n'.format(it+1))
        # Also copy the rasscf.h5 file
        f.write('>> COPY $Project.rasscf.h5 {:d}.rasscf.h5\n'.format(it + 1))
        # Write molcas commands to copy current root specific RasOrb and SpdOrb
        # files to new locations to prevent them being overwritten
        if c_max_orb > 0:
            f.write('>> FOREACH ROOT in (1..{:d})\n'.format(c_max_orb))
            f.write(
                '>> SHELL mv $Project.RasOrb.$ROOT {:d}.RasOrb.$ROOT\n'.format(
                    it + 1
                )
            )
            f.write(
                '>> SHELL mv $Project.SpdOrb.$ROOT {:d}.SpdOrb.$ROOT\n'.format(
                    it + 1
                )
            )
            f.write('>> ENDDO\n')

        if extract_orbs:
            # molcas_suite orbs command for analysing output orbitals
            f.write(
                '>> EXEC molcas_suite orbs '
                '{:d}.rasscf.h5 --out {:d}_rasorb\n'.format(it + 1, it + 1)
            )

    return


def write_rassi(f, roots, extra=[]):
    """
        Writes RASSI section of molcas input file to specified file object

    Parameters
    ----------
    f : file object
        File object corresponding to final input file
    roots : list
        List of # of roots for each spin state
    extra : list, optional
        Extra string keywords/commands for RASSI section(s)
    Returns
    -------
    None
    """

    # Write section header
    f.write("\n&RASSI\n")

    # Write roots list
    f.write("Nr of JobIph= {} ".format(len(roots)))

    # Loop over each spin state and add each total number of roots to the list
    # Note if this is a lanthanide then the list of roots is truncated at a
    # certain energy value
    for root in roots:
        if root < 500:
            # Write total number of roots for this spin state
            f.write("{:d} ".format(root))
        else:
            f.write("x ")

    f.write("; ")

    # Loop over each spin state and add each individual root number to the list
    for it, root in enumerate(roots):
        if 0 < root < 500:
            for r in range(root):
                f.write("{:d} ".format(r+1))
            if it+1 != len(roots):
                f.write(";")

    f.write("\nSpin\n")
    f.write("IPHN\n")

    for i in range(len(roots)):
        f.write("{:d}_IPH\n".format(i+1))

    # Set optional parameters

    f.write("MEES\n")
    f.write("EJob\n")
    f.write("PROP\n")
    f.write("3\n")
    f.write("'ANGMOM' 1\n")
    f.write("'ANGMOM' 2\n")
    f.write("'ANGMOM' 3\n")
    f.write("EPRG\n")
    f.write("7.0D-1\n")

    if len(extra):
        for e in extra:
            f.write("{}\n".format(e))

    return


def write_single_aniso(f, central_atom_lab, n_active_orb, quax=[],
                       skip_magneto=False, verbose=False, extra=[]):
    """
    Writes single aniso section of final input file

    Parameters
    ----------
    f : file object
        File object corresponding to final input file
    central_atom_lab : str
        Atomic label of central atom
    n_active_orb : int
        Number of active orbitals
    quax : list, optional
        List of Lists containing rotation matrix for CFP reference frame
    skip_magneto : bool, default False
        If True, skip calculation of magnetic data
    verbose : bool, default False
        If True, Print information to screen
    extra : list, optional
        Extra keywords/commands for SINGLE_ANISO section

    Returns
    -------
    None
    """
    central_atom_lab = xyzp.remove_label_indices(
        [central_atom_lab]
    )[0].capitalize()

    central_atom_num = xyzp.atom_lab_num[central_atom_lab]

    # Request CFPs for TM, Ln, Ac
    if 21 <= central_atom_num <= 30 and n_active_orb == 5:
        crys = True
    elif 57 <= central_atom_num <= 71 and n_active_orb == 7:
        crys = True
    elif 89 <= central_atom_num < 103 and n_active_orb == 7:
        crys = True
    else:
        if verbose:
            print(
                dedent(
                    """
                    \033[93m **** Please assign multiplet dimension in MLTP of SINGLE_ANISO, otherwise calculation will fail! **** \033[0m
                    """ # noqa
                )
            )
        crys = False

    # Write output file
    f.write("\n&SINGLE_ANISO\n")

    if crys:
        f.write("CRYS\n")
        f.write("{}\n".format(central_atom_lab.lower()))
        f.write("MLTP\n")
        f.write("1; 2\n")
    # If no CFPs, request D, g for lowest energy spin state
    else:
        f.write("MLTP\n")
        f.write("1; ?\n")

    if not skip_magneto:
        f.write("TINT\n")
        f.write("0.0  330.0  330  0.0001\n")
        f.write("HINT\n")
        f.write("0.0  10.0  201\n")
        f.write("TMAG\n")
        f.write("6 1.8 2 4 5 10 20\n")

    # Specific reference frame
    if quax is not None:
        f.write("QUAX\n")
        f.write("3\n")
        for row in quax:
            f.write("{:.15f} {:.15f} {:.15f}\n".format(*row))
    else:
        f.write("QUAX\n")
        f.write("1\n")

    if len(extra):
        for e in extra:
            f.write("{}\n".format(e))

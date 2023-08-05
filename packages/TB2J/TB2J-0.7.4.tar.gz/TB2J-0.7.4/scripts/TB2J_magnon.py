#!/usr/bin/env python3
from TB2J.plot import plot_magnon_band, write_eigen
from TB2J.versioninfo import print_license
import argparse
"""
The script to plot the magnon band structure.
"""


def plot_magnon():
    print_license()
    parser = argparse.ArgumentParser(
        description="TB2J_magnon: Plot magnon band structure from the TB2J magnetic interaction parameters"
    )
    parser.add_argument("--fname",
                        default='exchange.xml',
                        type=str,
                        help='exchange xml file name. default: exchange.xml')

    parser.add_argument(
        "--qpath",
        default=None,
        type=str,
        help='The names of special q-points. If not given, the path will be automatically choosen. See https://wiki.fysik.dtu.dk/ase/ase/dft/kpoints.html for the table of special kpoints and the default path.'
    )

    parser.add_argument(
        "--figfname",
        default=None,
        type=str,
        help='The file name of the figure. It should be e.g. png, pdf or other types of files which could be generated by matplotlib.'
    )

    parser.add_argument(
        "--Jq",
        action="store_true",
        help="To plot the eigenvalues of -J(q) instead of the magnon band",
        default=False)

    parser.add_argument("--no_Jiso",
                        action="store_true",
                        help="switch off isotropic exchange",
                        default=None)

    parser.add_argument("--no_dmi",
                        action="store_true",
                        help="switch off dmi",
                        default=None)

    parser.add_argument("--no_Jani",
                        action="store_true",
                        help="switch off anisotropic exchange",
                        default=None)

    parser.add_argument("--write_emin",
                        action="store_true",
                        help="switch to write emin",
                        default=False)

    parser.add_argument("--show",
                        action="store_true",
                        help="whether to show magnon band structure.",
                        default=False)

    args = parser.parse_args()
    if args.Jq:
        print(
            "Plotting the eigenvalues of -J(q). The figure is written to %s" %
            (args.figfname))
        if args.figfname is None:
            args.figfname = 'Eigen_Jq.pdf'
    else:
        print(
            "Plotting the magnon band structure. The figure is written to %s" %
            (args.figfname))
        if args.figfname is None:
            args.figfname = 'magnon_band.pdf'

    def nonone(x):
        if x is None:
            return x
        else:
            return not x

    if args.write_emin:
        write_eigen(has_exchange=nonone(args.no_Jiso),
                    has_dmi=nonone(args.no_dmi),
                    has_bilinear=nonone(args.no_Jani))
    else:
        plot_magnon_band(fname=args.fname,
                         knames=args.qpath,
                         npoints=300,
                         Jq=args.Jq,
                         figfname=args.figfname,
                         show=args.show,
                         has_exchange=nonone(args.no_Jiso),
                         has_dmi=nonone(args.no_dmi),
                         has_bilinear=nonone(args.no_Jani))


plot_magnon()

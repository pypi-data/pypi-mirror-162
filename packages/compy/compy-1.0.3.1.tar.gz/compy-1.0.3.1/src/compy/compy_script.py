#!/usr/bin/env python3

"""
A command line script for processing CoMPASS data
"""
import os
import sys
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import click

from compy import compassrun, utilities


def main():
    """Process user-selected runs and plot filtered TOF spectra."""
    args = sys.argv[1:]
    argc = len(args)
    if argc > 0:
        folders = [str(Path(arg).resolve()) for arg in args]
        print(f"Folders specified: {folders}")
    else:
        folders = None

    # process data
    pkl_flag = click.confirm(
        "\nWould you like to load data from pickle?", default=False
    )
    if pkl_flag:
        runs = utilities.load_pickle()
    else:
        key_tuples, VERBOSE = compassrun.initialize(folders=folders)
        runs = compassrun.process_runs(key_tuples)
        merge_flag = click.confirm("\nWould you like to merge runs?", default=True)
        if merge_flag:
            utilities.merge_related_runs(runs, quiet=True)

    # plot filtered TOF spectra for all keys
    print_flag = click.confirm(
        "\nWould you like to plot the (filtered) spectra?", default=False
    )
    if print_flag:
        plt.figure(figsize=(16, 9))
        for key in runs.keys():
            print(key)
            if ("TOF" in runs[key].spectra["filtered"]) and (
                "vals" in runs[key].spectra["filtered"]["TOF"]
            ):
                vals_raw = np.array(runs[key].spectra["filtered"]["TOF"]["vals"])
                bins = np.array(runs[key].spectra["filtered"]["TOF"]["bins"])
                t = runs[key].t_meas
                print("plotting key: ", key, t, sum([i for i in vals_raw]))
                vals_err = np.sqrt(vals_raw) / t
                vals = vals_raw / t
                plt.errorbar(
                    x=bins,
                    y=vals,
                    yerr=vals_err,
                    marker="s",
                    linestyle="None",
                    drawstyle="steps-mid",
                    label=key.replace("_", "-"),
                )
            else:
                print(f"Did not find TOF data for key: {key}.")
        if len(runs.keys()) > 0:
            plt.xlim(25, 185)
            plt.xlabel(r"TIME [$\mu$s]")
            plt.ylabel("COUNTS/MINUTE")
            # plt.ylim(0, 3.5)
            plt.legend()
            plt.tight_layout()
            plt.show()
        else:
            print("No spectra found to plot!")

    # calculate, plot, and write to file transmission for target runs
    trans_flag = click.confirm(
        "\nWould you like to calculate transmission?", default=False
    )
    if trans_flag:
        trans_plot_flag = click.confirm(
            "\nWould you like to plot transmission?", default=False
        )
        trans_write_flag = click.confirm(
            "\nWould you like to write transmission to file?", default=False
        )
        keys = list(runs.keys())
        print("\nProcessed keys are", f"{keys}")
        key_ob_all = input(
            "\nWhich key would you like to use for open beam? Press <ENTER> to select individually.\n"
        )
        # add transmission
        for key in keys:
            if not key_ob_all:
                key_ob = input(
                    f"\n{key}: which key would you like to use for open beam? Press <ENTER> to skip key.\n"
                )
            else:
                key_ob = key_ob_all
            if key_ob and (key != key_ob):
                runs[key].add_trans(runs, key_ob, t_offset=0)
                if trans_plot_flag:
                    runs[key].plot_trans(t_offset=7.20)
                if trans_write_flag:
                    print(f"Writing transmission to trans_{key}.txt...")
                    runs[key].write_trans(fname=f"trans_{key}.txt")

    # save data to pickle
    save_flag = click.confirm(
        "\nWould you like to save the runs as a pickle?", default=False
    )
    if save_flag:
        utilities.save_pickle(runs)
    print("\nThank you for using compy, the CoMPASS Python Companion!")

    return runs


if __name__ == "__main__":
    os.chdir(Path.cwd())
    runs = main()

# *- encoding: utf-8 -*-
"""
Utilities to download localizer fMRI datasets
"""
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import contextlib
import collections
import os
import tarfile
import zipfile
import sys
import shutil
import time
import hashlib
import fnmatch
import warnings
import re
import base64

import numpy as np
from scipy import ndimage
from sklearn.datasets.base import Bunch

from ...core.datasets import HttpDataset


class BrainomicsDataset(HttpDataset):
    """Download and load Brainomics Localizer dataset (94 subjects).

    "The Functional Localizer is a simple and fast acquisition
    procedure based on a 5-minute functional magnetic resonance
    imaging (fMRI) sequence that can be run as easily and as
    systematically as an anatomical scan. This protocol captures the
    cerebral bases of auditory and visual perception, motor actions,
    reading, language comprehension and mental calculation at an
    individual level. Individual functional maps are reliable and
    quite precise. The procedure is decribed in more detail on the
    Functional Localizer page."
    (see http://brainomics.cea.fr/localizer/)

    "Scientific results obtained using this dataset are described in
    Pinel et al., 2007" [1]

    Parameters
    ----------
    contrasts: list of str
        The contrasts to be fetched (for all 94 subjects available).
        Allowed values are:
            {"checkerboard",
            "horizontal checkerboard",
            "vertical checkerboard",
            "horizontal vs vertical checkerboard",
            "vertical vs horizontal checkerboard",
            "sentence listening",
            "sentence reading",
            "sentence listening and reading",
            "sentence reading vs checkerboard",
            "calculation (auditory cue)",
            "calculation (visual cue)",
            "calculation (auditory and visual cue)",
            "calculation (auditory cue) vs sentence listening",
            "calculation (visual cue) vs sentence reading",
            "calculation vs sentences",
            "calculation (auditory cue) and sentence listening",
            "calculation (visual cue) and sentence reading",
            "calculation and sentence listening/reading",
            "calculation (auditory cue) and sentence listening vs "
            "calculation (visual cue) and sentence reading",
            "calculation (visual cue) and sentence reading vs checkerboard",
            "calculation and sentence listening/reading vs button press",
            "left button press (auditory cue)",
            "left button press (visual cue)",
            "left button press",
            "left vs right button press",
            "right button press (auditory cue)",
            "right button press (visual cue)",
            "right button press",
            "right vs left button press",
            "button press (auditory cue) vs sentence listening",
            "button press (visual cue) vs sentence reading",
            "button press vs calculation and sentence listening/reading"}
        or equivalently on can use the original names:
            {"checkerboard",
            "horizontal checkerboard",
            "vertical checkerboard",
            "horizontal vs vertical checkerboard",
            "vertical vs horizontal checkerboard",
            "auditory sentences",
            "visual sentences",
            "auditory&visual sentences",
            "visual sentences vs checkerboard",
            "auditory calculation",
            "visual calculation",
            "auditory&visual calculation",
            "auditory calculation vs auditory sentences",
            "visual calculation vs sentences",
            "auditory&visual calculation vs sentences",
            "auditory processing",
            "visual processing",
            "visual processing vs auditory processing",
            "auditory processing vs visual processing",
            "visual processing vs checkerboard",
            "cognitive processing vs motor",
            "left auditory click",
            "left visual click",
            "left auditory&visual click",
            "left auditory & visual click vs right auditory&visual click",
            "right auditory click",
            "right visual click",
            "right auditory&visual click",
            "right auditory & visual click vs left auditory&visual click",
            "auditory click vs auditory sentences",
            "visual click vs visual sentences",
            "auditory&visual motor vs cognitive processing"}

    n_subjects: int, optional
        The number of subjects to load. If None is given,
        all 94 subjects are used.

    get_tmaps: boolean
        Whether t maps should be fetched or not.

    get_masks: boolean
        Whether individual masks should be fetched or not.

    get_anats: boolean
        Whether individual structural images should be fetched or not.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location.

    url: string, optional
        Override download URL. Used for test only (or if you setup a mirror of
        the data).

    resume: bool
        Whether to resume download of a partly-downloaded file.

    verbose: int
        Verbosity level (0 means no message).

    Returns
    -------
    data: Bunch
        Dictionary-like object, the interest attributes are :
        'cmaps': string list
            Paths to nifti contrast maps
        'tmaps' string list (if 'get_tmaps' set to True)
            Paths to nifti t maps
        'masks': string list
            Paths to nifti files corresponding to the subjects individual masks
        'anats': string
            Path to nifti files corresponding to the subjects structural images

    References
    ----------
    [1] Pinel, Philippe, et al.
        "Fast reproducible identification and large-scale databasing of
         individual functional cognitive networks."
        BMC neuroscience 8.1 (2007): 91.

    """
    def fetch(self, contrasts, n_subjects=None, get_tmaps=False,
              get_masks=False, get_anats=False, url=None,
              resume=True, force=False, verbose=1):
        if isinstance(contrasts, _basestring):
            raise ValueError('Contrasts should be a list of strings, but '
                             'a single string was given: "%s"' % contrasts)
        if n_subjects is None:
            n_subjects = 94  # 94 subjects available
        if (n_subjects > 94) or (n_subjects < 1):
            warnings.warn("Wrong value for \'n_subjects\' (%d). The maximum "
                          "value will be used instead (\'n_subjects=94\')")
            n_subjects = 94  # 94 subjects available

        # we allow the user to use alternatives to Brainomics contrast names
        contrast_name_wrapper = {
            # Checkerboard
            "checkerboard": "checkerboard",
            "horizontal checkerboard": "horizontal checkerboard",
            "vertical checkerboard": "vertical checkerboard",
            "horizontal vs vertical checkerboard":
                "horizontal vs vertical checkerboard",
            "vertical vs horizontal checkerboard":
                "vertical vs horizontal checkerboard",
            # Sentences
            "sentence listening": "auditory sentences",
            "sentence reading": "visual sentences",
            "sentence listening and reading": "auditory&visual sentences",
            "sentence reading vs checkerboard": "visual sentences vs checkerboard",
            # Calculation
            "calculation (auditory cue)": "auditory calculation",
            "calculation (visual cue)": "visual calculation",
            "calculation (auditory and visual cue)": "auditory&visual calculation",
            "calculation (auditory cue) vs sentence listening":
                "auditory calculation vs auditory sentences",
            "calculation (visual cue) vs sentence reading":
                "visual calculation vs sentences",
            "calculation vs sentences": "auditory&visual calculation vs sentences",
            # Calculation + Sentences
            "calculation (auditory cue) and sentence listening":
                "auditory processing",
            "calculation (visual cue) and sentence reading":
                "visual processing",
            "calculation (visual cue) and sentence reading vs "
            "calculation (auditory cue) and sentence listening":
                "visual processing vs auditory processing",
            "calculation (auditory cue) and sentence listening vs "
            "calculation (visual cue) and sentence reading":
                "auditory processing vs visual processing",
            "calculation (visual cue) and sentence reading vs checkerboard":
                "visual processing vs checkerboard",
            "calculation and sentence listening/reading vs button press":
                "cognitive processing vs motor",
            # Button press
            "left button press (auditory cue)": "left auditory click",
            "left button press (visual cue)": "left visual click",
            "left button press": "left auditory&visual click",
            "left vs right button press": "left auditory & visual click vs "
                + "right auditory&visual click",
            "right button press (auditory cue)": "right auditory click",
            "right button press (visual cue)": "right visual click",
            "right button press": "right auditory & visual click",
            "right vs left button press": "right auditory & visual click "
               + "vs left auditory&visual click",
            "button press (auditory cue) vs sentence listening":
                "auditory click vs auditory sentences",
            "button press (visual cue) vs sentence reading":
                "visual click vs visual sentences",
            "button press vs calculation and sentence listening/reading":
                "auditory&visual motor vs cognitive processing"}
        allowed_contrasts = list(contrast_name_wrapper.values())
        # convert contrast names
        contrasts_wrapped = []
        # get a unique ID for each contrast. It is used to give a unique name to
        # each download file and avoid name collisions.
        contrasts_indices = []
        for contrast in contrasts:
            if contrast in allowed_contrasts:
                contrasts_wrapped.append(contrast)
                contrasts_indices.append(allowed_contrasts.index(contrast))
            elif contrast in contrast_name_wrapper:
                name = contrast_name_wrapper[contrast]
                contrasts_wrapped.append(name)
                contrasts_indices.append(allowed_contrasts.index(name))
            else:
                raise ValueError("Contrast \'%s\' is not available" % contrast)

        # It is better to perform several small requests than a big one because:
        # - Brainomics server has no cache (can lead to timeout while the archive
        #   is generated on the remote server)
        # - Local (cached) version of the files can be checked for each contrast
        opts = {'uncompress': True}
        subject_ids = ["S%02d" % s for s in range(1, n_subjects + 1)]
        subject_id_max = subject_ids[-1]
        data_types = ["c map"]
        if get_tmaps:
            data_types.append("t map")
        rql_types = str.join(", ", ["\"%s\"" % x for x in data_types])
        root_url = "http://brainomics.cea.fr/localizer/"

        base_query = ("Any X,XT,XL,XI,XF,XD WHERE X is Scan, X type XT, "
                      "X concerns S, "
                      "X label XL, X identifier XI, "
                      "X format XF, X description XD, "
                      'S identifier <= "%s", ' % (subject_id_max, ) +
                      'X type IN(%(types)s), X label "%(label)s"')

        urls = ["%sbrainomics_data_%d.zip?rql=%s&vid=data-zip"
                % (root_url, i,
                   _urllib.parse.quote(base_query % {"types": rql_types,
                                              "label": c},
                                safe=',()'))
                for c, i in zip(contrasts_wrapped, contrasts_indices)]
        filenames = []
        for subject_id in subject_ids:
            for data_type in data_types:
                for contrast_id, contrast in enumerate(contrasts_wrapped):
                    name_aux = str.replace(
                        str.join('_', [data_type, contrast]), ' ', '_')
                    file_path = os.path.join(
                        "brainomics_data", subject_id, "%s.nii.gz" % name_aux)
                    file_tarball_url = urls[contrast_id]
                    filenames.append((file_path, file_tarball_url, opts))
        # Fetch masks if asked by user
        if get_masks:
            urls.append("%sbrainomics_data_masks.zip?rql=%s&vid=data-zip"
                        % (root_url,
                           _urllib.parse.quote(base_query % {"types": '"boolean mask"',
                                                      "label": "mask"},
                                        safe=',()')))
            for subject_id in subject_ids:
                file_path = os.path.join(
                    "brainomics_data", subject_id, "boolean_mask_mask.nii.gz")
                file_tarball_url = urls[-1]
                filenames.append((file_path, file_tarball_url, opts))
        # Fetch anats if asked by user
        if get_anats:
            urls.append("%sbrainomics_data_anats.zip?rql=%s&vid=data-zip"
                        % (root_url,
                           _urllib.parse.quote(base_query % {"types": '"normalized T1"',
                                                      "label": "anatomy"},
                                        safe=',()')))
            for subject_id in subject_ids:
                file_path = os.path.join(
                    "brainomics_data", subject_id,
                    "normalized_T1_anat_defaced.nii.gz")
                file_tarball_url = urls[-1]
                filenames.append((file_path, file_tarball_url, opts))
        # Fetch subject characteristics (separated in two files)
        if url is None:
            url_csv = ("%sdataset/cubicwebexport.csv?rql=%s&vid=csvexport"
                       % (root_url, _urllib.parse.quote("Any X WHERE X is Subject")))
            url_csv2 = ("%sdataset/cubicwebexport2.csv?rql=%s&vid=csvexport"
                        % (root_url,
                           _urllib.parse.quote("Any X,XI,XD WHERE X is QuestionnaireRun, "
                                        "X identifier XI, X datetime "
                                        "XD", safe=',')
                           ))
        else:
            url_csv = "%s/cubicwebexport.csv" % url
            url_csv2 = "%s/cubicwebexport2.csv" % url
        filenames += [("cubicwebexport.csv", url_csv, {}),
                      ("cubicwebexport2.csv", url_csv2, {})]

        # Actual data fetching
        files = self.fetcher.fetch(filenames, resume=resume, force=force, verbose=verbose)
        anats = None
        masks = None
        tmaps = None
        # combine data from both covariates files into one single recarray
        from numpy.lib.recfunctions import join_by
        ext_vars_file2 = files[-1]
        csv_data2 = np.recfromcsv(ext_vars_file2, delimiter=';')
        files = files[:-1]
        ext_vars_file = files[-1]
        csv_data = np.recfromcsv(ext_vars_file, delimiter=';')
        files = files[:-1]
        # join_by sorts the output along the key
        csv_data = join_by('subject_id', csv_data, csv_data2,
                           usemask=False, asrecarray=True)[:n_subjects]
        if get_anats:
            anats = files[-n_subjects:]
            files = files[:-n_subjects]
        if get_masks:
            masks = files[-n_subjects:]
            files = files[:-n_subjects]
        if get_tmaps:
            tmaps = files[1::2]
            files = files[::2]
        return Bunch(cmaps=files, tmaps=tmaps, masks=masks, anats=anats,
                     ext_vars=csv_data)


    def fetch_localizer_calculation_task(n_subjects=None, data_dir=None, url=None,
                                         verbose=1):
        """Fetch calculation task contrast maps from the localizer.

        This function is only a caller for the fetch_localizer_contrasts in order
        to simplify examples reading and understanding.
        The 'calculation (auditory and visual cue)' contrast is used.

        Parameters
        ----------
        n_subjects: int, optional
            The number of subjects to load. If None is given,
            all 94 subjects are used.

        data_dir: string, optional
            Path of the data directory. Used to force data storage in a specified
            location.

        url: string, optional
            Override download URL. Used for test only (or if you setup a mirror of
            the data).

        verbose: int, optional
            verbosity level (0 means no message).

        Returns
        -------
        data: Bunch
            Dictionary-like object, the interest attributes are :
            'cmaps': string list
                Paths to nifti contrast maps

        """
        data = fetch_localizer_contrasts(["calculation (auditory and visual cue)"],
                                         n_subjects=n_subjects,
                                         get_tmaps=False, get_masks=False,
                                         get_anats=False, data_dir=data_dir,
                                         url=url, resume=True, verbose=verbose)
        data.pop('tmaps')
        data.pop('masks')
        data.pop('anats')
        return data


def fetch_localizer_contrasts(contrasts, n_subjects=None, get_tmaps=False,
                              get_masks=False, get_anats=False,
                              data_dir=None, url=None, resume=True, verbose=1):
    return BrainomicsDataset(data_dir=data_dir).fetch(contrasts=contrasts,
                                                      n_subjects=n_subjects,
                                                      get_tmaps=get_tmaps,
                                                      get_masks=get_masks,
                                                      get_anats=get_anats,
                                                      url=url,
                                                      resume=resume,
                                                      verbose=verbose)
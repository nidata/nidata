# *- encoding: utf-8 -*-
# Author: Alexandre Abraham, Philippe Gervais
# License: simplified BSD

import os.path as op

from sklearn.datasets.base import Bunch

from ...core.datasets import HttpDataset


class NyuRestDataset(HttpDataset):
    """Download and loads the NYU resting-state test-retest dataset.

    Parameters
    ----------
    n_subjects: int, optional
        The number of subjects to load. If None is given, all the
        subjects are used.

    sessions: iterable of int, optional
        The sessions to load. Load only the first session by default.

    data_dir: string, optional
        Path of the data directory. Used to force data storage in a specified
        location. Default: None

    Returns
    -------
    data: sklearn.datasets.base.Bunch
        Dictionary-like object, the interest attributes are :
        'func': string list. Paths to functional images.
        'anat_anon': string list. Paths to anatomic images.
        'anat_skull': string. Paths to skull-stripped images.
        'session': numpy array. List of ids corresponding to images sessions.

    Notes
    ------
    This dataset is composed of 3 sessions of 26 participants (11 males).
    For each session, three sets of data are available:

    - anatomical:

      * anonymized data (defaced thanks to BIRN defacer)
      * skullstripped data (using 3DSkullStrip from AFNI)

    - functional

    For each participant, 3 resting-state scans of 197 continuous EPI
    functional volumes were collected :

    - 39 slices
    - matrix = 64 x 64
    - acquisition voxel size = 3 x 3 x 3 mm

    Sessions 2 and 3 were conducted in a single scan session, 45 min
    apart, and were 5-16 months after Scan 1.

    All details about this dataset can be found here :
    http://cercor.oxfordjournals.org/content/19/10/2209.full

    References
    ----------
    :Documentation:
        http://www.nitrc.org/docman/?group_id=274

    :Download:
        http://www.nitrc.org/frs/?group_id=274

    :Paper to cite:
        `The Resting Brain: Unconstrained yet Reliable
        <http://cercor.oxfordjournals.org/content/19/10/2209>`_
        Z. Shehzad, A.M.C. Kelly, P.T. Reiss, D.G. Gee, K. Gotimer,
        L.Q. Uddin, S.H. Lee, D.S. Margulies, A.K. Roy, B.B. Biswal,
        E. Petkova, F.X. Castellanos and M.P. Milham.

    :Other references:
        * `The oscillating brain: Complex and Reliable
          <http://dx.doi.org/10.1016/j.neuroimage.2009.09.037>`_
          X-N. Zuo, A. Di Martino, C. Kelly, Z. Shehzad, D.G. Gee,
          D.F. Klein, F.X. Castellanos, B.B. Biswal, M.P. Milham

        * `Reliable intrinsic connectivity networks: Test-retest
          evaluation using ICA and dual regression approach
          <http://dx.doi.org/10.1016/j.neuroimage.2009.10.080>`_,
          X-N. Zuo, C. Kelly, J.S. Adelstein, D.F. Klein,
          F.X. Castellanos, M.P. Milham

    """

    def fetch(self, n_subjects=None, sessions=[1], resume=True,
              force=False, verbose=1):

        fa1 = 'http://www.nitrc.org/frs/download.php/1071/NYU_TRT_session1a.tar.gz'
        fb1 = 'http://www.nitrc.org/frs/download.php/1072/NYU_TRT_session1b.tar.gz'
        fa2 = 'http://www.nitrc.org/frs/download.php/1073/NYU_TRT_session2a.tar.gz'
        fb2 = 'http://www.nitrc.org/frs/download.php/1074/NYU_TRT_session2b.tar.gz'
        fa3 = 'http://www.nitrc.org/frs/download.php/1075/NYU_TRT_session3a.tar.gz'
        fb3 = 'http://www.nitrc.org/frs/download.php/1076/NYU_TRT_session3b.tar.gz'
        fa1_opts = {'uncompress': True,
                    'move': op.join('session1', 'NYU_TRT_session1a.tar.gz')}
        fb1_opts = {'uncompress': True,
                    'move': op.join('session1', 'NYU_TRT_session1b.tar.gz')}
        fa2_opts = {'uncompress': True,
                    'move': op.join('session2', 'NYU_TRT_session2a.tar.gz')}
        fb2_opts = {'uncompress': True,
                    'move': op.join('session2', 'NYU_TRT_session2b.tar.gz')}
        fa3_opts = {'uncompress': True,
                    'move': op.join('session3', 'NYU_TRT_session3a.tar.gz')}
        fb3_opts = {'uncompress': True,
                    'move': op.join('session3', 'NYU_TRT_session3b.tar.gz')}

        p_anon = op.join('anat', 'mprage_anonymized.nii.gz')
        p_skull = op.join('anat', 'mprage_skullstripped.nii.gz')
        p_func = op.join('func', 'lfo.nii.gz')

        subs_a = ['sub05676', 'sub08224', 'sub08889', 'sub09607', 'sub14864',
                  'sub18604', 'sub22894', 'sub27641', 'sub33259', 'sub34482',
                  'sub36678', 'sub38579', 'sub39529']
        subs_b = ['sub45463', 'sub47000', 'sub49401', 'sub52738', 'sub55441',
                  'sub58949', 'sub60624', 'sub76987', 'sub84403', 'sub86146',
                  'sub90179', 'sub94293']

        # Generate the list of files by session
        anat_anon_files = [
            [(op.join('session1', sub, p_anon), fa1, fa1_opts)
                for sub in subs_a]
            + [(op.join('session1', sub, p_anon), fb1, fb1_opts)
                for sub in subs_b],
            [(op.join('session2', sub, p_anon), fa2, fa2_opts)
                for sub in subs_a]
            + [(op.join('session2', sub, p_anon), fb2, fb2_opts)
                for sub in subs_b],
            [(op.join('session3', sub, p_anon), fa3, fa3_opts)
                for sub in subs_a]
            + [(op.join('session3', sub, p_anon), fb3, fb3_opts)
                for sub in subs_b]]

        anat_skull_files = [
            [(op.join('session1', sub, p_skull), fa1, fa1_opts)
                for sub in subs_a]
            + [(op.join('session1', sub, p_skull), fb1, fb1_opts)
                for sub in subs_b],
            [(op.join('session2', sub, p_skull), fa2, fa2_opts)
                for sub in subs_a]
            + [(op.join('session2', sub, p_skull), fb2, fb2_opts)
                for sub in subs_b],
            [(op.join('session3', sub, p_skull), fa3, fa3_opts)
                for sub in subs_a]
            + [(op.join('session3', sub, p_skull), fb3, fb3_opts)
                for sub in subs_b]]

        func_files = [
            [(op.join('session1', sub, p_func), fa1, fa1_opts)
                for sub in subs_a]
            + [(op.join('session1', sub, p_func), fb1, fb1_opts)
                for sub in subs_b],
            [(op.join('session2', sub, p_func), fa2, fa2_opts)
                for sub in subs_a]
            + [(op.join('session2', sub, p_func), fb2, fb2_opts)
                for sub in subs_b],
            [(op.join('session3', sub, p_func), fa3, fa3_opts)
                for sub in subs_a]
            + [(op.join('session3', sub, p_func), fb3, fb3_opts)
                for sub in subs_b]]

        max_subjects = len(subs_a) + len(subs_b)

        # Check arguments
        if n_subjects is None:
            n_subjects = len(subs_a) + len(subs_b)
        if n_subjects > max_subjects:
            warnings.warn('Warning: there are only %d subjects' % max_subjects)
            n_subjects = 25

        anat_anon = []
        anat_skull = []
        func = []
        session = []
        for i in sessions:
            if not (i in [1, 2, 3]):
                raise ValueError('NYU dataset session id must be in [1, 2, 3]')
            anat_anon += anat_anon_files[i - 1][:n_subjects]
            anat_skull += anat_skull_files[i - 1][:n_subjects]
            func += func_files[i - 1][:n_subjects]
            session += [i] * n_subjects

        anat_anon = self.fetcher.fetch(anat_anon, resume=resume,
                                       force=force, verbose=verbose)
        anat_skull = self.fetcher.fetch(anat_skull, resume=resume,
                                        force=force, verbose=verbose)
        func = self.fetcher.fetch(func, resume=resume,
                                  force=force, verbose=verbose)

        return Bunch(anat_anon=anat_anon, anat_skull=anat_skull, func=func,
                     session=session)


def fetch_nyu_rest(n_subjects=None, sessions=[1], data_dir=None, resume=True,
                   verbose=1):
    return NyuRestDataset(data_dir=data_dir).fetch(n_subjects=n_subjects,
                                                   sessions=sessions,
                                                   resume=resume,
                                                   verbose=verbose)

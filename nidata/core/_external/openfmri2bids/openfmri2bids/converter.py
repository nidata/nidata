from __future__ import print_function

import errno
import os
import shutil
import json
import re
from os import path
from glob import glob

import pandas as pd
import numpy as np

NII_HANDLING_OPTS = ['empty', 'move', 'copy', 'link']  # first entry is default


def sanitize_label(label):
    return re.sub("[^a-zA-Z0-9]*", "", label)

def handle_nii(opt, src=None, dest=None):
    """Moves / copies / links / creates a .nii.gz.
    Note: many options will raise an error if the dest exists.
    """
    if opt == 'empty':
        open(dest, "w").close()
    elif opt == 'copy':
        shutil.copy(src, dest)
    elif opt == 'move':
        shutil.move(src, dest)
    elif opt == 'link':
        os.symlink(src, dest)
    else:
        raise NotImplementedError('Unrecognized nii_handling value: %s' % opt)

def convert(source_dir, dest_dir, nii_handling=NII_HANDLING_OPTS[0], warning=print, ses=""):
    if ses:
        folder_ses = "ses-%s"%ses
        filename_ses = "%s_"%folder_ses
    else:
        folder_ses = ""
        filename_ses = ""

    def mkdir(path):
        try:
            os.makedirs(path)
        except OSError as exc: # Python >2.5
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise
    
    openfmri_subjects = [s.split(os.sep)[-1] for s in glob(path.join(source_dir, "sub*"))]
    print("OpenfMRI subject IDs: " + str(openfmri_subjects))
    n_digits = len(str(len(openfmri_subjects)))
    subject_template = "sub-%0" + str(n_digits) + "d"
    BIDS_subjects = [subject_template%int(s[-3:]) for s in openfmri_subjects]
    print("BIDS subject IDs: " + str(BIDS_subjects))
    
    mkdir(dest_dir)
    for openfmri_s, BIDS_s in zip(openfmri_subjects, BIDS_subjects):
        mkdir(path.join(dest_dir, BIDS_s))
        
    tasks = set([s[:7] for s in os.listdir(path.join(source_dir, openfmri_subjects[0], "BOLD")) if s.startswith("task")])
    
    tasks_dict = {}
    for task in tasks:
        tasks_dict[task] = {"runs": set([s[8:] for s in os.listdir(path.join(source_dir, openfmri_subjects[0], "BOLD")) if s.startswith(task)])}
    
    with open(os.path.join(source_dir, "models", "model001", "condition_key.txt")) as f:
        for line in f:
            if line.strip() == "":
                break
            items = line.split()
            task = items[0]
            condition = items[1]
            condition_name = " ".join(items[2:])
            if "conditions" not in tasks_dict[task]:
                tasks_dict[task]["conditions"] = {}
            tasks_dict[task]["conditions"][condition] = condition_name
    
    with open(os.path.join(source_dir, "task_key.txt")) as f:
        for line in f:
            words = line.split()
            tasks_dict[words[0]]['name'] = " ".join(words[1:])
    
    for openfmri_s, BIDS_s in zip(openfmri_subjects, BIDS_subjects):
        for task in tasks:
            for run in tasks_dict[task]["runs"]:
                if len(tasks_dict[task]["runs"]) == 1:
                    trg_run = ""
                else:
                    trg_run = "_run%s"%run[4:]
                mkdir(path.join(dest_dir, BIDS_s, folder_ses, "functional"))
                dst = path.join(dest_dir, 
                                BIDS_s,
                                folder_ses, 
                                "functional",
                                "%s_%s%s%s_bold.nii.gz"%(BIDS_s, filename_ses, "task-%s"%sanitize_label(tasks_dict[task]['name']), trg_run))
                src = path.join(source_dir, 
                                openfmri_s, 
                                "BOLD", 
                                "%s_%s"%(task, run), 
                                "bold.nii.gz")
                if not os.path.exists(src):
                    warning("%s does not exist"%src)
                    continue

                handle_nii(nii_handling, src=src, dest=dst)
    
    anatomy_mapping = {"highres": "T1w",
                       "inplane": "inplaneT2"}
                    
    for openfmri_s, BIDS_s in zip(openfmri_subjects, BIDS_subjects):
        mkdir(path.join(dest_dir, BIDS_s, folder_ses, "anatomy"))
        for anatomy_openfmri, anatomy_bids in anatomy_mapping.iteritems():
            runs = [s[-10:-7] for s in glob(path.join(source_dir, 
                                                      openfmri_s, 
                                                      "anatomy", 
                                                      "%s*.nii.gz"%anatomy_openfmri))]
            for run in runs:
                src_run = run
                if run == anatomy_openfmri[-3:]:
                    run = "001"
                    src_run=""
                # dirty hack
                try:
                    int(run)
                except:
                    continue
                
                if len([s for s in runs if s.isdigit()]) <= 1:
                    trg_run = ""
                else:
                    trg_run = "_run%s"%run[1:]
                    
                dst = path.join(dest_dir, 
                                BIDS_s,
                                folder_ses,
                                "anatomy",
                                "%s_%s%s%s.nii.gz"%(BIDS_s, filename_ses, anatomy_bids, trg_run))
                src = path.join(source_dir, 
                                openfmri_s, 
                                "anatomy", 
                                "%s%s.nii.gz"%(anatomy_openfmri, src_run))

                handle_nii(nii_handling, src=src, dest=dst)
    
    scan_parameters_dict = {}
    with open(os.path.join(source_dir, "scan_key.txt")) as f:
        for line in f:
            items = line.split()
            if items[0] == "TR":
                scan_parameters_dict["RepetitionTime"] = float(items[1])

    for openfmri_s, BIDS_s in zip(openfmri_subjects, BIDS_subjects):
        scans_dfs = []
        for task in tasks_dict.keys():
            for run in tasks_dict[task]["runs"]:
                if len(tasks_dict[task]["runs"]) == 1:
                    trg_run = ""
                else:
                    trg_run = "_run%s"%run[4:]

                dfs = []
                parametric_columns = []
                for condition_id, condition_name in tasks_dict[task]["conditions"].iteritems():
                    # TODO: check if onsets are in seconds
                    fpath = os.path.join(source_dir, 
                                       openfmri_s, 
                                       "model", 
                                       "model001", 
                                       "onsets", 
                                       "%s_%s"%(task, run), 
                                       "%s.txt"%condition_id)
                    if not os.path.exists(fpath):
                        warning("%s does not exist"%fpath)
                        continue
                    if os.stat(fpath).st_size == 0:
                        warning("%s is empty"%fpath)
                        continue
                    tmp_df = pd.read_csv(fpath,
                                         delimiter=r"\s+",
                                         names=["onset", "duration", "weight"], 
                                         header=None,
                                         engine="python",
                                         index_col=False,
                                         skip_blank_lines=True
                                        )
                    if tmp_df.duration.isnull().sum() > 0:
                        tmp_df = pd.read_csv(os.path.join(source_dir, 
                                                      openfmri_s, 
                                                      "model", 
                                                      "model001", 
                                                      "onsets", 
                                                      "%s_%s"%(task, run), 
                                                      "%s.txt"%condition_id),
                                         sep=" ",
                                         names=["onset", "duration", "weight"], 
                                         header=None,
                                         engine="python",
                                         index_col=False
                                        )
                    tmp_df["trial_type"] = condition_name
                    if len(tmp_df["weight"].unique()) != 1:
                        tmp_df[condition_name] = tmp_df["weight"]
                        parametric_columns.append(condition_name)
                    dfs.append(tmp_df)
                if dfs:
                    events_df = pd.concat(dfs, ignore_index=True)
                    if(parametric_columns):
                        events_df = events_df.sort(parametric_columns, na_position="first").drop_duplicates(["onset", "duration"], take_last=True)
                    events_df.drop('weight', axis=1, inplace=True)
                else:
                    continue
                
                
                beh_path = os.path.join(source_dir, 
                                        openfmri_s, 
                                        "behav",
                                        "%s_%s"%(task, run),
                                        "behavdata.txt")
                if os.path.exists(beh_path):
                    # There is a timing discrepancy between cond and behav - we need to use approximation to match them
                    if os.stat(beh_path).st_size == 0:
                        warning("%s is empty"%beh_path)
                        all_df = events_df
                    else:
                        unlabeled_beh = False
                        beh_df = pd.read_csv(beh_path,
                                             sep=None,
                                             #delimiter=r"\s+",
                                             engine="python",
                                             index_col=False
                                             )
                        if 'TrialOnset' in beh_df.columns:
                            beh_df.rename(columns={'TrialOnset': 'Onset'}, inplace=True)
                        if 'TR' in beh_df.columns:
                            beh_df["TR"] = (beh_df["TR"]-1)*scan_parameters_dict["RepetitionTime"]
                            beh_df["duration"] = beh_df['TR'].map(lambda x: scan_parameters_dict["RepetitionTime"])
                            beh_df.rename(columns={'TR': 'onset'}, inplace=True)
                            all_df = pd.concat([events_df, beh_df])
                            unlabeled_beh = True
                            
                        if "Onset" not in beh_df.columns:
                            if "onset" not in beh_df.columns:
                                beh_df_no_header = pd.read_csv(beh_path, sep=None, engine="python", index_col=False, header=None)
                                if len(beh_df_no_header.index) == len(events_df.index):
                                    events_df.sort(columns=["onset"], inplace=True)
                                    events_df.index = range(len(events_df))
                                    all_df = pd.concat([events_df, beh_df_no_header], axis=1)
                                    unlabeled_beh = True
                                elif len(beh_df.index) == len(events_df.index):
                                    events_df.sort(columns=["onset"], inplace=True)
                                    events_df.index = range(len(events_df))
                                    all_df = pd.concat([events_df, beh_df], axis=1)
                                    unlabeled_beh = True
                                else:
                                    # behdata are not events
                                    try:
                                        beh_df = pd.read_csv(beh_path,
                                                 sep=" ",
                                                 engine="python",
                                                 index_col=False
                                                 )
                                    except:
                                        beh_df = pd.read_csv(beh_path,
                                                 sep=",",
                                                 engine="python",
                                                 index_col=False
                                                 )
                                    beh_df["filename"] = path.join("functional",
                                                                   "%s_%s%s.nii.gz"%(BIDS_s, "task-%s"%sanitize_label(tasks_dict[task]['name']), trg_run))
                                    beh_df.set_index("filename", inplace=True)
                                    scans_dfs.append(beh_df)
                                    all_df = events_df
                            else:
                                beh_df.rename(columns={'onset': 'Onset'}, inplace=True)
                    
                        if not scans_dfs and not unlabeled_beh:
                            events_df["approx_onset"] = np.around(events_df["onset"],1)
                            beh_df["approx_onset"] = np.around(beh_df["Onset"],1)
        
                            all_df = pd.merge(left=events_df, right=beh_df, left_on="approx_onset", right_on="approx_onset", how="outer")
        
                            # Set onset to the average of onsets reported in cond and behav since we do not know which one is true
                            all_df["onset"].fillna(all_df["Onset"], inplace=True)
                            all_df["Onset"].fillna(all_df["onset"], inplace=True)
                            all_df["onset"] = (all_df["onset"]+all_df["Onset"])/2.0
                            all_df = all_df.drop(["Onset","approx_onset"], axis=1)
                else:
                    all_df = events_df
                
                all_df.sort(columns=["onset"], inplace=True)
                dest = path.join(dest_dir, 
                                 BIDS_s,
                                 folder_ses,
                                 "functional",
                                 "%s_%s%s%s_events.tsv"%(BIDS_s, filename_ses, "task-%s"%sanitize_label(tasks_dict[task]['name']), trg_run))
                #remove rows with zero duration:
                if (all_df.duration == 0).sum() > 0:
                    warning("%s original data had events with zero duration - removing."%dest)
                    warning(str(all_df[all_df.duration == 0] ))
                    all_df = all_df[all_df.duration != 0]
                # put onset, duration and trial_type in front
                cols = all_df.columns.tolist()
                cols.insert(0, cols.pop(cols.index("onset")))
                cols.insert(1, cols.pop(cols.index("duration")))
                cols.insert(2, cols.pop(cols.index("trial_type")))
                all_df = all_df[cols]
                
                all_df.to_csv(dest, sep="\t", na_rep="n/a", index=False)
                
        if scans_dfs:
            all_df = pd.concat(scans_dfs)
            all_df.to_csv(path.join(dest_dir, 
                                    BIDS_s,
                                    folder_ses,
                                    "%s%s_scans.tsv"%(filename_ses, BIDS_s)), sep="\t", na_rep="n/a", index=True)
            
    dem_file = os.path.join(source_dir,"demographics.txt")
    if not os.path.exists(dem_file):
        warning("%s does not exist"%dem_file)
    else:
        id_dict = dict(zip(openfmri_subjects, BIDS_subjects))
        participants = pd.read_csv(dem_file, delimiter=r"\s+", skip_blank_lines=True)
        if "subject_id" in participants.columns:
            participants["subject_id"] = participants["subject_id"].apply(lambda x: subject_template%int(x))
        else:
            participants = pd.read_csv(dem_file, delimiter=r"\s+", header=None, names=["dataset", "subject_id", "sex", "age", "handedness", "ethnicity"], skip_blank_lines=True).drop(["dataset"], axis=1)
            participants["subject_id"] = participants["subject_id"].apply(lambda x: id_dict[x])
        participants = participants.dropna(axis=1,how='all')
        participants.to_csv(os.path.join(dest_dir, "participants.tsv"), sep="\t", index=False, na_rep="n/a")
    
    for task in tasks:
        scan_parameters_dict["TaskName"] = tasks_dict[task]['name']
        json.dump(scan_parameters_dict, open(os.path.join(dest_dir, 
                                                          "%stask-%s_bold.json"%(filename_ses, sanitize_label(tasks_dict[task]['name']))), "w"),
                  sort_keys=True, indent=4, separators=(',', ': '))

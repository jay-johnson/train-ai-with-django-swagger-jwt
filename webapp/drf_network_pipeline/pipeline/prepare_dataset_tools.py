import logging
import pandas as pd
import glob
import copy
import random
from network_pipeline.consts import VALID
from network_pipeline.consts import INVALID
from network_pipeline.utils import ppj
from network_pipeline.utils import rnow
from network_pipeline.log.setup_logging import setup_logging
from celery_connectors.utils import ev


setup_logging()
name = "prepare"
log = logging.getLogger(name)


def find_all_headers(pipeline_files=[],
                     label_rules=None):
    log.info("find_all_headers - START")

    headers = ["src_file"]
    headers_dict = {"src_file": None}

    if label_rules:
        headers = ["src_file", "label_value", "label_name"]
        headers_dict = {"src_file": None,
                        "label_value": None,
                        "label_name": None}

    for c in pipeline_files:
        df = pd.read_csv(c)
        for h in df.columns.values:
            if h not in headers_dict:
                headers_dict[h] = "{}_{}".format(
                                    c,
                                    h)
                headers.append(h)
        # end for all headers in the file
    # end for all files to find common_headers

    log.info(("headers={}")
             .format(len(headers)))

    log.info("find_all_headers - END")
    return headers, headers_dict
# end of find_all_headers


def build_csv(
        pipeline_files=[],
        fulldata_file=None,
        clean_file=None,
        post_proc_rules=None,
        label_rules=None,
        meta_suffix="metadata.json"):

    save_node = {
        "status": INVALID,
        "pipeline_files": pipeline_files,
        "post_proc_rules": post_proc_rules,
        "label_rules": label_rules,
        "fulldata_file": fulldata_file,
        "fulldata_metadata_file": None,
        "clean_file": clean_file,
        "clean_metadata_file": None,
        "features_to_process": [],
        "feature_to_predict": None,
        "ignore_features": [],
        "df_json": {}
    }

    if not fulldata_file:
        log.error("missing fulldata_file - stopping")
        save_node["status"] = INVALID
        return save_node
    if not clean_file:
        log.error("missing clean_file - stopping")
        save_node["status"] = INVALID
        return save_node

    log.info("build_csv - START")

    common_headers, \
        headers_dict = find_all_headers(
                            pipeline_files=pipeline_files)

    log.info(("num common_headers={} headers={}")
             .format(len(common_headers),
                     common_headers))

    # since the headers can be different we rebuild a new one:

    hdrs = {}
    for h in common_headers:
        hdrs[h] = None

    features_to_process = []
    feature_to_predict = None
    ignore_features = []

    set_if_above = None
    labels = []
    label_values = []
    if label_rules:
        set_if_above = label_rules["set_if_above"]
        labels = label_rules["labels"]
        label_values = label_rules["label_values"]
    if post_proc_rules:
        if "predict_feature" in post_proc_rules:
            feature_to_predict = post_proc_rules["predict_feature"]
    if not feature_to_predict:
        if "label_name" in hdrs:
            feature_to_predict = "label_name"

    all_rows = []
    num_done = 0
    total_files = len(pipeline_files)
    for c in pipeline_files:
        log.info(("merging={}/{} csv={}")
                 .format(num_done,
                         total_files,
                         c))
        cf = pd.read_csv(c)
        log.info((" processing rows={}")
                 .format(len(cf.index)))
        for index, row in cf.iterrows():
            valid_row = True
            new_row = copy.deepcopy(hdrs)
            new_row["src_file"] = c
            for k in hdrs:
                if k in row:
                    new_row[k] = row[k]
            # end of for all headers to copy in

            if label_rules:
                test_rand = random.randint(0, 100)
                if test_rand > set_if_above:
                    new_row["label_value"] = label_values[1]
                    new_row["label_name"] = labels[1]
                else:
                    new_row["label_value"] = label_values[0]
                    new_row["label_name"] = labels[0]
            # end of applying label rules

            if valid_row:
                all_rows.append(new_row)
        # end of for all rows in this file

        num_done += 1
    # end of building all files into one list

    log.info(("fulldata rows={} generating df")
             .format(len(all_rows)))
    df = pd.DataFrame(all_rows)
    log.info(("df rows={} headers={}")
             .format(len(df.index),
                     df.columns.values))

    if ev("CONVERT_DF",
          "0") == "1":
        log.info("converting df to json")
        save_node["df_json"] = df.to_json()

    if clean_file:
        log.info(("writing fulldata_file={}")
                 .format(fulldata_file))
        df.to_csv(fulldata_file,
                  sep=',',
                  encoding='utf-8',
                  index=False)
        log.info(("done writing fulldata_file={}")
                 .format(fulldata_file))

        if post_proc_rules:

            clean_metadata_file = ""

            features_to_process = []
            ignore_features = []
            if label_rules:
                if feature_to_predict:
                    ignore_features = [feature_to_predict]

            if "drop_columns" in post_proc_rules:
                for p in post_proc_rules["drop_columns"]:
                    if p in headers_dict:
                        ignore_features.append(p)
                # post proce filter more features out
                # for non-int/float types

                for d in df.columns.values:
                    add_this_one = True
                    for i in ignore_features:
                        if d == i:
                            add_this_one = False
                            break
                    if add_this_one:
                        features_to_process.append(d)
                # for all df columns we're not ignoring...
                # add them as features to process

                fulldata_metadata_file = "{}/fulldata_{}".format(
                    "/".join(fulldata_file.split("/")[:-1]),
                    meta_suffix)
                log.info(("writing fulldata metadata file={}")
                         .format(fulldata_metadata_file))
                header_data = {"headers": list(df.columns.values),
                               "output_type": "fulldata",
                               "pipeline_files": pipeline_files,
                               "post_proc_rules": post_proc_rules,
                               "label_rules": label_rules,
                               "features_to_process": features_to_process,
                               "feature_to_predict": feature_to_predict,
                               "ignore_features": ignore_features,
                               "created": rnow()}

                with open(fulldata_metadata_file, "w") as otfile:
                    otfile.write(str(ppj(header_data)))

                keep_these = features_to_process
                if feature_to_predict:
                    keep_these.append(feature_to_predict)

                log.info(("creating new clean_file={} "
                          "keep_these={} "
                          "predict={}")
                         .format(clean_file,
                                 keep_these,
                                 feature_to_predict))

                # need to remove all columns that are all nan
                clean_df = df[keep_these].dropna(
                                axis=1, how='all').dropna()

                cleaned_features = clean_df.columns.values
                cleaned_to_process = []
                cleaned_ignore_features = []
                for c in cleaned_features:
                    if feature_to_predict:
                        if c == feature_to_predict:
                            cleaned_ignore_features.append(c)
                    else:
                        keep_it = True
                        for ign in ignore_features:
                            if c == ign:
                                cleaned_ignore_features.append(c)
                                keep_it = False
                                break
                        # end of for all feaures to remove
                        if keep_it:
                            cleaned_to_process.append(c)
                # end of new feature columns

                log.info(("writing DROPPED clean_file={} "
                          "features_to_process={} "
                          "ignore_features={} "
                          "predict={}")
                         .format(clean_file,
                                 cleaned_to_process,
                                 cleaned_ignore_features,
                                 feature_to_predict))

                write_clean_df = clean_df.drop(
                    columns=cleaned_ignore_features
                )
                log.info(("cleaned_df rows={}")
                         .format(len(write_clean_df.index)))
                write_clean_df.to_csv(
                         clean_file,
                         sep=',',
                         encoding='utf-8',
                         index=False)

                clean_metadata_file = "{}/cleaned_{}".format(
                    "/".join(clean_file.split("/")[:-1]),
                    meta_suffix)
                log.info(("writing clean metadata file={}")
                         .format(clean_metadata_file))
                header_data = {"headers": list(write_clean_df.columns.values),
                               "output_type": "clean",
                               "pipeline_files": pipeline_files,
                               "post_proc_rules": post_proc_rules,
                               "label_rules": label_rules,
                               "features_to_process": cleaned_to_process,
                               "feature_to_predict": feature_to_predict,
                               "ignore_features": cleaned_ignore_features,
                               "created": rnow()}
                with open(clean_metadata_file, "w") as otfile:
                    otfile.write(str(ppj(header_data)))
            else:

                for d in df.columns.values:
                    add_this_one = True
                    for i in ignore_features:
                        if d == i:
                            add_this_one = False
                            break
                    if add_this_one:
                        features_to_process.append(d)
                # for all df columns we're not ignoring...
                # add them as features to process

                fulldata_metadata_file = "{}/fulldata_{}".format(
                    "/".join(fulldata_file.split("/")[:-1]),
                    meta_suffix)
                log.info(("writing fulldata metadata file={}")
                         .format(fulldata_metadata_file))
                header_data = {"headers": list(df.columns.values),
                               "output_type": "fulldata",
                               "pipeline_files": pipeline_files,
                               "post_proc_rules": post_proc_rules,
                               "label_rules": label_rules,
                               "features_to_process": features_to_process,
                               "feature_to_predict": feature_to_predict,
                               "ignore_features": ignore_features,
                               "created": rnow()}

                with open(fulldata_metadata_file, "w") as otfile:
                    otfile.write(str(ppj(header_data)))

                keep_these = features_to_process
                if feature_to_predict:
                    keep_these.append(feature_to_predict)

                log.info(("creating new clean_file={} "
                          "keep_these={} "
                          "predict={}")
                         .format(clean_file,
                                 keep_these,
                                 feature_to_predict))

                # need to remove all columns that are all nan
                clean_df = df[keep_these].dropna(
                                axis=1, how='all').dropna()

                cleaned_features = clean_df.columns.values
                cleaned_to_process = []
                cleaned_ignore_features = []
                for c in cleaned_features:
                    if feature_to_predict:
                        if c == feature_to_predict:
                            cleaned_ignore_features.append(c)
                    else:
                        keep_it = True
                        for ign in ignore_features:
                            if c == ign:
                                cleaned_ignore_features.append(c)
                                keep_it = False
                                break
                        # end of for all feaures to remove
                        if keep_it:
                            cleaned_to_process.append(c)
                # end of new feature columns

                log.info(("writing DROPPED clean_file={} "
                          "features_to_process={} "
                          "ignore_features={} "
                          "predict={}")
                         .format(clean_file,
                                 cleaned_to_process,
                                 cleaned_ignore_features,
                                 feature_to_predict))

                write_clean_df = clean_df.drop(
                    columns=cleaned_ignore_features
                )
                log.info(("cleaned_df rows={}")
                         .format(len(write_clean_df.index)))
                write_clean_df.to_csv(
                         clean_file,
                         sep=',',
                         encoding='utf-8',
                         index=False)

                clean_metadata_file = "{}/cleaned_{}".format(
                    "/".join(clean_file.split("/")[:-1]),
                    meta_suffix)
                log.info(("writing clean metadata file={}")
                         .format(clean_metadata_file))
                header_data = {"headers": list(write_clean_df.columns.values),
                               "output_type": "clean",
                               "pipeline_files": pipeline_files,
                               "post_proc_rules": post_proc_rules,
                               "label_rules": label_rules,
                               "features_to_process": cleaned_to_process,
                               "feature_to_predict": feature_to_predict,
                               "ignore_features": cleaned_ignore_features,
                               "created": rnow()}
                with open(clean_metadata_file, "w") as otfile:
                    otfile.write(str(ppj(header_data)))

            # end of if/else

            save_node["clean_file"] = clean_file
            save_node["clean_metadata_file"] = clean_metadata_file

            log.info(("done writing clean_file={}")
                     .format(clean_file))
        # end of post_proc_rules

        save_node["fulldata_file"] = fulldata_file
        save_node["fulldata_metadata_file"] = fulldata_metadata_file

        save_node["status"] = VALID
    # end of writing the file

    save_node["features_to_process"] = features_to_process
    save_node["feature_to_predict"] = feature_to_predict
    save_node["ignore_features"] = ignore_features

    log.info("build_csv - END")

    return save_node
# end of build_csv


def find_all_pipeline_csvs(
        csv_glob_path="/opt/datasets/**/*.csv"):

    log.info("finding pipeline csvs in dir={}".format(csv_glob_path))

    pipeline_files = []

    for csv_file in glob.iglob(csv_glob_path,
                               recursive=True):
        log.info(("adding file={}")
                 .format(csv_file))
        pipeline_files.append(csv_file)
    # end of for all csvs

    log.info(("pipeline files={}")
             .format(len(pipeline_files)))

    return pipeline_files
# end of find_all_pipeline_csvs

import pandas
import numpy as np
import matplotlib.pyplot as plt


def get_from_pie_plot(df, minimum_emails=25):
    """
    Plot distribution of emails sorted by sender

    Args:
        df (pandas.DataFrame): Dataframe with emails
        minimum_emails (int): number of emails from one sender to consider as individual sender
    """
    df["from"].value_counts()
    dict_values = np.array(list(df["from"].value_counts().to_dict().values()))
    dict_keys = np.array(list(df["from"].value_counts().to_dict().keys()))
    ind = dict_values > minimum_emails
    dict_values_red = dict_values[ind].tolist()
    dict_keys_red = dict_keys[ind].tolist()
    dict_values_red.append(sum(dict_values[~ind]))
    dict_keys_red.append("other")

    fig1, ax1 = plt.subplots()
    ax1.pie(dict_values_red, labels=dict_keys_red)
    ax1.axis("equal")
    plt.show()


def get_labels_pie_plot(gmail, df):
    """
    Plot distribution of emails sorted by label

    Args:
        gmail (pydatamail_google.GoogleMailBase): Interface to Google Mail
        df (pandas.DataFrame): Dataframe with emails
    """
    label_lst = []
    for llst in df.labels.values:
        for ll in llst:
            label_lst.append(ll)

    label_lst = list(set(label_lst))
    label_lst = [label for label in label_lst if "Label_" in label]
    label_count_lst = [
        sum([True if label_select in label else False for label in df.labels])
        for label_select in label_lst
    ]
    label_convert_lst = [
        gmail._label_dict_inverse[label]
        if label in gmail._label_dict.values()
        else label
        for label in label_lst
    ]
    ind = np.argsort(label_count_lst)

    fig1, ax1 = plt.subplots()
    ax1.pie(
        np.array(label_count_lst)[ind][::-1],
        labels=np.array(label_convert_lst)[ind][::-1],
    )
    ax1.axis("equal")
    plt.show()


def get_number_of_email_plot(df, steps=8, total=False):
    """
    Plot increase of emails over time

    Args:
        df (pandas.DataFrame): Dataframe with emails
        steps (int): number of dates on the x-axis
        total (bool): plot the total number of emails vs. monthly new emails
    """
    start_month = [d.year * 12 + d.month for d in pandas.to_datetime(df.date)]

    counts, month = np.histogram(start_month, bins=steps)
    if total:
        counts = np.cumsum(counts)
    width = np.mean((month - np.roll(month, 1))[1:])
    plt.bar(month[1:], counts, width=width)
    plt.xticks(
        np.linspace(np.min(start_month), np.max(start_month), steps),
        [
            str(int(month // 12)) + "-" + str(int(month % 12))
            for month in np.linspace(np.min(start_month), np.max(start_month), steps)
        ],
    )
    plt.xlabel("Date")
    plt.ylabel("Number of Emails")

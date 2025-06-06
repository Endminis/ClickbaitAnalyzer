import matplotlib.pyplot as plt
import seaborn as sns

def plot_histogram(df, column, bins, hue=None):
    plt.figure(figsize=(8, 5))
    sns.histplot(
        data=df,
        x=column,
        hue=hue,
        bins=bins,
        kde=True,
        stat='count',
        common_norm=False,
        alpha=0.4
    )
    title = f'Гістограма + KDE {column}'
    if hue:
        title += f' (hue={hue})'
    plt.title(title)
    plt.xlabel(column)
    plt.tight_layout()
    plt.show()


def plot_scatter(df, x_col, y_col):
    plt.figure()
    df.plot.scatter(x=x_col, y=y_col)
    plt.title(f'Scatter: {y_col} vs {x_col}')
    plt.tight_layout()
    plt.show()


def plot_pie(df, column):
    counts = df[column].value_counts()
    plt.figure()
    counts.plot.pie(autopct='%1.1f%%', startangle=90)
    plt.ylabel('')
    plt.title(f'Pie Chart of {column}')
    plt.tight_layout()
    plt.show()

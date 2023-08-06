import itertools
from string import Template

import ipywidgets as widgets
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from IPython.display import Math, display
from matplotlib.patches import Rectangle
from sklearn.cluster import KMeans
from sklearn.datasets import make_blobs
from sklearn.exceptions import NotFittedError
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    precision_score,
    recall_score,
)
from sklearn.utils.validation import check_is_fitted


class ConfusionMatrixWidget:
    def __init__(self, model, X_test, y_test):
        self.model = model
        self.X_test = X_test
        self.y_test = y_test
        self._y_pred = None
        self._cnf_matrix = None

    def __repr__(self):
        class_name = type(self).__name__
        model = type(self.model).__name__
        X_test = type(self.X_test).__name__
        y_test = type(self.y_test).__name__
        return "{}(model={}, X_test={}, y_test={})".format(
            class_name, model, X_test, y_test
        )

    def __str__(self):
        class_name = type(self).__name__
        model = type(self.model).__name__
        X_test = type(self.X_test).__name__
        y_test = type(self.y_test).__name__
        return "{}(model={}, X_test={}, y_test={})".format(
            class_name, model, X_test, y_test
        )

    def __generate_predictions(self, thresh=0.5):
        try:
            check_is_fitted(self.model)
        except NotFittedError:
            self.model.fit(self.X_test, self.y_test)

        try:
            pred_proba = self.model.predict_proba(self.X_test)[:, -1]
            self._y_pred = pred_proba > thresh
        except AttributeError:
            raise AttributeError(
                "Widget only works with models that have a `predict_proba` method."
            )

    def __generate_cnf(self, thresh=0.5, rot90=False):
        self.__generate_predictions(thresh)
        _cnf_matrix = confusion_matrix(self.y_test, self._y_pred)
        if rot90:
            _cnf_matrix = np.rot90(_cnf_matrix, axes=(1, 0))
        self._cnf_matrix = _cnf_matrix

    def __acc_score_equation(self, w, short_eq=False):
        with self.accuracy_plt:
            self.accuracy_plt.clear_output(wait=True)
            self.__generate_cnf(self.t_widget.value)
            tn, fp, fn, tp = self._cnf_matrix.ravel()
            score = round(sum([tp + tn]) / sum([tp, fp, fn, tn]), 2)
            if short_eq:
                s = r"""\text{Accuracy} = $SCORE"""
            else:
                s = r"""
                    \text{Accuracy} = \dfrac{
                        \color{orange}{$TP}
                        + \color{blue}{$TN}
                    }{
                        \color{orange}{$TP}
                        + \color{purple}{$FN}
                        + \color{blue}{$TN}
                        + \color{red}{$FP}
                    } = $SCORE
                """
            temp = Template(s).substitute(
                TP=tp, FP=fp, TN=tn, FN=fn, SCORE=score
            )
            display(Math(temp))

    def __precision_score_equation(self, w, short_eq=False):
        with self.precision_plt:
            self.precision_plt.clear_output(wait=True)
            self.__generate_cnf(self.t_widget.value)
            _, fp, _, tp = self._cnf_matrix.ravel()
            score = round(tp / (tp + fp), 2)
            if short_eq:
                s = r"""\text{Precision} = $SCORE"""
            else:
                s = r"""
                    \text{Precision} = \dfrac{
                        \color{orange}{$TP}
                    }{
                        \color{orange}{$TP}
                        + \color{red}{$FP}
                    } = $SCORE
                """
            temp = Template(s).substitute(TP=tp, FP=fp, SCORE=score)
            display(Math(temp))

    def __recall_score_equation(self, w, short_eq=False):
        with self.recall_plt:
            self.recall_plt.clear_output(wait=True)
            self.__generate_cnf(self.t_widget.value)
            _, _, fn, tp = self._cnf_matrix.ravel()
            score = round(tp / (tp + fn), 2)
            if short_eq:
                s = r"""\text{Recall} = $SCORE"""
            else:
                s = r"""
                    \text{Recall} = \dfrac{
                        \color{orange}{$TP}
                    }{
                        \color{orange}{$TP}
                        + \color{purple}{$FN}
                    } = $SCORE
                """
            temp = Template(s).substitute(TP=tp, FN=fn, SCORE=score)
            display(Math(temp))

    def __three_short(self, w):
        with self.three_short_plt:
            self.three_short_plt.clear_output(wait=True)
            self.__generate_cnf(self.t_widget.value)
            prec = round(
                precision_score(self.y_test, self._y_pred, zero_division=0), 2
            )
            acc = round(accuracy_score(self.y_test, self._y_pred), 2)
            rec = round(
                recall_score(self.y_test, self._y_pred, zero_division=0), 2
            )

            s = r"""
                \begin{align}
                    \text{Accuracy} & = $ACC\\
                    \text{Precision} & = $PREC\\
                    \text{Recall} & = $REC
                \end{align}
            """

            temp = Template(s).substitute(ACC=acc, PREC=prec, REC=rec)
            display(Math(temp))

    def __costs_equation(
        self, w, costs={"tn": 0, "fp": 500, "fn": 50000, "tp": 0}
    ):
        with self.costs_plt:
            self.costs_plt.clear_output(wait=True)
            self.__generate_cnf(self.t_widget.value)
            _, fp, fn, _ = self._cnf_matrix.ravel()
            fp_total = format(fp * costs["fp"], "6,d").replace(",", "{,}")
            fn_total = format(fn * costs["fn"], "6,d").replace(",", "{,}")
            grand_total = format(
                (fn * costs["fn"] + fp * costs["fp"]), "6,d"
            ).replace(",", "{,}")
            s = r"""
                    \begin{align}
                        \text{Wasted admin costs:} &~€ & $FP_TOTAL\\
                        \text{Wasted legal costs:} &~€ & $FN_TOTAL \\
                        \hline \\
                        \text{Total wasted costs:} &~€ & $GRAND_TOTAL
                    \end{align}
            """

            temp = Template(s).substitute(
                FP_TOTAL=fp_total, FN_TOTAL=fn_total, GRAND_TOTAL=grand_total
            )
            display(Math(temp))

    def __cnf_matrix(self, w, font_size=25):
        # https://github.com/jupyter-widgets/ipywidgets/issues/1919
        with self.cnf_plot:
            # Clear output
            self.cnf_plot.clear_output(wait=True)

            # Create confusion matrix
            self.__generate_cnf(self.t_widget.value, rot90=True)

            # Set colors
            color_matrix = np.array([["purple", "blue"], ["orange", "red"]])

            # Create fig
            fig = plt.figure(figsize=(10, 10))  # noQA F841
            ax = plt.subplot(111, aspect="equal")

            # Create plot
            for i, j in itertools.product(
                range(self._cnf_matrix.shape[0]),
                range(self._cnf_matrix.shape[1]),
            ):
                # Add patch
                sq = Rectangle(
                    xy=(i, j),
                    width=1,
                    height=1,
                    fc=color_matrix[i, j],
                    alpha=0.5,
                    ec="black",
                    label="Label",
                )
                ax.add_patch(sq)

                # Calculate label position
                rx, ry = sq.get_xy()
                cx = rx + sq.get_width() / 2.0
                cy = ry + sq.get_height() / 2.0

                # Add labels
                ax.annotate(
                    self._cnf_matrix[i, j],
                    (cx, cy),
                    color="black",
                    ha="center",
                    va="center",
                    fontsize=font_size,
                )
            ax.autoscale_view()
            ax.set_frame_on(False)
            ax.yaxis.label.set_size(font_size)
            ax.xaxis.label.set_size(font_size)
            plt.xticks(
                ticks=(0.5, 1.5), labels=[False, True], fontsize=font_size
            )
            plt.yticks(
                ticks=(0.5, 1.5), labels=[True, False], fontsize=font_size
            )
            plt.xlabel("Predicted label")
            plt.ylabel("True label")
            plt.show()

    def show(self):
        # Create widgets
        self.cnf_plot = widgets.Output(
            layout=widgets.Layout(height="300px", width="300px")
        )
        self.accuracy_plt = widgets.Output(
            layout=widgets.Layout(height="80px", width="400px")
        )
        self.precision_plt = widgets.Output(
            layout=widgets.Layout(height="80px", width="400px")
        )
        self.recall_plt = widgets.Output(
            layout=widgets.Layout(height="80px", width="400px")
        )
        self.t_widget = widgets.FloatSlider(
            value=0.5,
            min=0.0,
            max=1,
            step=0.1,
            description="Threshold:",
            continuous_update=False,
        )

        # Run helper funtions
        self.__cnf_matrix([])
        self.__acc_score_equation([])
        self.__precision_score_equation([])
        self.__recall_score_equation([])

        # Attach threshold widget to helper functions
        self.t_widget.observe(self.__cnf_matrix)
        self.t_widget.observe(self.__acc_score_equation)
        self.t_widget.observe(self.__precision_score_equation)
        self.t_widget.observe(self.__recall_score_equation)

        equations = widgets.VBox(
            [self.accuracy_plt, self.precision_plt, self.recall_plt]
        )
        hbx = widgets.HBox([self.cnf_plot, equations])
        display(self.t_widget, hbx)

    def show_eu(self, costs={"tn": 0, "fp": 500, "fn": 50000, "tp": 0}):
        try:
            costs = dict(costs)
        except ValueError:
            raise ValueError("`costs` should by a dictionary.")

        # Create widgets
        self.cnf_plot = widgets.Output(
            layout=widgets.Layout(height="300px", width="300px")
        )
        self.three_short_plt = widgets.Output(
            layout=widgets.Layout(height="150px", width="150px")
        )
        self.costs_plt = widgets.Output(
            layout=widgets.Layout(height="150px", width="300px")
        )
        self.t_widget = widgets.FloatSlider(
            value=0.5,
            min=0.0,
            max=1,
            step=0.1,
            description="Threshold:",
            continuous_update=False,
        )

        # Run helper funtions
        self.__cnf_matrix([])
        self.__three_short([])
        self.__costs_equation([])

        # Attach threshold widget to helper functions
        self.t_widget.observe(self.__cnf_matrix)
        self.t_widget.observe(self.__three_short)
        self.t_widget.observe(self.__costs_equation)

        vbx = widgets.VBox([self.three_short_plt, self.costs_plt])
        hbx = widgets.HBox([self.cnf_plot, vbx])
        display(self.t_widget, hbx)


class ClusterWidget:
    def __init__(
        self, X=None, n_clusters=3, seeds=np.array([[0, 4], [4, 2], [-2, 4]])
    ):
        self.n_clusters = n_clusters
        self.seeds = seeds
        if X is None:
            self.X = self.__make_cluster_data()
        else:
            self.X = X

    def __make_cluster_data(self):
        X, _ = make_blobs(
            n_samples=300,
            n_features=2,
            centers=3,
            cluster_std=2,
            random_state=0,
        )
        return X

    def __plot_kmeans_steps(self, w):
        with self.scatter_plot:
            step = self.step_widget.value
            self.scatter_plot.clear_output(wait=True)

            iters = step // 2
            if iters:
                kmeans = KMeans(
                    n_clusters=self.n_clusters,
                    max_iter=iters,
                    n_init=1,
                    init=self.seeds,
                )
                kmeans.fit(self.X)
                centroids = kmeans.cluster_centers_
                labels = kmeans.labels_
            else:
                centroids = self.seeds
                labels = "0.5"
            if step % 2:
                kmeans = KMeans(
                    n_clusters=self.n_clusters,
                    max_iter=iters + 1,
                    n_init=1,
                    init=self.seeds,
                )
                kmeans.fit(self.X)
                labels = kmeans.labels_

            title = (
                f"Step {step+0}: "
                + ["Set Centroids", "Assign Clusters"][step % 2]
            )
            if step > 1:
                title += " (again)"

            plt.scatter(*self.X.T, c=labels, cmap="viridis", alpha=0.5)
            plt.scatter(
                *centroids.T,
                c=range(self.n_clusters),
                cmap="viridis",
                marker="*",
                s=150,
                linewidths=1,
                edgecolors="k",
            )
            plt.title(title)
            plt.show()

    def show(self):
        # Create widgets
        self.scatter_plot = widgets.Output(
            layout=widgets.Layout(height="400px", width="400px")
        )
        self.step_widget = widgets.IntSlider(
            min=0,
            max=10,
            value=0,
            step=1,
            description="Step:",
            continuous_update=False,
        )

        # Run helper functions
        self.__plot_kmeans_steps([])

        # Attach widget
        self.step_widget.observe(self.__plot_kmeans_steps)

        # Layout
        vbx = widgets.VBox([self.step_widget, self.scatter_plot])

        # Display
        display(vbx)


class SCFClusterWidget:
    def __init__(self, x, y, n_clusters=3):
        self.x = pd.Series(x)
        self.y = pd.Series(y)
        self.n_clusters = n_clusters
        self.__set_seeds()

    def __repr__(self):
        class_name = type(self).__name__
        return f"{class_name}(x={self.x.shape}, y={self.y.shape}, n_clusters={self.n_clusters})"

    def __set_seeds(self):
        x_coords = np.linspace(
            self.x.min(), self.x.max(), self.n_clusters + 2
        )[1:-1].reshape(-1, 1)
        y_coords = np.linspace(
            self.y.min(), self.y.max(), self.n_clusters + 2
        )[1:-1].reshape(-1, 1)
        self.seeds = np.hstack([x_coords, y_coords])

    def make_model(self, step):
        iters = step // 2

        # Step 0
        if not iters:
            self.centroids = self.seeds
            self.labels = "0.5"

        # Step 2 and following evens
        if iters:
            self.kmeans = KMeans(
                n_clusters=self.n_clusters,
                max_iter=iters,
                n_init=1,
                init=self.seeds,
            )
            self.kmeans.fit(pd.DataFrame({"x": self.x, "y": self.y}))
            self.centroids = self.kmeans.cluster_centers_
            self.labels = self.kmeans.labels_

        # Step 1 and following odds
        if step % 2:
            self.kmeans = KMeans(
                n_clusters=self.n_clusters,
                max_iter=iters + 1,
                n_init=1,
                init=self.seeds,
            )
            self.kmeans.fit(pd.DataFrame({"x": self.x, "y": self.y}))
            self.labels = self.kmeans.labels_

    def __make_plot(self, w):
        with self.plot:
            plt.rcParams.update({"font.size": 25})
            self.plot.clear_output(wait=True)
            step = self.slider.value
            self.make_model(step)

            # Create fig
            fig, (ax1, ax2) = plt.subplots(
                nrows=1, ncols=2, figsize=(19, 7), constrained_layout=True
            )

            # Left axis, data
            ax1.scatter(
                self.x / 1e6,
                self.y / 1e6,
                c=self.labels,
                cmap="Accent",
                s=200,
                alpha=0.25,
            )

            # Left axis, centroids
            ax1.scatter(
                *(self.centroids / 1e6).T,
                c=range(self.n_clusters),
                cmap="Accent",
                alpha=1,
                marker="*",
                s=600,
                linewidths=1,
                edgecolors="black",
            )

            ax1.set_xlabel("Household Debt [$1M]")
            ax1.set_ylabel("Home Value [$1M]")

            # Right axis, log transform
            np.seterr(divide="ignore")
            log_x = np.log(self.x)
            log_y = np.log(self.y)
            log_centroids = np.log(self.centroids)
            np.seterr(divide="warn")

            # Right axis, data
            ax2.scatter(
                x=log_x,
                y=log_y,
                c=self.labels,
                cmap="Accent",
                alpha=0.25,
                s=200,
            )

            # Right axis, centroids
            ax2.scatter(
                *log_centroids.T,
                c=range(self.n_clusters),
                cmap="Accent",
                alpha=1,
                marker="*",
                s=600,
                linewidths=1,
                edgecolors="black",
            )

            ax2.set_xlabel("Household Debt [log($)]")
            ax2.set_ylabel("Home Value [log($)]")

            # Plot title
            title = (
                f"Step {step+0}: "
                + ["Set Centroids", "Assign Clusters"][step % 2]
            )
            if step > 1:
                title += " (again)"
            plt.suptitle(title)

            plt.show()
            matplotlib.rcdefaults()

    def show(self):
        # Create plot widget
        self.plot = widgets.Output(
            layout=widgets.Layout(height="220px", width="550px")
        )

        # Create slider widget
        self.slider = widgets.IntSlider(
            min=0,
            max=10,
            value=0,
            step=1,
            description="Step:",
            continuous_update=False,  # Always use
        )

        # Initialize plot function
        # Note empty list for `w`
        self.__make_plot([])

        # Attach slider to plot function
        self.slider.observe(self.__make_plot)

        # Set layout (vertical box)
        vbx = widgets.VBox([self.slider, self.plot])

        # Display widget
        display(vbx)


class ExampleWidget:
    """So that I don't forget how to do this."""

    def __init__(self):
        """Stuff you want from the user"""
        pass

    def __plot_datapoint(self, w):
        """Plots a single datapoint

        Parameters
        ----------
        w : list
            Dummy variable that prevents crashing. Don't use.
        """
        # `plot` defined below
        with self.plot:
            # Clear plot
            self.plot.clear_output(wait=True)
            # Make plot
            # If you need val from `slider`, defined below
            val = self.slider.value
            plt.scatter(val, val, s=200)
            plt.xlim((0, 6))
            plt.ylim((0, 6))
            plt.title("Hot to Plot")
            plt.show()

    def show(self):
        # Create plot widget
        self.plot = widgets.Output(
            layout=widgets.Layout(height="400px", width="400px")
        )

        # Crete slider widget
        self.slider = widgets.IntSlider(
            min=1,
            max=5,
            value=2,
            step=1,
            description="Val",
            continuous_update=False,  # Always use
        )

        # Initialize plot function
        # Note empty list for `w`
        self.__plot_datapoint([])

        # Attach slider to plot function
        self.slider.observe(self.__plot_datapoint)

        # Set layout (vertical box)
        vbx = widgets.VBox([self.slider, self.plot])

        # Display widget
        display(vbx)

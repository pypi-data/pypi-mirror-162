from relevanceai.apps.report_app.advanced_blocks.pyplot import PyplotReportBlock
from relevanceai.apps.report_app.advanced_blocks.plotly import PlotlyReportBlock
from relevanceai.apps.report_app.advanced_blocks.altair import AltairReportBlock


class ReportAdvancedBlocks(PyplotReportBlock, PlotlyReportBlock, AltairReportBlock):
    def plot_by_method(
        self, plot, plot_method, title="", height=None, width=None, add=True
    ):
        if plot_method == "plotly":
            self.plotly(plot, title=title, height=height, width=width, add=add)
        elif plot_method == "pyplot":
            self.pyplot(plot, title=title, height=height, width=width, add=add)

    # def plot_dendrogram()
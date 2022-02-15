from analyze_app_gui import AnalyzerApp
from analyze_app_service import Analyzer

if __name__ == "__main__":

    analyzer = Analyzer()
    app = AnalyzerApp(analyzer)
    app.mainloop()
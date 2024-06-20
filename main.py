from PSWC import PddiktiScrapper
import typer

app = typer.Typer(
    name="Pddikti Scrapper With Concurrency",
    help="Scrapper Pddikti with concurrency",
    no_args_is_help=True,
)
scraper = PddiktiScrapper()

@app.command()
def dump_all_univ(output: str = None, csv: bool = True, excel: bool = False):
    scraper.dump_all_univ(
        output=output,
        csv=csv,
        excel=excel,
        export=True
    )

@app.command()
def dump_all_prodi(output: str = None, max_workers: int = 5):
    scraper.get_all_univ_prodi_detail(
        output=output,
        max_workers=max_workers
    )
if __name__ == '__main__':
    app()
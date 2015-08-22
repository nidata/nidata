import click
from converter import convert


@click.command()
@click.argument('openfmri_dataset_path', required=True, type=click.Path(exists=True))
@click.argument('output_folder', required=True, type=click.Path())
@click.option('--first_session_label', type=(str))
@click.option('--additional_session', type=(str, click.Path()), multiple=True)
def main(openfmri_dataset_path, output_folder, first_session_label, additional_session):
    """Convert OpenfMRI dataset to BIDS."""
    click.echo('{0}, {1}.'.format(openfmri_dataset_path, output_folder))
    
    if additional_session:
        convert(openfmri_dataset_path, output_folder, ses=first_session_label, empty_nii=True)
        for session in additional_session:
            convert(session[1], output_folder, ses=session[0], empty_nii=True)
    else:
        convert(openfmri_dataset_path, output_folder, empty_nii=True)


if __name__ == '__main__':
    main()
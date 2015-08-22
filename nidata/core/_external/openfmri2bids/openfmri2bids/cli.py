import click

from .converter import convert, NII_HANDLING_OPTS

@click.command()
@click.argument('openfmri_dataset_path', required=True, type=click.Path(exists=True))
@click.argument('output_folder', required=True, type=click.Path())
@click.option('--first_session_label', type=(str))
@click.option('--additional_session', type=(str, click.Path()), multiple=True)
@click.option('--nii_handling', type=click.Choice(NII_HANDLING_OPTS), default=NII_HANDLING_OPTS[0])
def main(openfmri_dataset_path, output_folder, first_session_label,
         additional_session, nii_handling):
    """Convert OpenfMRI dataset to BIDS."""
    click.echo('{0}, {1}.'.format(openfmri_dataset_path, output_folder))

    if additional_session:
        convert(openfmri_dataset_path, output_folder,
                ses=first_session_label, nii_handling=nii_handling)
        for session in additional_session:
            convert(session[1], output_folder, ses=session[0],
                    nii_handling=nii_handling)
    else:
        convert(openfmri_dataset_path, output_folder,
                nii_handling=nii_handling)


if __name__ == '__main__':
    main()

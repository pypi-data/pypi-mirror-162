from dataclasses import dataclass
from pollination_dsl.function import Function, command, Inputs, Outputs


@dataclass
class AnnualDaylightMetrics(Function):
    """Calculate annual daylight metrics for annual daylight simulation."""

    folder = Inputs.folder(
        description='This folder is an output folder of annual daylight recipe. Folder '
        'should include grids_info.json and sun-up-hours.txt. The command uses the list '
        'in grids_info.json to find the result files for each sensor grid.',
        path='raw_results'
    )

    schedule = Inputs.file(
        description='Path to an annual schedule file. Values should be 0-1 separated '
        'by new line. If not provided an 8-5 annual schedule will be created.',
        path='schedule.txt', optional=True
    )

    thresholds = Inputs.str(
        description='A string to change the threshold for daylight autonomy and useful '
        'daylight illuminance. Valid keys are -t for daylight autonomy threshold, -lt '
        'for the lower threshold for useful daylight illuminance and -ut for the upper '
        'threshold. The default is -t 300 -lt 100 -ut 3000. The order of the keys is not '
        'important and you can include one or all of them. For instance if you only '
        'want to change the upper threshold to 2000 lux you should use -ut 2000 as '
        'the input.', default='-t 300 -lt 100 -ut 3000'
    )

    @command
    def calculate_annual_metrics(self):
        return 'honeybee-radiance-postprocess post-process annual-daylight raw_results ' \
            '--schedule schedule.txt {{self.thresholds}} --sub-folder metrics'

    # outputs
    annual_metrics = Outputs.folder(
        description='Annual metrics folder. This folder includes all the other '
        'subfolders which are also exposed as separate outputs.', path='metrics'
    )

    metrics_info = Outputs.file(
        description='A config file with metrics subfolders information for '
        'visualization. This config file is compatible with honeybee-vtk config.',
        path='metrics/config.json'
    )

    daylight_autonomy = Outputs.folder(
        description='Daylight autonomy results.', path='metrics/da'
    )

    continuous_daylight_autonomy = Outputs.folder(
        description='Continuous daylight autonomy results.', path='metrics/cda'
    )

    useful_daylight_illuminance_lower = Outputs.folder(
        description='Lower useful daylight illuminance results.',
        path='metrics/udi_lower'
    )

    useful_daylight_illuminance = Outputs.folder(
        description='Useful daylight illuminance results.', path='metrics/udi'
    )

    useful_daylight_illuminance_upper = Outputs.folder(
        description='Upper useful daylight illuminance results.',
        path='metrics/udi_upper'
    )
